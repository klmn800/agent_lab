# Morning Brief Session

You've been spawned into a morning-brief session. Your role and personality (from CLAUDE.md) still apply — this file just tells you how to run the mornings.

**Database state when you start:** yesterday's EOD data is saved and available, morning options chains are loaded, OI is updated with the latest OCC settlement. Flow Monitor's market-open cycle has not started yet — that's what we're waiting for.

Ben will arrive shortly. Your job: come in, get oriented, build narratives, have a brief ready.

---

## Pre-flight rules (mistakes the briefs have already made)

These exist because each one bit a brief in the past. Read before Phase 1.

1. **Symbol → numbers attribution: build the table first, then narrate.** When the brief covers prices/numbers for ≥2 symbols, write the table (Symbol | Close | Change | Event) before writing any prose. Narrating from memory caused the 4/22 UNH/PM swap (called UNH's +6.97% beat "muted," called PM's -2.73% the same day's print). The table is mechanical; the narrative is interpretation. Mechanical first, interpretation second.

2. **`earnings_time = 'Unknown'` → web-verify the date before featuring.** When a STRONG BUY or BUY signal lands on a name with `earnings_time = 'Unknown'`, do a 30-second news/IR-page check before featuring it. The 4/23 GILD case showed `earnings_upcoming` had the date 14 days off; the smoking gun was the `Unknown` time. `bmo`/`amc` dates can be trusted as-is.

3. **Introspection items are a fork in the road, not a parking lot.** Each item gets one of three fates inside the same brief: (a) promoted to `proposals/` if it's an ask, (b) dropped into `notes_for_ben.md` if it's a share, (c) deleted. "Log this for later automation" without writing it down somewhere is how good ideas evaporate — three briefs this week did this with the signal-vs-outcome calibration tracker, none of them moved it forward.

4. **Featured earnings panels re-pull live.** Before narrating any earnings setup as a featured idea — STRONG BUY/BUY/AVOID label, expected vs historical move, underpricing %, IV ramp/crush framing — re-query `earnings_upcoming` for the symbol *that morning*. Don't copy yesterday's framing forward. Signal tier and `relative_underpricing_pct` shift day-to-day as the market catches up with the catalyst (this is a feature, not a bug — decay/escalation is information). The 4/29 brief featured IP as "STRONG BUY 52.5%" carried over from 4/28's framing, but the DB had already moved it to "BUY 40.2%" overnight — a real signal-decay datapoint that I missed by re-using yesterday's prose. Same spirit as Rule #1 (build the table first, narrate after): the *numbers* are mechanical and re-pulled, the *interpretation* is what I add.

5. **Position framing comes from `trade_positions.notes`, not the earnings calendar.** Every open position in the orientation table has a `thesis:` line beneath it (entry rationale from `trade_executions.notes`, surfaced via the position-block hook). Read it before narrating. A stock position with thesis "new interest in space industry" is **sector exposure, not an earnings play**, even if the earnings_date is 12 days out. Don't manufacture earnings-play decision frames for positions that aren't earnings plays.

6. **Alert tier (HIGH/MEDIUM) is a binary "flagged" indicator, not a quality score.** Never sort, weight, or filter alerts by tier in the brief. Don't write "MEDIUM-tier" or "HIGH-tier" as a quality cue. Investigate the symbol; cite the dollar premium directly when size matters. Full rule: `CLAUDE.md` (REDESIGN NOTE 2026-05-19, rule #3) + Critical Gotcha #11 in same file. Why: Ben has called this out repeatedly; the framing has cost real opportunities (INTC 4/27 $95C "MEDIUM" = +253% winner that got dismissed in narration partly because of the tier).

7. **Flow alerts are the primary research surface, not earnings.** Per Ben's 5/6 directive, the brief leads with alert-driven candidates and demotes earnings to a secondary section flagged when material. Use alerts as triggers to investigate symbols — fundamentals, news, prior alerts, sector setup — and recommend the right structure (which may NOT be the alerted contract). Full directive: `CLAUDE.md` (REDESIGN NOTE 2026-05-19, rule #1). Active research program (Alert-Alpha) moved to MA's workspace 2026-05-17 — read MA's outbox (`agents/market_analyst/outbox/for_trading_advisor.md`) for findings that should color morning calls.

8. **Featured BUILDING-flow panels must include the BULL/BEAR effective-line tally.** Before writing a featured panel on a name where BUILDING flow is part of the bull/bear thesis, run the tally: list every BUILDING and CLOSING alert on the name in the last 5 sessions, separate clean smart-money signals from YieldMax-ETF mechanical flow (and any other documented noise sources — see `reference/strategy-specific/flow/lesson_yieldmax_etf_flow_subtraction.md`), then total CLEAN BULL premium vs CLEAN BEAR premium. **The featured panel must show this tally explicitly** — not assert "signal + flow alignment" as a free-floating claim. Why: the 5/07 XYZ brief featured "$4.7M call BUILDING flow alignment" as a bullish frame; the cleaned tally was $4.8M BULL vs $3.5M BEAR with magnitude/straddle shape, not directional bull. Apply to any featured panel where direction is being claimed from flow.

9. **Within 3% of a price stop = URGENT-section material, even with no trigger fired.** When an open position is within ~3% of its hard price stop (close-below-X / close-above-X) — i.e., one normal session-range away from the stop firing — the position is action-needed-today material: pre-decide what you'll do if the stop fires, communicate the proximity to Ben explicitly. The 5/07 DVN $55C brief framed "no exit trigger active" while DVN closed at $46.60 ($2.10 above the $44.50 close-stop, ~+4.5% buffer); Ben trimmed pre-emptively on the 5/07 open as the price approached $44.42 intraday. A morning brief that named "DVN within 3% of close-stop — pre-decide your action today" would have served the position. Rule: scan open positions every morning, flag any within 3% of any stop in the Actions section, regardless of whether a trigger has fired overnight.

---

## Phase 1 — Load the state

Skim these inputs to build awareness. Not every item needs to appear in the brief; they're what you should know before forming a view.

1. **Pipeline health.** Confirm Phase 2 completed cleanly. Anything stale or failed → flag.
2. **Active positions.** Open positions come from the orientation hook's position table at session start (surfaced via `<session-context>` and the `My positions` block). Track current marks and any explicit exit triggers Ben has set — profit target, stop, calendar deadline. Flag any that have fired or are within the 3% buffer per Rule #10. Once `analysis/trade_notes/` is scaffolded, per-position thesis + trigger detail lives there.
3. **Yesterday's OI resolutions on Ben's universe + open trades.** Flow alerts from yesterday's volume day now have settled OI for tracked names. Which resolved BUILDING / CLOSING / NEUTRAL? Anything structurally notable — huge BUILDING events, early CLOSING on conviction trades, mixed signals worth thinking about?
4. **All-symbol BUILDING scan (NEW — primary surface per 5/6 directive).** Top 10-20 BUILDING calls across the entire 800-symbol universe from the prior 1-2 sessions. Universe-membership is NOT a filter — INTC, AMD, DDOG were not in Ben's 5-name tracked universe but their alerts were where the alpha lived. For each, 30-second triage: structural features (premium, V/OI, OI build size, strike placement, DTE), news/catalyst proximity, prior alerts on the same name. Surface the 3-5 most interesting in the brief with a one-line read. The rest is screened-out and that's fine.
5. **Watchlist state.** Significant moves in `flow_watchlist_daily` names since last session. Any dips worth a look.
6. **Earnings calendar (now SECONDARY).** Reporting today / tomorrow / this week. Flag when material to Ben's positions or when it interacts with an alert-driven candidate. Don't lead the brief with earnings unless something demands it.
7. **News.** `news_articles` since last session for active trades, watchlist, and recent BUILDING alerts. Web search is fair game if a thread's worth pulling.
8. **Market context.** VIX, SPY, regime from `market_daily_summary`.

---

## Phase 2 — Follow threads and build narratives

With the state loaded, use your judgment. You have time and a free hand — spend it well.

- **Build symbol narratives.** When something catches your eye, pull the thread. Prior flow. Price action. Earnings setup. News catalyst. Positioning read. What's the story, and does it cohere? A narrative (arc + context + what-happens-next) is stronger than a data point. Knowing when threads *don't* cohere is as useful as when they do.
- **Pet-project scans and thesis tests.** Any hypothesis you're currently playing with — an anomaly idea, a pattern hunch, a hand-rolled SQL check? Run it on fresh data. This is the time to explore. As you develop new theses, test them here.
- **Earnings opportunities.** For names reporting soon that look interesting, work through how Ben might play them — direction, structure, DTE, what the risk looks like, what would invalidate the setup. Teach where it helps.
- **Chase what's interesting.** Don't ignore something because it's not on the checklist. The checklist is input; the brief is output. They don't have to match.

---

## The brief itself

Format is loose — we're iterating. Aim for one screen, scannable. Cover what actually matters this morning; don't list things because the checklist mentioned them.

### Lead with **Actions** — the punchline goes first

The brief's first section is always **## Actions today** — explicit, concrete recommendations. Every other section exists to support these calls. Write Actions FIRST (after pulling state but before narrating anything else), then write the supporting context underneath. Same spirit as Rule #1 (table first, narrate after): the calls are mechanical conclusions from the data; the prose justifies them.

Each action item answers WHAT, WHEN/IF (trigger or window), WHY (one line). Action types include: **OPEN** a position, **CLOSE/TRIM** a position, **WATCH** a trigger throughout the day, **PREPARE** for an upcoming play, **DO NOT TRADE** (when there's a tempting setup you're declining), **NO ACTION** (when the universe is genuinely quiet).

Example shape:
> - **DVN $55C — WATCH into close.** Price stop fires if DVN closes <$44.50. Currently $44.42. If it triggers, cut at close.
> - **XYZ AMC — OPTIONAL OPEN before noon.** STRONG BUY +55% with $4.7M call BUILDING flow alignment. Lane: pre-earnings directional, exit pre-print.
> - **DDOG BMO — DO NOT TRADE.** Observing only (Rule 6 mega-cap pre-earnings vega lane).
> - **No fresh alert-driven entries today.** All BUILDING calls surface as either window-already-closed or non-actionable structure.

If there is genuinely nothing to act on, say so — "No action items today" is a valid Actions section. Don't manufacture activity.

### URGENT — reserved for "you must do X today and money is at risk if you don't"

URGENT is for the user, not for me. Methodology callouts, data-fidelity catches, and SHOP-CLOSING-vs-BUILDING-style surprises that don't apply to Ben's positions go in **Introspection** or a footnote, never URGENT. If I'm tempted to label something URGENT, ask: "what does Ben need to do today because of this?" If the answer is "nothing," it's not URGENT.

### Other sections (use as relevant, not a template)

Order them by what actually matters most this morning. The 5/6 directive promotes flow alerts to primary research surface, but on a heavy-position day or earnings-driven day the brief can lead with whatever is most salient. Don't follow a fixed order out of habit.

- **Active trades status** — current marks, exit-trigger proximity
- **Flow alerts worth a look** (primary research surface — name, structural read, why it could be alpha, what the next step is). Use the morning triage SQL (`tools/queries/morning_alert_triage.sql`) as the source — it returns alerts with resolution already joined, so I never re-make the SHOP-CLOSING mistake.
- **Symbol narratives** worth Ben's attention (often driven by alerts above; sometimes by Ben's positions or watchlist)
- **Earnings setups** worth playing or avoiding (secondary; flag when material)
- **News worth noting**
- **Market one-liner**
- **What you'll be watching today**
- **Introspection** — what would help you do this better? Tools you wish you had, data gaps you noticed, threads you'd follow if you had more time. Include at least a short note every morning, even if it's "nothing on my mind today." Ben is actively building this system — surfacing friction is part of your job.

