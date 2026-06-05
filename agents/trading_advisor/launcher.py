#!/usr/bin/env python3
"""
Trading Advisor Launcher
=========================
Spawns a Claude Code session for the Trading Advisor in a visible window.

Supports multiple modes via --prompt flag:
  - Research mode: --prompt PROMPT_RESEARCH.md (nightly autonomous research)
  - Morning brief: --prompt morning_brief_prompt.md
  - Interactive: (no --prompt, launches interactive claude)

Usage:
    python agents/trading_advisor/launcher.py --prompt PROMPT_RESEARCH.md
    python agents/trading_advisor/launcher.py --prompt PROMPT_RESEARCH.md --prepare-only
    python agents/trading_advisor/launcher.py --prompt morning_brief_prompt.md

Author: Ben (with Claude)
Date: 2026-04-22
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Project root is grandparent of this script's directory (agents/trading_advisor/ -> options_scanner/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Agent workspace — Claude Code must launch from here so it loads .claude/settings.local.json
AGENT_DIR = PROJECT_ROOT / 'agents' / 'trading_advisor'

# Configure UTF-8 encoding for Windows compatibility (MANDATORY)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def spawn_visible(prompt_file, title="Trading Advisor"):
    """Spawn Claude Code in a visible window.

    Args:
        prompt_file: Path to the prompt file
        title: Window title

    Returns:
        bool: True if spawned successfully
    """
    claude_path = shutil.which('claude')
    if not claude_path:
        print("ERROR: 'claude' command not found in PATH")
        return False

    print(f"Found claude at: {claude_path}")

    # Create batch file to spawn visible window
    # Must cd into agent dir so Claude Code finds .git and loads .claude/settings.local.json
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
        f.write('@echo off\n')
        f.write(f'cd /d {AGENT_DIR}\n')
        f.write('echo ================================================\n')
        f.write(f'echo  {title} Session Starting...\n')
        f.write('echo ================================================\n')
        f.write('echo.\n')
        f.write(f'claude --permission-mode auto @{prompt_file}\n')
        batch_file = f.name

    print(f"Launching Claude Code in new window...")

    # Use start to open in a new window
    result = subprocess.run(
        f'start "{title}" cmd /k "{batch_file}"',
        shell=True,
        cwd=str(AGENT_DIR)
    )

    if result.returncode == 0:
        print("Claude Code launched successfully")
        return True
    else:
        print(f"Failed to launch (exit code {result.returncode})")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Trading Advisor — Launch a session'
    )
    parser.add_argument('--prompt', type=str, required=True,
                        help='Path to prompt file (relative to agent dir or absolute)')
    parser.add_argument('--prepare-only', action='store_true',
                        help='Write session prompt and exit (for batch file use)')

    args = parser.parse_args()

    # Resolve prompt file path
    prompt_file = Path(args.prompt)
    if not prompt_file.is_absolute():
        prompt_file = AGENT_DIR / prompt_file

    if not prompt_file.exists():
        print(f"ERROR: Prompt file not found: {prompt_file}")
        return

    # Determine mode from prompt filename for display
    prompt_name = prompt_file.stem.upper()
    if 'research' in prompt_name.lower():
        mode = "Research"
    elif 'morning' in prompt_name.lower() or 'brief' in prompt_name.lower():
        mode = "Morning Brief"
    else:
        mode = "Session"

    # Build session prompt: date context + main prompt
    now = datetime.now()
    date_header = (
        f"**Today is {now.strftime('%A, %B %d, %Y')}. "
        f"Current time: {now.strftime('%I:%M %p')} ET. "
        f"Day of week: {now.strftime('%A')}. "
        f"This is a fact, not an estimate.**\n\n"
    )

    prompt_text = date_header + prompt_file.read_text(encoding='utf-8')

    # Write combined prompt to temp file in agent dir
    session_prompt = AGENT_DIR / '.session_prompt.md'
    session_prompt.write_text(prompt_text, encoding='utf-8')

    title = f"Trading Advisor — {mode}"

    print(f"{'=' * 50}")
    print(f"  {title}")
    print(f"  {now.strftime('%A, %B %d, %Y %I:%M %p')}")
    print(f"{'=' * 50}")
    print(f"  Prompt: {prompt_file}")
    print(f"  Workspace: {AGENT_DIR}")
    print()

    if args.prepare_only:
        print(f"Session prompt written to: {session_prompt}")
        print(f"Ready for: cd /d {AGENT_DIR} && claude --permission-mode auto @.session_prompt.md")
    else:
        success = spawn_visible(session_prompt, title=title)
        if success:
            print(f"Watch the Claude Code window for progress.")


if __name__ == '__main__':
    main()
