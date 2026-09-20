# Chunk contract (macro ↔ micro)

**For agents:** Start with [LEGACY.md](LEGACY.md) § Agent read order. Read this file before Stage D.

Each chunk invocation runs the **standalone** micro coworker loop ([physics-paper-editing](../../physics-paper-editing/legacy-v1/LEGACY.md)) on **one ≤12-sentence unit**. The section orchestrator **does not** inline-edit chunk body prose.

Routing and verifier inheritance: [cross-skill.md](cross-skill.md) § Verifier model profile.

## Macro → micro (inputs)

| Field | Required | Description |
|-------|----------|-------------|
| `chunk_id` | yes | Manifest id, e.g. `c03` |
| `chunk_text` | yes | ≤12 sentences for this chunk only |
| `edit_gate` | yes | `polish` \| `rewrite` |
| `pace` | yes | `fast` \| `full` — frozen in Stage A |
| `user_special_requests` | yes | Full § User special requests from `session.md` |
| `section_brief` | yes | Full `section-brief.md` |
| `adjacent_context` | recommended | 1–3 sentences from prev/next chunk |
| `verifier_model_profile` | yes | From session.md when `user_confirmed: true`; else defaults |
| `tex_anchor` | yes | Where to wrap / write back |
| `[bracket comments]` | if any | Inline editing instructions |
| `worker_plan_seed` | yes | `chunk_id`, `edit_gate`, `pace`, `N` — micro completes the worker plan |
| `job_id` | yes | Unique; disk at `jobs/<job_id>/` |

### Invoking the micro skill

1. Read micro [SKILL.md](../../physics-paper-editing/legacy-v1/LEGACY.md) and run the coworker loop on **`chunk_text` only**.
2. Treat `user_special_requests` as editing instructions (same priority as `[bracket comments]`).
3. Skip micro job/pace questions when `edit_gate`, `pace`, and a user-confirmed model profile are supplied.
4. Every chunk worker plan carries `caller: section-orchestrator`. The standalone fast-polish math skip **never** applies to a chunk.
5. Wrap the `tex_anchor` span with `% PPE-BEGIN` / `% PPE-END` ([job-state.md](../../physics-paper-editing/legacy-v1/job-state.md)). Snapshot. Schedule verification under the runtime contract; return control when it is asynchronous — do not wait for `OVERALL: PASS`.
   If micro **definition halt** fires for unresolved essential scientific ambiguity, leave the affected chunk `pending` (or `conflict`) and ask the specific scientific question. A valid construction or absence of an operational criterion alone does not halt Stage D; independent chunks may proceed.
6. On a later wake, harvest + merge ([merge-policy.md](../../physics-paper-editing/legacy-v1/merge-policy.md)). Write back the merged interior between the marks (or unmark on `PASS`).
7. Return Mode line + CHECKS (when a round finished) + compliance lines for `session.md`.

### tex_anchor write-back

Locate boundaries by `start_marker` and `end_marker`. After the first draft, the construction-area sentinels are the handle — prefer them over drifting markers. If markers are ambiguous after structural edits, refresh anchors in the manifest.

## Micro → macro (outputs)

| Output | Destination |
|--------|-------------|
| Chunk `status` | `drafted` / `checking` / `conflict` / `pass` |
| `job_id` | manifest + `jobs/<job_id>/` |
| Verbatim `<!-- CHECKS ... -->` | `chunks/<chunk_id>.checks` on `pass`; also `jobs/<id>/round.md` |
| 2-line summary | manifest `summary` on pass |
| Micro `Mode:` line | Audit drawer, prefixed with `section-edit · chunk:<id> ·` |

On `OVERALL: CONFLICTS`, leave the user’s text, set `conflict`, ask one decision. On `PARTIAL`, keep `checking` and relaunch open/dirty labels. The orchestrator does **not** mark `pass` until unmarked + `PASS`.

## Orchestrator rules (Stage D)

**Allowed:** pick a pending chunk; invoke micro; start **next piece** while another job is checking; archive CHECKS on pass.

**Forbidden:**

- Authoring chunk body prose without the micro loop.
- Launching micro verifier jobs from the section orchestrator.
- Waiting for `PASS` before the user may start another piece.
- Marking `pass` when CHECKS lacks `compliance_orchestrator_plan: PASS` and `compliance_worker_reports: PASS` (unless the round is `PARTIAL`/`CONFLICTS` — those are not pass).
- Nesting marks.

## Verifier profile handoff

When `verifier_model_profile` is supplied from **confirmed** `session.md`:

- Sentence verifier jobs → `sentence` (fast tier)
- Narrative + math → `deep`
- Synthesizer → `synth`

Document: `Verifier profile: inherited from session.md`.
