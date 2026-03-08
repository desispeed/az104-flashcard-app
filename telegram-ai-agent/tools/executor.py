"""Task execution engine — runs shell commands and file operations.

Provides sandboxed execution so the AI agent can take real actions on the
host machine (read/write files, run scripts, etc.) similar to OpenClaw.

Security layers:
  1. Shell sandbox: allowlist of safe base commands
  2. Shell chain detection: blocks pipes, semicolons, backticks, $() in sandbox mode
  3. Blocked patterns: catches known destructive commands
  4. Path restrictions: blocks access to sensitive files/directories
  5. Audit logging: all tool executions logged to disk
"""

import asyncio
import datetime
import json
import os
import re
import shlex
from config import Config

# ── Shell sandbox ──

SAFE_COMMANDS = {
    "ls", "cat", "head", "tail", "wc", "date", "whoami", "pwd", "echo",
    "find", "grep", "sort", "uniq", "df", "du", "uptime", "uname",
    "python3", "python", "node", "curl", "wget", "jq", "git",
    "pip", "npm", "docker", "docker-compose",
}

BLOCKED_PATTERNS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=", ":(){", "fork bomb",
    "> /dev/sd", "chmod -R 777 /", "chmod 777 /", "shutdown", "reboot",
    "init 0", "init 6", "halt", "poweroff",
    "passwd", "useradd", "userdel", "groupadd",
    "iptables -F", "ufw disable",
]

# Characters that allow chaining/injecting additional commands
SHELL_CHAIN_CHARS = re.compile(r"[;|&`$]|\$\(")

# ── Path security ──

SENSITIVE_PATHS = [
    ".env", ".ssh", ".gnupg", ".aws", ".config/gcloud",
    ".docker/config.json", ".kube/config",
    "/etc/shadow", "/etc/passwd", "/etc/sudoers",
    "/etc/crontab", "/var/spool/cron",
    "id_rsa", "id_ed25519", "credentials", "secrets",
    ".git/config",  # may contain tokens
]

BLOCKED_WRITE_DIRS = [
    "/etc", "/usr", "/bin", "/sbin", "/boot", "/proc", "/sys",
    "/var/run", "/var/lock", "/root",
]

# ── Audit log ──

AUDIT_LOG = os.path.join(Config.MEMORY_DIR, "_audit.log")


def _audit(tool: str, params: dict, result: dict):
    """Append a line to the audit log."""
    os.makedirs(Config.MEMORY_DIR, exist_ok=True)
    entry = {
        "ts": datetime.datetime.now().isoformat(),
        "tool": tool,
        "params": {k: v[:200] if isinstance(v, str) else v for k, v in params.items()},
        "ok": result.get("ok"),
    }
    try:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ── Path validation ──

def _is_sensitive_path(path: str) -> bool:
    """Check if a path accesses sensitive files."""
    normalized = os.path.normpath(os.path.expanduser(path))
    # Check against sensitive path fragments
    for sensitive in SENSITIVE_PATHS:
        if sensitive in normalized:
            return True
    return False


def _is_blocked_write_dir(path: str) -> bool:
    """Check if writing to a restricted system directory."""
    normalized = os.path.normpath(os.path.expanduser(path))
    for blocked in BLOCKED_WRITE_DIRS:
        if normalized.startswith(blocked):
            return True
    return False


# ── Shell validation ──

def _is_safe_command(command: str) -> tuple[bool, str]:
    """Validate a shell command against security rules."""
    # Check blocked patterns first (applies in all modes)
    for pattern in BLOCKED_PATTERNS:
        if pattern in command:
            return False, f"Blocked dangerous pattern: `{pattern}`"

    if not Config.SANDBOX_MODE:
        return True, ""

    # In sandbox mode: block shell chaining characters
    if SHELL_CHAIN_CHARS.search(command):
        return False, (
            "Shell chaining (`;`, `|`, `&`, `` ` ``, `$()`) is blocked in sandbox mode. "
            "Run commands one at a time, or set SANDBOX_MODE=false."
        )

    # Check base command against allowlist
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return False, f"Invalid command syntax: {e}"

    if not parts:
        return False, "Empty command"

    base_cmd = os.path.basename(parts[0])
    if base_cmd not in SAFE_COMMANDS:
        return False, (
            f"Command `{base_cmd}` not in sandbox allowlist. "
            f"Allowed: {', '.join(sorted(SAFE_COMMANDS))}. "
            "Set SANDBOX_MODE=false to disable restrictions."
        )

    return True, ""


