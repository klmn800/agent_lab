"""
System Analyst context injection hook.
Fires on every UserPromptSubmit.

Always: injects full project CLAUDE.md so the agent has complete system context
even though its project root is agents/system_analyst/ (not the parent repo).

When new content is detected: surfaces a <mailbox-notices> block with:
  - directive.md content (if non-empty)
  - TA mailbox tail (if mtime newer than last seen)
  - MA mailbox tail (if mtime newer than last seen)
  - ER mailbox tail (if mtime newer than last seen)
  - inbox/ unprocessed files
  - new proposals/feedback/ files
  - new TA proposals (agents/trading_advisor/proposals/) that may need SA input

State markers live in this directory as `.last_*` files.
First run for any check is silent (initializes the marker).

Output: JSON with hookSpecificOutput.additionalContext
"""

import sys
import json
from pathlib import Path
from datetime import datetime

CLAUDE_MD_PATH = Path(r'E:\options_scanner\CLAUDE.md')
HOOK_DIR = Path(__file__).parent
WORKSPACE = Path(r'E:\options_scanner\agents\system_analyst')

# Cross-agent / inbox sources (outbox/ since 2026-05-18 — was memory/)
TA_MAILBOX = Path(r'E:\options_scanner\agents\trading_advisor\outbox\for_system_analyst.md')
MA_MAILBOX = Path(r'E:\options_scanner\agents\market_analyst\outbox\for_system_analyst.md')
ER_MAILBOX = Path(r'E:\options_scanner\agents\earnings_researcher\outbox\for_system_analyst.md')
TA_PROPOSALS_DIR = Path(r'E:\options_scanner\agents\trading_advisor\proposals')
INBOX_DIR = WORKSPACE / 'inbox'
FEEDBACK_DIR = WORKSPACE / 'proposals' / 'feedback'
DIRECTIVE_FILE = WORKSPACE / 'directive.md'

# State markers (in this hooks/ dir)
MARK_TA_MAILBOX = HOOK_DIR / '.last_ta_mailbox_seen'
MARK_MA_MAILBOX = HOOK_DIR / '.last_ma_mailbox_seen'
MARK_ER_MAILBOX = HOOK_DIR / '.last_er_mailbox_seen'
MARK_FEEDBACK = HOOK_DIR / '.last_feedback_seen'
MARK_TA_PROPOSALS = HOOK_DIR / '.last_ta_proposals_seen'

INLINE_CAP_BYTES = 2048


# -- marker helpers --

def safe_mtime(path):
    try:
        return path.stat().st_mtime
    except Exception:
        return None


def read_marker_float(p):
    try:
        return float(p.read_text().strip())
    except Exception:
        return None


def write_marker_float(p, v):
    try:
        p.write_text(str(v))
    except Exception:
        pass


def read_marker_set(p):
    try:
        return set(line.strip() for line in p.read_text().splitlines() if line.strip())
    except Exception:
        return set()


def write_marker_set(p, values):
    try:
        p.write_text('\n'.join(sorted(values)))
    except Exception:
        pass


def tail_inline(content, cap=INLINE_CAP_BYTES):
    """Return last `cap` bytes of content, with a leading marker if truncated."""
    if len(content) <= cap:
        return content
    return (
        f'... [truncated, full file is {len(content):,} bytes — '
        f'read the file for full content] ...\n' + content[-cap:]
    )


def head_and_tail_inline(content, cap=INLINE_CAP_BYTES):
    """Return first `cap` + last `cap` bytes of content with the middle elided.

    Mailbox files use mixed conventions across agents — some prepend new entries
    at the top, some append at the bottom, some do both (see TA mailbox 2026-05-20).
    Showing both ends ensures new content is surfaced regardless of convention.
    If the file is small enough (<= 2*cap), returns it whole with no separator.
    """
    if len(content) <= 2 * cap:
        return content
    head = content[:cap]
    tail = content[-cap:]
    return (
        head +
        f'\n\n... [middle elided — full file is {len(content):,} bytes; '
        f'read the source path for entries between head and tail] ...\n\n' +
        tail
    )


# -- checks --

def check_directive():
    """Surface directive content INLINE if non-empty. Self-clears when agent empties the file."""
    if not DIRECTIVE_FILE.exists():
        return None
    try:
        content = DIRECTIVE_FILE.read_text(encoding='utf-8').strip()
    except Exception:
        return None
    if not content:
        return None
    return (
        'DIRECTIVE for this session (Ben wrote this for you — read, '
        'address it, then clear `directive.md`):\n```\n' + content + '\n```'
    )


