# PRD 0001 — Commit Hygiene: pre-commit scanning, a shared standard, and a weekly reviewer agent

**Status:** Draft for Ben's review
**Date:** 2026-09-30
**Owner:** Ben (human approver on every finding)

---

## 1. Introduction / Overview

Most commits across Ben's GitHub portfolio are written by AI coding agents, and they come too fast for Ben to review each one. Two things can go wrong, and both matter to anyone reading the portfolio (hiring managers, recruiters, an employer):

1. **Data safety.** A secret, a real person's name, an email address, a phone number, or a real data file gets committed and pushed.
2. **Professionalism.** A commit message is crude, flippant, uninformative, or about a topic that would read badly to an outsider.

This PRD defines a three-part system that adds a second set of eyes:

| Part | What it is | When it acts | Kind of check |
|---|---|---|---|
| **A. Global pre-commit hook** | gitleaks, run on every commit on every machine Ben uses | Before a commit is created | Deterministic (regex rules) — *prevention* |
| **B. Commit Hygiene Standard** | One rubric document defining what is and isn't acceptable | Read by Ben, by coding agents, and by the reviewer | The shared definition both A and C enforce |
| **C. Weekly reviewer agent** | A read-only Claude Code agent in `agent_lab` that reviews the week's commits across the whole portfolio and writes a report | Sunday morning | Judgment (LLM) — *detection and advice* |

**Why both A and C?** They catch different things. A regex can reliably spot an API key or a phone number *before it leaves the machine*, but it cannot tell whether "Maria Lopez" in a test fixture is a real person or whether a commit message is unprofessional. An LLM can make those judgment calls, but only after the fact, and a pushed secret is already exposed. Prevention handles what can be matched; review handles what needs judgment.

**Goal:** Nothing secret or real reaches GitHub, and every commit message in the portfolio would hold up to a hiring manager reading it — while Ben's role shrinks to making decisions on a short weekly report.

---

## 2. Goals

1. Block commits containing secrets, email addresses, or phone numbers at commit time, on both of Ben's machines, across every repository, with no per-repo setup.
2. Define one written standard for commit content (data and tone) that Ben's coding agents can follow and the reviewer can enforce.
3. Every week, review every new commit (message + diff) in every active, non-archived repo Ben owns, and produce one prioritized report.
4. For every finding, give Ben a concrete recommendation he can act on without further research — including a clean replacement message for weak or unprofessional commit messages.
5. Turn recurring findings into proposed fixes at the source (the coding agents' instructions), so the same mistake stops recurring.
6. The reviewer never changes any repository. It reads and reports; Ben decides.

---

## 3. User Stories

- **As Ben**, I want a commit that contains a secret or someone's phone number to be refused on my machine, so it never reaches GitHub in the first place.
- **As Ben**, I want the same protection on my work laptop without setting it up per repo, so I'm covered everywhere I commit.
- **As Ben**, I want one weekly report that tells me what's wrong, how bad it is, and exactly what to do about it, so I can make decisions quickly instead of auditing commits myself.
- **As Ben**, I want suggested replacement wording for bad commit messages, so I can see what "good" looks like and decide whether a rewrite is worth it.
- **As Ben**, when my coding agents keep making the same mistake, I want a proposed change to their instructions, so I fix the cause instead of repeating the cleanup.
- **As Ben**, I want findings I've already dismissed to stay dismissed, so the report doesn't re-raise the same false alarms every week.
- **As one of Ben's coding agents**, I want a single standard document I can read, so I know what a compliant commit looks like before I make one.
- **As a hiring manager browsing Ben's GitHub**, I see clear, professional commit history and no personal or sensitive data.

---

## 4. Functional Requirements

### Part A — Global pre-commit hook (gitleaks)

**A1.** The system must install a single global git hook directory, stored in Ben's `claude-config` repo (`~/.claude/git-hooks/`), so it syncs to every machine that uses `claude-config`.

**A2.** Each machine must point git at that directory with one global setting (`git config --global core.hooksPath ...`). Setup on a new machine must be documented as a short, numbered runbook (install gitleaks, set one config value, run a self-test).

**A3.** The `pre-commit` hook must run gitleaks against the **staged changes only** (not the whole repo), so commits stay fast.

**A4.** The hook must **block the commit** (non-zero exit with a clear message) when gitleaks finds:
- any secret matched by gitleaks' built-in rule set, or
- an email address, or
- a phone number,
unless the match is allowlisted (A6).

**A5.** The block message must say, in plain English: what was found, in which file and line, why it's blocked, and the three ways forward — remove it, mark it as an intentional exception (inline `gitleaks:allow` comment or the repo's `.gitleaksignore`), or (last resort) bypass with `--no-verify`. The matched value must be **redacted** in the output.

