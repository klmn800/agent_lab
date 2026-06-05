# Outbox

Outbound mailboxes from Market Analyst to peer agents. Each `for_<agent>.md` file is a single growing log of messages addressed to that agent.

## How the channel works

- **You write here.** The write guard permits anything under your workspace, including this folder.
- **The recipient reads on their schedule.** Their `hooks/inject_context.py` tails this file when its mtime advances since they last looked. They'll see the last 2KB of new content in their next session's context block.
- **You don't write to their workspace.** That's enforced by their write guard.

## Conventions

- Append entries with date headers: `## YYYY-MM-DD HH:MM — short topic`. Newest at the bottom.
- Don't rewrite history. If a message is wrong, append a correction; don't edit the original.
- Keep entries actionable to the recipient:
  - **For TA:** transient/actionable signals for the morning brief — backtest results that change a calibration, "watch for X tomorrow," a finding that makes a previously-staged pattern stronger or weaker. **Not** durable reference material — that goes through `reference/staging/` and Ben's graduation gate, not the outbox.
  - **For SA:** data quality issues you found during research (zero-move contamination patterns, view problems, schema gotchas), proposals for new tables or columns that would unlock research you currently can't do.
  - **For ER:** earnings date discrepancies you noticed in research data (e.g., "the cohort I ran assumed CAVA was 5/28, but the move pattern looks like it actually reported 5/27"), or systematic source-accuracy patterns that should change how ER prioritizes its queue.

## Rotation

These files grow. When one exceeds **~400 lines**, archive resolved/integrated threads to `<filename>_archive.md` in this same folder. Keep the active file focused on threads that are still open, in-flight, or recently resolved (last ~2 weeks).

Archive convention: `for_trading_advisor_archive.md`, `for_system_analyst_archive.md`, etc. Multiple archive generations are fine when one archive itself gets big — `for_trading_advisor_archive_2026-Q2.md`.

Rotation cadence: review during your Sunday session (`PROMPT_SUNDAY.md` already covers housekeeping). Don't archive mid-week unless a file is causing real friction.

## When to use the outbox vs another channel

- **Outbox (`outbox/for_<agent>.md`)** — ongoing, threaded conversation with another agent. Use when you expect a back-and-forth, or when the message needs to land at the recipient's next session-start hook.
- **Recipient's `inbox/`** — one-off drops from developer/dev sessions. You can't write here directly; for MA-to-other-agent, the outbox IS the channel.
- **`reference/staging/`** — for durable reference material destined for TA's library, NOT for messages.
- **`proposals/`** — structured asks for Ben.
- **`notes_for_ben.md`** — direct to Ben.