def _check_mailbox(path, marker, label, rel_path):
    """Generic mailbox surfacer. Shows head + tail so neither prepend-at-top
    nor append-at-bottom conventions miss new entries. First run initializes silently.
    """
    if not path.exists():
        return None
    current = safe_mtime(path)
    last = read_marker_float(marker)
    if last is None:
        write_marker_float(marker, current)
        return None
    if current <= last:
        return None
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        write_marker_float(marker, current)
        return f'{label} mailbox updated but unreadable: {e}'
    when = datetime.fromtimestamp(current).strftime('%Y-%m-%d %H:%M')
    block = [
        f'{label} MAILBOX UPDATED — `{rel_path}` (mtime {when})',
        'Head + tail shown (new entries may be at top OR bottom depending on agent convention):',
        '```markdown',
        head_and_tail_inline(content),
        '```',
    ]
    write_marker_float(marker, current)
    return '\n'.join(block)


def check_ta_mailbox():
    return _check_mailbox(
        TA_MAILBOX, MARK_TA_MAILBOX, 'TA',
        'agents/trading_advisor/outbox/for_system_analyst.md'
    )


def check_ma_mailbox():
    return _check_mailbox(
        MA_MAILBOX, MARK_MA_MAILBOX, 'MA',
        'agents/market_analyst/outbox/for_system_analyst.md'
    )


def check_er_mailbox():
    return _check_mailbox(
        ER_MAILBOX, MARK_ER_MAILBOX, 'ER',
        'agents/earnings_researcher/outbox/for_system_analyst.md'
    )


def check_inbox():
    """Surface unprocessed inbox files. Self-clears via the move-to-processed convention."""
    if not INBOX_DIR.exists():
        return None
    items = []
    for entry in INBOX_DIR.iterdir():
        if entry.is_file() and entry.name not in ('README.md',):
            items.append(entry.name)
    if not items:
        return None
    return (
        f'INBOX has {len(items)} unprocessed file(s) — read each, integrate '
        f'into memory, then move to `inbox/processed/`:\n  - ' +
        '\n  - '.join(sorted(items))
    )


def check_new_feedback():
    """Surface new feedback files since last session. First run initializes silently."""
    if not FEEDBACK_DIR.exists():
        return None
    current = set(
        f.name for f in FEEDBACK_DIR.iterdir()
        if f.is_file() and f.name != 'README.md'
    )
    last = read_marker_set(MARK_FEEDBACK)
    if not last:
        write_marker_set(MARK_FEEDBACK, current)
        return None
    new = current - last
    if not new:
        return None
    write_marker_set(MARK_FEEDBACK, current)
    return (
        f'NEW PROPOSAL FEEDBACK ({len(new)}) in `proposals/feedback/`:\n  - ' +
        '\n  - '.join(sorted(new))
    )


def check_new_ta_proposals():
    """Surface new TA proposals since last session — may need SA input."""
    if not TA_PROPOSALS_DIR.exists():
        return None
    current = set(
        f.name for f in TA_PROPOSALS_DIR.iterdir()
        if f.is_file() and f.suffix == '.md' and f.name not in ('INDEX.md', 'README.md')
    )
    last = read_marker_set(MARK_TA_PROPOSALS)
    if not last:
        write_marker_set(MARK_TA_PROPOSALS, current)
        return None
    new = current - last
    if not new:
        return None
    write_marker_set(MARK_TA_PROPOSALS, current)
    return (
        f'NEW TA PROPOSAL(S) ({len(new)}) in `agents/trading_advisor/proposals/` '
        f'— may need SA review/input:\n  - ' + '\n  - '.join(sorted(new))
    )


# -- main --

def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    parts = []

    # Mailbox notices first (transient + actionable; close to user prompt)
    notices = []
    for fn in (check_directive, check_ta_mailbox, check_ma_mailbox,
               check_er_mailbox, check_inbox, check_new_feedback,
               check_new_ta_proposals):
        try:
            result = fn()
            if result:
                notices.append(result)
        except Exception as e:
            notices.append(f'<!-- check error: {fn.__name__}: {e} -->')

    if notices:
        parts.append('<mailbox-notices>')
        parts.append('\n\n'.join(notices))
        parts.append('</mailbox-notices>')
        parts.append('')

    # Then: full CLAUDE.md as reference context
    try:
        if CLAUDE_MD_PATH.exists():
            content = CLAUDE_MD_PATH.read_text(encoding='utf-8')
            parts.append('<project-context source="CLAUDE.md">')
            parts.append(content)
            parts.append('</project-context>')
        else:
            parts.append(f'<!-- CLAUDE.md not found at {CLAUDE_MD_PATH} -->')
    except Exception as e:
        parts.append(f'<!-- Error reading CLAUDE.md: {e} -->')

    output = {
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': '\n'.join(parts)
        }
    }
    json.dump(output, sys.stdout)


if __name__ == '__main__':
    main()
