# Stages A–E

**For agents:** Start with [SKILL.md](SKILL.md) § Agent read order. This file is canonical for Stages A–E step detail.

**Read with the Read tool** when running the macro pipeline ([SKILL.md](SKILL.md)). Micro handoff per chunk: [chunk-contract.md](chunk-contract.md) · shared rules: [cross-skill.md](cross-skill.md). User-facing copy: [user-communication.md](../physics-paper-editing/user-communication.md).

---

## Stage A — Intake & section brief

**Goal:** Understand the section and freeze shared context before structural work.

```
1. Read target section + 1–3 sentences before/after + abstract/intro if needed
2. Create .physics-edit/<section-slug>/ (see disk-layout.md)
3. Job mode:
     • polish — tighten existing prose
     • rewrite — compose from placeholders / draft
     • mixed — mostly polish; list rewrite chunks (placeholders, \todo, [INSERT PROSE])
   Pace: fast | full — background-check scope only (inherit or default fast)
4. Ask polish/rewrite/mixed only if unclear. Inherit pace + models when
   session.md already has a recorded profile, or record the runtime fallback and
   mention once ([user-communication.md](../physics-paper-editing/user-communication.md)).
   If a user decision is required, wait for it before Stage B verification. Use the active runtime's interaction capability; do not assume a particular turn lifecycle.
5. Write section-brief.md and session.md
6. Mirror job_mode, pace, and the profile schema to manifest.json; retain the actual user_confirmed value
   only when the user accepted or selected it, or when it is explicitly inherited from a user-confirmed profile
7. Update session.md next action (Stage B)
8. Audit: Mode: section-edit · stage:A · <slug>
```

**Forbidden at Stage A:** launching section-scoped verifier jobs before the profile is recorded; copying model identifiers from a prior chat without saying so.

**Mid-run user directives:** append to session.md § User special requests with dated bullet; do not overwrite **standing** without user intent to replace.

---

## Stage B — Macro structural pass

**Goal:** Fix big narrative/logical structure **without authoring new body prose**.

Section-scoped verifiers may run asynchronously ([scope-and-verifiers.md](scope-and-verifiers.md), [coworker-loop.md](../physics-paper-editing/coworker-loop.md) harvest rules). Structure-only writes do not wait for those verifier jobs if the moves are already clear; still persist findings in `findings-ledger.md`.

```
1. Schedule section-scoped narrative + math verifier jobs (asynchronous when supported)
   — Scope: section, deep-tier model from session.md
2. Collect FAIL items → structural findings list
3. Apply structure-only fixes in .tex:
     • reorder / split paragraphs
     • add signposts, move labels
     • [INSERT PROSE: …] placeholders for Stage D
     • flag missing physical motivation or unresolved meaning; distinguish presentation suggestions from essential scientific choices — do not invent interpretation
   — do NOT write new body prose here
4. Re-read section; update section-brief.md if framing shifted
5. Update session.md — pipeline_stage: B
6. Receipt: what you reordered / placeholders you left
   Audit: Mode: section-edit · stage:B · <slug>
```

---

## Stage C — Chunking & manifest

**Goal:** Split into micro-invokable units and write manifest.

```
1. Count sentences per candidate chunk — each ≤12
2. Split on natural boundaries (paragraph / sub-claim)
3. Never break inside \(...\), $...$, equation envs, \cite{}, \ref{}
4. Assign chunk_id, order, tex_anchor (start_marker + end_marker)
5. If job_mode: mixed — set edit_gate on each ChunkRecord
6. Write manifest.json — all chunks status: pending
7. Update session.md — rewrite_chunks list, pipeline_stage: C
8. Receipt: how many pieces. You can start the first or keep reading.
   Audit: Mode: section-edit · stage:C · <slug> · <N> chunks
```

Use the same feasibility rules as the micro gate ([gate.md](../physics-paper-editing/gate.md)).

---

## Stage D — Draft + background check (non-blocking)

**Goal:** Put a piece in the file with marks and start its job. The user may keep editing it or start another piece.

```
1. Read session.md — job_mode, pace, verifier profile
   — if a job is checking, run the micro wake protocol first
2. If the user said next piece (or this is the first): pick lowest order
   with status: pending
3. Set status: drafted (then checking once the job launches)
4. Extract chunk_text from .tex using tex_anchor
5. Build adjacent_context from neighboring chunks (1–3 sentences each side)
6. Invoke micro coworker loop per chunk-contract.md:
     — edit_gate from session or manifest override
     — pace from session.md
     — wrap tex_anchor with PPE marks; snapshot; runtime-aware verifier jobs
     — skip micro job/pace questions when supplied with a confirmed profile
     — caller: section-orchestrator (no fast-polish math skip)
     — definition halt only for unresolved essential scientific ambiguity; construction-based definitions are allowed
7. Write jobs/<job_id>/; set chunk job_id + status: checking
8. Return control when the runtime permits — do not wait for OVERALL: PASS
   (Definition halt on that chunk: Need your call on the specific scientific choice; leave chunk pending; other chunks may proceed)
9. Audit: Mode: section-edit · chunk:<id> · verify:running · …
```

**Next piece while one is checking:** allowed. Second mark, second job. One job per marked region. Do not nest verifier fan-out.

**Wake / user edited a marked piece:** micro interrupt → harvest → merge. Update that chunk’s `status` to `conflict` if `OVERALL: CONFLICTS`, `pass` when unmarked after `PASS`, else keep `checking`.

**Resume:** any chat / **next piece** / **stop** → read session.md, then jobs + manifest.

If no pending chunks remain **and** every chunk is `pass` (unmarked, no open conflicts) → Stage E.

---

## Stage E — Integration pass

**Goal:** Verify the assembled section hangs together at chunk boundaries.

```
1. Re-read full section in .tex (all chunks pass / unmarked)
2. Launch section-scoped narrative + math verifiers (background OK)
   — scope-and-verifiers.md, Stage E context (boundary focus)
3. If FAIL on boundaries:
     • identify ≤12-sentence fix span
     • route fix through micro coworker loop
     • update manifest if a new chunk record is needed
4. When integration PASS → emit <!-- SECTION DONE ... --> in the audit drawer
5. Update session.md — pipeline_stage: done
6. Receipt: transitions reviewed. Audit: Mode: section-edit · stage:E · <slug> · integration:PASS
```

**Section DONE** = all manifest chunks `pass` AND integration PASS.

---

## Stage summary table

| Stage | Writes .tex? | Subagents? | Ends turn? |
|-------|--------------|------------|------------|
| A | brief + session | collect a user decision only if needed | while awaiting the decision |
| B | structure only | section verifiers (background OK) | after receipt |
| C | manifest only | no | after receipt |
| D | via micro draft+mark | micro background verifiers | **yes — after launch**, not after PASS |
| E | via micro if fixes | section verifiers | after receipt / DONE |
