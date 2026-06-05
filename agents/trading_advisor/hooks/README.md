# Trading Advisor — Hooks

Per-agent hooks wired in `.claude/settings.local.json`. Each fires automatically; nothing here needs manual invocation.

## Hooks

### `inject_context.py` — UserPromptSubmit
Injects datetime + market session, market snapshot (5-min cooldown), live Tradier quotes (2-min cooldown), and cross-agent mailbox notices (P018). Edit freely.

### `query_linter.py` — PreToolUse (Bash)
Lints Bash commands for known DB query foot-guns. See `query_linter.README.md`.

### `check_commitments.py` — Stop (P014)
Scans your assistant messages since the last user prompt for unfulfilled commitment phrases ("I'll write", "let me log", "I'll set up", etc.). If a commitment exists with no following tool call in the same stop window, the hook returns a `block` decision and force-continues with a system-reminder telling you to either fulfill the commitment or explicitly cancel it.

**Why it exists:** the inline-write rule in CLAUDE.md cannot self-enforce — each session reads it cold and applies it imperfectly. The hook patches the failure point structurally. See proposal `proposals/014_session_commitment_enforcement_hooks.md` for the originating incident (2026-05-07).

**Trigger phrases:** `I'll`/`I will`/`let me` followed by `write|log|note|file|drop|fold|set up|add this to|record|capture|jot|save`.

**Fulfillment criteria:** any `tool_use` event (Write, Edit, Bash, NotebookEdit, anything) following the commitment phrase in the same stop window. Broad on purpose — most "I'll write the SQL" phrasings end with a Bash call and shouldn't false-positive.

**Escape valve:** if the hook flags a false positive, write the literal phrase **"Cancelling commitment to X"** in your response. The hook recognizes the cancellation and exits silent on retry.

**Loop guard:** receives `stop_hook_active` from Claude Code. If true, the hook exits silent — you've already been prompted once this stop cycle.

**Test mode:** `python check_commitments.py --test-transcript path/to/fixture.jsonl`. Four fixtures live in `test_fixtures/`:
- `unfulfilled.jsonl` → expects block decision
- `fulfilled.jsonl` → expects silent (tool_use followed commitment)
- `no_commitment.jsonl` → expects silent (no trigger phrases)
- `cancelled.jsonl` → expects silent (explicit cancellation)

Run all four after editing the regex to confirm no regression:

```bash
for f in agents/trading_advisor/hooks/test_fixtures/*.jsonl; do
  echo "--- $f ---"
  python agents/trading_advisor/hooks/check_commitments.py --test-transcript "$f"
  echo
done
```

## What's NOT in your write boundary

Write guard, `.claude/settings.local.json`, and anything outside `agents/trading_advisor/` belong to Ben. Propose changes via `proposals/` rather than edit directly.
