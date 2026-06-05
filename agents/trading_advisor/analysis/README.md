# Analysis Directory

TA's writeable workspace for trade tracking, morning briefs, and live trade campaigns. Post-split layout (2026-05-18).

## Structure

```
analysis/
├── trade_notes/                 # live position notes (one per open position)
│   ├── README.md
│   └── _TEMPLATE.md
├── paper_trade_notes/           # hypothetical setups w/ explicit triggers
│   ├── README.md
│   └── _TEMPLATE.md
├── case_studies/                # closed-trade narratives (Saturday cadence)
│   ├── INDEX.md
│   └── _TEMPLATE.md
├── daily_briefs/                # morning brief archive (YYYY-MM-DD.md)
├── campaigns/                   # multi-trade thesis arcs (one-pager each)
├── dvn_ctra_campaign/           # HISTORICAL — first formalized campaign (closed)
└── README.md                    # this file
```

## What goes where

- **Open a position →** create `trade_notes/<SYM>_<date>.md` from `_TEMPLATE.md`.
- **Log a hypothetical trigger →** create `paper_trade_notes/<SYM>_<date>.md` from `_TEMPLATE.md`.
- **Close a position →** Saturday, write `case_studies/<SYM>_<entry_date>.md`, add to `case_studies/INDEX.md`, retire the trade note.
- **Morning brief →** `daily_briefs/<YYYY-MM-DD>.md`.
- **Multi-trade thesis arc** (e.g., a sector-level positioning campaign with multiple legs and multiple decisions): one-pager in `campaigns/<YYYY-MM>_<theme>.md`. If it grows into substantial scaffolding (queries, dossiers, daily checks), promote to its own subdirectory like the historical `dvn_ctra_campaign/`.

## Historical

- `dvn_ctra_campaign/` — the first formalized campaign workspace (2026-04-23 → 2026-05-18, position closed today). Kept in place as historical reference; its keeper lessons are captured in `analysis/case_studies/case_study_DVN_2026-04-23.md` and `analysis/case_studies/case_study_DVN_2026-05-06.md`.
- `campaigns/2026-04_dvn_ctra_merger.md` — the campaign one-pager that paired with the workspace above.
- Ad-hoc dated files at this level (`2026-04-22_DAL_sympathy.md`, `2026-04-23_earnings_date_bug_report.md`, `week_plan_2026-04-27.md`) — pre-scaffolding artifacts. Leave in place; new ad-hoc work goes into the appropriate subdirectory above.

## What used to be here (moved to MA on 2026-05-17)

- `peer_sympathy_program/` — MA-owned now
- `alert_alpha_program/` — MA-owned now
- `low_oi_anomaly/` — MA-owned now
- `research/` — MA-owned now

If you find references to these in old files, they live in MA's `analysis/` now.
