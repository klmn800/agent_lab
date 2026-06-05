# Strategy-Specific Reference

Two strategies live here. TA reads the matching folder when actively screening or interpreting a setup in that domain.

## Earnings (`earnings/`)

Pre-earnings and earnings-cycle plays driven by the Earnings Intelligence (EI) signal system. Two named lanes:

- **The IV Ramp** — directional pre-earnings drift. Enter into the IV expansion, exit before the print. Direction-agnostic signal + flow + price action determine call vs put.
- **The Earnings Straddle** — magnitude-only play. Buy ATM straddle 1-3 days before the print, sell the morning after. Profits when realized move > market-implied expected move.

Read order when an earnings signal needs interpretation: `earnings/README.md` → `earnings/playbook.md`. Read `earnings/mechanics.md` when a number on the watchlist needs explanation or you're checking a gotcha (BMO/AMC baseline, denominator artifacts, IV crush tiers).

## Flow (`flow/`)

Substrate present, codification pending. Patterns, mechanics, and case studies for the Flow Monitor's BUILDING/CLOSING resolution work, low-OI anomalies, ATM short-dated call builds, and predictive alerts. To be codified after the earnings lane lands.

## What "strategy-specific" means here

A doc earns its place here when TA actually consults it during morning briefs or trade interpretation. System architecture and pipeline internals live in the main codebase's `docs/` — this folder is for the trader's-eye reference, not the operator's.
