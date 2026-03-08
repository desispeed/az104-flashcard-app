# Git Helper

Manage git repositories through chat.

## When to use
When the user asks about git status, commits, branches, diffs, or wants to perform git operations.

## How to use
Use the `run_shell` tool with git commands:

- **Status**: `git -C /path/to/repo status`
- **Log**: `git -C /path/to/repo log --oneline -10`
- **Diff**: `git -C /path/to/repo diff --stat`
- **Branches**: `git -C /path/to/repo branch -a`
- **Pull**: `git -C /path/to/repo pull`

Always confirm with the user before pushing or force operations.
