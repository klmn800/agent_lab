#!/usr/bin/env python3
"""
Earnings Researcher Launcher
==============================
Spawns a Claude Code session for the Earnings Date Researcher in a visible window.

The researcher reads disputed earnings dates from performance.db, researches
the correct dates via web search, and confirms them via CLI tools.

Usage:
    python agents/earnings_researcher/launcher.py              # Launch in visible window
    python agents/earnings_researcher/launcher.py --headless   # Run headless (no window)

Author: Ben (with Claude Code)
Date: 2026-04-23
"""

import argparse
import shutil
import subprocess
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Project root is grandparent of this script's directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_DIR = PROJECT_ROOT / 'agents' / 'earnings_researcher'
PERF_DB = PROJECT_ROOT / 'data' / 'performance.db'

# Configure UTF-8 encoding for Windows compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


DISPUTE_PRIORITY = {'date_disagreement': 0, 'confirmed_row_diverged': 0, 'both': 1, 'unknown_time': 2}


def get_unresolved_disputes(limit=None):
    """Get unresolved disputes for today, prioritized by type.

    Priority: date_disagreement > both > unknown_time
    Within each type, sorted by earnings date ASC (nearest first).

    Returns:
        list of (symbol, dispute_reason, db_date) tuples
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    try:
        conn = sqlite3.connect(str(PERF_DB), timeout=10)
        rows = conn.execute("""
            SELECT symbol, dispute_reason, db_date
            FROM earnings_date_disputes
            WHERE trade_date = ? AND (resolution = 'unresolved' OR resolution IS NULL)
            ORDER BY db_date ASC, symbol ASC
        """, (today_str,)).fetchall()
        conn.close()

        # Sort by priority (date_disagreement first, then both, then unknown_time)
        rows.sort(key=lambda r: (DISPUTE_PRIORITY.get(r[1], 9), r[2] or '9999'))

        if limit:
            rows = rows[:limit]
        return rows
    except Exception as e:
        print("Could not check disputes: {}".format(e))
        return []


def get_unresolved_count():
    """Check how many unresolved disputes exist for today."""
    return len(get_unresolved_disputes())


def spawn_visible(prompt_file):
    """Run Claude Code inline in the current window (no second window spawned).

    The orchestrator wraps `python launcher.py` in `cmd /k`, so this window
    stays open after Claude exits — letting the user read the final summary.
    """
    claude_path = shutil.which('claude')
    if not claude_path:
        print("ERROR: 'claude' command not found in PATH")
        return False

    print("Starting Claude Code session in this window...")
    print()

    result = subprocess.run(
        [claude_path, '--permission-mode', 'auto', '@{}'.format(prompt_file)],
        cwd=str(AGENT_DIR),
    )

    return result.returncode == 0


def spawn_headless(prompt_file):
    """Spawn Claude Code headless (no window, captures output)."""
    claude_path = shutil.which('claude')
    if not claude_path:
        print("ERROR: 'claude' command not found in PATH")
        return False, ""

    print("Running Earnings Researcher headless (this may take several minutes)...")

    prompt_text = Path(prompt_file).read_text(encoding='utf-8')

    result = subprocess.run(
        [claude_path, '-p', '--permission-mode', 'auto'],
        input=prompt_text,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=2700,  # 45 minute timeout
        cwd=str(AGENT_DIR)
    )

    if result.returncode == 0:
        print("Earnings Researcher session completed successfully")
        return True, result.stdout
    else:
        print("Session failed (exit code {})".format(result.returncode))
        if result.stderr:
            print("stderr: {}".format(result.stderr[:500]))
        return False, result.stdout


def main():
    parser = argparse.ArgumentParser(
        description='Earnings Date Researcher -- verify disputed earnings dates'
    )
    parser.add_argument('--headless', action='store_true',
                        help='Run headless (no visible window)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Max symbols to research per session (default: all)')
    parser.add_argument('--prompt', type=str, default=None,
                        help='Path to a standalone prompt file (e.g. PROMPT_SUNDAY.md). '
                             'When set, runs a maintenance session: bypasses the dispute '
                             'check/early-exit and tells the context hook to suppress the '
                             'dispute list (.session_mode=weekend).')
    parser.add_argument('--prepare-only', action='store_true',
                        help='Write .session_prompt.md and exit without launching Claude '
                             '(for the two-step .bat launch used by Task Scheduler).')

    args = parser.parse_args()

    # Ensure workspace directories exist (needed by both modes)
    (AGENT_DIR / 'memory').mkdir(parents=True, exist_ok=True)
    (AGENT_DIR / 'reference').mkdir(parents=True, exist_ok=True)
    (AGENT_DIR / 'analysis').mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    date_header = (
        "**Today is {}. Day of week: {}. "
        "Current time: {}. This is a fact, not an estimate.**\n\n".format(
            now.strftime('%A, %B %d, %Y'),
            now.strftime('%A'),
            now.strftime('%I:%M %p')
        )
    )
    session_prompt = AGENT_DIR / '.session_prompt.md'
    session_mode = AGENT_DIR / '.session_mode'

    # -----------------------------------------------------------------
    # Maintenance mode (standalone prompt file, e.g. the Sunday session)
    # -----------------------------------------------------------------
    if args.prompt:
        prompt_file = Path(args.prompt)
        if not prompt_file.is_absolute():
            prompt_file = AGENT_DIR / prompt_file
        if not prompt_file.exists():
            print("ERROR: Prompt file not found: {}".format(prompt_file))
            return

        prompt_text = date_header + prompt_file.read_text(encoding='utf-8')
        session_prompt.write_text(prompt_text, encoding='utf-8')

        # Tell the context hook to suppress the dispute-list this session.
        session_mode.write_text('weekend', encoding='utf-8')

        # Clear stale dispute-batch markers left by a prior daily run.
        for stale in ('.session_injected', '.session_limit'):
            p = AGENT_DIR / stale
            if p.exists():
                p.unlink()

        print("=" * 50)
        print("  Earnings Researcher -- Maintenance Session")
        print("  {}".format(now.strftime('%A, %B %d, %Y %I:%M %p')))
        print("  Prompt: {}".format(prompt_file.name))
        print("=" * 50)

        if args.prepare_only:
            print("Session prompt written to: {}".format(session_prompt))
            print("Ready for: cd /d {} && claude --permission-mode auto @.session_prompt.md".format(AGENT_DIR))
        elif args.headless:
            success, output = spawn_headless(session_prompt)
            if output:
                print("\n" + "=" * 50)
                print("Session Output:")
                print("=" * 50)
                print(output[-2000:] if len(output) > 2000 else output)
        else:
            spawn_visible(session_prompt)
        return

    # -----------------------------------------------------------------
    # Daily dispute-resolution mode (default)
    # -----------------------------------------------------------------
    # Reset the hook's mode marker so a stale 'weekend' value from a Sunday
    # run can't suppress today's dispute list.
    session_mode.write_text('daily', encoding='utf-8')

    # Check for disputes (all of them, for total count)
    all_disputes = get_unresolved_disputes()
    if not all_disputes:
        print("No unresolved earnings date disputes for today. Nothing to do.")
        return

    # Apply limit — prioritized batch
    batch = get_unresolved_disputes(limit=args.limit)
    total_count = len(all_disputes)
    batch_count = len(batch)

    # Write session limit file — hook reads this to enforce the cap.
    # "0" means no limit (process all). Positive integer = hard cap.
    session_limit = AGENT_DIR / '.session_limit'
    session_limit.write_text(str(args.limit or 0), encoding='utf-8')

    # Clear sentinel from previous session so hook injects fresh
    sentinel = AGENT_DIR / '.session_injected'
    if sentinel.exists():
        sentinel.unlink()

    prompt_text = date_header + PROMPT_TEMPLATE.format(
        date=now.strftime('%Y-%m-%d'),
        N=batch_count,
    )

    # Write session prompt
    session_prompt.write_text(prompt_text, encoding='utf-8')

    print("=" * 50)
    print("  Earnings Date Researcher")
    print("  {}".format(now.strftime('%A, %B %d, %Y %I:%M %p')))
    if args.limit and batch_count < total_count:
        print("  Disputes: {} of {} (batch limit {})".format(batch_count, total_count, args.limit))
    else:
        print("  Disputes to research: {} (all)".format(batch_count))

    # Show priority breakdown
    type_counts = {}
    for _, reason, _ in batch:
        type_counts[reason] = type_counts.get(reason, 0) + 1
    parts = []
    for reason in ('date_disagreement', 'both', 'unknown_time'):
        cnt = type_counts.get(reason, 0)
        if cnt:
            parts.append("{} {}".format(cnt, reason))
    if parts:
        print("  Priority: {}".format(", ".join(parts)))
    print("=" * 50)

    if args.headless:
        success, output = spawn_headless(session_prompt)
        if output:
            print("\n" + "=" * 50)
            print("Session Output:")
            print("=" * 50)
            print(output[-2000:] if len(output) > 2000 else output)
    else:
        # spawn_visible blocks until Claude exits (single-window mode).
        spawn_visible(session_prompt)


# ---------------------------------------------------------------------------
# Session prompt template
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """# Earnings Date Research Session

