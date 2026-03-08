"""AI Brain — the core intelligence layer using Claude.

Manages the system prompt, tool use, memory context, and conversation
with the Claude API. This is the "thinking" part of the agent.
"""

import json
import logging
import anthropic
from config import Config
from memory_store import MemoryStore
from skills import SkillManager
from tools import executor

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a personal AI assistant running as a Telegram bot. You are proactive, \
helpful, and capable of taking real actions on the user's machine.

## Your Capabilities
You can execute these tools by responding with JSON tool calls:

### run_shell
Execute shell commands on the host. Use for automation, scripts, system info.
Parameters: {"command": "...", "timeout": 30}

### read_file
Read a file from the filesystem.
Parameters: {"path": "..."}

### write_file
Write content to a file.
Parameters: {"path": "...", "content": "..."}

### list_directory
List files in a directory.
Parameters: {"path": "."}

### save_memory
Save a fact or preference to long-term memory.
Parameters: {"key": "...", "value": "...", "type": "fact|preference"}

### schedule_task
Schedule a recurring task using cron syntax.
Parameters: {"job_id": "...", "cron": "minute hour day month weekday", "prompt": "..."}

### remove_task
Remove a scheduled task.
Parameters: {"job_id": "..."}

## Guidelines
- Be concise but thorough.
- When the user asks you to DO something (not just answer), use the appropriate tool.
- For multi-step tasks, execute tools sequentially and report results.
- Remember user preferences and context across conversations.
- If a tool call fails, explain what happened and suggest alternatives.
- When responding to HEARTBEAT checks, only message if there's something useful to say.
- Format responses for Telegram (Markdown).

{skills_prompt}

{memory_context}
"""


class AIBrain:
    def __init__(self, memory: MemoryStore, skill_manager: SkillManager):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.memory = memory
        self.skill_manager = skill_manager
        self.conversation_cache: dict[int, list] = {}  # user_id -> recent messages

    async def think(self, user_id: int, user_message: str) -> str:
        # Build context
        facts = await self.memory.get_all_facts(user_id)
        prefs = await self.memory.get_all_preferences(user_id)
        recent = await self.memory.get_recent_messages(user_id, days=2)

        memory_context = ""
        if facts or prefs:
            memory_context = "## User Memory\n"
            if facts:
                memory_context += f"### Known Facts\n{facts}\n"
            if prefs:
                memory_context += f"### Preferences\n{prefs}\n"

        system = SYSTEM_PROMPT.format(
            skills_prompt=self.skill_manager.get_skills_prompt(),
            memory_context=memory_context,
        )

        # Build message history
        messages = self._get_conversation(user_id)
        messages.append({"role": "user", "content": user_message})

        # Save to memory
        await self.memory.save_message(user_id, "user", user_message)

        # Call Claude
        try:
            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=Config.MAX_TOKENS,
                system=system,
                messages=messages[-20:],  # keep last 20 turns
            )
        except Exception as e:
            logger.error("Claude API error: %s", e)
            return f"Error calling AI: {e}"

        assistant_text = response.content[0].text

        # Check for tool calls in response
        result = await self._process_tool_calls(user_id, assistant_text)

        # Update conversation cache
        messages.append({"role": "assistant", "content": result})
        self._set_conversation(user_id, messages[-20:])

        # Save to memory
        await self.memory.save_message(user_id, "assistant", result)

        return result

    async def _process_tool_calls(self, user_id: int, text: str) -> str:
        """Extract and execute tool calls from the AI response."""
        # Look for ```tool or ```json blocks that contain tool calls
        import re
        tool_pattern = re.compile(
            r"```(?:tool|json)\s*\n(\{.*?\})\s*\n```", re.DOTALL
        )
        matches = tool_pattern.findall(text)

        if not matches:
            return text

        results = []
        # Keep text outside tool blocks
        clean_text = tool_pattern.sub("", text).strip()
        if clean_text:
            results.append(clean_text)

        for match in matches:
            try:
                call = json.loads(match)
                tool_name = call.get("tool", "")
                result = await self._execute_tool(user_id, tool_name, call)
                results.append(f"**Tool: {tool_name}**\n```\n{json.dumps(result, indent=2)[:2000]}\n```")
            except json.JSONDecodeError:
                continue
            except Exception as e:
                results.append(f"Tool error: {e}")

        return "\n\n".join(results)

    async def _execute_tool(self, user_id: int, tool_name: str, params: dict) -> dict:
        if tool_name == "run_shell":
            return await executor.run_shell(
                params.get("command", ""),
                params.get("timeout", 30),
            )
        elif tool_name == "read_file":
            return await executor.read_file(params.get("path", ""))
        elif tool_name == "write_file":
            return await executor.write_file(
                params.get("path", ""), params.get("content", "")
            )
        elif tool_name == "list_directory":
            return await executor.list_directory(params.get("path", "."))
        elif tool_name == "save_memory":
            mem_type = params.get("type", "fact")
            if mem_type == "preference":
                await self.memory.save_preference(
                    user_id, params.get("key", ""), params.get("value", "")
                )
            else:
                await self.memory.save_fact(
                    user_id, params.get("key", ""), params.get("value", "")
                )
            return {"ok": True, "saved": params.get("key", "")}
        elif tool_name == "schedule_task":
            # Handled by bot.py via scheduler
            return {"ok": True, "note": "Task scheduling handled by scheduler"}
        elif tool_name == "remove_task":
            return {"ok": True, "note": "Task removal handled by scheduler"}
        else:
            return {"ok": False, "error": f"Unknown tool: {tool_name}"}

    def _get_conversation(self, user_id: int) -> list:
        return self.conversation_cache.get(user_id, []).copy()

    def _set_conversation(self, user_id: int, messages: list):
        self.conversation_cache[user_id] = messages
