   ```
7. **Update dispute resolution**:
   ```bash
   python E:\options_scanner\tools\direct_db_query.py --db E:\options_scanner\data\performance.db --write --sql "UPDATE earnings_date_disputes SET resolution='confirmed_agent', resolved_date='{DATE}', resolved_time='{TIME}', resolved_at='{NOW}', research_url='{URL}' WHERE trade_date='{TODAY}' AND symbol='{SYM}'"
   ```
8. **Log your work** to `memory/research_log.md`.

---

## Session Modes

You run in one of two modes. `launcher.py` writes a `.session_mode` marker that your context hook reads to decide what to inject.

| Mode | When | Prompt | What the hook injects |
|------|------|--------|------------------------|
| **Daily** (default) | Weekdays, via the orchestrator | embedded template in `launcher.py` | `<dispute-list>` — today's disputes + unconfirmed backfill |
| **Maintenance** | Sundays, via Task Scheduler | `PROMPT_SUNDAY.md` | `<maintenance-session>` — workspace stats, no disputes |

The Sunday session is workspace upkeep + self-calibration, NOT research: archive the research log into `memory/archive/` (quarterly, named by earnings season), promote recurring facts into `memory/reference_company_cadence.md`, prune `notes_for_ben.md`, rotate `outbox/`, and update `STATUS.md`. The dispute list is suppressed on purpose that day — follow `PROMPT_SUNDAY.md`. Launched by `scheduled_tasks/start_earnings_researcher_sunday.bat` (two-step: `launcher.py --prepare-only --prompt PROMPT_SUNDAY.md`, then a visible `claude` window).

---

## Critical Rules

- **NEVER overwrite a date confirmed by Ben** (`date_confirmed_by = 'ben'`). If you disagree with Ben's date, log it in `memory/research_log.md` but do NOT change it.