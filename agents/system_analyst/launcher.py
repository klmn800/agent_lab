#!/usr/bin/env python3
"""
System Analyst Launcher
========================
Spawns a Claude Code session for the System Analyst in a visible window.

The analyst reads the system, queries databases, and produces proposals
for system improvements. It writes ONLY to its own workspace (agents/system_analyst/).

Usage:
    python agents/system_analyst/launcher.py              # Launch in visible window
    python agents/system_analyst/launcher.py --headless   # Run headless (no window)

Author: Ben (with Claude)
Date: 2026-04-17
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Project root is grandparent of this script's directory (agents/system_analyst/ -> options_scanner/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Agent workspace — Claude Code must launch from here so it loads .claude/settings.local.json
AGENT_DIR = PROJECT_ROOT / 'agents' / 'system_analyst'

# Configure UTF-8 encoding for Windows compatibility (MANDATORY)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Paths
PROMPT_FILE = PROJECT_ROOT / 'agents' / 'system_analyst' / 'PROMPT.md'
REVIEWS_DIR = PROJECT_ROOT / 'agents' / 'system_analyst' / 'proposals'
MEMORY_DIR = PROJECT_ROOT / 'agents' / 'system_analyst' / 'memory'


def get_session_number():
    """Determine the next session number from existing proposals and journal."""
    # Check proposals for highest numbered file
    max_num = 0
    if REVIEWS_DIR.exists():
        for f in REVIEWS_DIR.glob('*.md'):
            name = f.stem
            # Extract leading number from filenames like "003_feedback-loop-design"
            parts = name.split('_', 1)
            if parts[0].isdigit():
                max_num = max(max_num, int(parts[0]))

    # Also check journal for session references
    journal = MEMORY_DIR / 'journal.md'
    if journal.exists():
        import re
        text = journal.read_text(encoding='utf-8')
        # Find "Session NNN" patterns
        for match in re.finditer(r'Session\s+(\d+)', text):
            max_num = max(max_num, int(match.group(1)))

    return max_num + 1


def spawn_visible(prompt_file):
    """Spawn Claude Code in a visible window.

    Args:
        prompt_file: Path to the prompt file

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
        f.write('echo  System Analyst Session Starting...\n')
        f.write('echo ================================================\n')
        f.write('echo.\n')
        f.write(f'claude --model claude-opus-4-7 --permission-mode auto @{prompt_file}\n')
        batch_file = f.name

    print(f"Launching Claude Code in new window...")

    # Use start to open in a new window
    result = subprocess.run(
        f'start "System Analyst" cmd /k "{batch_file}"',
        shell=True,
        cwd=str(AGENT_DIR)
    )

    if result.returncode == 0:
        print("Claude Code launched successfully")
        return True
    else:
        print(f"Failed to launch (exit code {result.returncode})")
        return False


def spawn_headless(prompt_file):
    """Spawn Claude Code headless (no window, captures output).

    Args:
        prompt_file: Path to the prompt file

    Returns:
        tuple: (success: bool, output: str)
    """
    claude_path = shutil.which('claude')
    if not claude_path:
        print("ERROR: 'claude' command not found in PATH")
        return False, ""

    print("Running System Analyst headless (this may take several minutes)...")

    prompt_text = Path(prompt_file).read_text(encoding='utf-8')

    result = subprocess.run(
        [claude_path, '-p', '--model', 'claude-opus-4-7', '--permission-mode', 'auto'],
        input=prompt_text,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=1800,  # 30 minute timeout
        cwd=str(AGENT_DIR)
    )

    if result.returncode == 0:
        print("System Analyst session completed successfully")
        return True, result.stdout
    else:
        print(f"Session failed (exit code {result.returncode})")
        if result.stderr:
            print(f"stderr: {result.stderr[:500]}")
        return False, result.stdout


def main():
    parser = argparse.ArgumentParser(
        description='System Analyst — Launch an autonomous analysis session'
    )
    parser.add_argument('--headless', action='store_true',
                        help='Run headless (no visible window)')
    parser.add_argument('--prompt', type=str, default=None,
                        help='Path to prompt file (default: agents/system_analyst/PROMPT.md)')
    parser.add_argument('--prepare-only', action='store_true',
                        help='Write session prompt and exit (for batch file use)')

    args = parser.parse_args()

    # Determine which prompt file to use
    prompt_file = Path(args.prompt) if args.prompt else PROMPT_FILE
    if not prompt_file.is_absolute():
        prompt_file = PROJECT_ROOT / prompt_file

    # Verify prompt exists
    if not prompt_file.exists():
        print(f"ERROR: Prompt file not found: {prompt_file}")
        return

    # Ensure workspace directories exist
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    (REVIEWS_DIR / 'feedback').mkdir(exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    (MEMORY_DIR / 'observations').mkdir(exist_ok=True)

    session_num = get_session_number()

    # Build session prompt: date context + main prompt
    # Date injection prevents Claude's day-of-week confusion
    now = datetime.now()
    date_header = (
        f"**Today is {now.strftime('%A, %B %d, %Y')}. "
        f"Day of week: {now.strftime('%A')}. "
        f"This is a fact, not an estimate.**\n\n"
    )

    prompt_text = date_header + prompt_file.read_text(encoding='utf-8')

    # Write combined prompt to temp file
    session_prompt = PROJECT_ROOT / 'agents' / 'system_analyst' / f'.session_prompt.md'
    session_prompt.write_text(prompt_text, encoding='utf-8')

    print(f"{'=' * 50}")
    print(f"  System Analyst — Session {session_num:03d}")
    print(f"  {now.strftime('%A, %B %d, %Y %I:%M %p')}")
    print(f"{'=' * 50}")
    print(f"  Prompt: {prompt_file}")
    print(f"  Workspace: {MEMORY_DIR.parent}")
    print(f"  Reviews: {REVIEWS_DIR}")
    print()

    if args.prepare_only:
        print(f"Session prompt written to: {session_prompt}")
        print("Ready for: cd /d E:\\options_scanner\\agents\\system_analyst && claude --permission-mode auto @.session_prompt.md")
    elif args.headless:
        success, output = spawn_headless(session_prompt)
        if output:
            print(f"\n{'=' * 50}")
            print("Session Output:")
            print(f"{'=' * 50}")
            print(output[-2000:] if len(output) > 2000 else output)
    else:
        success = spawn_visible(session_prompt)
        if success:
            print("Watch the Claude Code window for progress.")
            print(f"Proposals will appear in: {REVIEWS_DIR}")


if __name__ == '__main__':
    main()
