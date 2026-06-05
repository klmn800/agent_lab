# Trade Notes

Live position notes — one file per active position. Dated, data-driven, easily findable.

## Purpose

While a trade is open, the trade note is the durable memory for it. The orientation hook surfaces the position (symbol, qty, marks); the trade note surfaces the *why*, the *plan*, and the *state evolution*. Future-TA reads it to remember what this position is doing here and what to look at when assessing it.

## Lifecycle

1. **Open.** Position appears (Ben opens, or paper-trade trigger fires). Create `<SYM>_<entry_date>.md` from `_TEMPLATE.md`. Fill the thesis + plan + initial state.
2. **Live.** Append dated state-evolution entries when something changes — price level breaks, IV move, flow update, news, sector context. One short entry per change, not a daily journal.
3. **Close.** When the position closes, the trade note is the substrate for the Saturday case study. Once the case study lands in `analysis/case_studies/`, this trade note is cleared (deleted) — the case study has the durable narrative.

## Discipline

- **Objective. Just the facts.** Price, IV, OI, flow, news, sector. Ben's behavior is also a fact — log it ("Ben took half off here", "Ben raised stop to $X", "Ben said he was uncomfortable with the drawdown but holding"). No conviction ratings, no TA "calls", no pre-decided entries/exits unless Ben said so.
- **Descriptive, not prescriptive.** OK: "thesis line A intact, line B broken (WTI closed below $75)." Not OK: "I'd close this here." Unless Ben asks for the read, the trade note is the log, not the recommendation.
- **One file per position.** A roll keeps the same file; the entry-date in the filename is the *first* entry of the campaign. New strike/expiry on the same name = new section in the same file with a clear "ROLL" header.
- **Don't repeat reference docs.** If the thesis uses a pattern documented in `reference/`, cite it — don't re-explain.

## Naming

- `<SYM>_<YYYY-MM-DD>.md` — symbol + first-entry date.
- Multi-leg or multi-name arcs that are coherent (e.g., DVN+CTRA paired on a merger): one file titled by the primary leg, with the paired leg as a section inside. If the arc grows into a campaign with substantial scaffolding (queries, dossiers, daily checks), promote to its own subdirectory under `analysis/campaigns/`. See `analysis/dvn_ctra_campaign/` for the historical example of that promotion.

## What this replaces

The old `memory/trade_calls.md` model (one file mixing live state + conviction ratings + paper trades + calibration). Retired 2026-05-18 per workspace reset. Conviction ratings deferred; calibration is MA's lane now.
