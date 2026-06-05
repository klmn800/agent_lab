#!/usr/bin/env python3
"""
Market Analyst Launcher
========================
Spawns a Claude Code session for the Market Analyst in a visible window.

Supports multiple modes via --prompt flag:
  - Research (default):    --prompt PROMPT.md             (nightly autonomous research)
  - Saturday closure:      --prompt PROMPT_SATURDAY.md    (trade grading + reflection)
  - Sunday housekeeping:   --prompt PROMPT_SUNDAY.md      (audit + week-ahead planning)

Usage:
    python agents/market_analyst/launcher.py --prompt PROMPT.md
    python agents/market_analyst/launcher.py --prompt PROMPT.md --prepare-only
    python agents/market_analyst/launcher.py --prompt PROMPT_SATURDAY.md

Date: 2026-05-17
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_DIR = PROJECT_ROOT / 'agents' / 'market_analyst'

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def spawn_visible(prompt_file, title="Market Analyst"):
    claude_path = shutil.which('claude')
    if not claude_path:
        print("ERROR: 'claude' command not found in PATH")
        return False

    print(f"Found claude at: {claude_path}")

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
    parser = argparse.ArgumentParser(description='Market Analyst — Launch a session')
    parser.add_argument('--prompt', type=str, default='PROMPT.md',
                        help='Path to prompt file (relative to agent dir or absolute)')
    parser.add_argument('--prepare-only', action='store_true',
                        help='Write session prompt and exit (for batch file use)')

    args = parser.parse_args()

    prompt_file = Path(args.prompt)
    if not prompt_file.is_absolute():
        prompt_file = AGENT_DIR / prompt_file

    if not prompt_file.exists():
        print(f"ERROR: Prompt file not found: {prompt_file}")
        return

    prompt_name = prompt_file.stem.upper()
    if 'saturday' in prompt_name.lower():
        mode = "Saturday Closure"
    elif 'sunday' in prompt_name.lower():
        mode = "Sunday Housekeeping"
    else:
        mode = "Research"

    now = datetime.now()
    date_header = (
        f"**Today is {now.strftime('%A, %B %d, %Y')}. "
        f"Current time: {now.strftime('%I:%M %p')} ET. "
        f"Day of week: {now.strftime('%A')}. "
        f"This is a fact, not an estimate.**\n\n"
    )

    prompt_text = date_header + prompt_file.read_text(encoding='utf-8')

    session_prompt = AGENT_DIR / '.session_prompt.md'
    session_prompt.write_text(prompt_text, encoding='utf-8')

    title = f"Market Analyst — {mode}"

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
            print("Watch the Claude Code window for progress.")


if __name__ == '__main__':
    main()
