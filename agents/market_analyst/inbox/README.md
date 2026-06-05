# Market Analyst Inbox

A drop zone for asynchronous handoffs to the Market Analyst. You don't need me to be running for you to leave a note — I'll read everything here at the start of my next session.

## Who writes here

- **Developer Claude Code sessions** — when you make a code change that affects research surfaces (new tables, schema changes, query DB sync changes, data quality fixes, things I should re-validate).
- **Ben** — informal notes that don't rise to the level of a directive. Use `directive.md` (root of my workspace) if you want to set my session focus; use the inbox for everything else.
- **Other agents** (TA, SA, ER) — prefer the mailbox pattern: write `outbox/for_market_analyst.md` in your own workspace for ongoing back-and-forth. Use this inbox only for one-off drops where appending to an outbox would feel out of place.

## How to write here

Drop a markdown file with the filename pattern:

```
YYYY-MM-DD_short-kebab-topic.md
```

Examples:
- `2026-05-20_new-column-earnings-snapshots.md`
- `2026-05-21_query-db-schema-change.md`
- `2026-05-22_ben-note-research-direction.md`

Keep it short — a few hundred words max. Structure I find useful:

1. **What changed** (one line)
2. **Why** (one line)
3. **Files touched** (list, optional)
4. **Impact on research** (what I should re-read, re-compute, or stop trusting)

Don't worry about formatting polish. I'd rather have a terse note than none.

## What happens after I read it

1. I integrate the information into my memory (research_backlog, session_notes, predictions_log, MEMORY index — wherever it lands).
2. I move the file into `inbox/processed/` with the same filename.
3. If the note triggers further action (a proposal, a follow-up study, a question back to you), I handle it in my normal workflow.

Files in `processed/` are kept indefinitely — cheap storage, useful historical record of changes that crossed my radar.

## When NOT to use this

- If you want me to do something specific next session → write to `directive.md` in my workspace root.
- If it's a bug I should track but not act on urgently → it'll surface when I look at the data. No need to flag.
- If it's a proposed change you want me to design → propose it in a regular chat with Ben; this inbox is for completed/in-flight work, not feature requests.
