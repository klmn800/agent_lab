# Tasks — PRD 0001: Commit Hygiene

Source PRD: `tasks/0001-prd-commit-hygiene.md`

## Relevant Files

*(Filled in with the sub-tasks.)*

## Tasks

- [ ] 1.0 Write the Commit Hygiene Standard (`~/.claude/standards/COMMIT_HYGIENE.md`) — data rules, provenance labeling, message rules, severities and the action each one requires (PRD Part B). Comes first because the hook allowlist, the reviewer and the eval fixture all reference it.
- [ ] 2.0 Build the global gitleaks hooks in `claude-config` — install gitleaks, shared `gitleaks.toml` (defaults + email/phone rules + allowlist), `pre-commit` (staged scan, redacted, fail-loud, chains repo-local hooks), `commit-msg`, a self-test, the new-machine runbook in `SETUP.md`, then turn it on for this machine (PRD Part A).
- [ ] 3.0 Build the mailbox notification hook — a global `SessionStart` hook that announces new entries in any agent's `outbox/for_ben.md`, with a path config, `.last_*` markers, fail-soft behavior, a self-test, and registration in `settings.json` + `settings.template.json` (PRD Part D).
- [ ] 4.0 Scaffold the Commit Reviewer workspace and build the deterministic collector — `agents/commit_reviewer/` in the agent_lab shape, gitignore rules, `config.local` (exclude list, gitleaks-only list), and `collect.py` (repo discovery, mirror clones, commit window with overlap, gitleaks, data-file check, delimited and size-capped review bundle) (PRD C1–C6).
- [ ] 5.0 Build the review session — agent `CLAUDE.md` with the prompt-injection rule, `PROMPT.md`, read-only permission lockdown, `launcher.py` (pinned Opus), report format, `DECISION:` lines, known-findings memory and carry-over, proposals, and the `for_ben.md` summary (PRD C7–C16).
- [ ] 6.0 Build the evaluation fixture and pass the acceptance test — a script that generates a local test repo with every planted problem from C18 (including the injection attempt), and a run of collector + review that must catch all of them and pass the clean cases.
- [ ] 7.0 Go live — run the one-time baseline (`PROMPT_BASELINE.md`, batched if needed), review it with Ben, then add the scheduled `.bat`, register the Sunday task with missed-run catch-up, and update agent_lab's README/CLAUDE.md and the solutions_laboratory CLAUDE.md (PRD C3, C17).
