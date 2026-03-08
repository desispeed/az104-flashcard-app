#!/usr/bin/env python3
"""Telegram AI Agent — an OpenClaw-inspired personal AI assistant.

A Telegram bot that acts as a proactive personal AI agent. It can:
- Answer questions using Claude AI
- Execute shell commands and manage files
- Remember facts and preferences across conversations
- Run scheduled tasks (cron jobs) and heartbeat checks
- Load extensible skills from SKILL.md files

Usage:
    python bot.py              # Start the bot
    python bot.py --list-skills  # List available skills
"""

import argparse
import json
import logging
import re
import sys

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

from config import Config
from memory_store import MemoryStore
from ai_brain import AIBrain
from skills import SkillManager
from scheduler import TaskScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Globals ──
memory = MemoryStore()
skill_manager = SkillManager()
brain = AIBrain(memory, skill_manager)
scheduler = TaskScheduler()


# ── Auth ──

def is_authorized(user_id: int) -> bool:
    if not Config.ALLOWED_USERS:
        return True
    return user_id in Config.ALLOWED_USERS


# ── Telegram Handlers ──

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user.id):
        await update.message.reply_text("Unauthorized.")
        return

    await update.message.reply_text(
        f"Hey {user.first_name}! I'm your personal AI agent.\n\n"
        "I can answer questions, run commands, manage files, remember things, "
        "and run scheduled tasks — all through this chat.\n\n"
        "*Commands:*\n"
        "/start — This message\n"
        "/skills — List loaded skills\n"
        "/jobs — List scheduled jobs\n"
        "/cron — Schedule a task (e.g. /cron daily\\_report 0 9 \\* \\* \\* Give me a morning briefing)\n"
        "/rmjob — Remove a scheduled job\n"
        "/forget — Clear conversation history\n"
        "/heartbeat — Toggle heartbeat checks\n\n"
        "Or just send me a message and I'll help!",
        parse_mode=ParseMode.MARKDOWN,
    )

    # Start heartbeat for this user
    scheduler.start_heartbeat(user.id)


async def cmd_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    skills = skill_manager.list_skills()
    if not skills:
        await update.message.reply_text(
            "No skills loaded. Add SKILL.md files to the `skills/` directory."
        )
        return
    text = "*Loaded Skills:*\n" + "\n".join(
        f"• *{s['name']}* — {s['description']}" for s in skills
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    jobs = scheduler.list_jobs(update.effective_user.id)
    if not jobs:
        await update.message.reply_text("No scheduled jobs.")
        return
    text = "*Scheduled Jobs:*\n" + "\n".join(
        f"• `{j['id']}` — next: {j['next_run']}" for j in jobs
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_cron(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /cron <job_id> <min> <hour> <day> <month> <dow> <prompt>"""
    if not is_authorized(update.effective_user.id):
        return
    args = context.args
    if not args or len(args) < 7:
        await update.message.reply_text(
            "Usage: `/cron job_id min hour day month dow Your prompt here`\n"
            "Example: `/cron morning 0 9 * * * Give me a morning news briefing`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    job_id = args[0]
    cron_expr = " ".join(args[1:6])
    prompt = " ".join(args[6:])

    result = scheduler.add_cron_job(update.effective_user.id, job_id, cron_expr, prompt)
    await update.message.reply_text(result)


async def cmd_rmjob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/rmjob job_id`", parse_mode=ParseMode.MARKDOWN)
        return
    result = scheduler.remove_job(update.effective_user.id, context.args[0])
    await update.message.reply_text(result)


async def cmd_forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    brain.conversation_cache.pop(update.effective_user.id, None)
    await update.message.reply_text("Conversation history cleared. Long-term memory preserved.")


async def cmd_heartbeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    user_id = update.effective_user.id
    job_id = f"heartbeat_{user_id}"
    job = scheduler.scheduler.get_job(job_id)
    if job:
        scheduler.scheduler.remove_job(job_id)
        await update.message.reply_text("Heartbeat disabled.")
    else:
        scheduler.start_heartbeat(user_id)
        await update.message.reply_text(
            f"Heartbeat enabled (every {Config.HEARTBEAT_INTERVAL} min)."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all non-command text messages."""
    user = update.effective_user
    if not is_authorized(user.id):
        return

    text = update.message.text
    if not text:
        return

    # Show typing indicator
    await update.message.chat.send_action("typing")

    # Get AI response
    response = await brain.think(user.id, text)

    # Check if AI wants to schedule a task
    schedule_match = re.search(
        r'"tool"\s*:\s*"schedule_task".*?"job_id"\s*:\s*"([^"]+)".*?'
        r'"cron"\s*:\s*"([^"]+)".*?"prompt"\s*:\s*"([^"]+)"',
        response, re.DOTALL,
    )
    if schedule_match:
        job_id, cron_expr, prompt = schedule_match.groups()
        result = scheduler.add_cron_job(user.id, job_id, cron_expr, prompt)
        response += f"\n\n{result}"

    # Split long messages (Telegram max is 4096 chars)
    for chunk in _split_message(response):
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # Fallback without markdown if parsing fails
            await update.message.reply_text(chunk)


def _split_message(text: str, max_len: int = 4000) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to split at newline
        idx = text.rfind("\n", 0, max_len)
        if idx == -1:
            idx = max_len
        chunks.append(text[:idx])
        text = text[idx:].lstrip("\n")
    return chunks


# ── Scheduler callbacks ──

async def send_message_callback(user_id: int, text: str):
    """Send a message to a user (used by scheduler)."""
    app = _app
    if not app:
        return
    for chunk in _split_message(text):
        try:
            await app.bot.send_message(user_id, chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await app.bot.send_message(user_id, chunk)


async def ai_callback(user_id: int, prompt: str) -> str:
    """Query AI for a user (used by scheduler)."""
    return await brain.think(user_id, prompt)


# ── Main ──

_app: Application = None


def main():
    global _app

    parser = argparse.ArgumentParser(description="Telegram AI Agent")
    parser.add_argument("--list-skills", action="store_true", help="List loaded skills")
    args = parser.parse_args()

    if args.list_skills:
        skills = skill_manager.list_skills()
        if not skills:
            print("No skills loaded. Add SKILL.md files to skills/")
        else:
            for s in skills:
                print(f"  {s['name']}: {s['description']}")
        sys.exit(0)

    if not Config.TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)
    if not Config.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)

    # Build app
    _app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    _app.add_handler(CommandHandler("start", cmd_start))
    _app.add_handler(CommandHandler("skills", cmd_skills))
    _app.add_handler(CommandHandler("jobs", cmd_jobs))
    _app.add_handler(CommandHandler("cron", cmd_cron))
    _app.add_handler(CommandHandler("rmjob", cmd_rmjob))
    _app.add_handler(CommandHandler("forget", cmd_forget))
    _app.add_handler(CommandHandler("heartbeat", cmd_heartbeat))
    _app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Setup scheduler
    scheduler.set_callbacks(send_message_callback, ai_callback)
    scheduler.start()

    logger.info("Bot starting... Press Ctrl+C to stop.")
    _app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
