#!/usr/bin/env bash
# Claude Code statusLine command
# Mirrors Git Bash PS1: user@host MSYSTEM cwd [git-branch]
# Colors are intentionally kept; the terminal will apply its dimming.

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')

# Green: user@host
user_host="$(whoami)@$(hostname -s)"

# Magenta: MSYSTEM (e.g. MINGW64) — fall back gracefully if not set
msystem="${MSYSTEM:-}"

# Yellow: working directory
work_dir="$cwd"

# Cyan: git branch (skip optional locks, suppress errors)
git_branch=""
if git -C "$cwd" --no-optional-locks rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null \
             || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        git_branch=" ($branch)"
    fi
fi

# ANSI color codes
GREEN='\033[32m'
MAGENTA='\033[35m'
YELLOW='\033[33m'
CYAN='\033[36m'
RESET='\033[0m'

if [ -n "$msystem" ]; then
    printf "${GREEN}%s${RESET} ${MAGENTA}%s${RESET} ${YELLOW}%s${RESET}${CYAN}%s${RESET}" \
        "$user_host" "$msystem" "$work_dir" "$git_branch"
else
    printf "${GREEN}%s${RESET} ${YELLOW}%s${RESET}${CYAN}%s${RESET}" \
        "$user_host" "$work_dir" "$git_branch"
fi
