# Disk layout & manifest

**For agents:** Start with [SKILL.md](SKILL.md) § Agent read order. **Read with the Read tool** when Stages A or C run, when a Stage D job starts, or when resuming.

All cross-turn state lives under **`.physics-edit/<section-slug>/`** relative to the workspace root (or the `.tex` file's project root). Prefer a slug derived from `\section{...}` title or `\label{...}`.

## Directory layout

```
.physics-edit/<section-slug>/
├── session.md
├── section-brief.md
├── manifest.json
├── findings-ledger.md          # Stage B/E structural notes
├── chunks/
│   └── <chunk_id>.checks       # archived job-round CHECKS when a chunk PASSes
└── jobs/
    └── <job_id>/               # snapshot.tex, sentences.json, findings.jsonl, round.md, agents.json
```

Job folder schema: [job-state.md](../physics-paper-editing/job-state.md).

**Git:** add `.physics-edit/` to the project `.gitignore` if edits are ephemeral.

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
- **pace:** fast | full
- **Rationale:** <1–2 sentences>
- **rewrite_chunks:** [c01, …] — only when mixed

## Verifier model profile (Stage A — mirror of session.md)
- Sentence: <slug>
- Deep: <slug> — narrative + math (Stages B/E too)
- Synth: <slug>
```

Pass slugs to micro chunks only when `session.md` has `user_confirmed: true`.

## manifest.json schema

```json
{
  "section_slug": "Q-correctable-errors",
  "tex_file": "Notes/example.tex",
  "section_label": "sec:Q-correctable",
  "created": "2026-09-03",
  "job_mode": "polish",
  "pace": "fast",
  "verifier_profile": {
    "sentence": "composer-2.5-fast",
    "deep": "claude-4.6-sonnet-medium-thinking",
    "synth": "claude-4.6-sonnet-medium-thinking"
  },
  "chunks": []
}
```

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
  "job_id": null,
  "checks_path": null,
  "summary": null
}
```

| Field | Purpose |
|-------|---------|
| `chunk_id` | Stable id (`c01`, `c02`, …) |
| `order` | Default draft order |
| `tex_anchor` | Text anchors, not line numbers |
| `status` | `pending` \| `drafted` \| `checking` \| `conflict` \| `pass` |
| `edit_gate` | Required on each chunk when `job_mode: mixed` |
| `job_id` | Active or last `.physics-edit/.../jobs/<id>` |
| `checks_path` | Set on pass, e.g. `chunks/c03.checks` |
| `summary` | Two-line what-changed, set on pass |

### Status transitions

```
pending → drafted     (micro wrote marked interior)
drafted → checking    (background job launched)
checking → checking   (merge round; still dirty / open labels)
checking → conflict   (OVERALL: CONFLICTS — user decision)
conflict → checking   (user resolved; new wave)
checking → pass       (OVERALL: PASS, unmarked, no running Tasks)
pass → checking       (Stage E boundary fix re-opens the span)
```

More than one chunk may be `checking` at a time (one job per marked region).

## Archiving CHECKS

On chunk `pass`, write the synthesizer's verbatim `<!-- CHECKS ... -->` to `chunks/<chunk_id>.checks`. Keep only the 2-line `summary` in orchestrator context.

## session.md (rewrite every turn)

Create from [examples/session.example.md](examples/session.example.md) at Stage A. **Read first on every resume.**

| Section | Purpose |
|---------|---------|
| MANDATORY read order | Boot sequence |
| Job mode | Frozen `polish` \| `rewrite` \| `mixed` |
| Pace | Frozen `fast` \| `full` |
| User special requests | Standing + deferred_edits |
| Verifier model profile | Slugs + `user_confirmed` |
| Last turn compliance | From CHECKS — not invented by the orchestrator |
| Current position | `pipeline_stage`, how many pieces are in the file / still being read |
| Hard rules | One job per mark; honor job_mode + pace; no “reply continue” |
| Next action | Single imperative |

**Authority:** `manifest.json` for chunk `status`; `session.md` for job_mode, pace, profile, special requests, next action.

## Resuming

1. Read **`session.md`** first.
2. Read `manifest.json` + `section-brief.md` + any `jobs/*/agents.json`.
3. If any job is `checking` → micro wake protocol first.
4. Else if user said **next piece** → first `pending` by order.
5. Else if all `pass` → Stage E (or DONE).
6. Rewrite `session.md` before ending the turn.
7. Skip Stages A–C unless the user requests a re-run.
