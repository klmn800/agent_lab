# Reference Staging — Pre-Graduation Findings

Material in this directory is **provisional**. It does not appear in TA's working knowledge until Ben (the graduation gate) promotes it to `E:/options_scanner/agents/trading_advisor/reference/`.

---

## Frontmatter Schema (required on every staged file)

Every file in `reference/staging/` MUST start with YAML frontmatter:

```yaml
---
title: <short descriptive title>
type: <pattern | mechanic | lesson | case_study | calibration>
hypothesis: <one-sentence claim being made>
sample_size: <n>
hit_rate: <decimal, e.g. 0.72>
date_range: <YYYY-MM-DD to YYYY-MM-DD>
confidence: <low | medium | high>
confidence_rationale: <one sentence — why this confidence level>
session: <NNN>
drafted: <YYYY-MM-DD>
status: <draft | ready_for_review | revision_requested>
supersedes: <filename or "none">
---
```

Body follows: methodology, queries run, raw results, interpretation, edge cases, limits, recommended use in morning briefs.

---

## Graduation Process

1. **MA writes:** Drop file in `reference/staging/` with frontmatter `status: draft`. Iterate until you believe it's ready. Change frontmatter to `status: ready_for_review`.
2. **MA flags:** Append a one-liner in `notes_for_ben.md`: "Ready for review: `reference/staging/<filename>.md`". You do NOT write to TA's workspace.
3. **Ben reviews:** Three outcomes:
   - **Promote:** Ben runs `python E:/options_scanner/tools/graduate_reference.py <filename>` (or copies manually). The tool copies the file into TA's `reference/`, strips frontmatter, and moves your staged copy to `reference/staging/promoted/<filename>`.
   - **Send back with notes:** Ben appends a `## Ben's Notes (YYYY-MM-DD)` section at the bottom of the staged file, changes frontmatter `status: revision_requested`, drops a one-liner in `directive.md` pointing you at the file. You revise in-place and bump status back to `ready_for_review`.
   - **Decline:** Ben appends `## Ben's Notes — DECLINED (YYYY-MM-DD): <reason>` and moves to `reference/staging/declined/<filename>`. You may re-propose with substantially different evidence — supersedes the declined file's name.

---

## What "Sent Back with Notes" Looks Like

Concretely, in the staged file:

```markdown
---
title: Peer-Sympathy Earnings — Airlines
type: pattern
hypothesis: ...
sample_size: 47
hit_rate: 0.68
date_range: 2025-09-01 to 2026-04-30
confidence: medium
confidence_rationale: 47 events split across only 4 reporter-peer pairs; small N per pair
session: 042
drafted: 2026-05-16
status: revision_requested
supersedes: none
---

# Peer-Sympathy Earnings — Airlines

(body...)

## Ben's Notes (2026-05-18)

The 68% hit rate looks fine on the surface but you're mixing post-earnings days. T+1 vs T+5 entry behaves very differently in the airline cohort. Re-cut with T+1 isolated, then with T+2-T+5 isolated, and see if one regime dominates. If T+1 is doing the heavy lifting, the playbook needs to specify same-day entry.

Also — sample is heavy on DAL/UAL (n=31 of 47). Spell out generalization risk in the body.

Revise and re-flag.
```

You read Ben's notes at session start (or when directed via `directive.md`), revise in-place, bump status to `ready_for_review` again. The append-only history keeps the iteration visible.

---

## What Goes in `reference/` (MA's own) vs `staging/` (TA-bound)

| Goes in `reference/` (MA's permanent library) | Goes in `reference/staging/` (TA-bound) |
|---|---|
| Research methodology docs | Patterns / mechanics / lessons MA wants TA to use in trade calls |
| MA's own glossary, calibration framework | New case studies of completed trades |
| Notes on how MA conducts sessions | Validated playbook entries |

The split: `reference/` is MA's working library (writeable). `reference/staging/` is the pipeline TO TA.
