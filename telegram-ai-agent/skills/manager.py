"""Extensible skills system — load SKILL.md files that teach the AI new capabilities.

Each skill is a Markdown file describing what the skill does, when to use it,
and any tool definitions it provides. The AI receives these as part of its
system prompt so it knows what it can do.
"""

import os
import re
from config import Config


class SkillManager:
    def __init__(self):
        self.skills_dir = Config.SKILLS_DIR
        os.makedirs(self.skills_dir, exist_ok=True)
        self.skills: dict[str, dict] = {}
        self._load_skills()

    def _load_skills(self):
        for fname in os.listdir(self.skills_dir):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(self.skills_dir, fname)
            with open(path, "r") as f:
                content = f.read(20_000)  # cap skill size at 20KB
            name = fname[:-3]
            description = ""
            match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
            if match:
                description = match.group(1)[:200]
            self.skills[name] = {
                "name": name,
                "description": description,
                "content": content,
                "path": path,
            }

    def reload(self):
        self.skills.clear()
        self._load_skills()

    def get_skills_prompt(self) -> str:
        if not self.skills:
            return ""
        parts = ["## Available Skills\n"]
        for skill in self.skills.values():
            parts.append(f"### {skill['name']}\n{skill['content']}\n---\n")
        return "\n".join(parts)

    def list_skills(self) -> list[dict]:
        return [
            {"name": s["name"], "description": s["description"]}
            for s in self.skills.values()
        ]

    def add_skill(self, name: str, content: str) -> str:
        # Limit total number of skills to prevent abuse
        if len(self.skills) >= 50:
            raise ValueError("Maximum skill limit (50) reached. Remove a skill first.")
        safe_name = re.sub(r"[^a-z0-9_-]", "_", name.lower())[:60]
        content = content[:20_000]  # cap content size
        path = os.path.join(self.skills_dir, f"{safe_name}.md")
        with open(path, "w") as f:
            f.write(content)
        self.reload()
        return path
