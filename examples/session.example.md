# Section edit session: <section-slug>

<!-- Copy to .physics-edit/<section-slug>/session.md at Stage A. Rewrite every orchestrator turn. -->

## MANDATORY — read first on every turn

1. **This file** (`session.md`)
2. `manifest.json`
3. `section-brief.md`
4. Skill files per pipeline stage below

## Job mode

- **job_mode:** `polish` | `rewrite` | `mixed`
- **Rationale:** <one line — see `section-brief.md` § Job mode>
- **rewrite_chunks:** `[c01, …]` — only when `job_mode: mixed`; omit otherwise
- **Phase 1:** ON (polish) | OFF (rewrite) | per-chunk (mixed — check next chunk `edit_gate`)

Do **not** re-run micro edit gate Q2 on resume — inherit `edit_gate` from this file or manifest.

## User special requests

Standing editing constraints from the user — **read every turn**; pass to every micro chunk invocation and section verifier prompt.

- **standing:** (bullet list — verbatim or faithful paraphrase of user directives at task creation)
  - e.g. *Do only minor edits in place; do not restructure or rewrite whole paragraphs without approval.*
  - e.g. *Report any need for major edits (reorder, new argument, substantial rephrase) in the stage report — do not ship without user OK.*
- **added:** `<YYYY-MM-DD>` Stage A (append dated bullets when user adds mid-run)
- **deferred_edits:** (optional) major edits flagged but not applied — chunk id, one-line description, awaiting user

**Hard rule:** If a verifier or edit would violate **standing** requests, apply only minor fixes, note the conflict in **deferred_edits**, and report to the user — do not silently override.

## Verifier model profile (Stage A — AskQuestion required)

**Hard stop:** Do **not** launch any verifier `Task` until `user_confirmed: true` below.

| Role | Slug | Used for |
|------|------|----------|
| Phase 1 sentence | `<slug>` | Phase 1 SUBAGENTS (polish only); may equal Phase 2 sentence |
| Phase 2 sentence | `<slug>` | Changed-sentence verifier Tasks; default for Phase 1 when row above omitted |
| Phase 2 deep | `<slug>` | Narrative + math verifier Tasks; macro Stages B/E |
| Phase 2 synth | `<slug>` | Synthesizer (`OVERALL`; never fast tier) |

- **user_confirmed:** `true` | `false` — set `true` **only** after Stage A `AskQuestion` (*Verifier model profile*) returns
- **confirmed_at:** Stage A · `<YYYY-MM-DD>` (or `—` if not yet confirmed)
- **manifest mirror:** `manifest.json` → `verifier_profile` must match this table when confirmed

On resume: if `user_confirmed: false` → **AskQuestion before any verifier Task** (Stages B, D, E). Never auto-select slugs from brief/manifest alone.

Micro chunk agents inherit this profile when `user_confirmed: true` — document `Verifier profile: inherited from session.md (Stage A confirmed)`.

## Last turn compliance

Copied from synthesizer CHECKS after each chunk PASS — orchestrator does **not** invent these values.

- **chunk:** `<id>`
- **compliance_orchestrator_plan:** PASS | FAIL
- **compliance_worker_reports:** PASS | FAIL
- **phase1_sentence_tasks:** `<launched>/<required>` (e.g. `3/3`)
- **phase2_sentence_tasks:** `<launched>/<changed>` (e.g. `0/0`)
- **batched:** `false` | `<note if §3.1 only>`

If `compliance_*: FAIL` on last turn, **re-run that chunk** with corrected Task plan before advancing.

## Current position

- **pipeline_stage:** A | B | C | D | E | done
- **progress:** `<N>/<M> pass`
- **next_chunk_id:** `<id>` or `—` (Stage E / done)
- **last_completed:** `<id>` — <one-line summary from manifest>
- **last_mode_line:** (optional) `<verbatim Mode line from last turn>`

## File map

| Path | Role |
|------|------|
| `Notes/example.tex` | Target TeX |
| `section-brief.md` | Content, notation, job mode rationale |
| `manifest.json` | Chunk state, optional per-chunk `edit_gate` |
| `chunks/*.checks` | Archived micro CHECKS per passed chunk |
| `~/.cursor/skills/physics-paper-editing-section/SKILL.md` | Macro orchestrator |
| `~/.cursor/skills/physics-paper-editing-section/stages.md` | Stages A–E steps |
| `~/.cursor/skills/physics-paper-editing-section/chunk-contract.md` | Stage D micro handoff |
| `~/.cursor/skills/physics-paper-editing/cross-skill.md` | Micro ↔ macro routing and canonical rules |
| `~/.cursor/skills/physics-paper-editing/gate.md` | Edit gate Q2 reference (frozen at Stage A) |
| `~/.cursor/skills/physics-paper-editing/SKILL.md` | Micro skill (Stage D per chunk) |

## Hard rules (orchestrator)

- One chunk per turn; **END TURN** after chunk PASS
- Orchestrator writes structure only; chunk prose via micro skill only
- Micro Phase 2 **always** required for shipped prose
- Honor **job_mode** / `edit_gate` — do not re-run edit gate Q2 on resume
- Honor **User special requests** — standing directives override default polish aggressiveness
- **Verifier models:** use slugs from § Verifier model profile only when `user_confirmed: true`; else AskQuestion first
- Update this file + manifest before END TURN

## Skill read order by stage

| Stage | Read |
|-------|------|
| A–C, E | macro `SKILL.md`, `stages.md`, `disk-layout.md`; B/E also `scope-and-verifiers.md` |
| D | macro `chunk-contract.md` + micro `SKILL.md` for current chunk only |

## Next action

<single imperative sentence — e.g. Process chunk c03 only with edit_gate polish via micro skill; update manifest and this file; END TURN.>
