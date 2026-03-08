import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # AI Provider: "anthropic" or "openai" (covers Ollama, LM Studio, vLLM, etc.)
    AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic")

    # Anthropic settings
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

    # OpenAI-compatible settings (Ollama, LM Studio, vLLM, etc.)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama3")

    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
    MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "10"))

    ALLOWED_USERS = [
        int(uid.strip())
        for uid in os.getenv("ALLOWED_USERS", "").split(",")
        if uid.strip()
    ]

    ENABLE_TASK_EXECUTION = os.getenv("ENABLE_TASK_EXECUTION", "true").lower() == "true"
    SANDBOX_MODE = os.getenv("SANDBOX_MODE", "true").lower() == "true"
    HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))

    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "10"))

    MEMORY_DIR = os.getenv("MEMORY_DIR", "./memory")
    SKILLS_DIR = os.getenv("SKILLS_DIR", "./skills")
