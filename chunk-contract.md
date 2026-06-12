# Chunk contract (macro ↔ micro)

**Read with the Read tool** before Stage D.

Each chunk invocation runs the full micro skill ([physics-paper-editing](../physics-paper-editing/SKILL.md)) on **one ≤12-sentence unit**. The section orchestrator **does not** inline-edit chunk prose.

## Macro → micro (inputs)

Pass all of the following in the chunk-agent prompt (or as structured context the Producer reads):

| Field | Required | Description |
|-------|----------|-------------|
| `chunk_id` | yes | Manifest id, e.g. `c03` |
| `chunk_text` | yes | ≤12 sentences LaTeX/text for this chunk only |
| `edit_gate` | yes | `polish` \| `rewrite` — from session `job_mode` or manifest per-chunk override when mixed |
| `user_special_requests` | yes | Full § User special requests from `session.md` (standing + deferred_edits) |
| `section_brief` | yes | Full contents of `section-brief.md` (shared across chunks) |
| `adjacent_context` | recommended | 1–3 sentences from prev/next chunk for boundary continuity |
| `verifier_model_profile` | yes | From session.md § Verifier model profile when `user_confirmed: true`; else AskQuestion before Tasks |
| `tex_anchor` | yes | From manifest — where to write back in the `.tex` file |
| `[bracket comments]` | if any | User inline editing instructions for this chunk |

### Invoking the micro skill

Tell the chunk agent explicitly:

1. Read micro [SKILL.md](../physics-paper-editing/SKILL.md) and run steps 1–7 on **`chunk_text` only**.
2. Treat `user_special_requests` as **editing instructions** in step 1 (Context) — same priority as `[bracket comments]`.
3. **Skip micro edit gate Q2** when `edit_gate` is supplied — route directly:
   - `polish` → Phase 1 source verify + Phase 2 ([gate.md](../physics-paper-editing/gate.md) polish path)
   - `rewrite` → compose draft (skip Phase 1) + Phase 2 ([gate.md](../physics-paper-editing/gate.md) § Major rewrite path)
4. **Skip** the micro AskQuestion for verifier models **only when** session.md has `user_confirmed: true` — pass `{ sentence, deep, synth }` from session.md § Verifier model profile (Phase 1 sentence slug = `phase1_sentence` or same as Phase 2 sentence when omitted).
5. If `user_confirmed: false` → run AskQuestion (*Verifier model profile*) before any verifier Task; update session.md on answer.
6. On `OVERALL: PASS`, write the edited chunk back to `tex_anchor` in the source `.tex` file.
7. Return outputs below to the orchestrator.

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

On `OVERALL: FAIL`, the micro skill loops internally until PASS or turn limits; the orchestrator does **not** mark the chunk pass. If the turn ends mid-chunk, leave `in_progress` and resume next turn.

## Orchestrator rules (Stage D)

**Allowed:** pick next pending chunk; set `in_progress`; invoke micro with `edit_gate`; archive CHECKS; update manifest **and session.md**; end turn.

**Forbidden:**

- Authoring or applying chunk prose without micro Phase 2 PASS.
- Processing multiple chunks in one turn (context explosion).
- Launching micro verifier Tasks from the orchestrator (no nested dispatch).
- Re-AskQuestion for verifier models when session.md `user_confirmed: false` or profile missing.
- Launching verifier Tasks using slugs from manifest/brief alone without Stage A AskQuestion confirmation.
- Re-running micro edit gate Q2 when `edit_gate` is supplied from session/manifest.

## Verifier profile handoff

When `verifier_model_profile` is supplied from **confirmed** session.md:

- **Phase 1 SUBAGENTS:** sentence Tasks use `phase1_sentence` or `profile.sentence` (fast tier).
- **Phase 2:** sentence Tasks → `profile.sentence`; narrative + math → `profile.deep`; synthesizer → `profile.synth`.

Document in the chunk turn: `Verifier profile: inherited from session.md (Stage A confirmed).`