Today is {date}. You have {N} symbols to research.

Your dispute list has been injected via context hook.

## Step 0 — Open the session with a table + plan

Before any tool calls, print a session-opener so Ben can see what's on deck. Format:

```
=== Earnings Research: YYYY-MM-DD (Day) HH:MM ET — N symbols ===

Sym   DB Date    Time  DaysOut  Finnhub     Δ    Reason             IR
────  ────────  ────  ───────  ──────────  ───  ─────────────────  ──
SYM1  MM-DD     bmo   +N       MM-DD       ±Nd  date_disagreement  yes
...

Plan:
  1. <symbols + reason in plain English>
  2. ...
Diving in.
```

Column rules:
- **DB Date / Time**: from the injected dispute list (use `???` if Time is Unknown).
- **DaysOut**: signed integer days from today to the DB date (e.g. `+7`, `+1`, `0`).
- **Finnhub / Δ**: finnhub date and signed days vs. DB date (`+7d`, `-2d`). Use `—` for both columns when finnhub has no date.
- **Reason**: the dispute_reason string verbatim (`date_disagreement`, `both`, `unknown_time`, `unconfirmed`).
- **IR**: `yes` if a cached IR URL is present in the dispute data, else `no`.

Sort rows by priority: `date_disagreement` → `both` → `unknown_time` → `unconfirmed`. Within a group, soonest DaysOut first.

