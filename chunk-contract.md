# Chunk contract (macro ↔ micro)

**For agents:** Start with [SKILL.md](SKILL.md) § Agent read order. Read this file before Stage D.

**Read with the Read tool** before Stage D.

Each chunk invocation runs the **standalone** micro skill ([physics-paper-editing](../physics-paper-editing/SKILL.md)) on **one ≤12-sentence unit** — same steps 1–7 as a direct user quote, plus the extra inputs below. The section orchestrator **does not** inline-edit chunk prose.

Routing and verifier inheritance: [cross-skill.md](../physics-paper-editing/cross-skill.md) § Verifier model profile.

## Macro → micro (inputs)

Pass all of the following in the chunk-agent prompt (or as structured context the Producer reads):

| Field | Required | Description |
|-------|----------|-------------|
| `chunk_id` | yes | Manifest id, e.g. `c03` |
| `chunk_text` | yes | ≤12 sentences LaTeX/text for this chunk only |
| `edit_gate` | yes | `polish` \| `rewrite` — from session `job_mode` or manifest per-chunk override when mixed |
| `pace` | yes | `fast` \| `full` — frozen in Stage A and inherited by every chunk |
| `user_special_requests` | yes | Full § User special requests from `session.md` (standing + deferred_edits) |
| `section_brief` | yes | Full contents of `section-brief.md` (shared across chunks) |
| `adjacent_context` | recommended | 1–3 sentences from prev/next chunk for boundary continuity |
| `verifier_model_profile` | yes | From session.md § Verifier model profile when `user_confirmed: true`; else AskQuestion before Tasks |
| `tex_anchor` | yes | From manifest — where to write back in the `.tex` file |
| `[bracket comments]` | if any | User inline editing instructions for this chunk |
| `task_plan_seed` | yes | `chunk_id`, `edit_gate`, `pace`, `N` from manifest/session — micro producer completes full [Task plan](../physics-paper-editing/compliance-monitoring.md) before Tasks |

### Invoking the micro skill

Tell the chunk agent explicitly:

1. Read micro [SKILL.md](../physics-paper-editing/SKILL.md) and run steps 1–7 on **`chunk_text` only**.
2. Treat `user_special_requests` as **editing instructions** in step 1 (Context) — same priority as `[bracket comments]`.
3. Skip micro intake when `edit_gate`, `pace`, and confirmed models are supplied:
   - `polish` + `fast` → Phase 1 INLINE + full Phase 2
   - `polish` + `full` → Phase 1 sentence Tasks + full Phase 2
   - `rewrite` → compose draft (skip Phase 1) + Phase 2 ([gate.md](../physics-paper-editing/gate.md) § Rewrite path)
   - "Full Phase 2" here always means narrative + math (when applicable) + synthesizer against the whole manuscript. The `caller: micro` fast-polish exception in [fast-polish.md](../physics-paper-editing/fast-polish.md) — narrower delta scope, possible math-Task skip — never applies to a chunk agent; every chunk Task plan carries `caller: section-orchestrator`.
4. **Skip** micro `AskQuestion` for verifier models **only when** `session.md` has `user_confirmed: true` — pass slugs from § Verifier model profile (`Phase 1 sentence`, `Phase 2 sentence`, `Phase 2 deep`, `Phase 2 synth`). When `Phase 1 sentence` is omitted, use `Phase 2 sentence` for Phase 1 SUBAGENTS ([cross-skill.md](../physics-paper-editing/cross-skill.md) § Verifier model profile).
5. If `user_confirmed: false` → run the single AskQuestion (*Editing setup*)
   before any editing Task; update session.md on answer.
6. On `OVERALL: PASS` **and** `compliance_orchestrator_plan: PASS` + `compliance_worker_reports: PASS` in CHECKS, write the edited chunk back to `tex_anchor` in the source `.tex` file.
7. Return outputs below to the orchestrator (include CHECKS + Mode line + § Last turn compliance for `session.md`).

### tex_anchor write-back

Locate chunk boundaries in `tex_anchor.file` by matching `start_marker` and `end_marker` (unique substrings). Replace the span between them with the passing chunk text. If markers are ambiguous after structural edits, refresh anchors in the manifest before Stage D.

## Micro → macro (outputs)

The chunk agent / orchestrator records:

| Output | Destination |
|--------|-------------|
| `OVERALL: PASS` | Required to set manifest `status: pass` |
| Verbatim `<!-- CHECKS ... -->` | `chunks/<chunk_id>.checks` |
| 2-line summary | `manifest.json` chunk record `summary` |
| Micro `Mode:` line | Section response (prefixed with `section-edit · chunk:<id> ·`) |
| `last_turn_compliance` | Orchestrator copies synthesizer CHECKS compliance lines into `session.md` |

On `OVERALL: FAIL` (content or procedural), the micro skill loops internally until PASS or turn limits; the orchestrator does **not** mark the chunk pass. If the turn ends mid-chunk, leave `in_progress` and resume next turn.

**Procedural FAIL** (batched sentence Tasks, missing Phase 1): relaunch micro with corrected Task plan — do not mark chunk pass.

## Orchestrator rules (Stage D)

**Allowed:** pick next pending chunk; set `in_progress`; invoke micro with
`edit_gate` and `pace`; archive CHECKS; update manifest and session; end turn.

**Forbidden:**

- Authoring or applying chunk prose without micro Phase 2 PASS.
- Processing multiple chunks in one turn (context explosion).
- Launching micro verifier Tasks from the section orchestrator (chunk agent / micro producer only).
- Skipping `AskQuestion` when `session.md` `user_confirmed: false` or profile is incomplete.
- Launching verifier Tasks using slugs from manifest/brief alone without Stage A AskQuestion confirmation.
- Re-running micro job or pace intake when supplied from session/manifest.
- Marking chunk `pass` when CHECKS lacks `compliance_orchestrator_plan: PASS` and `compliance_worker_reports: PASS`.

## Verifier profile handoff

When `verifier_model_profile` is supplied from **confirmed** `session.md`:

- **Phase 1 SUBAGENTS:** `Phase 1 sentence` slug, or `Phase 2 sentence` when Phase 1 row omitted (fast tier).
- **Phase 2:** sentence Tasks → `Phase 2 sentence`; narrative + math → `Phase 2 deep`; synthesizer → `Phase 2 synth`.

Document in the chunk turn: `Verifier profile: inherited from session.md (Stage A confirmed).`
