# Disk layout & manifest

**Read with the Read tool** when Stages A or C run, or when resuming a section edit.

All cross-turn state lives under **`.physics-edit/<section-slug>/`** relative to the workspace root (or the `.tex` file's project root). Prefer a slug derived from `\section{...}` title or `\label{...}` (e.g. `Q-correctable-errors`).

## Directory layout

```
.physics-edit/<section-slug>/
├── session.md              # boot script — read first on every resume (procedure + job mode + pointer)
├── section-brief.md        # Stage A — message, placement, notation, job mode rationale, verifier profile
├── manifest.json           # ordered chunk records
└── chunks/
    └── <chunk_id>.checks   # archived micro <!-- CHECKS --> block per passed chunk
```

**Git:** add `.physics-edit/` to the project `.gitignore` if edits are ephemeral; commit manifest + brief + session if you want resumable section edits in version control.

## section-brief.md (Stage A)

Write at intake. Template:

```markdown
# Section brief: <title>

## Central message
<one paragraph>

## Placement
- File: <path>
- Section: <\section title or label>
- Neighbors: <prior / following sections>

## Notation & conventions
<symbols introduced or heavily used in this section>

## Audience & prerequisites
<what readers need before this section>

## Job mode (Stage A — frozen for section)
- **job_mode:** polish | rewrite | mixed
- **Rationale:** <1–2 sentences — user intent + placeholder scan>
- **rewrite_chunks:** [c01, …] — only when mixed

## Verifier model profile (Stage A — mirror of session.md)
- Phase 2 sentence: <slug Q1> — also used for Phase 1 SUBAGENTS unless overridden in session.md
- Phase 2 deep: <slug Q2> — narrative + math (macro Stages B/E use this slug)
- Phase 2 synth: <slug Q3>
```

Canonical handoff rules: [cross-skill.md](../physics-paper-editing/cross-skill.md) § Verifier model profile. The orchestrator passes slugs to micro chunk invocations **only when** `session.md` has `user_confirmed: true` from Stage A `AskQuestion`.

## manifest.json schema

Top-level object:

```json
{
  "section_slug": "Q-correctable-errors",
  "tex_file": "Notes/symdrome-specific correctable errors.tex",
  "section_label": "sec:Q-correctable",
  "created": "2026-06-11",
  "verifier_profile": {
    "sentence": "composer-2.5-fast",
    "deep": "claude-4.6-sonnet-medium-thinking",
    "synth": "claude-4.6-sonnet-medium-thinking"
  },
  "chunks": [ "<ChunkRecord>", "..." ]
}
```

`verifier_profile` keys (`sentence`, `deep`, `synth`) mirror `session.md` § Verifier model profile Phase 2 rows. Use only when `user_confirmed: true`.

Each **ChunkRecord**:

```json
{
  "chunk_id": "c03",
  "order": 3,
  "sentence_count": 8,
  "tex_anchor": {
    "file": "Notes/example.tex",
    "start_marker": "A finite set $\\mathbb{E}=\\{",
    "end_marker": "where $W=(W_{ab})$ is Hermitian."
  },
  "status": "pending",
  "edit_gate": "polish",
  "checks_path": null,
  "summary": null
}
```

### Field notes

| Field | Purpose |
|-------|---------|
| `chunk_id` | Stable id (`c01`, `c02`, …) — never reuse after pass |
| `order` | Processing order in Stage D |
| `tex_anchor` | **Text anchors**, not line numbers — lines drift as earlier chunks change length |
| `status` | `pending` \| `in_progress` \| `pass` |
| `edit_gate` | Optional — `polish` \| `rewrite`. Required on each chunk when `job_mode: mixed` in session/brief. Omit or `polish` when section is polish-only. Micro edit gate Q2 is **not** re-run when supplied. |
| `checks_path` | Set on pass, e.g. `chunks/c03.checks` |
| `summary` | Two-line what-changed, set on pass |

### Status transitions

```
pending → in_progress   (orchestrator picks chunk for this turn)
in_progress → pass      (micro OVERALL: PASS; CHECKS archived)
in_progress → pending   (micro FAIL abandoned this turn — rare; reset on retry)
```

Only one chunk should be `in_progress` at a time.

## Archiving CHECKS

On chunk PASS, write the synthesizer's verbatim `<!-- CHECKS ... -->` block to `chunks/<chunk_id>.checks`. The orchestrator's context keeps only the 2-line `summary` — not full verifier reports.

## session.md (Stage A — rewrite every turn)

Create from [examples/session.example.md](examples/session.example.md) at Stage A. **Read first on every resume** — before manifest or brief.

| Section | Purpose |
|---------|---------|
| MANDATORY read order | Boot sequence for cold resume after context compaction |
| Job mode | Frozen edit-gate Q2 outcome: `polish` \| `rewrite` \| `mixed` + `rewrite_chunks` |
| User special requests | Standing user directives + deferred major edits — honor every turn |
| Verifier model profile | Stage A AskQuestion slugs + `user_confirmed` — required before any verifier Task |
| Phase 1 reminder | ON / OFF / per-chunk — do not re-derive from gate.md |
| Last turn compliance | From synthesizer CHECKS: `compliance_orchestrator_plan`, `compliance_worker_reports`, `phase1`/`phase2` task counts — **not** written by orchestrator |
| Current position | `pipeline_stage`, progress, `next_chunk_id`, `last_completed` |
| Hard rules | One chunk/turn, honor job_mode, END TURN |
| Next action | Single imperative for this turn only |

**Rule:** `session.md` is rewritten from `manifest.json` at end of each turn — never the source of truth for chunk status. **`job_mode` is frozen at Stage A** (change only if user explicitly revises scope).

## Resuming

1. Read **`session.md`** first.
2. Read `manifest.json` + `section-brief.md`.
3. Read skill files per `session.md` skill read order.
4. Execute **Next action**.
5. If any `in_progress`, resume that chunk (or reset to `pending` if the turn was interrupted).
6. Else pick lowest `order` with `status: pending` → Stage D.
7. Else if all pass → Stage E (or report DONE if E complete).
8. **Rewrite `session.md`** before END TURN.
9. Skip Stages A–C unless the user requests a re-run.