**A6.** A shared gitleaks configuration (`~/.claude/git-hooks/gitleaks.toml`) must extend gitleaks' default rules with the email and phone rules and an allowlist covering at minimum:
- GitHub `noreply` addresses (`*@users.noreply.github.com`, `noreply@*`)
- reserved example domains (`example.com`, `example.org`, `test.com`, etc.)
- reserved fictional phone ranges (e.g. `555-01xx`)
- Ben's own public contact details, if he chooses to publish any (configured locally, see A9)

**A7.** The hook must also run any **repo-local** pre-commit hook that exists (`.git/hooks/pre-commit`), after gitleaks passes. Setting a global `core.hooksPath` otherwise silently disables repo-local hooks; this requirement prevents that.

**A8.** If gitleaks is not installed, the hook must **fail loudly** (block the commit with an install instruction) rather than silently pass. A missing scanner must never look like a clean scan.

**A9.** Anything machine- or person-specific (e.g. an allowlisted personal address) must live in a local, uncommitted override file, not in the shared config — `claude-config` itself must not contain PII.

**A10 (should).** A `commit-msg` hook should run the same PII/secret rules against the commit message text, since messages are published too.

**A11.** Commit author identity: the runbook must include switching the global git author email to Ben's GitHub `noreply` address, and enabling GitHub's "block command line pushes that expose my email" setting. (Existing history is out of scope — see Non-Goals.)

### Part B — Commit Hygiene Standard

**B1.** A single document, `~/.claude/standards/COMMIT_HYGIENE.md`, must define the standard. It lives with Ben's other standards so it syncs to both machines and his coding agents can be pointed at it.

**B2.** The standard must define **data rules** (applies identically to public and private repos):
- **Never committed:** secrets/credentials; real people's names (other than Ben's own, see B4); email addresses; phone numbers; postal addresses; account, case, or ID numbers; any real data extract (rows from a real database, spreadsheet, export, log, or email).
- **Data files** (`.csv`, `.xlsx`, `.json` data, `.db`/`.sqlite`, `.parquet`, `.msg`/`.eml`, etc.) are allowed **only if synthetic and labeled as synthetic**.
- **Labeling convention** (the standard must define exactly one, e.g.): the data file's folder contains a `DATA_PROVENANCE.md` stating the files are synthetic and how they were generated (script name or method). A data file without a provenance note is a finding even if it looks fake.

**B3.** The standard must define **message rules**:
- **Professionalism (moderate bar):** flag profanity, insults, politics, inside jokes, venting, and anything that would embarrass Ben in front of a hiring manager, recruiter, or employer. Casual-but-clear wording is acceptable.
- **Quality:** flag uninformative messages (`fix`, `wip`, `updates`, `stuff`, `asdf`), messages that don't describe the change, and messages that misdescribe the diff.
- **Good message format:** a short imperative summary line, optional body explaining *why*. The standard must include 3–5 good/bad examples.

**B4.** The standard must state that Ben's **name** is acceptable (LICENSE, README, author field), and that commit author **email** must be the GitHub noreply address going forward.

