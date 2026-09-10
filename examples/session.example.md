# Section edit session: <section-slug>

<!-- Copy to .physics-edit/<section-slug>/session.md at Stage A. Rewrite every orchestrator turn. -->

## MANDATORY — read first on every turn

1. **This file** (`session.md`)
2. `manifest.json`
3. `section-brief.md`
4. `jobs/*/agents.json` if any chunk is `checking`
5. Skill files per pipeline stage below

## Job mode

- **job_mode:** `polish` | `rewrite` | `mixed`
- **pace:** `fast` | `full`
- **Rationale:** <one line — see `section-brief.md` § Job mode>
- **rewrite_chunks:** `[c01, …]` — only when `job_mode: mixed`; omit otherwise

Do not re-run micro job or pace intake on resume; inherit both values.

## User special requests

Standing editing constraints from the user — **read every turn**; pass to every micro chunk invocation and section verifier prompt.

- **standing:** (bullet list)
- **added:** `<YYYY-MM-DD>` Stage A
- **deferred_edits:** (optional) major edits flagged but not applied

**Hard rule:** If a verifier or edit would violate **standing** requests, apply only minor fixes, note the conflict in **deferred_edits**, and report — do not silently override.

## Verifier model profile

| Role | Slug | Used for |
|------|------|----------|
| sentence | `<slug>` | Background changed-sentence Tasks |
| deep | `<slug>` | Narrative + math; Stages B/E |
| synth | `<slug>` | Job-round synthesizer (`OVERALL`; never fast tier) |

- **user_confirmed:** `true` | `false` — `true` after inherit, disclosed defaults, or AskQuestion
- **confirmed_at:** Stage A · `<YYYY-MM-DD>` (or `—`)
- **manifest mirror:** `manifest.json` → `verifier_profile` must match when confirmed

On resume: if `user_confirmed: false`, use disclosed defaults or AskQuestion before Tasks. Never silently invent slugs from brief/manifest alone.

## Last turn compliance

Copied from synthesizer CHECKS — orchestrator does **not** invent these values.

- **chunk:** `<id>`
- **job_id:** `<id>`
- **compliance_orchestrator_plan:** PASS | FAIL
- **compliance_worker_reports:** PASS | FAIL
- **phase1_sentence_tasks:** `0`
- **phase2_sentence_tasks:** `<launched>/<changed>`
- **OVERALL:** PASS | CONFLICTS | PARTIAL

## Current position

- **pipeline_stage:** A | B | C | D | E | done
- **in_file:** `<N>/<M>` pieces drafted
- **checking:** `[c01, …]` or `—`
- **next_chunk_id:** `<id>` or `—`
- **last_completed:** `<id>` — <one-line summary>
- **last_mode_line:** (optional) `<verbatim Mode line>`

## File map

| Path | Role |
|------|------|
| `Notes/example.tex` | Target TeX |
| `section-brief.md` | Content, notation, job mode rationale |
| `manifest.json` | Chunk state |
| `jobs/<id>/` | Snapshot + findings ledger |
| `chunks/*.checks` | Archived CHECKS per passed chunk |

## Hard rules (orchestrator)

- One **job** per marked region; next piece may start while another is checking
- Orchestrator writes structure only; chunk prose via micro coworker loop
- Do not wait for `PASS` before ending a draft-ready turn
- Honor `job_mode`, `edit_gate`, and `pace`
- Honor **User special requests**
- User-facing copy: workbench UX — no “reply continue”
- Update this file + manifest before ending the turn

## Skill read order by stage

| Stage | Read |
|-------|------|
| A–C, E | macro `SKILL.md`, `stages.md`, `disk-layout.md`; B/E also `scope-and-verifiers.md` |
| D | `chunk-contract.md` + micro `SKILL.md` + `coworker-loop.md` |

## Next action

<single imperative — e.g. Wake job j-c03 if checking; else draft pending c04 with marks and background verify; end turn.>
