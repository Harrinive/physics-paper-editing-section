# Stages A–E

**For agents:** Start with [SKILL.md](SKILL.md) § Agent read order. This file is canonical for Stages A–E step detail.

**Read with the Read tool** when running the macro pipeline ([SKILL.md](SKILL.md)). Micro handoff per chunk: [chunk-contract.md](chunk-contract.md) · shared rules: [cross-skill.md](../physics-paper-editing/cross-skill.md).

---

## Stage A — Intake & section brief

**Goal:** Understand the section and freeze shared context before structural work.

```
1. Read target section + 1–3 sentences before/after + abstract/intro if needed
2. Create .physics-edit/<section-slug>/ (see disk-layout.md)
3. Prepare one **Editing setup** intake after scope:
     • polish — tighten existing prose; Phase 1 ON per chunk
     • rewrite — compose from placeholders / draft; Phase 1 OFF per chunk
     • mixed — mostly polish; list rewrite chunks (placeholders, \todo, [INSERT PROSE])
     • fast — Phase 1 INLINE; Phase 2 unchanged
     • full — Phase 1 sentence Tasks; Phase 2 unchanged
4. AskQuestion — **Editing setup** (job, pace, and three verifier models):
     Q1 Job mode; Q2 Pace
     Q3 Sentence checker; Q4 Narrative & logic; Q5 Synthesizer
     Never auto-select slugs — user must confirm via AskQuestion.
     **END TURN after AskQuestion if user has not yet answered** — do not launch Stage B verifiers in the same turn.
5. Write section-brief.md and session.md with job_mode, pace, rationale, user
   requests, and model profile
6. Mirror job_mode, pace, and slugs to manifest.json; set user_confirmed: true
7. Update session.md next action (await Stage B or user approval)
8. Report Mode: section-edit · stage:A · <slug>
```

Skip AskQuestion only if resuming and session.md has `user_confirmed: true` with a complete profile table.

**Forbidden at Stage A:** launching section-scoped verifier Tasks before AskQuestion returns; copying slugs from a prior chat or "recommended" defaults without AskQuestion.

**Mid-run user directives:** append to session.md § User special requests with dated bullet; do not overwrite **standing** without user intent to replace.

**Checkpoint (recommended):** pause for user approval of brief before Stage B.

---

## Stage B — Macro structural pass

**Goal:** Fix big narrative/logical structure **without authoring new prose**.

```
1. Launch section-scoped narrative + math verifier Tasks
   — scope-and-verifiers.md, Scope: section, deep-tier model from session.md § Verifier model profile
   — **Hard stop:** if session.md `user_confirmed: false`, run AskQuestion first; END TURN if awaiting answer
2. Collect FAIL items → structural findings list
3. Apply structure-only fixes in .tex:
     • reorder / split paragraphs
     • add signposts, move labels
     • [INSERT PROSE: …] placeholders for Stage D
   — do NOT write new body prose here
4. Re-read section; update section-brief.md if framing shifted
5. Update session.md — pipeline_stage: B, next action
6. Report Mode: section-edit · stage:B · <slug> + findings applied
```

**Checkpoint (recommended):** user approves structural plan before chunking.

---

## Stage C — Chunking & manifest

**Goal:** Split into micro-invokable units and write manifest.

```
1. Count sentences per candidate chunk — each ≤12
2. Split on natural boundaries (paragraph / sub-claim)
3. Never break inside \(...\), $...$, equation envs, \cite{}, \ref{}
4. Assign chunk_id, order, tex_anchor (start_marker + end_marker)
5. If job_mode: mixed — set edit_gate on each ChunkRecord (rewrite or polish)
6. Write manifest.json — all chunks status: pending
7. Update session.md — rewrite_chunks list, pipeline_stage: C, next action
8. Report Mode: section-edit · stage:C · <slug> · <N> chunks
```

Use the same feasibility rules as the micro gate ([gate.md](../physics-paper-editing/gate.md) Q3).

**Checkpoint (recommended):** user approves chunk list before Stage D loop.

---

## Stage D — Chunk loop (one chunk per turn)

**Goal:** Edit and verify each chunk via the micro skill; bounded context.

```
1. Read session.md — confirm job_mode, pace, next chunk edit_gate, and verifier profile
   — if `user_confirmed: false`, AskQuestion (*Editing setup*) first; END TURN if awaiting answer
2. Read manifest — pick lowest order with status: pending
3. Set status: in_progress
4. Extract chunk_text from .tex using tex_anchor
5. Build adjacent_context from neighboring chunks (1–3 sentences each side)
6. Invoke micro skill per chunk-contract.md:
     — edit_gate from session job_mode or manifest per-chunk override
     — pace from session.md; never reselect per chunk
     — skip micro job/pace intake when supplied
     — polish + fast: Phase 1 INLINE; polish + full: Phase 1 sentence Tasks;
       rewrite: Phase 1 OFF
     — Phase 2 always; verifier profile from session.md when `user_confirmed: true` (no per-chunk re-ask)
     — write back to tex_anchor on OVERALL: PASS
7. Archive CHECKS → chunks/<id>.checks; set status: pass, summary
8. Rewrite session.md — progress, next_chunk_id, last_completed, next action
9. Report Mode: section-edit · chunk:<id> · <micro Mode line verbatim>
10. END TURN — do not start the next chunk in the same turn. Full pace asks the
    user to continue. Fast pace does not ask for per-chunk approval; when
    `/loop` is active, the next loop turn advances automatically.
```

**Resume:** user says "continue section edit" / "next chunk" / `/loop` → read session.md, then manifest, go to step 2.

If a chunk FAILs when fast automation is active: keep it `in_progress`, stop
automatic advancement, report the blocker in plain language, and resume that
same chunk after correction. Never skip to the next chunk.

If no pending chunks remain → Stage E.

---

## Stage E — Integration pass

**Goal:** Verify the assembled section hangs together at chunk boundaries.

```
1. Re-read full section in .tex (all chunks now pass)
2. Launch section-scoped narrative + math verifiers
   — scope-and-verifiers.md, Stage E context (boundary focus)
3. If FAIL on boundaries:
     • identify ≤12-sentence fix span
     • route fix through micro skill (chunk-contract.md)
     • update manifest if a new chunk record is needed
4. When integration PASS → emit <!-- SECTION DONE ... -->
5. Update session.md — pipeline_stage: done
6. Report Mode: section-edit · stage:E · <slug> · integration:PASS
```

**Section DONE** = all manifest chunks `pass` AND integration PASS.

---

## Stage summary table

| Stage | Writes .tex? | Subagents? | Ends turn? |
|-------|--------------|------------|------------|
| A | brief + session | AskQuestion | optional |
| B | structure only | section verifiers | optional |
| C | manifest only | no | optional |
| D | via micro PASS | micro verifiers per chunk | **yes — every chunk** |
| E | via micro if fixes | section verifiers | yes |