**B5.** The standard must define **severity levels** used by the reviewer:
- **Critical** — secret, or real personal/sensitive data, on any branch of any repo.
- **High** — PII-shaped content not yet confirmed real; unlabeled data file; author email exposure.
- **Medium** — unprofessional message or content.
- **Low** — uninformative or misleading message (quality).

**B6.** The standard must state what each severity *means for action*, so recommendations are consistent:
- **Critical on a public repo:** assume already exposed. Rotate the secret / notify as appropriate *first*, then rewrite history.
- **Critical/High on a private repo:** rewrite history before the repo is ever made public.
- **Medium/Low:** usually do **not** rewrite history (force-pushing is disruptive); fix forward and fix the cause (coding-agent instructions). Rewriting is Ben's call.

### Part C — Weekly reviewer agent

*Working name: **Commit Reviewer** (`agents/commit_reviewer/`). Not "repo reviewer," to avoid confusion with Ben's existing public `repo-reviewer` tool.*

**Workspace and conventions**

**C1.** The agent must follow the existing `agent_lab` workspace shape: `CLAUDE.md` (identity and operating rules), `PROMPT.md` (weekly session) and `PROMPT_BASELINE.md` (one-time baseline), `launcher.py`, `hooks/inject_context.py`, and workspace folders with committed `README.md` convention docs only.

**C2.** All reports, run state, clones, and local config must be **gitignored**. `agent_lab` is a public repo; the reviewer's output contains (masked) findings about private repos and must never be committed.

**C3.** The agent must be launched by Windows Task Scheduler every **Sunday morning**, using the existing `scheduled_tasks/*.bat` + `wt -w 0 new-tab` pattern, in a **visible** Windows Terminal tab, using **Opus**.

**Discovery and collection (deterministic code, not the LLM)**

**C4.** A Python collector script (`collect.py`) must do all mechanical work *before* the Claude session starts, so the LLM only does judgment:
1. List all of Ben's **non-archived, non-fork** repos via `gh`, minus an **exclude list** in local config.
2. Select repos with commits since the **last successful run** (read from a state file), with a **1-day overlap** so a late or failed run never leaves a gap. If there is no state file, use 8 days.
3. Maintain local read-only mirror clones in a gitignored cache and fetch updates. **All branches** are in scope, not just the default.
4. For each new commit: extract SHA, date, author name/email, message, and diff.
5. Run gitleaks over the new commits (with redaction) and record its results.
6. Flag data files (by extension) added or modified, and whether a provenance note exists beside them.
7. Write one review bundle (markdown or JSON) for the session to read.

**C5.** Diffs in the bundle must be size-capped per commit; lockfiles, binaries, and generated files are listed by name only. When a diff is truncated, the bundle must say so, so the report can mark that commit "partially reviewed" rather than implying a full review.

**C6. Work-derived repos (gitleaks-only tier).** Repos listed in the local config's **gitleaks-only** list must be scanned by gitleaks and the data-file check, but their **diffs and file contents must never be placed in the bundle** or otherwise sent to Claude. Only commit metadata, the gitleaks/data-file results (redacted), and the commit message may be included. *(Whether the message itself may be sent is an open question — see §9.)* The names of these repos live only in local, gitignored config, never in committed files.

**Review (the Claude session)**

**C7.** The session must review every commit in the bundle against `COMMIT_HYGIENE.md`: the message (professionalism and quality, including whether the message matches the diff) and the diff (data rules).

