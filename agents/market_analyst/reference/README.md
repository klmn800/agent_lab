# Market Analyst Reference Library

Your **working library** — methodology, frameworks, calibration notes, research conduct rules. Writeable by you.

Distinct from `reference/staging/`, which is the **pipeline to TA** — patterns and mechanics you want TA to use in trade calls, waiting for Ben's graduation gate.

## What belongs here (MA-only)
- Research methodology docs ("how I run a Saturday session", "validation vs discovery framing")
- MA-specific glossary or calibration framework
- Process notes that don't need to reach TA
- Copies of TA's reference docs that are MA-relevant too (e.g., `lesson_build_your_own_tools.md`)

## What belongs in `staging/` instead
- Patterns / mechanics / lessons MA wants TA to use in trade calls
- New case studies of completed trades
- Validated playbook entries

See `staging/README.md` for the graduation schema and process.

## Data-shape facts live with TA
Critical schema gotchas, table grains, data freshness — those live in `agents/trading_advisor/reference/`. Don't duplicate them here. If you discover something TA's docs miss, draft an update via `staging/`.
