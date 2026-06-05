"""
Earnings Researcher context injection hook.
Fires on every UserPromptSubmit.

Surfaces two independent context blocks:

  <mailbox-notices>   (only when something new is detected)
    - directive.md content (if non-empty)
    - inbox/ unprocessed files
    - inbound mailboxes: for_earnings_researcher.md from TA/SA/MA (tail if mtime changed)

  <dispute-list>      (always, with sentinel-based batching)
    - today's unresolved earnings date disputes (PERF_DB)
    - cached IR URLs (DATALAKE_DB.symbol_metadata)
    - backfill of unconfirmed-but-undisputed earnings_upcoming rows (within HORIZON)

Limit enforcement applies to the dispute block ONLY — mailbox notices are
always checked, even on re-injection turns, because handoffs may arrive
mid-session.

State markers live in this hooks/ directory as `.last_*` files.
First run for any mailbox/inbox check is silent (initializes the marker).

Output: JSON with hookSpecificOutput.additionalContext
"""

import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(r'E:\options_scanner')
AGENT_DIR = PROJECT_ROOT / 'agents' / 'earnings_researcher'
HOOK_DIR = Path(__file__).parent
DATALAKE_DB = PROJECT_ROOT / 'data' / 'datalake.db'
PERF_DB = PROJECT_ROOT / 'data' / 'performance.db'

SENTINEL = AGENT_DIR / '.session_injected'

# Mode marker written by launcher.py: 'weekend' for the maintenance (Sunday)
# session, 'daily' (or absent) for normal dispute-resolution runs.
SESSION_MODE_FILE = AGENT_DIR / '.session_mode'
ARCHIVE_DIR = AGENT_DIR / 'memory' / 'archive'
RESEARCH_LOG = AGENT_DIR / 'memory' / 'research_log.md'

# Daily ceiling on combined disputes + unconfirmed backfill (when .session_limit = 0).
# Disputes always come first (already prioritized by reason+date); remaining slots
# are filled from earnings_upcoming where date_confirmed = 0, sorted by earnings_date ASC.
TOTAL_CEILING = 25

# Only surface symbols whose earnings date is within this many days of today.
# Companies typically don't issue their "to Announce" press release more than
# ~3 weeks ahead, so further-out symbols are unresearchable noise.
HORIZON_DAYS = 14

# -- mailbox / inbox config --

INBOX_DIR = AGENT_DIR / 'inbox'
DIRECTIVE_FILE = AGENT_DIR / 'directive.md'

# Inbound mailboxes from other agents (each writes to their own workspace).
# Tuple format: (path, marker, label, rel_path_for_display)
# Sender path is `outbox/` since 2026-05-18 — was `memory/` before that.
INBOUND_MAILBOXES = [
    (
        PROJECT_ROOT / 'agents' / 'trading_advisor' / 'outbox' / 'for_earnings_researcher.md',
        HOOK_DIR / '.last_ta_mailbox_seen',
        'TA',
        'agents/trading_advisor/outbox/for_earnings_researcher.md',
    ),
    (
        PROJECT_ROOT / 'agents' / 'system_analyst' / 'outbox' / 'for_earnings_researcher.md',
        HOOK_DIR / '.last_sa_mailbox_seen',
        'SA',
        'agents/system_analyst/outbox/for_earnings_researcher.md',
    ),
    (
        PROJECT_ROOT / 'agents' / 'market_analyst' / 'outbox' / 'for_earnings_researcher.md',
        HOOK_DIR / '.last_ma_mailbox_seen',
        'MA',
        'agents/market_analyst/outbox/for_earnings_researcher.md',
    ),
]

INLINE_CAP_BYTES = 2048


# -- helpers --

def _read_limit():
    """Read batch limit from .session_limit. Returns 0 (no limit) or positive int."""
    try:
        text = (AGENT_DIR / '.session_limit').read_text(encoding='utf-8').strip()
        return int(text)
    except Exception:
        return 0


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


def tail_inline(content, cap=INLINE_CAP_BYTES):
    """Return last `cap` bytes of content, with a leading marker if truncated."""
    if len(content) <= cap:
        return content
    return (
        '... [truncated, full file is {:,} bytes — '
        'read the file for full content] ...\n'.format(len(content)) + content[-cap:]
    )


# -- mailbox / inbox checks --

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


def check_inbox():
    """Surface unprocessed inbox files. Self-clears via the move-to-processed convention."""
    if not INBOX_DIR.exists():
        return None
    items = []
    for entry in INBOX_DIR.iterdir():
        if entry.is_file() and entry.name not in ('README.md', '.gitkeep'):
            items.append(entry.name)
    if not items:
        return None
    return (
        'INBOX has {} unprocessed file(s) — read each, integrate into memory, '
        'then move to `inbox/processed/`:\n  - '.format(len(items)) +
        '\n  - '.join(sorted(items))
    )


