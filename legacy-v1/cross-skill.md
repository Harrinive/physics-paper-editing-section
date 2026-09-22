# Micro ↔ macro — shared rules

**For agents:** Start with the skill that matches scope — micro [physics-paper-editing/SKILL.md](../../physics-paper-editing/legacy-v1/LEGACY.md) § Agent read order for ≤12 sentences; this parent [LEGACY.md](LEGACY.md) § Agent read order for whole sections. Read this file only when routing, resuming, or handing off verifier models between parent and micro.

**Audience:** section orchestrator · micro agents **invoked from Stage D** · skill maintainers.

**Do not read this file** for a standalone short-passage edit (≤12 sentences, only the micro skill attached). That path is fully specified in [physics-paper-editing/SKILL.md](../../physics-paper-editing/legacy-v1/LEGACY.md) plus [coworker-loop.md](../../physics-paper-editing/legacy-v1/coworker-loop.md).

Canon for prose: sibling **`physics-paper-principles`**. Neither editing skill restates those principles.

| Read cross-skill when… | Section |
|------------------------|---------|
| Micro scope is **>12** or user wants a whole section | § Routing |
| Macro Stages A–E or resume | § ON RESUME · § Verifier model profile |
| Micro chunk agent with `session.md` / chunk-contract inputs | § Verifier model profile |
| Maintaining skills — avoid duplicating canonical tables | § Canonical rules |

| Skill | Path | Scope |
|-------|------|-------|
| **Principles** | [physics-paper-principles/SKILL.md](../../physics-paper-principles/legacy-v1/LEGACY.md) | What the prose should be |
| **Micro** | [physics-paper-editing/SKILL.md](../../physics-paper-editing/legacy-v1/LEGACY.md) | One passage **≤12 sentences** — coworker loop |
| **Macro (parent)** | [LEGACY.md](LEGACY.md) | Whole `\section{...}` or **>12 sentences** |

Standalone micro needs only one fact about the parent: **if the quote exceeds 12 sentences, stop** and suggest this skill or ask the user to narrow — [physics-paper-editing/SKILL.md](../../physics-paper-editing/legacy-v1/LEGACY.md) § Scope overflow.

---

## Routing

```
How many sentences in the target passage?
│
├─ ≤12 ──► micro skill
│           • Coworker loop in physics-paper-editing/SKILL.md
│           • Intake: job if unclear; inherit pace + models
│           • No parent required
│
└─ >12 or whole section ──► this parent skill
                            • Stages A–E; prose via micro per chunk
                            • Do not run micro on the full section in one turn
```

| Situation | Route |
|-----------|--------|
| User quotes ≤12 sentences | **Micro only** |
| User quotes >12 sentences | **Parent** (or ask user to narrow) |
| User asks to edit a whole `\section{...}` | **Parent** |
| Stage D chunk | **Micro** coworker loop on that `chunk_text` only |
| Stage E boundary fix | **Micro** on ≤12-sentence span |
| Writing without the coworker loop | **`physics-paper-principles` only** |

**Micro gate canonical:** [gate.md](../../physics-paper-editing/legacy-v1/gate.md) § Sentence-count thresholds.

---

## Terminology map

| Concept | Micro | Parent |
|---------|-------|--------|
| Pipeline unit | Passage (≤12 sentences) | Section → chunks |
| Main agent role | **Producer** — drafts, marks, merges | **Section orchestrator** — structure only |
| Verification | Background snapshot check; per-round synthesizer | Same **inside Stage D** per chunk |
| Source-audit Phase 1 | **Does not run** | **Does not run** |
| Pace | Background-check scope only | Frozen in Stage A; passed to every chunk |
| Grades `OVERALL` | Synthesizer only — job-round `PASS` \| `CONFLICTS` \| `PARTIAL` | Same per chunk; orchestrator never grades |
| First `.tex` write | Before checks finish (marked) | Same per chunk |
| Section-scale review | N/A | Stages **B** and **E** (`Scope: section`) |
| Disk state | `.physics-edit/micro/<job_id>/` | `.physics-edit/<slug>/` + `jobs/<id>/` |
| Resume boot | Live marks + `jobs/` | Read **`session.md` first** — § ON RESUME |

**Chunk agent** = micro producer invoked by Stage D. Same coworker loop; extra inputs in [chunk-contract.md](chunk-contract.md).

---

## Verifier model profile

### Standalone micro (no parent)

1. Ask polish vs rewrite only if unclear.
2. Inherit pace + the three slugs from this chat, **or** use recommended defaults and mention once ([user-communication.md](../../physics-paper-editing/legacy-v1/user-communication.md)).
3. Reuse the profile for every wave of this draft scope.

