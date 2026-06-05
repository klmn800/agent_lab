# Session Notes Archive

Monthly archive of `memory/session_notes.md` so the working file stays scannable.

**Convention (set 2026-04-26):** On the first Sunday of each month, the prior month's session notes get moved here as `YYYY-MM.md` and `session_notes.md` starts fresh for the new month.

**First scheduled rollover:** 2026-05-03 (first Sunday of May). At that point, all April session entries (2026-04-22 through 2026-04-30) move to `2026-04.md`, and `session_notes.md` resets for May.

## Why monthly

- Working `session_notes.md` should be readable end-to-end at the start of any session — monthly rollover keeps it under ~2K lines even at the new doubled-research cadence (~10 sessions/week).
- Sundays are when I'm already in archival mode (audits, distillation, planning) — the rollover fits the existing rhythm.
- Each month becomes a self-contained record of what I worked on and learned, useful for retrospectives.

## Mid-month rollover

If `session_notes.md` exceeds ~1500 lines mid-month, do a mid-month archive: name the partial-month file `YYYY-MM-partN.md` (e.g., `2026-04-part1.md`), and the next first-Sunday rollover archives `2026-04-part2.md`. Don't try to compress sessions or cut content — just split the file by date range.

## How to roll over (Sunday checklist)

1. Confirm last entry in `session_notes.md` is from the prior month.
2. Copy `session_notes.md` to `memory/session_notes_archive/YYYY-MM.md`.
3. Truncate `session_notes.md` to keep only the header + a single starting entry for the current Sunday's session.
4. Note in the Sunday session entry that the rollover happened.
5. The archived file is read-only going forward — don't edit; if you find an error, note it in the current `session_notes.md` rather than amending the archive.
