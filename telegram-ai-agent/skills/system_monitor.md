# System Monitor

Monitor system resources and report on health.

## When to use
When the user asks about system status, disk space, memory, CPU, or running processes.

## How to use
Use the `run_shell` tool with these commands:

- **CPU/Memory/Uptime**: `uptime`
- **Disk space**: `df -h`
- **Memory details**: `free -h` (Linux) or `vm_stat` (macOS)
- **Running processes**: `ps aux --sort=-%mem | head -20`
- **Network**: `curl -s ifconfig.me` for public IP

Combine multiple checks for a full health report.
