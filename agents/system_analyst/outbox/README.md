# Outbox

Outbound mailboxes from System Analyst to peer agents. Each `for_<agent>.md` file is a single growing log of messages addressed to that agent.

## How the channel works

- **You write here.** The write guard permits anything under your workspace, including this folder.
- **The recipient reads on their schedule.** Their `hooks/inject_context.py` tails this file when its mtime advances since they last looked. They'll see the last 2KB of new content in their next session's context block.
- **You don't write to their workspace.** That's enforced by their write guard; the workspace-isolation principle is why the mailbox exists.

## Conventions

- Append entries with date headers: `## YYYY-MM-DD HH:MM — short topic`. Newest at the bottom.
- Don't rewrite history. If a message is wrong, append a correction; don't edit the original.
- Keep entries actionable to the recipient. SA-flavored notes ("noticed a pipeline lag, here's the query that surfaced it") not analyst-stream-of-consciousness.
- For structured asks (system fixes, new tables, pipeline edits), prefer writing a proposal under `proposals/` and letting the recipient pick it up via their proposal-watch hook.

## Rotation

These files grow. When one exceeds **~400 lines**, archive resolved/integrated threads to `<filename>_archive.md` in this same folder. Keep the active file focused on threads that are still open, in-flight, or recently resolved (last ~2 weeks).

Archive convention (already in use): `for_trading_advisor_archive.md`, `for_market_analyst_archive.md`, `for_earnings_researcher_archive.md`. Multiple archive generations are fine when one archive itself gets big — `for_trading_advisor_archive_2026-Q2.md`, etc.

Rotation cadence: review during your Sunday self-care session. Don't archive mid-week unless a file is causing real friction.

## When to use the outbox vs another channel

- **Outbox (`outbox/for_<agent>.md`)** — ongoing, threaded conversation with another agent. Use when you expect a back-and-forth, or when the message needs to land at the recipient's next session-start hook.
- **Recipient's `inbox/`** — one-off drops from developer/dev sessions. You can't write here directly (write guard blocks); for SA-to-other-agent communication, the outbox IS the right channel.
- **`proposals/`** — structured asks for Ben. Different audience entirely.
- **`notes_for_ben.md`** — direct to Ben. Not for inter-agent traffic.
