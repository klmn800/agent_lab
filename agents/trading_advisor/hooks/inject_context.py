"""
Trade Advisor context injection hook.
Fires on every UserPromptSubmit.

Hook A (always): Current time, day of week, market session
Hook B (gated):  Market snapshot during pre-market/open, 5-min cooldown
                 - Market regime (SPY/VIX/breadth)
                 - Market-wide top-3 flow alerts
                 - Universe flow today (alerts on my positions/open-calls)
                 - My positions (live marks + P&L from ta_v_positions_live)
Hook C (gated):  Live Tradier quotes for SPY/VIX + universe + watchlist, 2-min cooldown

Output: JSON with hookSpecificOutput.additionalContext

Sources state from the four ta_v_* views (see proposals/011). Refactored
2026-04-27 to drop the trade_calls.md scrape in favor of the canonical
view stack.
"""

import sys
import json
import sqlite3
import re
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# -- Configuration --
HOOK_DIR = Path(__file__).parent
COOLDOWN_FILE = HOOK_DIR / '.last_market_snapshot'
LIVE_COOLDOWN_FILE = HOOK_DIR / '.last_live_quotes'
DB_PATH = Path(r'E:\options_scanner\data\datalake_query.db')
CONFIG_PATH = Path(r'E:\options_scanner\config.json')
LIVE_WATCHLIST_PATH = Path(r'E:\options_scanner\agents\trading_advisor\memory\live_watchlist.md')
COOLDOWN_MINUTES = 5
LIVE_COOLDOWN_MINUTES = 2
ET = ZoneInfo('America/New_York')

# -- Cross-agent mailbox notification (P018; outbox/ since 2026-05-18 — was memory/) --
SA_MAILBOX = Path(r'E:\options_scanner\agents\system_analyst\outbox\for_trading_advisor.md')
MARK_SA_MAILBOX = HOOK_DIR / '.last_sa_mailbox_seen'
ER_MAILBOX = Path(r'E:\options_scanner\agents\earnings_researcher\outbox\for_trading_advisor.md')
MARK_ER_MAILBOX = HOOK_DIR / '.last_er_mailbox_seen'
INLINE_CAP_BYTES = 2048


def get_eastern_now():
    return datetime.now(ET)


def market_session(now):
    """Classify current market session."""
    if now.weekday() >= 5:
        return 'weekend'
    t = now.hour * 60 + now.minute
    if 240 <= t < 570:      # 4:00 - 9:30
        return 'pre-market'
    elif 570 <= t < 960:     # 9:30 - 16:00
        return 'open'
    elif 960 <= t < 1200:    # 16:00 - 20:00
        return 'post-market'
    return 'closed'


def cooldown_ok():
    try:
        if not COOLDOWN_FILE.exists():
            return True
        last = float(COOLDOWN_FILE.read_text().strip())
        return (datetime.now().timestamp() - last) >= COOLDOWN_MINUTES * 60
    except Exception:
        return True


def touch_cooldown():
    try:
        COOLDOWN_FILE.write_text(str(datetime.now().timestamp()))
    except Exception:
        pass


def live_cooldown_ok():
    try:
        if not LIVE_COOLDOWN_FILE.exists():
            return True
        last = float(LIVE_COOLDOWN_FILE.read_text().strip())
        return (datetime.now().timestamp() - last) >= LIVE_COOLDOWN_MINUTES * 60
    except Exception:
        return True


def touch_live_cooldown():
    try:
        LIVE_COOLDOWN_FILE.write_text(str(datetime.now().timestamp()))
    except Exception:
        pass


def query_db(sql):
    """Read-only query, returns list of dicts. Empty list on error."""
    try:
        conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(sql).fetchall()]
        conn.close()
        return rows
    except Exception as e:
        return [{'_error': str(e)}]


def fmt(val, spec='.2f', prefix='', suffix=''):
    if val is None:
        return '-'
    try:
        return f'{prefix}{val:{spec}}{suffix}'
    except (ValueError, TypeError):
        return str(val)


# ── Universe + positions (sourced from views) ─────────────────────────

def query_universe_symbols():
    """Symbols in TA universe = positions UNION open/proposed trade_calls."""
    rows = query_db("""
        SELECT symbol FROM trade_positions
        UNION
        SELECT symbol FROM trade_calls WHERE status IN ('proposed','open')
        ORDER BY symbol
    """)
    if not rows or '_error' in rows[0]:
        return []
    return [r['symbol'] for r in rows]


