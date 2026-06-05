# Market Analyst Analysis

Working output from MA sessions. Distinct from `reference/` (durable library) and `reference/staging/` (pipeline to TA).

## Subdirectories

| Dir | Purpose |
|---|---|
| `research/` | Single-session research deep-dives. Migrated from TA at MA go-live. |
| `peer_sympathy_program/` | Active multi-session research program. Charter + current_state inside. |
| `alert_alpha_program/` | PRIMARY active research program (since 2026-05-06). Charter + current_state inside. |
| `low_oi_anomaly/` | Historical research that produced `pattern_low_oi_anomaly.md` in TA's reference. |
| `case_studies/` | NEW case studies (one per closed trade or notable resolved setup). Graduate the best ones via `reference/staging/`. |
| `grading/` | Trade-call grading output. Filename: `YYYY-MM-DD_<symbol>.md`. Saturday cadence. |

## What stays here vs what graduates

`analysis/` is your scratchpad and working space. Findings that should become part of TA's playbook get distilled into a staged file in `reference/staging/` with proper frontmatter. The original analysis stays here for traceability — staged files reference the source analysis path.