# ── Public API ──

async def run_shell(command: str, timeout: int = 30) -> dict:
    """Execute a shell command and return stdout/stderr."""
    params = {"command": command, "timeout": timeout}

    if not Config.ENABLE_TASK_EXECUTION:
        result = {"ok": False, "error": "Task execution is disabled."}
        _audit("run_shell", params, result)
        return result

    # Cap timeout to prevent abuse
    timeout = min(timeout, 120)

    safe, reason = _is_safe_command(command)
    if not safe:
        result = {"ok": False, "error": reason}
        _audit("run_shell", params, result)
        return result

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

        # Scrub output for sensitive data before returning
        stdout_text = _scrub_sensitive(stdout.decode(errors="replace")[:4000])
        stderr_text = stderr.decode(errors="replace")[:2000]

        result = {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": stdout_text,
            "stderr": stderr_text,
        }
    except asyncio.TimeoutError:
        proc.kill()
        result = {"ok": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    _audit("run_shell", params, result)
    return result


async def read_file(path: str) -> dict:
    """Read a file and return its contents."""
    params = {"path": path}

    if not Config.ENABLE_TASK_EXECUTION:
        result = {"ok": False, "error": "Task execution is disabled."}
        _audit("read_file", params, result)
        return result

    if _is_sensitive_path(path):
        result = {"ok": False, "error": f"Access denied: `{path}` is a sensitive file."}
        _audit("read_file", params, result)
        return result

    try:
        resolved = os.path.normpath(os.path.expanduser(path))
        with open(resolved, "r") as f:
            content = f.read(50_000)
        result = {"ok": True, "content": content, "path": resolved}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    _audit("read_file", params, result)
    return result


async def write_file(path: str, content: str) -> dict:
    """Write content to a file."""
    params = {"path": path, "content": f"({len(content)} bytes)"}

    if not Config.ENABLE_TASK_EXECUTION:
        result = {"ok": False, "error": "Task execution is disabled."}
        _audit("write_file", params, result)
        return result

    if _is_sensitive_path(path):
        result = {"ok": False, "error": f"Access denied: cannot write to sensitive path `{path}`."}
        _audit("write_file", params, result)
        return result

    if _is_blocked_write_dir(path):
        result = {"ok": False, "error": f"Access denied: cannot write to system directory `{path}`."}
        _audit("write_file", params, result)
        return result

    try:
        resolved = os.path.normpath(os.path.expanduser(path))
        parent = os.path.dirname(resolved)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(resolved, "w") as f:
            f.write(content)
        result = {"ok": True, "path": resolved, "bytes_written": len(content)}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    _audit("write_file", params, result)
    return result


async def list_directory(path: str = ".") -> dict:
    """List directory contents."""
    params = {"path": path}

    if not Config.ENABLE_TASK_EXECUTION:
        result = {"ok": False, "error": "Task execution is disabled."}
        _audit("list_directory", params, result)
        return result

    if _is_sensitive_path(path):
        result = {"ok": False, "error": f"Access denied: `{path}` is a sensitive directory."}
        _audit("list_directory", params, result)
        return result

    try:
        resolved = os.path.normpath(os.path.expanduser(path))
        entries = []
        for entry in sorted(os.listdir(resolved)):
            full = os.path.join(resolved, entry)
            kind = "dir" if os.path.isdir(full) else "file"
            size = os.path.getsize(full) if os.path.isfile(full) else None
            entries.append({"name": entry, "type": kind, "size": size})
        result = {"ok": True, "entries": entries}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    _audit("list_directory", params, result)
    return result


# ── Output scrubbing ──

_SECRET_PATTERNS = re.compile(
    r"(sk-[a-zA-Z0-9]{20,}|"           # Anthropic/OpenAI keys
    r"ghp_[a-zA-Z0-9]{36}|"            # GitHub PAT
    r"eyJ[a-zA-Z0-9_-]{50,}\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+|"  # JWT
    r"AKIA[A-Z0-9]{16}|"               # AWS access key
    r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----)",  # Private keys
    re.MULTILINE,
)


def _scrub_sensitive(text: str) -> str:
    """Redact secrets that might appear in command output."""
    return _SECRET_PATTERNS.sub("[REDACTED]", text)
