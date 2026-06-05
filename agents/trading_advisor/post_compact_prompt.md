# Post-Compact Re-Orientation Prompt

**Paste this as your first message to TA after the compact.**

---

You're TA. The session before this compact was a workspace planning session — first working session post-TA/MA split (split completed 2026-05-17). We discussed and amended a planning doc; no cleanup has been executed yet. Today is 2026-05-18 Monday, no open option positions, this is not a morning-brief day.

## Read first

`workspace_reset.md` at workspace root. End-to-end. This is the source of truth for the simplified TA role, the trade lifecycle, and every change order. Ben edited the doc directly with amendments during the session — the amendments are baked into the current text. Pay particular attention to:

- **Section 2** — TA's job + NOT-TA's-job + reshaped recommendation function (it's reshaped, not deferred entirely).
- **Section 3** — trade lifecycle (live notes → Saturday case studies).
- **Section 6** — confirmed change orders, including the subagent-mining of the session_notes archive (6.D).
- **Section 7** — proposed layout, with the note that closed case studies all move to MA's domain (per Ben's amendment, TA does not keep a case study library; MA digests and produces heuristics back).
- **Section 11** — Ben's answers to the three parked questions (objective+behavior trade notes; paper trades mirror live tracking; preserve as forward-prediction track).

## Amendments Ben confirmed in chat after the doc was finalized

These are also captured here in case the doc reading misses any nuance:

1. **Trade preferences doc** — lightweight. If truly small (just "no shorts, no 0-DTE, very limited day-trading"), can live as a section in CLAUDE.md. If it grows, `reference/trade_style.md` (routed via MA staging since reference is read-only). Draft in `analysis/` if going the reference route.
2. **Paper trade system mirrors live tracking** with "paper" in the name — `analysis/paper_trade_notes/` + `analysis/paper_case_studies/` mirroring the new live-trade directories.
3. **(This prompt itself.)** Compacting before executing the cleanup so the execution session starts clean.
4. **All case studies disappear into MA's domain.** TA may never see them again, and that's fine. TA writes case studies on Saturday cadence (Section 3 job retained) but they hand off to MA; MA digests into actionable heuristics or multi-case playbooks that flow back into TA's reference via the graduation gate. **This means `analysis/case_studies/` is likely a write-and-hand-off staging area, not a long-term library on TA's side.** Worth confirming the exact handoff mechanism with Ben before scaffolding.
5. **CLAUDE.md redesign is a post-compact task TA does together with Ben.** Don't bolt-on edits. The redesign principle: "every time" content stays in CLAUDE.md with clear pointers to conditional/referenced info. Currently CLAUDE.md is bloated with Core Market Mechanics + Database Access + Query Patterns sections that probably belong in referenced docs.

## Task list — pending execution

In rough recommended order; confirm with Ben before starting:

1. **Tools audit.** Compare TA's `tools/` against MA's `tools/`. Move research-era scripts to MA (candidates per 6.F: `lifecycle_classifier.py`, `run_classifier_batch.py`, `diff_v010_v020.py`, `spot_check_v020_sample.py`, `alert_filter_atm_short_dated.py`, `mna_smoke.py`, `typology/` subdir). Retire `log_trade_call.py` and `etl_trade_calls.py` if `trade_calls.md` is retiring (it is). Delete duplicates rather than move if MA already has them.

2. **Archive before clearing:**
   - `memory/trade_calls.md` → `memory/trade_calls_archive_pre_reset.md`
   - `memory/session_notes.md` → `memory/session_notes_archive/2026-05_pre_split_research_era.md`

3. **Subagent mine the session_notes archive** (per 6.D amendment). Dispatch general-purpose subagent(s) to read the 1,639-line archive, surface all lessons-learned with dates and source line refs, categorize, produce a single review-ready list. Present to Ben for keep/discard. Don't delete anything until Ben confirms.

4. **Clear stale workspace files:**
   - `agenda.md` → framework only, narrow TA scope
   - `directive.md` → empty, kept as Ben's async drop zone
   - `notes_for_ben.md` → narrow scope ("items needing Ben's decision, cleared once dispositioned")
   - **Scrub residual trade-call prose** across reference/morning_brief_prompt.md and any other surface that nudges TA toward convicted recommendations (per Section 2 NOT-job amendment).

5. **New trade-tracking scaffolding:**
   - `analysis/trade_notes/` with README + template (objective facts + Ben's behavior notes, no convictions, no judgments)
   - `analysis/paper_trade_notes/` with mirrored README + template
   - Migrate `analysis/dvn_ctra_campaign/` content into the trade_notes layout (it's the only active live arc)
   - For case studies: confirm handoff mechanism with Ben before scaffolding `analysis/case_studies/` — may just be a temp staging dir or write-direct-to-MA-inbox

6. **Case study handoff to MA.** All 8 existing case studies in `reference/case_study_*.md` (CC, GILD, GM, DVN-original, DVN-rolled, DAL, XYZ, ALB) move into MA's domain. Exact destination: likely `agents/market_analyst/analysis/case_studies/` or via MA's inbox protocol — confirm. After move, these are no longer in TA's reference.

7. **Trade preferences doc.** Draft the lightweight "what Ben has explicitly said" list (no shorts, no 0-DTE, very limited day-trading, anything else from the conversation history). If it stays at 3-5 lines, propose adding to CLAUDE.md. If it grows, draft as `analysis/trade_preferences_draft.md` and route to MA staging.

8. **CLAUDE.md redesign session with Ben.** Separate working session. Don't touch CLAUDE.md as bolt-on edits during the cleanup pass — wait for the redesign session.

## Deferred (per Section 10)

- Reference library review (separate working session, full structural pass)
- Pre-flight rule audit (review the 10 rules in `morning_brief_prompt.md`)
- Re-adding trade-call recommendations (once fundamentals-driven recommendation is working)
- Learning model design (Ben said figure out organically)

## Live state snapshot (today, 2026-05-18 PM)

- Zero open option positions.
- Stock book in flux through the day — DVN, DAL, DRAM, REXC, SMH; some additions/exits during the conversation. Confirm current state via orientation hook at session start.
- The DVN $50C 5/15 second-wave alert from Friday already noted in `memory/for_market_analyst.md` (with a hypothesis question routed to MA). Another DVN $50C alert fired today midday ($1.37M MEDIUM, on the position). Worth a one-line mention in the brief next morning, no action needed.
- Two mailboxes — `agents/system_analyst/memory/for_trading_advisor.md` (5/15 P015 schema review, still owe a response — but that's deferred since P015 was MA-bound work) and `agents/market_analyst/memory/for_trading_advisor.md` (empty, MA loop hasn't turned yet).

## Suggested first move post-compact

Read `workspace_reset.md`, then come back to Ben with:
1. Confirmation of the task ordering above (or proposed reorder)
2. The case-study-handoff mechanism question (where exactly do they go in MA's workspace, and via what protocol)
3. Then start executing from task 1.

Don't rush. This is foundational cleanup; the next 4-6 weeks of TA's work depend on getting it right.
