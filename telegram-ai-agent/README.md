# Telegram AI Agent

An OpenClaw-inspired personal AI assistant that runs as a Telegram bot. Supports **Claude** and any **OpenAI-compatible API** (Ollama, LM Studio, vLLM — zero API cost with local models). Features an agentic tool-use loop, persistent memory, cron scheduling, and self-improving skills.

## Features

- **Agentic Tool-Use Loop** — AI calls tools, inspects results, decides next step, repeats (up to 10 rounds per message)
- **Dual Provider** — Claude (Anthropic) or any OpenAI-compatible endpoint (Ollama, LM Studio, vLLM)
- **Task Execution** — Run shell commands, read/write files directly from chat
- **Natural Language Scheduling** — Say "remind me every morning at 9" and the AI converts it to cron
- **Persistent Memory** — Remembers facts, preferences, and conversations as Markdown files
- **Heartbeat** — Proactive background checks every N minutes
- **Self-Improving Skills** — AI can create new SKILL.md files to teach itself new capabilities
- **Extensible Skills** — Drop SKILL.md files into `skills/` or ask the AI to create them
- **Sandboxed** — Configurable command allowlist for safety

## Quick Start

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token

### 2. Choose Your AI Provider

**Option A: Claude (Anthropic API)**
```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
CLAUDE_MODEL=claude-sonnet-4-20250514
```

**Option B: Local / Free (Ollama, LM Studio, etc.)**
```bash
AI_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1   # Ollama default
OPENAI_MODEL=llama3
OPENAI_API_KEY=not-needed
```

### 3. Configure & Run

```bash
cp .env.example .env
# Edit .env with your tokens and provider choice

pip install -r requirements.txt
python bot.py
```

**Or with Docker:**
```bash
docker compose up -d
```

## How It Works — The Agentic Loop

Unlike a simple chatbot, this agent uses an **iterative tool-use loop**:

```
User message
  → AI decides which tool to call
    → Tool executes, returns result
      → AI sees result, decides next action
        → Repeat until task is complete (up to MAX_TOOL_ROUNDS)
          → Final response sent to user
```

This means the AI can handle multi-step tasks autonomously:
1. "Check disk space and clean up if over 80%" → runs `df`, analyzes output, runs cleanup if needed
2. "What's in my project folder?" → lists directory, reads key files, summarizes

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message + enable heartbeat |
| `/skills` | List loaded skills |
| `/jobs` | List scheduled jobs |
| `/cron <id> <cron> <prompt>` | Schedule a recurring task (or just ask in natural language) |
| `/rmjob <id>` | Remove a scheduled job |
| `/forget` | Clear conversation cache |
| `/heartbeat` | Toggle heartbeat on/off |

## Examples

**Run commands:**
> "Check my disk space"
> "Show me the last 10 git commits"

**Natural language scheduling:**
> "Every weekday at 8:30am, give me a morning briefing"
> "Remind me every Sunday at 6pm to review my weekly goals"

**Memory:**
> "Remember that my server IP is 192.168.1.100"
> "My preferred language is Python"

**Multi-step tasks:**
> "Read my docker-compose.yml, check if any containers are down, and restart them"

**Self-improving:**
> "Create a skill for monitoring Docker containers"

## Available Tools

| Tool | Description |
|------|-------------|
| `run_shell` | Execute shell commands (sandboxed) |
| `read_file` | Read file contents |
| `write_file` | Write/create files |
| `list_directory` | List directory contents |
| `save_memory` | Store facts/preferences to long-term memory |
| `schedule_task` | Create cron-scheduled recurring tasks |
| `remove_task` | Remove scheduled tasks |
| `list_tasks` | Show all scheduled tasks |
| `create_skill` | Create a new SKILL.md to learn new capabilities |

## Adding Skills

Create a Markdown file in `skills/`, or ask the AI to create one for you:

```markdown
# My Custom Skill

Description of what this skill does.

## When to use
Describe when the AI should use this skill.

## How to use
Provide tool call examples and patterns.
```

3 skills included out of the box: web search, system monitor, git helper.

## Architecture

```
telegram-ai-agent/
├── bot.py              # Telegram bot + command handlers
├── ai_brain.py         # Agentic loop + dual provider (Anthropic/OpenAI)
├── memory_store.py     # Persistent markdown-based memory
├── scheduler.py        # Cron jobs + heartbeat system
├── config.py           # Environment configuration
├── tools/
│   └── executor.py     # Sandboxed shell/file execution engine
├── skills/
│   ├── manager.py      # Skill loader + hot-reload
│   ├── web_search.md   # Web search skill
│   ├── system_monitor.md # System monitoring skill
│   └── git_helper.md   # Git operations skill
├── memory/             # Persisted conversations, facts, preferences
├── Dockerfile
└── docker-compose.yml
```

## Security

- **ALLOWED_USERS** — Restrict access to specific Telegram user IDs
- **SANDBOX_MODE** — Limits shell commands to a safe allowlist
- **Blocked patterns** — Prevents dangerous commands like `rm -rf /`
- **MAX_TOOL_ROUNDS** — Caps the agentic loop to prevent runaway execution
- All memory stored locally — data only sent to your chosen AI provider

## Configuration

See `.env.example` for all options. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `anthropic` | `anthropic` or `openai` |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Claude model (when using Anthropic) |
| `OPENAI_BASE_URL` | `http://localhost:11434/v1` | API endpoint (Ollama, LM Studio, etc.) |
| `OPENAI_MODEL` | `llama3` | Model name for OpenAI-compatible provider |
| `MAX_TOOL_ROUNDS` | `10` | Max tool-use iterations per message |
| `SANDBOX_MODE` | `true` | Restrict shell commands to allowlist |
| `HEARTBEAT_INTERVAL` | `30` | Minutes between heartbeat checks (0 = off) |