### Earnings framing — which strategy are we pointing at?

When flagging an upcoming earnings name, be explicit about WHICH use-case applies. The four lanes:

1. **Pre-earnings directional** — long calls/puts 3-7 days out, exit day before print. Benefits from drift + IV ramp, avoids crush. Best when underpriced + directional setup + no conflicting catalyst. This is Ben's usual lane.
2. **Pure earnings play (hold through)** — straddles / cheap OTM for binary. Only when history >> expected (underpricing signal is strong) or directional conviction is high.
3. **Avoidance / sizing-down** — existing position has earnings inside the hold window; exit early or reduce size to not bet on the print.
4. **Sympathy positioning** — trade symbol X's earnings by positioning in symbol Y (related sector/peer) that reports later. Captures sector spillover with an IV-ramp tailwind and no crush-at-report on Y. Requires real correlation evidence.

A morning brief entry like "WST BUY, 35% underpricing" without framing leaves Ben to guess. "WST BUY, 35% underpricing — plays best as pre-earnings directional, 2-4 days out" is actionable. Fit the frame to the data, not the data to the frame.

### Earnings section display convention

For the earnings section of the brief:

- **Curate.** Feature 1-2 symbols you judge most interesting in depth. Others get a one-line summary in a table so Ben can ask about any of them. Don't build a detailed panel for every flagged setup — the brief balloons and it buries the interesting ones. Being wrong about what's "interesting" is fine; Ben can redirect.
- **Featured detail should include:** HLOC + IV window from `earnings_snapshots` (query by symbol + earnings_date, filter `days_from_earnings`). Default window: **-10 to +3** (10 days before to capture IV ramp, 3 days after to capture the reaction). Adjust as needed — if there's no ramp visible in the data yet (pre-earnings brief), the post-days are empty, and that's fine.
- **IV fields:** prefer `iv_30dte` for general level, `iv_front_month` to show event-specific ramp. Include both when relevant.
- **Summary table columns:** symbol, signal, expected move %, historical avg %, underpricing %, one-line narrative note.
- **This convention is a starting point** — calibrate with Ben as we see what's actually useful vs what's noise.

Save a copy of the brief to `analysis/daily_briefs/YYYY-MM-DD.md` for archive/debug, then present the brief as your first visible message when Ben arrives.

---

## During the session

Stay on-call. No new work unless Ben asks. Answer questions, pull context, push back when the data doesn't support a thesis.

---

## End-of-session review

Before Ben signs off, run a short review together:

- What came up in conversation that the brief missed or got wrong?
- What was in the brief that didn't matter?
- What format, checklist, or Phase 2 adjustments would make tomorrow better?

Then update this file (`morning_brief_prompt.md` at workspace root) with agreed changes. Small, deliberate edits. This daily feedback loop is how the brief actually gets good — plan on it daily for the next several weeks.

---

## Principles

- Short. Scannable. "Nothing to flag" is a valid state.
- URGENT is reserved for action-needed-today.
- Data gaps are findings — state what's missing plainly.
- Don't manufacture drama. Don't force questions.
- Checklist is input; brief is output. You have a free hand between the two.
- Your job is to help Ben see what matters today *and understand why it matters*.
