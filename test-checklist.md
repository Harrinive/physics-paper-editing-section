# End-to-end test checklist

**For agents:** Start with [SKILL.md](SKILL.md) § Agent read order. **Read before** declaring a section edit complete, or to validate a dry-run setup.

## Dry-run (no .tex writes)

```
[ ] Count sentences in target section — must be >12 for macro (or user wants whole section)
[ ] Identify \section{} boundaries and tex file path
[ ] Estimate chunk count (sentences ÷ ~8–10 per chunk)
[ ] Confirm no chunk would break inside equations/cites/refs
[ ] Choose section-slug for .physics-edit/
```

Report: `Dry-run: <N> sentences → ~<M> chunks feasible`.

## Full acceptance (after Stage E)

```
[ ] section-brief.md exists with job_mode, pace, and verifier profile mirror
[ ] session.md exists; pipeline_stage matches manifest; profile resolved
[ ] manifest.json — every chunk status: pass
[ ] PPE marks removed from passed chunks
[ ] chunks/*.checks — one file per passed chunk with OVERALL: PASS
[ ] chunks/*.checks — compliance_* PASS; one sentence_S*k*: line per label (no ranges)
[ ] jobs/<id>/findings.jsonl exists for each job that ran
[ ] Source .tex — anchors resolve; no [INSERT PROSE] placeholders remain
[ ] Stage E integration — no unresolved FAIL
[ ] Audit drawer includes <!-- SECTION DONE ... --> with integration: PASS
```

## Regression checks

```
[ ] Micro skill works standalone on ≤12-sentence quotes (draft-first, marks, background verify)
[ ] Micro gate routes >12 sentences to this macro skill
[ ] Stage D may start next piece while another job is checking (one job per mark)
[ ] Stage D does **not** wait for PASS before ending the turn
[ ] Hook allows verify:running / verify:partial without CHECKS; no FAIL reloop
[ ] Verifier profile inherited or defaulted — not re-asked per chunk
[ ] Orchestrator did not author chunk body prose
[ ] Task plan has phase1_sentence_tasks: 0
[ ] Full-scope chunks: no fast-polish math skip (caller: section-orchestrator)
[ ] Section orchestrator did not launch micro verifier Tasks directly
[ ] Cold resume honors job_mode and pace; wake protocol runs if a job is checking
[ ] CONFLICTS leaves user text and asks one decision
[ ] Definition halt: construction-led named object → ask for operational criterion before drafting that chunk
[ ] User-facing turns use named states — no progress bars, no “reply continue”
```

## Example dry-run target

Any `\section{...}` with **>12** typographic sentences is a valid parent-skill candidate. Count sentences, estimate chunks (roughly 8–10 sentences each), and confirm no chunk would split inside math, `\cite{}`, or `\ref{}`.

**Dry-run result shape:** `Dry-run: <N> sentences → ~<M> chunks feasible`. Sample: [examples/dry-run-manifest.example.json](examples/dry-run-manifest.example.json).

## Failure recovery

| Symptom | Action |
|---------|--------|
| Agent forgot workflow / improvised edits | Read `session.md` first; follow Next action |
| User directive ignored | Re-read § User special requests; deferred_edits |
| Construction marks missing | Last snapshot + tex_anchor; ask before re-wrap |
| Chunk stuck `checking` | Wake protocol; harvest jsonl; do not drop findings |
| tex_anchor not found | Prefer PPE sentinels; else refresh markers |
| Integration FAIL at boundary | ≤12-sentence span → micro coworker loop → re-run Stage E |
