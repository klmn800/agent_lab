# Feedback Convention

Each feedback file in this directory should begin with a single STATUS line so the System Analyst (and any reviewing Claude) can read proposal lifecycle at a glance without parsing prose.

## Format

First line of the file:

```
STATUS: <STATE> [YYYY-MM-DD] [— optional one-line note]
```

Where `<STATE>` is one of:
- `IMPLEMENTED` — Ben (or a dev session) has shipped the change. Date = when implemented.
- `APPROVED` — Decision is yes, but not yet built.
- `DEFERRED` — Not now, revisit later. Note explains *why*.
- `DECLINED` — Not doing this. Note explains *why*.
- `IN_REVIEW` — Ben is actively considering. Optional, used when feedback is being drafted.

After the STATUS line, a blank line, then the rest of the feedback prose as before.

## Naming

- Numbered proposal feedback: `NNN_proposal_name.md` (matches the proposal number).
- Ad-hoc feedback (not tied to a numbered proposal): `adhoc_YYYYMMDD_topic.md` or any descriptive name. Still gets a STATUS line if applicable, otherwise omit.

## Why

Before this convention, I had to either spot-check the code to see if a proposal was implemented, or read the full feedback prose to infer Ben's intent. The single STATUS line makes status machine-readable and lets `INDEX.md` / `STATUS.md` stay in sync without duplicate work.

## Maintenance

- When Ben writes new feedback, he can add the STATUS line if convenient. If not, the System Analyst adds it during session-start integration based on Ben's prose.
- If a status changes (e.g., DEFERRED becomes IMPLEMENTED later), update the line in the existing feedback file rather than creating a new one. Add a date suffix to track the change: `STATUS: IMPLEMENTED 2026-05-15 (was DEFERRED 2026-04-19)`.

*Convention added 2026-04-23 (Session 014).*
