import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

    ALLOWED_USERS = [
        int(uid.strip())
        for uid in os.getenv("ALLOWED_USERS", "").split(",")
        if uid.strip()
    ]

    ENABLE_TASK_EXECUTION = os.getenv("ENABLE_TASK_EXECUTION", "true").lower() == "true"
    SANDBOX_MODE = os.getenv("SANDBOX_MODE", "true").lower() == "true"
    HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))

    MEMORY_DIR = os.getenv("MEMORY_DIR", "./memory")
    SKILLS_DIR = os.getenv("SKILLS_DIR", "./skills")