def query_positions_live():
    """All current positions with live marks + P&L. Joins trade_positions.notes for entry thesis."""
    return query_db("""
        SELECT v.position_key, v.symbol, v.instrument_type, v.strike, v.option_type, v.expiration_date,
               v.net_qty, v.avg_buy_price, v.current_mark, v.current_pnl_pct,
               v.target_pct, v.stop_pct, v.pct_to_target, v.pct_to_stop,
               v.dte_remaining, v.days_to_time_stop,
               tp.notes
        FROM ta_v_positions_live v
        LEFT JOIN trade_positions tp ON tp.position_key = v.position_key
        ORDER BY v.symbol, v.expiration_date
    """)


def query_universe_flow_today():
    """Flow alerts on universe symbols hitting today."""
    return query_db("""
        SELECT trade_date, symbol, strike, option_type, premium_value, alert_level, scope_reason
        FROM ta_v_position_flow_recent
        WHERE trade_date = date('now', 'localtime')
        ORDER BY premium_value DESC
        LIMIT 5
    """)


def build_positions_block(positions):
    """Render the my-positions section. None if empty."""
    if not positions or '_error' in positions[0]:
        return None

    lines = ['My positions (live marks):']
    for p in positions:
        sym = p['symbol']
        qty = p['net_qty']
        avg = p['avg_buy_price']
        mark = p['current_mark']
        pnl = p['current_pnl_pct']

        if (p.get('instrument_type') == 'option' and p.get('strike')
                and p.get('option_type') and p.get('expiration_date')):
            try:
                ed = datetime.strptime(p['expiration_date'], '%Y-%m-%d')
                exp_short = f'{ed.month}/{ed.day}'
            except Exception:
                exp_short = p['expiration_date']
            contract = f'{sym} {exp_short} {p["strike"]:g}{p["option_type"][0]}'
        else:
            contract = f'{sym} stock'

        avg_s = fmt(avg, '.2f', prefix='$')
        mark_s = fmt(mark, '.2f', prefix='$')
        pnl_s = fmt(pnl, '+.1f', suffix='%') if pnl is not None else '-'
        line = f'  {contract:18s} qty {qty} @ {avg_s} -> {mark_s}  {pnl_s}'

        extras = []
        if p.get('pct_to_target') is not None:
            extras.append(f'{p["pct_to_target"]:+.0f}% to target')
        if p.get('pct_to_stop') is not None:
            extras.append(f'{p["pct_to_stop"]:+.0f}% to stop')
        if p.get('dte_remaining') is not None:
            extras.append(f'{p["dte_remaining"]} DTE')
        if p.get('days_to_time_stop') is not None:
            extras.append(f'time-stop in {p["days_to_time_stop"]}d')
        if extras:
            line += f'  ({" / ".join(extras)})'

        lines.append(line)

        notes = (p.get('notes') or '').strip()
        if notes:
            note_lines = [ln.strip() for ln in notes.splitlines() if ln.strip()]
            if note_lines:
                lines.append(f'      thesis: {note_lines[0]}')
                for nl in note_lines[1:]:
                    lines.append(f'              {nl}')
    return '\n'.join(lines)


def build_universe_flow_block(rows):
    """Render flow alerts hitting universe symbols today. None if empty."""
    if not rows or '_error' in rows[0]:
        return None
    lines = [f'Flow on my universe today: {len(rows)}']
    for r in rows:
        pv = fmt(r['premium_value'], ',.0f', prefix='$')
        scope = r.get('scope_reason') or '-'
        lines.append(
            f'  {r["symbol"]} {r["strike"]} {r["option_type"]} {pv} '
            f'[{r["alert_level"]}] [{scope}]'
        )
    return '\n'.join(lines)


# ── Watchlist + Tradier ──────────────────────────────────────────────

def read_live_watchlist():
    """Optional live watchlist file. One symbol per line, # comments."""
    try:
        if not LIVE_WATCHLIST_PATH.exists():
            return []
        text = LIVE_WATCHLIST_PATH.read_text(encoding='utf-8')
        symbols = []
        for line in text.split('\n'):
            line = line.split('#', 1)[0].strip()
            if line and re.match(r'^[A-Z][A-Z0-9\.]{0,5}$', line):
                symbols.append(line)
        return symbols
    except Exception:
        return []


def fetch_tradier_quotes(symbols):
    if not symbols:
        return {}
    try:
        cfg = json.load(open(CONFIG_PATH))
        key = cfg['tradier']['api_key']
        base = cfg['tradier'].get('base_url', 'https://api.tradier.com')
        sym_csv = ','.join(symbols)
        url = f'{base}/v1/markets/quotes?symbols={sym_csv}'
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {key}', 'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.load(r)
        quotes = data.get('quotes', {}).get('quote', [])
        if isinstance(quotes, dict):
            quotes = [quotes]
        out = {}
        for q in quotes:
            out[q['symbol']] = {
                'last': q.get('last'),
                'chg_pct': q.get('change_percentage'),
                'bid': q.get('bid'),
                'ask': q.get('ask'),
            }
        return out
    except Exception as e:
        return {'_error': str(e)}