def check_inbound_mailbox(path, marker, label, rel_path):
    """Tail an inbound mailbox if mtime advanced past the marker. First run initializes silently."""
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
        return '{} mailbox updated but unreadable: {}'.format(label, e)
    when = datetime.fromtimestamp(current).strftime('%Y-%m-%d %H:%M')
    block = [
        '{} MAILBOX UPDATED — `{}` (mtime {})'.format(label, rel_path, when),
        'Tail (last 2KB; read full file at orientation if you want context above):',
        '```markdown',
        tail_inline(content),
        '```',
    ]
    write_marker_float(marker, current)
    return '\n'.join(block)


def build_mailbox_notices():
    """Return joined notices string, or None if nothing to surface."""
    notices = []

    # directive + inbox first
    for fn in (check_directive, check_inbox):
        try:
            result = fn()
            if result:
                notices.append(result)
        except Exception as e:
            notices.append('<!-- check error: {}: {} -->'.format(fn.__name__, e))

    # inbound mailboxes
    for path, marker, label, rel_path in INBOUND_MAILBOXES:
        try:
            result = check_inbound_mailbox(path, marker, label, rel_path)
            if result:
                notices.append(result)
        except Exception as e:
            notices.append('<!-- check error: inbound {}: {} -->'.format(label, e))

    if not notices:
        return None
    return '<mailbox-notices>\n' + '\n\n'.join(notices) + '\n</mailbox-notices>'


# -- session mode --

def read_session_mode():
    """Return 'weekend' for the maintenance session, else 'daily' (the default)."""
    try:
        mode = SESSION_MODE_FILE.read_text(encoding='utf-8').strip().lower()
        return mode or 'daily'
    except Exception:
        return 'daily'


def build_maintenance_block(now):
    """Orientation block for the weekly maintenance (Sunday) session.

    Replaces the <dispute-list>. No disputes/backfill are surfaced — this
    session is workspace upkeep + calibration, not date research. Gives a
    few cheap signals so the agent can size up the cleanup at a glance.
    """
    parts = ['<maintenance-session>']
    parts.append("Today's date: {} ({})".format(now.strftime('%Y-%m-%d'), now.strftime('%A')))
    parts.append('Weekly maintenance session — the dispute list is suppressed on purpose. '
                 'Follow PROMPT_SUNDAY.md.')
    parts.append('')

    try:
        text = RESEARCH_LOG.read_text(encoding='utf-8')
        lines = text.count('\n') + 1
        kb = len(text.encode('utf-8')) / 1024
        parts.append("research_log.md: {:,} lines (~{:.0f} KB)".format(lines, kb))
    except Exception:
        parts.append("research_log.md: not found")

    try:
        archives = sorted(f.name for f in ARCHIVE_DIR.glob('*.md')) if ARCHIVE_DIR.exists() else []
        if archives:
            parts.append("memory/archive/: {} file(s) — {}".format(len(archives), ', '.join(archives)))
        else:
            parts.append("memory/archive/: empty (no rolled-off logs yet)")
    except Exception:
        pass

    parts.append('')
    parts.append('Open carry-over symbols + next-check dates live in STATUS.md / the '
                 'research-log header.')
    parts.append('</maintenance-session>')
    return '\n'.join(parts)


# -- dispute-list (unchanged behavior, just extracted) --

