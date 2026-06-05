# Earnings Researcher Inbox

A drop zone for asynchronous handoffs to the Earnings Researcher. You don't need me to be running for you to leave a note — I'll read everything here at the start of my next session.

## Who writes here

- **Developer Claude Code sessions** — when you change something that affects how I research earnings dates: dispute table schema, `earnings_confirm.py` CLI, `ir_earnings_url` column behavior, source-priority rules, new data sources to try, retired sources to stop using.
- **Ben** — informal notes that don't rise to the level of changing my CLAUDE.md. Examples: "for this batch, skip ADRs," "the BABA IR URL stopped working — re-find it," "I confirmed CRM manually, ignore the dispute."
- **Other agents** (System Analyst, Trading Advisor, Market Analyst) — for one-off drops. If there's ongoing back-and-forth, use the mailbox pattern: write `outbox/for_earnings_researcher.md` in your own workspace and my hook will surface it when its mtime changes.

## How to write here

Drop a markdown file with the filename pattern:

```
YYYY-MM-DD_short-kebab-topic.md
```

Examples:
- `2026-05-20_dispute-table-new-column.md`
- `2026-05-21_skip-adrs-this-batch.md`
- `2026-05-22_ben-note-prioritize-tech.md`

Keep it short — a few hundred words max. Structure I find useful:

1. **What changed** (one line)
2. **Why** (one line)
3. **Files touched** (list, optional)
4. **Impact on my research** (what I should do differently — new behavior, sources to add/drop, symbols to skip, etc.)

## What happens after I read it

1. I integrate the information into my research approach for the session and, if it's durable, into `memory/` (research_log.md or a new project_*.md memory file).
2. I move the file into `inbox/processed/` with the same filename.
3. If the note triggers further action (a question back to you, a finding worth flagging to Ben), I handle it in my normal workflow (`notes_for_ben.md`, or outbound mailbox to the relevant agent).

Files in `processed/` are kept indefinitely — cheap storage and useful as a historical record.

## When NOT to use this

- If you want a permanent rule change in how I research → propose it as a CLAUDE.md edit instead.
- If it's a one-time symbol confirmation Ben already did → just run `earnings_confirm.py --by ben`; I read `date_confirmed_by` and won't overwrite.
- If it's a bug in `earnings_confirm.py` or `direct_db_query.py` → that's developer-side; fix it directly. I'll pick up the new behavior on next run.

## How I learn about new inbox files

My `hooks/inject_context.py` runs on every prompt and lists any non-`README.md` files sitting in this directory. I'll see "INBOX has N unprocessed file(s)" in the injected context block.
