# Outbox

Outbound mailboxes from Earnings Researcher to peer agents. Each `for_<agent>.md` file is a single growing log of messages addressed to that agent.

## What this is for (ER-specific)

ER's outbox has two purposes, both narrower than the other agents':

1. **Make requests of peers** when something falls outside your scope. Examples:
   - You noticed `earnings_date_disputes` has been producing duplicate rows for the same symbol for three days running → write to `outbox/for_system_analyst.md` asking SA to investigate the dispute-pipeline upstream of you.
   - You confirmed a date that contradicts what an MA dossier was built on → write to `outbox/for_market_analyst.md` so MA knows to re-validate the affected research.
2. **Answer questions / meet requests from peers.** When a peer agent writes to *their* `outbox/for_earnings_researcher.md` asking you something ("can you re-verify CRWV next session, my morning play depends on it"), you read it via your inbound hook, do the work, and reply by writing here. Reply lands in their next-session context block.

You are NOT a chatty agent. Most of your daily work (resolving disputes, updating IR URLs, logging confirmations) does NOT generate outbox traffic. The dispute table + the database ARE your communication channel for routine output. Outbox is for the unusual: requests, answers, escalations.

## How the channel works

- **You write here.** The write guard permits anything under your workspace, including this folder.
- **The recipient reads on their schedule.** Their `hooks/inject_context.py` tails this file when its mtime advances. They'll see the last 2KB of new content in their next session.
- **You don't write to their workspace.** Their write guard would block you anyway. Use this folder.

## Conventions

- Append entries with date headers: `## YYYY-MM-DD HH:MM — short topic`. Newest at the bottom.
- Don't rewrite history. If a confirmation is later overturned, append a correction; don't edit the original entry.
- Quote the request you're answering. When replying to "can you re-verify CRWV?", lead with `> Answering your 2026-05-21 question about CRWV.` so the peer agent can match reply to request.
- Be brief. The other agents have full context loads. A typical entry is 3-8 lines.

## Rotation

These files grow slowly for you (low traffic). When one exceeds **~400 lines**, archive resolved/integrated threads to `<filename>_archive.md` in this same folder. Keep the active file focused on threads still open or recently resolved (last ~2 weeks).

Archive convention: `for_trading_advisor_archive.md`, `for_system_analyst_archive.md`, `for_market_analyst_archive.md`. No fixed cadence — rotate when a `ls outbox/` shows a file getting big.

## When to use the outbox vs another channel

- **Outbox (`outbox/for_<agent>.md`)** — requests to a peer or answers to their requests.
- **`notes_for_ben.md`** — anything for Ben (questions, unresolvable disputes, recurring confirmation friction). Not for peer agents.
- **`memory/research_log.md`** — your own working notes. Not for anyone else.
- **Inbox (`inbox/`)** — your inbound from dev sessions / Ben / one-off drops. You don't write here; you process and move to `inbox/processed/`.
- **The database itself** — for routine output (`earnings_confirm.py`, `ir_earnings_url` updates). The dispute table closing out IS communication; it doesn't need an outbox note too.