def build_live_quotes_block(now):
    """Live Tradier quotes for SPY/VIX + universe + watchlist."""
    universe_syms = query_universe_symbols()
    wl_syms = read_live_watchlist()
    # Macro context: SPY (broad market), VIX (vol regime), USO (oil — leading
    # indicator for energy-exposed positions like DVN/CTRA, added 2026-05-07
    # after sector-driven DVN selloff revealed the gap).
    ctx_syms = ['SPY', 'VIX', 'USO']

    seen = set()
    all_syms = []
    for s in ctx_syms + universe_syms + wl_syms:
        if s not in seen:
            all_syms.append(s)
            seen.add(s)
    if not all_syms:
        return None

    quotes = fetch_tradier_quotes(all_syms)
    if '_error' in quotes:
        return f'Live quotes unavailable: {quotes["_error"]}'

    def row(sym, q):
        last = q.get('last')
        chg = q.get('chg_pct')
        bid = q.get('bid')
        ask = q.get('ask')
        last_s = f'{last:>8.2f}' if isinstance(last, (int, float)) else f'{str(last):>8}'
        chg_s = f'{chg:+.2f}%' if isinstance(chg, (int, float)) else f'{chg}'
        line = f'  {sym:6s} {last_s}  {chg_s:>7}'
        if isinstance(bid, (int, float)) and isinstance(ask, (int, float)):
            line += f'  (bid {bid} / ask {ask})'
        return line

    lines = [f'Live quotes (as of {now.strftime("%I:%M %p ET")}, Tradier):']
    for s in ctx_syms:
        if s in quotes:
            lines.append(row(s, quotes[s]))

    universe_only = [s for s in universe_syms if s not in ctx_syms]
    if universe_only:
        lines.append('  -- my universe --')
        for s in universe_only:
            if s in quotes:
                lines.append(row(s, quotes[s]))

    wl_only = [s for s in wl_syms if s not in ctx_syms and s not in universe_syms]
    if wl_only:
        lines.append('  -- watchlist --')
        for s in wl_only:
            if s in quotes:
                lines.append(row(s, quotes[s]))

    return '\n'.join(lines)


# ── Market snapshot ──────────────────────────────────────────────────

def build_market_snapshot(now):
    lines = []
    ts = now.strftime('%Y-%m-%d %I:%M %p ET')
    lines.append(f'<market-snapshot as-of="{ts}">')

    # 1. Market regime
    rows = query_db("""
        SELECT trade_date, regime_classification, market_direction,
               spy_close, spy_change_percent,
               vix_close, vix_change_percent,
               advancing_stocks, declining_stocks
        FROM market_daily_summary
        ORDER BY trade_date DESC LIMIT 1
    """)
    if rows and '_error' not in rows[0]:
        m = rows[0]
        lines.append(f'Market ({m["trade_date"]}): {m["regime_classification"]} | {m["market_direction"]}')
        lines.append(
            f'SPY: {fmt(m["spy_close"])} ({fmt(m["spy_change_percent"], "+.2f", suffix="%")})'
            f' | VIX: {fmt(m["vix_close"])} ({fmt(m["vix_change_percent"], "+.2f", suffix="%")})'
        )
        lines.append(
            f'Breadth: {m.get("advancing_stocks", "-")} advancing'
            f' / {m.get("declining_stocks", "-")} declining'
        )
    elif rows:
        lines.append(f'Market data error: {rows[0]["_error"]}')
    else:
        lines.append('No market summary available.')

    # 2. Market-wide flow alerts: count + newest 5 by alert_timestamp
    # (Replaced top-3-by-premium 2026-04-28 — that was sticky all day and clipped
    # mid-tier alerts that fired intraday. Newest-by-timestamp surfaces what's
    # happening NOW between prompts. Full feed always queryable from flow_alerts.)
    count_rows = query_db(
        "SELECT COUNT(*) as cnt FROM flow_alerts WHERE trade_date = date('now', 'localtime')"
    )
    count = count_rows[0]['cnt'] if count_rows and '_error' not in count_rows[0] else 0

    newest = query_db("""
        SELECT symbol, strike, option_type, premium_value, alert_level, alert_timestamp
        FROM flow_alerts
        WHERE trade_date = date('now', 'localtime')
        ORDER BY alert_timestamp DESC LIMIT 5
    """)

    lines.append('')
    lines.append(f'Flow alerts today: {count} (showing newest 5)')
    if newest and '_error' not in newest[0]:
        for a in newest:
            pv = fmt(a['premium_value'], ',.0f', prefix='$')
            ts = a.get('alert_timestamp', '')
            hhmm = ts[11:16] if isinstance(ts, str) and len(ts) >= 16 else ''
            lines.append(
                f'  {hhmm} {a["symbol"]} {a["strike"]} {a["option_type"]} {pv} [{a["alert_level"]}]'
            )

    # 3. Universe flow today (only if any)
    uflow = query_universe_flow_today()
    uflow_block = build_universe_flow_block(uflow)
    if uflow_block:
        lines.append('')
        lines.append(uflow_block)

    # 4. Live Tradier quotes (gated by 2-min cooldown)
    if live_cooldown_ok():
        lq_block = build_live_quotes_block(now)
        if lq_block:
            lines.append('')
            lines.append(lq_block)
            touch_live_cooldown()

    lines.append('</market-snapshot>')
    return '\n'.join(lines)


