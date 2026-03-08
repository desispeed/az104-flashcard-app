"""Persistent memory system using local Markdown files.

Stores conversation context, user preferences, and facts as markdown
documents — similar to OpenClaw's approach for deep personalization.
"""

import os
import re
import datetime
import aiofiles
from config import Config


class MemoryStore:
    def __init__(self):
        self.memory_dir = Config.MEMORY_DIR
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "conversations"), exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "facts"), exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "preferences"), exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "tasks"), exist_ok=True)

    def _user_dir(self, user_id: int, category: str) -> str:
        path = os.path.join(self.memory_dir, category, str(user_id))
        os.makedirs(path, exist_ok=True)
        return path

    # ── Conversation history ──

    async def save_message(self, user_id: int, role: str, content: str):
        today = datetime.date.today().isoformat()
        path = os.path.join(self._user_dir(user_id, "conversations"), f"{today}.md")
        now = datetime.datetime.now().strftime("%H:%M:%S")
        async with aiofiles.open(path, "a") as f:
            await f.write(f"\n### [{role}] {now}\n{content}\n")

    async def get_recent_messages(self, user_id: int, days: int = 3) -> str:
        messages = []
        conv_dir = self._user_dir(user_id, "conversations")
        today = datetime.date.today()
        for i in range(days):
            day = (today - datetime.timedelta(days=i)).isoformat()
            path = os.path.join(conv_dir, f"{day}.md")
            if os.path.exists(path):
                async with aiofiles.open(path, "r") as f:
                    messages.append(await f.read())
        return "\n".join(reversed(messages))

    # ── Facts / long-term memory ──

    async def save_fact(self, user_id: int, key: str, value: str):
        safe_key = re.sub(r"[^a-z0-9_-]", "_", key.lower())
        path = os.path.join(self._user_dir(user_id, "facts"), f"{safe_key}.md")
        async with aiofiles.open(path, "w") as f:
            await f.write(f"# {key}\n\n{value}\n\n_Updated: {datetime.datetime.now().isoformat()}_\n")

    async def get_all_facts(self, user_id: int) -> str:
        facts_dir = self._user_dir(user_id, "facts")
        facts = []
        for fname in sorted(os.listdir(facts_dir)):
            if fname.endswith(".md"):
                async with aiofiles.open(os.path.join(facts_dir, fname), "r") as f:
                    facts.append(await f.read())
        return "\n---\n".join(facts) if facts else ""

    # ── Preferences ──

    async def save_preference(self, user_id: int, key: str, value: str):
        safe_key = re.sub(r"[^a-z0-9_-]", "_", key.lower())
        path = os.path.join(self._user_dir(user_id, "preferences"), f"{safe_key}.md")
        async with aiofiles.open(path, "w") as f:
            await f.write(f"# Preference: {key}\n\n{value}\n")

    async def get_all_preferences(self, user_id: int) -> str:
        pref_dir = self._user_dir(user_id, "preferences")
        prefs = []
        for fname in sorted(os.listdir(pref_dir)):
            if fname.endswith(".md"):
                async with aiofiles.open(os.path.join(pref_dir, fname), "r") as f:
                    prefs.append(await f.read())
        return "\n".join(prefs) if prefs else ""

    # ── Scheduled tasks persistence ──

    async def save_scheduled_task(self, user_id: int, task_id: str, task_data: dict):
        path = os.path.join(self._user_dir(user_id, "tasks"), f"{task_id}.md")
        async with aiofiles.open(path, "w") as f:
            await f.write(f"# Scheduled Task: {task_id}\n\n")
            for k, v in task_data.items():
                await f.write(f"- **{k}**: {v}\n")

    async def get_scheduled_tasks(self, user_id: int) -> list[dict]:
        tasks_dir = self._user_dir(user_id, "tasks")
        tasks = []
        for fname in sorted(os.listdir(tasks_dir)):
            if fname.endswith(".md"):
                async with aiofiles.open(os.path.join(tasks_dir, fname), "r") as f:
                    content = await f.read()
                    tasks.append({"id": fname[:-3], "content": content})
        return tasks
