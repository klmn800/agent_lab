# Trading Advisor Inbox

A drop zone for asynchronous handoffs to me (the Trading Advisor). You don't need me to be running for you to leave a note — I'll read everything in this folder at the start of my next session.

Modeled on the System Analyst's inbox protocol (`agents/system_analyst/inbox/README.md`); same shape, separate folder.

## Who writes here

- **Developer Claude Code sessions** — when you've done work that affects my analysis or trading workflow: a System Analyst proposal that I authored just got executed, a new tool/script landed that I should know about, a data backfill cleared a gap in one of my studies, a bug got fixed that I'd flagged.
- **Ben** — informal notes that don't rise to the level of a directive. Use `directive.md` (root of my workspace) if you want to set my session focus; use the inbox for everything else (FYIs, "take a look at this when you can," design proposals you want my opinion on, etc.).
- **System Analyst** — already has a working bidirectional channel via `agents/system_analyst/outbox/for_trading_advisor.md` ↔ `agents/trading_advisor/outbox/for_system_analyst.md` (each writes their outbound in their own workspace; receivers' hooks tail by mtime). Keep using those mailboxes for ongoing back-and-forth. Drop one-off cross-agent notifications here if an outbox entry would feel out of place.

## How to write here

Drop a markdown file with the filename pattern:

```
YYYY-MM-DD_short-kebab-topic.md
```

Examples:
- `2026-04-25_proposal-003-executed.md`
- `2026-04-25_earnings-radar-proposal.md`
- `2026-04-30_tradier-quote-cli-extended.md`

Keep it short — a few hundred words is plenty. Structure I find useful, but not required:

1. **What changed / what's the ask** (one line)
2. **Why** (one line)
3. **Files touched / data affected** (list, optional)
4. **Impact on my work** (what I should re-read, re-compute, stop trusting, or act on)

Don't worry about formatting polish. A terse note beats no note. If you want to drop a longer design proposal for me to review, that's fine too — say so explicitly so I treat it as a review request rather than an FYI.

## What happens after I read it

The same routing rules apply regardless of who dropped the note:

1. **Integrate into my workspace.** The note's information goes wherever it belongs — `reference/data_quality_guards.md` if it's a contamination flag, `reference/schema_guide.md` if it's a column rename, `proposals/INDEX.md` if it closes out a proposal of mine, `memory/research_backlog.md` if it unblocks a study, etc. The inbox file itself is the *notification*, not the home.
2. **Move the original file to `inbox/processed/`** with the same filename. This preserves the audit trail.
3. **Reply through my normal channels** when the note needs a response:
   - **System Analyst questions / mailbox replies** → I write to `outbox/for_system_analyst.md`. They'll see it at their next session start.
   - **Ben questions, FYIs, opinions** → I write to `notes_for_ben.md` (low-action items) or `proposals/` (when I have a structured opinion or design ask Ben should route).
   - **Proposal review requests from Ben (via developer)** → I write a structured response document at `proposals/<NNN>_<topic>.md` and flag its existence in `notes_for_ben.md`. Ben can then forward to whoever needs to see it (typically System Analyst for implementation thoughts).
   - **Bug or anomaly flagged that I want to track** → it becomes a `proposals/` entry with INDEX.md updated.
4. **Quick acknowledgments stay inline** — if a note is purely informational ("X was deployed, no action needed"), processing it is just integration + archive. No reply file.

The summary I want to leave for myself in a session: when you read this folder at session start, every file moves *somewhere* before the session ends. Either to `processed/`, to a downstream document, or both.

## What this inbox is NOT for

- **Setting my session focus.** That's `directive.md`. The inbox is FYI / async handoffs; the directive is "do this, specifically."
- **Holding my replies.** Replies live in the destination channel (`outbox/for_<agent>.md`, `notes_for_ben.md`, etc.), not back in the inbox. The inbox is one-directional intake; outbound traffic uses other doors.
- **Holding stuff you want me to track but not act on.** I'll process it (move it to `processed/`) every session — if the relevant info doesn't get integrated into a durable doc, it disappears from my session-start view. If you want me to monitor something on a recurring basis, write it into the relevant `reference/`, `memory/`, or `agenda.md` entry directly (or have me do so via a directive).

## Locations referenced from here

- **My workspace root:** `agents/trading_advisor/`
- **Reply channels:**
  - `agents/trading_advisor/outbox/for_system_analyst.md` — cross-agent mailbox to System Analyst (also `for_market_analyst.md`, `for_earnings_researcher.md`)
  - `agents/trading_advisor/notes_for_ben.md` — informal notes for Ben
  - `agents/trading_advisor/outbox/for_market_analyst.md` — for structured asks that would have gone to `proposals/` pre-split; MA writes proposals now
- **System Analyst's mirror:** `agents/system_analyst/inbox/README.md` — the protocol I patterned this on. If something here drifts out of sync with the SA inbox in a way that confuses developer sessions writing to both, prefer the SA version's wording.

## Worked examples

`processed/2026-04-25_proposal-003-executed.md` — short FYI: a developer session executed a proposal I had pending; I integrated the cutover doc into `reference/data_quality_guards.md`, marked the proposal IMPLEMENTED in `proposals/INDEX.md`, archived the inbox note. No reply file needed.

`processed/2026-04-25_earnings-radar-proposal.md` — design review request from Ben (via developer): I read the proposal, wrote a structured opinion at `proposals/010_earnings_radar_review.md`, flagged the response's existence in `notes_for_ben.md`, archived the inbox note. Ben can forward my response wherever it needs to go.
