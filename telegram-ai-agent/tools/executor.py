"""Task execution engine — runs shell commands and file operations.

Provides sandboxed execution so the AI agent can take real actions on the
host machine (read/write files, run scripts, etc.) similar to OpenClaw.
"""

import asyncio
import os
import shlex
from config import Config

SAFE_COMMANDS = {
    "ls", "cat", "head", "tail", "wc", "date", "whoami", "pwd", "echo",
    "find", "grep", "sort", "uniq", "df", "du", "uptime", "uname",
    "python3", "python", "node", "curl", "wget", "jq", "git",
    "pip", "npm", "docker", "docker-compose",
}

BLOCKED_PATTERNS = [
    "rm -rf /", "mkfs", "dd if=", ":(){", "fork bomb",
    "> /dev/sd", "chmod -R 777 /",
]


def _is_safe(command: str) -> tuple[bool, str]:
    for pattern in BLOCKED_PATTERNS:
        if pattern in command:
            return False, f"Blocked dangerous pattern: {pattern}"

    if Config.SANDBOX_MODE:
        base_cmd = shlex.split(command)[0] if command.strip() else ""
        base_cmd = os.path.basename(base_cmd)
        if base_cmd not in SAFE_COMMANDS:
            return False, (
                f"Command `{base_cmd}` not in sandbox allowlist. "
                f"Allowed: {', '.join(sorted(SAFE_COMMANDS))}. "
                "Set SANDBOX_MODE=false to disable restrictions."
            )
    return True, ""


async def run_shell(command: str, timeout: int = 30) -> dict:
    """Execute a shell command and return stdout/stderr."""
    if not Config.ENABLE_TASK_EXECUTION:
        return {"ok": False, "error": "Task execution is disabled."}

    safe, reason = _is_safe(command)
    if not safe:
        return {"ok": False, "error": reason}

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": stdout.decode(errors="replace")[:4000],
            "stderr": stderr.decode(errors="replace")[:2000],
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"ok": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def read_file(path: str) -> dict:
    """Read a file and return its contents."""
    if not Config.ENABLE_TASK_EXECUTION:
        return {"ok": False, "error": "Task execution is disabled."}
    try:
        path = os.path.expanduser(path)
        with open(path, "r") as f:
            content = f.read(50_000)  # cap at 50KB
        return {"ok": True, "content": content, "path": path}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def write_file(path: str, content: str) -> dict:
    """Write content to a file."""
    if not Config.ENABLE_TASK_EXECUTION:
        return {"ok": False, "error": "Task execution is disabled."}
    try:
        path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return {"ok": True, "path": path, "bytes_written": len(content)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def list_directory(path: str = ".") -> dict:
    """List directory contents."""
    if not Config.ENABLE_TASK_EXECUTION:
        return {"ok": False, "error": "Task execution is disabled."}
    try:
        path = os.path.expanduser(path)
        entries = []
        for entry in sorted(os.listdir(path)):
            full = os.path.join(path, entry)
            kind = "dir" if os.path.isdir(full) else "file"
            size = os.path.getsize(full) if os.path.isfile(full) else None
            entries.append({"name": entry, "type": kind, "size": size})
        return {"ok": True, "entries": entries}
    except Exception as e:
        return {"ok": False, "error": str(e)}
