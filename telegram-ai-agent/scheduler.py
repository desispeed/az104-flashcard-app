"""Scheduled tasks and heartbeat system.

Provides cron-like scheduling so the bot can proactively run tasks,
send reminders, and check on things — just like OpenClaw's cron + heartbeat.
"""

import json
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from config import Config

logger = logging.getLogger(__name__)

JOBS_FILE = os.path.join(Config.MEMORY_DIR, "_scheduled_jobs.json")


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._send_fn = None  # set by bot after init
        self._ai_fn = None    # set by bot after init

    def set_callbacks(self, send_fn, ai_fn):
        """Set callback functions for sending messages and querying AI."""
        self._send_fn = send_fn
        self._ai_fn = ai_fn

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            self._load_persisted_jobs()
            logger.info("Scheduler started")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    # ── Heartbeat ──

    def start_heartbeat(self, user_id: int):
        interval = Config.HEARTBEAT_INTERVAL
        if interval <= 0:
            return
        job_id = f"heartbeat_{user_id}"
        if self.scheduler.get_job(job_id):
            return
        self.scheduler.add_job(
            self._heartbeat_tick,
            IntervalTrigger(minutes=interval),
            id=job_id,
            args=[user_id],
            replace_existing=True,
        )
        logger.info("Heartbeat started for user %s every %s min", user_id, interval)

    async def _heartbeat_tick(self, user_id: int):
        if not self._ai_fn or not self._send_fn:
            return
        try:
            response = await self._ai_fn(
                user_id,
                "[HEARTBEAT] Check if there is anything pending or noteworthy "
                "for the user. If there is nothing important, respond with "
                "exactly 'HEARTBEAT_SKIP'. Otherwise, send a brief update.",
            )
            if response and "HEARTBEAT_SKIP" not in response:
                await self._send_fn(user_id, f"*Heartbeat*\n{response}")
        except Exception as e:
            logger.error("Heartbeat error for user %s: %s", user_id, e)

    # ── Cron jobs ──

    def add_cron_job(
        self, user_id: int, job_id: str, cron_expr: str, prompt: str
    ) -> str:
        """Add a cron-scheduled job. cron_expr format: 'minute hour day month day_of_week'."""
        parts = cron_expr.split()
        if len(parts) != 5:
            return "Invalid cron expression. Use: minute hour day month day_of_week"

        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )

        full_id = f"cron_{user_id}_{job_id}"
        self.scheduler.add_job(
            self._run_cron_job,
            trigger,
            id=full_id,
            args=[user_id, prompt],
            replace_existing=True,
        )
        self._persist_job(full_id, user_id, cron_expr, prompt)
        return f"Scheduled job `{job_id}` with cron `{cron_expr}`"

    def remove_job(self, user_id: int, job_id: str) -> str:
        full_id = f"cron_{user_id}_{job_id}"
        job = self.scheduler.get_job(full_id)
        if not job:
            return f"No job found with id `{job_id}`"
        self.scheduler.remove_job(full_id)
        self._unpersist_job(full_id)
        return f"Removed job `{job_id}`"

    def list_jobs(self, user_id: int) -> list[dict]:
        jobs = []
        for job in self.scheduler.get_jobs():
            if str(user_id) in job.id:
                jobs.append({
                    "id": job.id.replace(f"cron_{user_id}_", ""),
                    "next_run": str(job.next_run_time),
                    "trigger": str(job.trigger),
                })
        return jobs

    async def _run_cron_job(self, user_id: int, prompt: str):
        if not self._ai_fn or not self._send_fn:
            return
        try:
            response = await self._ai_fn(user_id, f"[SCHEDULED TASK] {prompt}")
            if response:
                await self._send_fn(user_id, f"*Scheduled Task*\n{response}")
        except Exception as e:
            logger.error("Cron job error: %s", e)

    # ── Persistence ──

    def _persist_job(self, full_id: str, user_id: int, cron_expr: str, prompt: str):
        jobs = self._load_jobs_file()
        jobs[full_id] = {
            "user_id": user_id,
            "cron_expr": cron_expr,
            "prompt": prompt,
        }
        self._save_jobs_file(jobs)

    def _unpersist_job(self, full_id: str):
        jobs = self._load_jobs_file()
        jobs.pop(full_id, None)
        self._save_jobs_file(jobs)

    def _load_persisted_jobs(self):
        jobs = self._load_jobs_file()
        for full_id, data in jobs.items():
            parts = data["cron_expr"].split()
            if len(parts) != 5:
                continue
            trigger = CronTrigger(
                minute=parts[0], hour=parts[1], day=parts[2],
                month=parts[3], day_of_week=parts[4],
            )
            self.scheduler.add_job(
                self._run_cron_job,
                trigger,
                id=full_id,
                args=[data["user_id"], data["prompt"]],
                replace_existing=True,
            )
        if jobs:
            logger.info("Restored %d persisted jobs", len(jobs))

    def _load_jobs_file(self) -> dict:
        os.makedirs(Config.MEMORY_DIR, exist_ok=True)
        if os.path.exists(JOBS_FILE):
            with open(JOBS_FILE, "r") as f:
                return json.load(f)
        return {}

    def _save_jobs_file(self, jobs: dict):
        os.makedirs(Config.MEMORY_DIR, exist_ok=True)
        with open(JOBS_FILE, "w") as f:
            json.dump(jobs, f, indent=2)
