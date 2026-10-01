# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`agent_lab` is a **framework skeleton** for running a fleet of long-lived, scheduled **Claude Code** agents that share a workspace, hand off to each other through files, and accumulate durable knowledge over time. It was extracted from a live options-trading system (`E:\options_scanner`) — the machinery and conventions were kept; the accumulated domain content (memory, research output, mailboxes) was left behind. Genericization is **in progress**, so the prompts and hooks still carry trading-flavored examples and hardcoded `E:\options_scanner` paths that illustrate the patterns.

There is **no build, no package, no test runner, no dependency manifest.** Everything is standalone Python 3 scripts (stdlib only, plus `zoneinfo`) driven by `.bat` files and Claude Code itself. Read `README.md` for the design narrative.

## The four mechanisms (read these to understand the system)

The whole framework is four moving parts. Understanding them requires reading across `launcher.py`, `hooks/inject_context.py`, and the prompt files together — no single file tells the whole story.

1. **`launcher.py` — session preparation.** Each agent has one. It injects the current date into a chosen `PROMPT_*.md`, writes `.session_prompt.md`, sets a `.session_mode` marker, then spawns Claude Code (visible window or `--headless`). `--prepare-only` writes the prompt and exits *without* launching — this two-step split exists so a scheduled `.bat` can prep the prompt and then open the Windows Terminal tab separately (Task Scheduler can't do the handoff in one step). `PROJECT_ROOT` is always `Path(__file__).resolve().parent.parent.parent` (i.e. `agents/<name>/` → repo root).

2. **`hooks/inject_context.py` — per-turn context injection.** A Claude Code `UserPromptSubmit` hook that fires every turn and returns `{"hookSpecificOutput": {"additionalContext": ...}}` on stdout. It feeds the agent date/session context plus a `<mailbox-notices>` block surfacing anything new since last seen. **State markers (`.last_*`) track what's already been surfaced so nothing is re-shown; the first run of each check is intentionally silent** (it just records the baseline mtime). Expensive blocks (DB queries, live quotes) are gated behind cooldown files (`.last_market_snapshot`, `.last_live_quotes`). This output appears in *every* prompt — keep it lean.

3. **Session modes.** One agent, several cadences. `launcher.py` writes a `.session_mode` marker (`daily`, `weekend`, …) and the hook reads it to decide what to inject. E.g. the Earnings Researcher's `--prompt PROMPT_SUNDAY.md` path writes `weekend`, which tells the hook to *suppress* the dispute work-queue so the Sunday session does housekeeping instead.

4. **Mailbox mesh + graduation gate.** Agents talk by appending to `outbox/for_<other_agent>.md`; the recipient's hook surfaces it as a mailbox notice. A **graduation gate** governs knowledge promotion: findings are staged in `reference/staging/` and only a human-approved move promotes them into a working `reference/` library — so unvetted conclusions never silently enter a live playbook. Conventions live in each `outbox/README.md` and the agent `CLAUDE.md` files.

## Agent workspace layout

Every agent under `agents/<name>/` follows the same shape:

```
CLAUDE.md            identity + operating rules (the agent's "who am I"; loaded by CC)
PROMPT*.md           one per session mode (daily / saturday / sunday / research)
launcher.py          prepares the session + spawns Claude Code
hooks/inject_context.py   the per-turn context hook
memory/ reference/ analysis/ outbox/ inbox/ proposals/   workspace dirs
```

Only `README.md` convention docs are committed inside the workspace dirs; live content is gitignored. The per-agent `CLAUDE.md` is the agent's own operating contract (e.g. `agents/trading_advisor/CLAUDE.md` defines what that agent may write without asking) — **it is not** generic repo guidance, so don't treat it as authority for the framework itself.

## Roundtable

`agents/roundtable/orchestrator.py` runs a turn-taking debate between two agents (SA ↔ TA), each persisted across turns via `claude --resume` (session_id harvested from the first turn's JSON output). A shared markdown transcript is the wire; agents deliver each reply as a JSON result file (`{"reply", "next"}`) written to a pre-approved path under `roundtable/state/`. Ben observes live and is paused in when an agent tags `BEN`. On clean exit each agent writes its commitments back to its own `directive.md`.

> **Gotcha:** `orchestrator.py` imports `from tools.claude_code_runner import run_claude_task`. That `tools/` module is part of the live `E:\options_scanner` system and was **not** extracted into this skeleton — so the orchestrator will not run as-is here. `_smoke_test.py` (which calls the `claude` CLI directly, bypassing the runner) is the working reference for the `--resume` primitive; see `SMOKE_TEST_NOTES.md`.

## Running agents

```powershell
# Launch an agent session in a visible window (from repo root):
python agents\trading_advisor\launcher.py --prompt PROMPT_RESEARCH.md
python agents\market_analyst\launcher.py --prompt PROMPT_SUNDAY.md

# Prepare the prompt only (no window) — used by scheduled .bat files:
python agents\trading_advisor\launcher.py --prompt PROMPT_SUNDAY.md --prepare-only

# Earnings Researcher (daily dispute mode is the default; needs data\performance.db):
python agents\earnings_researcher\launcher.py            # visible
python agents\earnings_researcher\launcher.py --headless --limit 5

# Roundtable (note the tools/ dependency caveat above):
python agents\roundtable\orchestrator.py                 # stub smoke handshake
python agents\roundtable\orchestrator.py --seed-question Q4
python agents\roundtable\orchestrator.py --seed "your topic text"
```

Scheduled launches live in `scheduled_tasks\*.bat` and are wired into Windows Task Scheduler. They use the `wt -w 0 new-tab ... cmd /k "cd /d <dir> && claude ... @.session_prompt.md"` pattern — Task Scheduler bypasses the default-terminal handoff, so `wt` must be invoked explicitly, and the `cd` is folded into `cmd /k` because a new `wt` tab does **not** inherit the `.bat`'s working directory.

## Testing

No framework. Tests are ad-hoc scripts and a manual hook-driver convention:

```powershell
# Drive a context hook by hand (this is the documented self-test, e.g. in inject_context.py's footer):
echo '{"prompt":"test"}' | python agents\trading_advisor\hooks\inject_context.py

# Commitment-check hook has fixtures under hooks\test_fixtures\*.jsonl:
python agents\trading_advisor\hooks\check_commitments.py

# Roundtable resume-primitive smoke test:
python agents\roundtable\_smoke_test.py
```

## Conventions that matter when editing

- **Windows is the only target.** Use PowerShell syntax. Every script does `sys.stdout.reconfigure(encoding='utf-8')` near the top — keep that; emoji/box-drawing output to a Windows console breaks without it. Read/write files with `encoding='utf-8'` explicitly.
- **Hooks must fail soft.** The context hook wraps DB queries, file reads, and marker writes in broad `try/except` returning a neutral value — a hook that raises would break *every* turn of that agent. Preserve that discipline.
- **The deferred-promise anti-pattern.** The agent operating contracts (e.g. `agents/trading_advisor/CLAUDE.md`) treat "I'll log this later" as a bug: if something is worth recording, the file gets the entry the moment it's decided. This is a load-bearing convention of the system's design, not a style note.
- **Known genericization debt (per README):** hardcoded `E:\options_scanner` paths in hooks/launchers, a Tradier-quote fetch and SQLite view queries (`ta_v_*`) embedded in the Trading Advisor hook, the missing `tools/claude_code_runner.py`, and trading domain language throughout the prompts. No secrets are committed — API keys are read at runtime from external config (`E:\options_scanner\config.json`).
