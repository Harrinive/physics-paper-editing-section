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
   session.md already has user_confirmed: true, or use micro defaults and
   mention once ([user-communication.md](../physics-paper-editing/user-communication.md)).
   If you must AskQuestion, END TURN until it returns — do not launch Stage B checkers yet.
5. Write section-brief.md and session.md
6. Mirror job_mode, pace, and slugs to manifest.json; set user_confirmed: true
   when the profile is inherited, defaulted-and-disclosed, or AskQuestion-confirmed
7. Update session.md next action (Stage B)
8. Audit: Mode: section-edit · stage:A · <slug>
```

**Forbidden at Stage A:** launching section-scoped verifier Tasks before models are resolved; copying slugs from a prior chat without saying so.

**Mid-run user directives:** append to session.md § User special requests with dated bullet; do not overwrite **standing** without user intent to replace.

---

## Stage B — Macro structural pass

**Goal:** Fix big narrative/logical structure **without authoring new body prose**.

Section-scoped verifiers may run in the background ([scope-and-verifiers.md](scope-and-verifiers.md), [coworker-loop.md](../physics-paper-editing/coworker-loop.md) harvest rules). Structure-only writes do not wait for those Tasks if the moves are already clear; still persist findings in `findings-ledger.md`.

```
1. Launch section-scoped narrative + math verifier Tasks (background OK)
   — Scope: section, deep-tier model from session.md
2. Collect FAIL items → structural findings list
3. Apply structure-only fixes in .tex:
     • reorder / split paragraphs
     • add signposts, move labels
     • [INSERT PROSE: …] placeholders for Stage D
     • flag construction-led definitions (recipe before operational criterion); do **not** invent the criterion — placeholder or user call
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
     — wrap tex_anchor with PPE marks; snapshot; background Tasks
     — skip micro job/pace AskQuestion when supplied
     — caller: section-orchestrator (no fast-polish math skip)
     — definition halt: do not wrap a construction-only named-object definition
7. Write jobs/<job_id>/; set chunk job_id + status: checking
8. End the turn — do not wait for OVERALL: PASS
   (Definition halt on that chunk: Need your call; leave chunk pending; do not wrap a construction-only draft)
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
| A | brief + session | AskQuestion only if needed | if waiting on AskQuestion |
| B | structure only | section verifiers (background OK) | after receipt |
| C | manifest only | no | after receipt |
| D | via micro draft+mark | micro background verifiers | **yes — after launch**, not after PASS |
| E | via micro if fixes | section verifiers | after receipt / DONE |