def build_dispute_list(now, today_str, horizon_str, limit):
    """Build the <dispute-list> string. Honors sentinel for limited-batch sessions."""
    parts = []

    # If a limit is set and we already injected once this session, don't re-inject
    if limit > 0 and SENTINEL.exists():
        try:
            sentinel_date = SENTINEL.read_text(encoding='utf-8').strip()
            if sentinel_date == today_str:
                return (
                    '<dispute-list>\nBatch already injected (limit {}). '
                    'No new disputes to add.\n</dispute-list>'.format(limit)
                )
        except Exception:
            pass

    # Date header
    parts.append('<dispute-list>')
    parts.append("Today's date: {} ({})".format(today_str, now.strftime('%A')))
    parts.append("Current time: {}".format(now.strftime('%I:%M %p')))
    parts.append('')

    # Get unresolved disputes, prioritized: date_disagreement > both > unknown_time
    PRIORITY = {'date_disagreement': 0, 'both': 1, 'unknown_time': 2}
    disputes = []
    try:
        conn = sqlite3.connect(str(PERF_DB), timeout=10)
        conn.execute("PRAGMA busy_timeout = 10000")
        rows = conn.execute("""
            SELECT symbol, db_date, db_time, yfinance_date, finnhub_date, dispute_reason
            FROM earnings_date_disputes
            WHERE trade_date = ?
              AND (resolution = 'unresolved' OR resolution IS NULL)
              AND db_date <= ?
            ORDER BY db_date ASC, symbol ASC
        """, (today_str, horizon_str)).fetchall()
        conn.close()
        rows.sort(key=lambda r: (PRIORITY.get(r[5], 9), r[1] or '9999'))
        if limit > 0:
            disputes = rows[:limit]
        else:
            disputes = rows
    except Exception as e:
        parts.append("Error reading disputes: {}".format(e))

    # Backfill: if no .session_limit and disputes < TOTAL_CEILING, pull unconfirmed
    # symbols from earnings_upcoming (date_confirmed = 0) sorted by soonest first.
    backfill_count = 0
    if limit == 0 and len(disputes) < TOTAL_CEILING:
        remaining = TOTAL_CEILING - len(disputes)
        existing = {d[0] for d in disputes}
        try:
            conn = sqlite3.connect(str(DATALAKE_DB), timeout=10)
            conn.execute("PRAGMA busy_timeout = 10000")
            unconfirmed = conn.execute("""
                SELECT symbol, earnings_date, earnings_time
                FROM earnings_upcoming
                WHERE (date_confirmed = 0 OR date_confirmed IS NULL)
                  AND earnings_date >= ?
                  AND earnings_date <= ?
                ORDER BY earnings_date ASC, symbol ASC
            """, (today_str, horizon_str)).fetchall()
            conn.close()
            for sym, ed, et in unconfirmed:
                if sym in existing:
                    continue
                if remaining <= 0:
                    break
                disputes.append((sym, ed, et, None, None, 'unconfirmed'))
                remaining -= 1
                backfill_count += 1
        except Exception as e:
            parts.append("Note: unconfirmed backfill failed: {}".format(e))

    if not disputes:
        parts.append("No unresolved disputes for today.")
        parts.append('</dispute-list>')
        return '\n'.join(parts)

    # Get cached IR URLs and company names
    ir_urls = {}
    company_names = {}
    try:
        conn = sqlite3.connect(str(DATALAKE_DB), timeout=10)
        conn.execute("PRAGMA busy_timeout = 10000")
        symbols = [d[0] for d in disputes]
        placeholders = ','.join('?' * len(symbols))
        for row in conn.execute(
            "SELECT symbol, company_name, ir_earnings_url FROM symbol_metadata WHERE symbol IN ({})".format(
                placeholders), symbols):
            company_names[row[0]] = row[1]
            if row[2]:
                ir_urls[row[0]] = row[2]
        conn.close()
    except Exception:
        pass

    # Get confirmed-by-ben symbols (agent must never overwrite these)
    ben_confirmed = set()
    try:
        conn = sqlite3.connect(str(DATALAKE_DB), timeout=10)
        conn.execute("PRAGMA busy_timeout = 10000")
        for row in conn.execute(
            "SELECT symbol FROM earnings_upcoming WHERE date_confirmed_by = 'ben'"):
            ben_confirmed.add(row[0])
        conn.close()
    except Exception:
        pass

    if backfill_count > 0:
        dispute_only = len(disputes) - backfill_count
        parts.append("Symbols to research ({} total: {} disputes, {} unconfirmed-but-undisputed):".format(
            len(disputes), dispute_only, backfill_count))
    else:
        parts.append("Symbols to research ({} disputes):".format(len(disputes)))
    for i, (sym, db_date, db_time, yf_date, fh_date, reason) in enumerate(disputes, 1):
        company = company_names.get(sym, 'Unknown')
        parts.append("{}. {} ({}) -- DB date: {}, time: {}, reason: {}".format(
            i, sym, company, db_date, db_time or 'Unknown', reason))
        if yf_date and yf_date != db_date:
            parts.append("   yfinance: {}, finnhub: {}".format(yf_date, fh_date or 'None'))
        elif fh_date and fh_date != db_date:
            parts.append("   finnhub: {} (disagrees with DB)".format(fh_date))
        cached_url = ir_urls.get(sym)
        if cached_url:
            parts.append("   Cached IR URL: {}".format(cached_url))
        else:
            parts.append("   Cached IR URL: None")
        if sym in ben_confirmed:
            parts.append("   *** CONFIRMED BY BEN — DO NOT OVERWRITE ***")

    parts.append('</dispute-list>')

    # Write sentinel if limit is set — prevents re-injection on subsequent turns
    if limit > 0:
        try:
            SENTINEL.write_text(today_str, encoding='utf-8')
        except Exception:
            pass

    return '\n'.join(parts)


# -- main --

def main():
    # Consume stdin (hook sends JSON input)
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    horizon_str = (now + timedelta(days=HORIZON_DAYS)).strftime('%Y-%m-%d')
    limit = _read_limit()

    blocks = []

    # Mailbox notices always checked — even on re-injection turns
    notices = build_mailbox_notices()
    if notices:
        blocks.append(notices)
        blocks.append('')

    # Weekend maintenance session suppresses the dispute list entirely;
    # daily sessions get the sentinel-gated dispute-list as usual.
    if read_session_mode() == 'weekend':
        blocks.append(build_maintenance_block(now))
    else:
        blocks.append(build_dispute_list(now, today_str, horizon_str, limit))

    output = {
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': '\n'.join(blocks)
        }
    }
    json.dump(output, sys.stdout)


if __name__ == '__main__':
    main()
