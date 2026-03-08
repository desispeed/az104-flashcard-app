# Telegram AI Agent

An OpenClaw-inspired personal AI assistant that runs as a Telegram bot. Powered by Claude, it can execute tasks, remember context, run scheduled jobs, and learn new skills.

## Features

- **AI-Powered Chat** — Claude handles conversations with full context
- **Task Execution** — Run shell commands, read/write files from chat
- **Persistent Memory** — Remembers facts, preferences, and conversations (stored as Markdown)
- **Scheduled Tasks** — Cron-style recurring jobs (morning briefings, reminders, etc.)
- **Heartbeat** — Proactive background checks every 30 min
- **Extensible Skills** — Drop SKILL.md files into `skills/` to teach it new tricks
- **Sandboxed** — Configurable command allowlist for safety

## Quick Start

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token

### 2. Get an Anthropic API Key

Get one at [console.anthropic.com](https://console.anthropic.com)

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your tokens
```

### 4. Run

**With Python:**
```bash
pip install -r requirements.txt
python bot.py
```

**With Docker:**
```bash
docker compose up -d
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message + enable heartbeat |
| `/skills` | List loaded skills |
| `/jobs` | List scheduled jobs |
| `/cron <id> <min> <hr> <day> <mon> <dow> <prompt>` | Schedule a recurring task |
| `/rmjob <id>` | Remove a scheduled job |
| `/forget` | Clear conversation cache |
| `/heartbeat` | Toggle heartbeat on/off |

## Examples

**Run a command:**
> "Check my disk space"

**Schedule a daily briefing:**
> `/cron morning 0 9 * * * Give me today's top 5 tech news headlines`

**Remember something:**
> "Remember that my server IP is 192.168.1.100"

**File operations:**
> "Read the contents of ~/notes/todo.md"

## Adding Skills

Create a Markdown file in `skills/`:

```markdown
# My Custom Skill

Description of what this skill does.

## When to use
Describe when the AI should use this skill.

## How to use
Provide tool call examples.
```

The bot loads all `*.md` files from the skills directory on startup.

## Architecture

```
telegram-ai-agent/
├── bot.py              # Telegram bot + command handlers
├── ai_brain.py         # Claude AI integration + tool execution
├── memory_store.py     # Persistent markdown-based memory
├── scheduler.py        # Cron jobs + heartbeat system
├── config.py           # Environment configuration
├── tools/
│   └── executor.py     # Shell/file execution engine
├── skills/
│   ├── manager.py      # Skill loader
│   └── *.md            # Skill definitions
├── memory/             # Persisted conversations, facts, prefs
├── Dockerfile
└── docker-compose.yml
```

## Security

- **ALLOWED_USERS** — Restrict access to specific Telegram user IDs
- **SANDBOX_MODE** — Limits shell commands to a safe allowlist
- **Blocked patterns** — Prevents dangerous commands like `rm -rf /`
- All memory stored locally — no data sent anywhere except the Claude API

## Configuration

See `.env.example` for all options. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `SANDBOX_MODE` | `true` | Restrict commands to allowlist |
| `HEARTBEAT_INTERVAL` | `30` | Minutes between heartbeat checks (0 = off) |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `MAX_TOKENS` | `4096` | Max response length |