**C8.** Each finding in the report must include:
- severity (B5), repo, branch, short SHA, date, and a GitHub link
- what rule it breaks (cite the standard's section)
- the evidence, **masked** (e.g. `***-***-4821`, `j***@g***.com`, first/last 3 characters of a secret only). The report must never contain a full secret or full PII value.
- the recommended action (from B6), stated concretely
- for message findings: a **clean replacement message**
- a decision line for Ben (C11)

**C9.** The report must also state coverage: repos checked, repos with activity, commits reviewed, commits partially reviewed (truncated), gitleaks-only repos scanned, and any repo that failed to fetch. A clean week must say "clean" explicitly — silence must never look like a pass.

**C10.** **Feedback loop:** when the same kind of finding recurs (same rule, two or more times in a run or across recent runs), the agent must draft a **proposal** — a suggested change to the relevant coding-agent instructions (`CLAUDE.md`, a standard, a skill) — in `proposals/`, using the existing STATUS-line convention. It must never edit those instructions itself.

**Ben's decisions**

**C11.** Each finding must end with a machine-readable decision line Ben (or another agent reading to him) can fill in, following the existing STATUS convention, e.g.:
`DECISION: OPEN` → `FIX` / `ACCEPT` (intentional, no action) / `DISMISS` (false positive) / `DEFER`.

**C12.** Findings Ben marks `ACCEPT` or `DISMISS` must be recorded (by a stable fingerprint: repo + SHA + rule + location) in a known-findings file, and must not be re-reported in later runs.

**C13.** At the start of each run, the agent must surface any findings from previous reports still marked `OPEN`, so nothing falls off the list.

**C14.** A short summary (counts by severity, top items, report path) must be appended to `notes_for_ben.md` in the agent's workspace.

**Read-only guarantee**

**C15.** Read-only must be enforced **at the tool boundary**, not just requested in the prompt. The agent's Claude Code permission settings must deny: `git push`, `git commit`, history-rewriting commands, `gh` write operations (issues, PRs, repo edits, releases), and file writes outside its own workspace. *(Commit content is untrusted input — a commit message could contain instructions aimed at the agent. Permissions are the enforcement; the prompt is not.)*

**C16.** The mirror clones must be used read-only. The agent must never write to Ben's working copies of any repo.

**Baseline**

**C17.** A one-time baseline run (`PROMPT_BASELINE.md`) must: run gitleaks over the **full history** of every in-scope repo (including gitleaks-only repos), run the data-file check over the current tree of every repo, and have Claude review **every commit message** in history (not historical diffs). Output is a baseline report in the same format. It may be run in batches if large.

### Verification

**C18.** An evaluation fixture must exist: a small local test repo (generated by a script, never pushed) with planted problems — a fake secret in a known gitleaks format, a fake email and phone, an unlabeled synthetic CSV, a labeled synthetic CSV (should pass), a crude message, a `wip` message, a message that misdescribes its diff, and a clean commit (should pass). The collector and the review must catch every planted problem and pass the two clean cases. This is the acceptance test before the first real run, and the regression test after changes to the standard or prompt.

**C19.** The hook (Part A) must have a self-test: a script that creates a temp repo, attempts commits with a fake secret, an email, a phone, an allowlisted address, and a clean change, and checks each is blocked or allowed as expected.

---

## 5. Non-Goals (Out of Scope)

- **The agent does not fix anything.** No commits, pushes, rewrites, issues, PR comments, or edits to any repo or to coding-agent instructions.
- **No automatic history rewriting.** Rewriting pushed history (e.g. to replace a commit message or purge data) is Ben's decision and a separate, manual procedure. This PRD only makes sure the report says when it's warranted.
- **Rewriting existing history to remove the old author email** is out of scope for this PRD (see §9).
- **Not a code-quality review.** Bugs, architecture, test coverage, and README accuracy are not in scope (Ben's `repo-reviewer` tool covers README-vs-code). This agent reviews commit *content* against the hygiene standard only.
- **No GitHub issues or cloud output.** Reports stay on Ben's machine.
- **No server-side enforcement** (GitHub secret scanning / push protection) in this PRD. Worth enabling separately where available, but it's a GitHub settings task, not a build.
- **No real-time monitoring.** Weekly cadence only.

---

## 6. Design Considerations

**Report layout** (`reports/YYYY-MM-DD.md`):

1. **Headline** — one line: `CLEAN` or counts by severity, plus anything Critical called out by name.
2. **Carry-over** — previous findings still `OPEN`.
3. **Findings**, Critical first, grouped by repo. One block per finding (C8), ending with its `DECISION:` line.
4. **Proposals raised this run** (C10), with links.
5. **Coverage** (C9).

It must be readable aloud by another agent: plain sentences, no tables required to understand a finding, masked values written so they can be spoken.

**Hook messages** are read by a person in the middle of a commit, or by a coding agent. They should be short, name the file and line, and end with the exact command or comment syntax for each way forward.

---

## 7. Technical Considerations

- **Platform:** Windows only. Git for Windows runs hooks through its bundled `sh`, so the hook is a POSIX shell script; it must not assume WSL. Every Python script uses `sys.stdout.reconfigure(encoding='utf-8')` and explicit `encoding='utf-8'`, per `agent_lab` convention.
- **gitleaks version and syntax** (staged-scan command, `[extend] useDefault`, allowlist format, redaction flag) must be verified against the installed version's docs during implementation — the CLI changed across v8 releases.
- **`core.hooksPath` with `~`:** confirm git expands `~` in this setting on Windows; otherwise the runbook uses an absolute path per machine.
- **Work laptop:** installing the gitleaks binary may need IT approval. The hook's fail-loud behavior (A8) means the laptop is blocked from committing until it's installed — the runbook must say to install gitleaks *before* setting `core.hooksPath`.
- **`gh` auth:** the collector uses the existing `gh` login (`repo` scope). It needs read access only; a narrower token is a nice-to-have.
- **Subscription usage:** most weeks touch a handful of repos, so the weekly run is modest. The baseline is the expensive run; C17 limits it to messages, and it can run in batches.
- **Task Scheduler + visible tab:** a `wt` tab needs a logged-in desktop session. After a Windows Update restart that leaves the PC at the sign-in screen, the Sunday run will not start. See §9.
- **Model pinning:** pin an explicit Opus model ID in the launcher (per `AI_BUILD_SECURITY.md` §2), not "latest."
- **Reuse:** launcher, hook, `.bat`, inbox/outbox, and STATUS conventions are copied from existing `agent_lab` agents. Their known genericization debt (hardcoded `E:\options_scanner` paths) must not be copied in.

---

## 8. Success Metrics

- **Prevention:** zero secrets or PII pushed to any repo after the hook is installed, verified by each weekly gitleaks pass over new commits.
- **Detection:** the evaluation fixture (C18) passes 100% before the first real run and after every change to the standard or prompt.
- **Signal quality:** after the first month, `DISMISS` decisions make up a small minority of findings. If not, the standard or allowlist is tuned.
- **Root-cause fixes:** recurring finding types decline over time as proposals (C10) are approved and applied.
- **Reliability:** every scheduled Sunday produces a report or a visible failure. No silent missed weeks.
- **Baseline:** completed once, with every Critical finding resolved or explicitly accepted.

---

## 9. Open Questions

1. **Gitleaks-only repos and commit messages.** Should commit *messages* from work-derived repos be sent to Claude for tone/quality review, or should those repos get no LLM involvement at all? (Messages rarely contain data, but they can.)
2. **Restart resilience.** Should the scheduled task also run on "next logon if missed," and should the agent leave a "last run" marker that Ben's other agents can check, so a missed Sunday is noticed?
3. **Old author email in existing history.** Leave it (it's already public), or plan a separate history-rewrite effort for public repos?
4. **Who reads the report aloud?** Is there an existing agent that should get an outbox message pointing at each new report, or does Ben read `notes_for_ben.md` directly for now?
5. **Phone-number rule tuning.** Phone-shaped numbers appear in code (IDs, timestamps). How aggressive should the phone regex be before false blocks become annoying? Plan: start strict, tune from real blocks during the first two weeks.
6. **GitHub push protection.** Enable GitHub secret scanning / push protection on public repos as a separate settings task?
