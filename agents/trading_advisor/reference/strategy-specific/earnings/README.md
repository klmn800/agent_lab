# Earnings Strategy

Trading Advisor (TA) agent opens this folder when:
- An earnings signal (WATCH+) appears on the watchlist and needs interpretation for the morning brief.
- A setup with an earnings catalyst inside the next 14 days is being evaluated.
- Ben asks "what's coming up this week?" or "should we play X's earnings?"
BEN: IS THIS TRIGGERED BY SOMETHING? A HOOK?

## The two lanes

The Earnings Intelligence (EI) system produces a single signal per name (AVOID / NEUTRAL / WATCH / BUY / STRONG BUY). **That signal is direction-agnostic** — it measures magnitude underpricing, not which way the stock will move. From a WATCH+ signal you have two viable trade structures:

| Lane | Thesis | Direction | Hold through earnings? |
|---|---|---|---|
| **The IV Ramp** | Pre-earnings vega expansion + directional drift | Yes — call OR put, derived from flow + price action | **No** — exit before the print, avoid IV crush |
| **The Earnings Straddle** | Realized move > market-implied expected move | **No** — bet on magnitude in either direction | **Yes** — sell morning after |

The screening workflow in `playbook.md` walks through which lane (if any) the data supports for each WATCH+ candidate.

## Direction is not in the signal

EI's "STRONG BUY" is a magnitude-mispricing flag. It does not predict up or down. The IV Ramp lane needs directional input from elsewhere — flow first, price action second. Treating EI's signal as a bullish call is the most common way TA gets tripped up here.

## Read order

1. `playbook.md` — daily screening workflow + lane-selection + per-lane execution. Where TA spends most of its time.
2. `mechanics.md` — how the EI signal system works, formulas, gotchas, key columns. Reference when a number needs explanation or a calibration question comes up.

## Out of scope

System architecture, pipeline internals, file references, and schema details for the EI production system live in `docs/` in the main codebase. This folder is trader-facing only.
