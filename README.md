# agent_lab

A framework for running a fleet of specialized, scheduled **Claude Code** agents that share a workspace, talk to each other, and accumulate durable knowledge over time.

This is the **framework skeleton** extracted from a live options-trading system — the machinery and conventions, with the accumulated domain content (memory, research output, mailboxes) left behind. It's being genericized; the prompts and hooks still carry trading-flavored examples that show the patterns in action.

---

## The idea

Each agent is a long-lived **Claude Code** persona with its own workspace, identity, memory namespace, and schedule. Rather than one monolithic assistant, the work is split across specialists that hand off to each other through files:

| Agent | Role |
|---|---|
| **System Analyst** | Audits data quality, proposes system improvements |
| **Trading Advisor** | Morning brief, intraday calls, live campaign tracking |
| **Market Analyst** | Evening research, backtests, grades the Advisor's calls |
| **Earnings Researcher** | Narrow scope: verifies disputed earnings dates |
| **Roundtable** | An orchestrator that runs turn-taking debates *between* agents |

## How an agent works

Every agent workspace follows the same shape:

```
agents/<name>/
  CLAUDE.md            identity + operating rules (the "who am I")
  PROMPT*.md           one per session mode (daily / saturday / sunday / research)
  launcher.py          prepares the session + spawns Claude Code
  hooks/
    inject_context.py  context-injection hook (see below)
  memory/  reference/  analysis/  outbox/  inbox/  proposals/
                       workspace dirs (README convention docs included; content excluded)
```

Four mechanisms make it work:

1. **`launcher.py` — session preparation.** Injects the current date into the chosen `PROMPT_*.md`, writes a `.session_prompt.md`, sets a `.session_mode` marker, then spawns Claude Code either visibly (a terminal tab) or `--headless`. The two-step `--prepare-only` path exists so a `.bat` can prep the prompt and then open the window separately.

2. **`hooks/inject_context.py` — context injection.** A Claude Code hook that fires each turn and feeds the agent exactly what it needs: the shared project context, plus a `<mailbox-notices>` block surfacing anything new — messages from other agents, unprocessed `inbox/` files, fresh directives. State markers (`.last_*`) track what's already been seen so nothing is re-surfaced. First run for each check is silent.

3. **Session modes.** One agent, several cadences. A `.session_mode` marker (`daily`, `weekend`, …) tells the hook what to inject — e.g. the Earnings Researcher suppresses its work queue on Sundays so the session can do housekeeping instead of research.

4. **The mailbox mesh + graduation gate.** Agents communicate by appending to `outbox/for_<agent>.md` files (conventions in each `outbox/README.md`). A **graduation gate** governs promotion of knowledge: the Market Analyst stages findings in `reference/staging/`, and only a human-approved promotion moves them into the Trading Advisor's working `reference/` library — preventing unvetted conclusions from contaminating the live playbook.

## Roundtable: agents debating agents

`agents/roundtable/orchestrator.py` runs a turn-taking conversation between two agents, each persisted across turns via `claude --resume` so context stays warm. A shared transcript is the wire between them; the orchestrator pumps replies back and forth, pauses when an agent tags the human, and (on exit) asks each agent to write its commitments back to its own `directive.md`. See `agents/roundtable/README.md` and `PLANNING.md` for the full design.

## Scheduling

`scheduled_tasks/*.bat` launch the agents via Windows Task Scheduler. They use the `wt -w 0 new-tab` pattern so each scheduled session opens as a tab in the existing Windows Terminal window (Task Scheduler bypasses the default-terminal handoff, so invoking `wt` explicitly is required — the `cd` is folded into `cmd /k` because a `wt` tab doesn't inherit the `.bat`'s working directory).

---

## Status

Extracted skeleton — **work in progress toward generic, reusable scaffolding.** Known trading-specific bits still to genericize: hardcoded `E:\options_scanner` paths in the hooks, a Tradier-quote fetch embedded in the Trading Advisor's hook, and domain language throughout the prompts. None of it contains secrets (API keys are read from external config, not committed here).