Plan narrative: one short line per symbol or per group, explaining why I'm tackling them in that order or flagging quirks (e.g. "WSM reports tomorrow", "UEC DB date looks too early"). Keep the whole opener under ~20 lines.

## Step 1+ — Research each symbol

For each symbol:

1. Check if there's a cached IR URL in the dispute data. If so, try WebFetch on it first.
2. If no cached URL, WebSearch for the company's earnings date (e.g., "GILD earnings date Q2 2026" or "Gilead Sciences investor relations earnings"). Do this yourself, do not spawn agents.
3. Look for the official IR press release or investor events page. Do not use third party pages. Be mindful of the current date, the correct earnings date should be within a few weeks of that.
4. Extract: correct earnings date + BMO/AMC timing.
5. Confirm via CLI:
   ```
   python E:\\options_scanner\\tools\\earnings_confirm.py --symbol SYM --date YYYY-MM-DD --time bmo --by agent
   ```
6. Save the IR URL:
   ```
   python E:\\options_scanner\\tools\\direct_db_query.py --db E:\\options_scanner\\data\\datalake.db --sql "UPDATE symbol_metadata SET ir_earnings_url='URL', ir_url_last_verified='{date}' WHERE symbol='SYM'"
   ```
7. Update dispute resolution:
   ```
   python E:\\options_scanner\\tools\\direct_db_query.py --db E:\\options_scanner\\data\\performance.db --sql "UPDATE earnings_date_disputes SET resolution='confirmed_agent', resolved_date='DATE', resolved_time='TIME', resolved_at='TIMESTAMP', research_url='URL' WHERE trade_date='{date}' AND symbol='SYM'"
   ```
8. If you can't find a reliable source, or do not have enough confidence to lock in a date, skip and log to memory/research_log.md.

Focus on symbols with 'date_disagreement' or 'both' first (these are more likely to be wrong), then 'unknown_time' (just need timing info).

Don't use third-party services. Check for "estimated" in reference to earnings dates to see if it's confirmed or speculative. Your job is to find the authoritative source and report that.

When done, print a summary of your work.
"""


if __name__ == '__main__':
    main()