### Parent (section edit)

1. **Stage A** — freeze `job_mode`; obtain the one model-profile choice defined by [runtime-contract.md](../../physics-paper-editing/legacy-v1/runtime-contract.md), then persist role tiers, resolved identifiers, reasoning levels, and source in `session.md`, `section-brief.md`, and `manifest.json`.
2. Set **`user_confirmed: true`** only after the user accepts the role-based profile, selects inheritance, or supplies custom mappings. Displaying defaults alone leaves it `false`.
3. **Stages B, D, E** — reuse the recorded user-confirmed profile; a pending profile cannot authorize worker launch.
4. **Per chunk (Stage D)** — no re-ask when the profile is recorded:

| Session row | Used for |
|-------------|----------|
| sentence | Changed-sentence verifier jobs |
| deep | Narrative + math (Stages B/E and micro) |
| synth | Synthesizer only — never fast tier |

**Invalid skips:** `manifest.json` / `section-brief.md` model entries without a matching recorded profile in `session.md`.

**Hard stop:** do not delegate verification until the user confirms a profile for this top-level job or it is inherited from a user-confirmed parent section session. A no-interaction fallback is self-only; it cannot authorize worker launch. Do not re-ask for every chunk.

---

## Canonical rules (single source per topic)

| Topic | Canonical file | Section |
|-------|----------------|---------|
| Sentence / narrative / math principles | [physics-paper-principles](../../physics-paper-principles/legacy-v1/LEGACY.md) | Layer files |
| Physical lead | [physical-lead.md](../../physics-paper-principles/legacy-v1/physical-lead.md) | Full file |
| Severity / BLOCKER lists | [severity.md](../../physics-paper-editing/legacy-v1/severity.md) | Full file |
| Coworker loop | [coworker-loop.md](../../physics-paper-editing/legacy-v1/coworker-loop.md) | Full file |
| Marks / snapshot / interrupt | [job-state.md](../../physics-paper-editing/legacy-v1/job-state.md) | Full file |
| Merge | [merge-policy.md](../../physics-paper-editing/legacy-v1/merge-policy.md) | Full file |
| User-facing UX | [user-communication.md](../../physics-paper-editing/legacy-v1/user-communication.md) | Full file |
| Job × pace | [gate.md](../../physics-paper-editing/legacy-v1/gate.md) | Decision tree · Sentence-count thresholds |
| Background verify | [phase2-verify-subagents.md](../../physics-paper-editing/legacy-v1/phase2-verify-subagents.md) | Full file |
| Worker plan · COMPLIANCE | [compliance-monitoring.md](../../physics-paper-editing/legacy-v1/compliance-monitoring.md) | Full file |
| Sentence assignment count · batching | [sentence-check-subagents.md](../../physics-paper-editing/legacy-v1/sentence-check-subagents.md) | §3 |
| Macro stages A–E | [stages.md](stages.md) | Full file |
| Chunk I/O | [chunk-contract.md](chunk-contract.md) | Full file |
| Routing micro ↔ parent | **This file** | § Routing |
| Verifier inheritance | **This file** | § Verifier model profile |
| Section resume | **This file** | § ON RESUME |

---

## Writer ≠ grader · Orchestrator ≠ self-auditor

| Invariant | Rule |
|-----------|------|
| **Writer ≠ grader** | Producer / chunk agent never sets `OVERALL`; synthesizer only. `OVERALL` is a **job-round** status, not a ship gate. |
| **Orchestrator ≠ self-auditor** | Section orchestrator does not launch micro verifier jobs or certify assignment counts |
| **Pace** | Changes background-check scope only; never makes the user wait; never skips the synthesizer. Chunks always pass `caller: section-orchestrator`, so the standalone-micro fast-polish math skip never applies to a chunk. |

---

## ON RESUME (parent only)

When resuming a section edit (new chat, **next piece**, context compaction):

1. Read `.physics-edit/<slug>/`**session.md`** first.
2. Read `manifest.json` + `section-brief.md` + any `jobs/*/agents.json`.
3. If any job is `checking` → micro wake protocol (related hashes → interrupt → harvest → merge) **before** a new piece.
4. Honor `job_mode`, `pace`, and per-chunk `edit_gate`; do not re-ask.
5. Honor **User special requests**.
6. Profile must be user-confirmed for this job or inherited from a user-confirmed parent session before verifier jobs.
7. Execute **Next action**; rewrite `session.md` before ending the turn.

Detail: [disk-layout.md](disk-layout.md) § session.md · [automation.md](automation.md).
