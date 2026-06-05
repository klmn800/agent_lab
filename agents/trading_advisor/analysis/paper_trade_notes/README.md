# Paper Trade Notes

Hypothetical positions TA tracks because Ben doesn't have infinite cash to take every interesting setup. Per Ben (workspace_reset.md Section 11): "We SHOULD track hypothetical trades with set triggers, since I do not have infinite cash to test all opportunities. MA should be focused on looking back, TA should be focused on predicting forward."

Mirrors the `trade_notes/` layout, with stricter trigger discipline.

## Purpose

When an interesting setup surfaces (alert, flow pattern, earnings setup) but Ben doesn't take it, log it here with explicit triggers. Then track the outcome honestly. Over time, this gives a forward-looking record of what TA would have entered — material for MA's calibration loop without contaminating the live trade record.

## Lifecycle

1. **Open.** Setup catches attention → create `<SYM>_<YYYY-MM-DD>.md` from `_TEMPLATE.md`. **Entry must be triggered**, not assumed. The trigger spells out the exact condition that would have caused entry (e.g., "5/19 9:35 ET pre-market quote at $48.40, intent: buy $50C 6/18 at ~$1.40 with limit"). If the trigger never fires, the position never "opens" and the note closes as a no-trigger pass.
2. **Live (if triggered).** Same state-evolution discipline as `trade_notes/`. Mark prices using the closing mid each day; if a more precise mid is available from the orientation hook or Tradier quote, use that.
3. **Close.** When the exit trigger fires (target hit, stop hit, time stop), close the paper position with the closing mid. Compute % PnL.

## Discipline

- **Triggers are non-negotiable.** No "I would have entered around here" hand-waving. Either the trigger spec'd at open fires, or the position doesn't open.
- **Use mid, not bid/ask favorability.** Slippage assumption: paper fills happen at the midpoint of bid/ask at the trigger moment. If the spread is wide enough that fills would realistically be worse, note it.
- **No retro-entries.** If a setup surfaced 3 days ago and TA didn't log it, it doesn't get a backfill paper trade.
- **Tag the source.** Was this triggered by an alert, a brief observation, a flow pattern, a peer-sympathy read? The tag matters for MA's later analysis of where TA's forward-looking instinct works and where it doesn't.

## What this is NOT

- **Not a substitute for MA's backtesting.** Paper trades are forward-looking from the moment they're logged. MA does the look-back work with proper baselines and historical samples.
- **Not conviction-rated.** No "STRONG BUY" / "WATCH" labels. Just: the setup, the trigger, the outcome.
- **Not a complete record of every setup TA noticed.** Only the ones interesting enough to commit to with an explicit trigger.

## Naming

- `<SYM>_<YYYY-MM-DD>.md` — symbol + log date (which may be before or after trigger date, since triggers may be future-conditional).
