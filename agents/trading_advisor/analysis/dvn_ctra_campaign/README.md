# DVN / CTRA Campaign Workspace

Purpose: durable home for all research, tracking, and infrastructure related to Ben's DVN-CTRA merger thesis. Ben seeded this 2026-04-23 and asked me to build out what I need to support morning briefings, research sessions, and interactive reads on the campaign.

This is NOT a scratch folder. Everything here should be directly useful to a future session picking up the thread.

---

## Folder structure

```
dvn_ctra_campaign/
├── README.md                     ← this file
├── dossier.md                    ← master thesis, timeline, positions, catalysts (the single source of truth) ✅ BUILT
├── flow_log.md                   ← rolling log of notable DVN/CTRA flow alerts (append-only, human-readable) ✅ BUILT
├── daily_check.md                ← template + running daily check entries ✅ BUILT
├── queries/                      ← reusable query scripts (5/5 built ✅)
│   ├── 01_oi_progression.sql
│   ├── 02_flow_alerts_recent.sql
│   ├── 03_iv_term_structure.sql
│   ├── 04_chain_snapshot.sql
│   └── 05_price_vs_thresholds.sql
├── daily_updates/                ← dated "status report" files (one per update, keeps dossier clean)
└── snapshots/                    ← dated raw query output dumps (in case I need to look back)
```

**Status as of 2026-04-23 evening:** scaffolding fully built. Position open, infrastructure ready for daily/weekly use. Next session work is the historical validation pass (R-014 in backlog).

## How I use this

**Morning brief prep:** read `dossier.md` top section, run `queries/05_price_vs_thresholds.sql` and `queries/02_flow_alerts_recent.sql`. Two minutes. Know whether anything moved overnight that affects Ben's position.

**Research session:** pick up whatever thread is open. The `dossier.md` `## Open Threads` section lists them.

**Interactive session if Ben calls me to discuss:** the dossier is my cheat sheet. I can cite the shareholder vote date, deal terms, current ratio spread, recent flow activity, all from one file.

**Position resolution:** when the 5/29 $50C resolves (any exit trigger fires), the grading goes into `dossier.md` under `## Position Grading` and copies back to `memory/trade_calls.md`.

---

## Key references outside this workspace

- `memory/trade_calls.md` — the live trade entry (`2026-04-23 — DVN 5/29 $50C @ $1.80`)
- `memory/research_backlog.md` — R-014 is the formal research backlog entry
- `reference/pattern_merger_positioning.md` — the durable pattern doc this campaign seeded

---

## What I explicitly am NOT doing here

- Writing to production databases (workspace-only, per write guard)
- Replicating information that lives in reference/ — the thesis *uses* patterns documented there; it doesn't re-explain them
- Making this a narrative journal — dossier stays factual, daily_updates/ has the narrative log