# ── Cross-agent mailbox notification (P018) ───────────────────────────

def _safe_mtime(p):
    try:
        return p.stat().st_mtime
    except Exception:
        return None


def _read_marker_float(p):
    try:
        return float(p.read_text().strip())
    except Exception:
        return None


def _write_marker_float(p, v):
    try:
        p.write_text(str(v))
    except Exception:
        pass


def _tail_inline(content, cap=INLINE_CAP_BYTES):
    if len(content) <= cap:
        return content
    return (
        f'... [truncated, full file is {len(content):,} bytes — '
        f'read the file for full content] ...\n' + content[-cap:]
    )


def _check_mailbox(path, marker, label, rel_path):
    """Generic mailbox tail surfacer. First run initializes silently."""
    if not path.exists():
        return None
    current = _safe_mtime(path)
    last = _read_marker_float(marker)
    if last is None:
        _write_marker_float(marker, current)
        return None
    if current <= last:
        return None
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        _write_marker_float(marker, current)
        return f'{label} mailbox updated but unreadable: {e}'
    when = datetime.fromtimestamp(current).strftime('%Y-%m-%d %H:%M')
    block = [
        f'{label} MAILBOX UPDATED — `{rel_path}` (mtime {when})',
        'Tail (last 2KB; read full file at orientation if you want context above):',
        '```markdown',
        _tail_inline(content),
        '```',
    ]
    _write_marker_float(marker, current)
    return '\n'.join(block)


def check_sa_mailbox():
    return _check_mailbox(
        SA_MAILBOX, MARK_SA_MAILBOX, 'SA',
        'agents/system_analyst/outbox/for_trading_advisor.md'
    )


def check_er_mailbox():
    return _check_mailbox(
        ER_MAILBOX, MARK_ER_MAILBOX, 'ER',
        'agents/earnings_researcher/outbox/for_trading_advisor.md'
    )


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    now = get_eastern_now()
    session = market_session(now)

    parts = []

    # P018: cross-agent mailbox notices appear ABOVE session-context so
    # transient/actionable content sits closer to the user prompt.
    notices = []
    for fn in (check_sa_mailbox, check_er_mailbox):
        try:
            notice = fn()
            if notice:
                notices.append(notice)
        except Exception as e:
            notices.append(f'<!-- check error: {fn.__name__}: {e} -->')
    if notices:
        parts.append('<mailbox-notices>')
        parts.append('\n\n'.join(notices))
        parts.append('</mailbox-notices>')
        parts.append('')

    parts.extend([
        '<session-context>',
        f'Current datetime: {now.strftime("%Y-%m-%d %I:%M %p")} ET',
        f'Day of week: {now.strftime("%A")}',
        f'Market session: {session}',
        '</session-context>',
    ])

    within_cooldown = cooldown_ok()

    # Positions — all sessions (not gated by market hours), same 5-min cooldown
    if within_cooldown:
        positions = query_positions_live()
        pos_block = build_positions_block(positions)
        if pos_block:
            parts.append('')
            parts.append(pos_block)

    # Full market snapshot — market hours only
    if session in ('pre-market', 'open') and within_cooldown:
        parts.append('')
        parts.append(build_market_snapshot(now))

    if within_cooldown:
        touch_cooldown()

    output = {
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': '\n'.join(parts)
        }
    }
    json.dump(output, sys.stdout)


if __name__ == '__main__':
    main()


# ============================================================================
# NOTE TO TRADING ADVISOR AGENT:
#
# This hook injects context into every one of your conversations with Ben.
# Sourced from the four ta_v_* views (see proposals/011) — refactored
# 2026-04-27 to drop the trade_calls.md scrape in favor of the canonical
# view stack.
#
# After ~2 weeks of use, audit:
#   - Is the my-positions block too verbose with target/stop annotations?
#   - Is universe-flow-today catching real signal or mostly empty?
#   - Could position P&L move from 2-min to 5-min cooldown without me noticing?
#   - Any block adding <5% utility per turn but ~50 tokens? Kill it.
#
# Death by a thousand paper cuts is real — this output appears in EVERY prompt.
#
# Test changes by running: echo '{"prompt":"test"}' | python <this_file>
# ============================================================================
