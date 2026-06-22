# End-to-end test checklist

**Read before** declaring a section edit complete, or to validate a dry-run setup.

## Dry-run (no .tex writes)

Use to verify a section is macro-eligible before Stages A–E:

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
[ ] section-brief.md exists with ## Job mode and verifier profile mirror
[ ] session.md exists; pipeline_stage matches manifest state; § Verifier model profile has `user_confirmed: true` before any verifier Task (brief/manifest alone insufficient — cross-skill.md)
[ ] manifest.json — every chunk status: pass
[ ] chunks/*.checks — one file per chunk with OVERALL: PASS
[ ] chunks/*.checks — `compliance_orchestrator_plan: PASS` and `compliance_worker_reports: PASS`; one `sentence_S*k*:` line per label (no `sentence_S1-S3` ranges)
[ ] session.md § Last turn compliance matches last chunk CHECKS
[ ] Source .tex — chunk anchors resolve; no [INSERT PROSE] placeholders remain
[ ] Stage E integration — narrative + math verifiers: no unresolved FAIL
[ ] Response includes <!-- SECTION DONE ... --> with integration: PASS
[ ] Every prose change in the section was verified by micro Phase 2 (trace via CHECKS files)
```

## Regression checks

```
[ ] Micro skill works standalone on ≤12-sentence quotes (no .physics-edit/, full AskQuestion path — cross-skill.md § Verifier model profile · standalone)
[ ] Micro gate routes >12 sentences to this macro skill (cross-skill.md § Routing)
[ ] Stage D never processes two chunks in one turn
[ ] Verifier profile asked once in Stage A, not re-asked per chunk
[ ] Orchestrator did not author chunk prose without micro PASS
[ ] Phase 1 polish chunks: CHECKS or Mode line shows N sentence Tasks (not one batched Task)
[ ] Section orchestrator did not launch micro verifier Tasks directly
[ ] Cold resume from session.md only — agent honors job_mode without re-running Q2
[ ] No verifier Task launched without Stage A AskQuestion confirmation (`user_confirmed: true`)
```

## Example dry-run target

For the Ancilla Optimization notes, `\section{$\mathfrak{Q}$-correctable errors}` in `Notes/syndrome-specific correctable errors.tex` is a valid macro candidate (>12 sentences, multiple subsections).

**Dry-run result:** prose sentence estimate >20 → macro eligible → ~4–6 chunks. Sample manifest: [examples/dry-run-manifest.example.json](examples/dry-run-manifest.example.json).

Expected flow: Stage A brief → Stage B structural on full section → Stage C ~4–6 chunks → Stage D one per turn → Stage E boundary check.

## Failure recovery

| Symptom | Action |
|---------|--------|
| Agent forgot workflow / improvised edits | Read `session.md` first; do not re-run edit gate Q2; follow Next action |
| User directive ignored (major edit shipped) | Re-read § User special requests; move violation to deferred_edits; revert or ask user |
| Verifier Tasks without model AskQuestion | Check `session.md` `user_confirmed`; if false, AskQuestion before any Task |
| Chunk stuck `in_progress` | Reset to `pending`; re-run Stage D for that id |
| tex_anchor not found | Refresh markers in manifest after structural edits |
| Micro FAIL loop exhausted | Fix in chunk turn; do not mark pass |
| Integration FAIL at boundary | Extract ≤12-sentence span → micro skill → re-run Stage E |
