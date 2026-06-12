# Automation & hooks (optional)

**Read when** resuming multi-turn section edits or configuring hooks. Resume boot sequence also in [cross-skill.md](../physics-paper-editing/cross-skill.md) and macro [SKILL.md](SKILL.md) § ON RESUME.

## Context reset between chunks (Stage D)

**Default:** one chunk per agent turn. After a chunk PASSes, **end the turn**. The next turn reads only:

- **`session.md`** (first — procedure, job mode, next action)
- `section-brief.md`
- `manifest.json`
- The next chunk's `chunk_text` + `adjacent_context`

Per-chunk verifier reports are **not** carried forward.

### Resume commands

| User says | Action |
|-----------|--------|
| "continue section edit" | Read session.md → manifest → next pending chunk → Stage D |
| "next chunk" | Same |
| `/loop` (if configured) | Same on interval |

Document in the Stage D report: **Next: continue with chunk `<id>`**.

## Context compaction recovery

If the chat was summarized, context feels stale, or the user asks anything about an in-progress section edit:

1. **Read `session.md` first** — before answering or editing.
2. Follow its **Next action** and **Hard rules**.
3. Do **not** re-run micro edit gate Q2 — honor `job_mode` / `edit_gate` from session or manifest.
4. Honor **User special requests** — standing directives and deferred_edits.
5. Do **not** launch verifier Tasks without `session.md` § Verifier model profile `user_confirmed: true` — AskQuestion first if false.
6. Do **not** improvise a shorter editing workflow.

**Recommendation:** start a **new chat per chunk** in addition to `session.md`. Long single-thread sessions still risk compaction dropping skill rules even when disk state is correct.

## Manifest-driven "next pending"

Orchestrator algorithm (each resume):

```
1. Read .physics-edit/<slug>/session.md
2. Load .physics-edit/<slug>/manifest.json + section-brief.md
3. If any in_progress → resume that chunk_id (or reset to pending if stale)
4. Else first pending by order → Stage D
5. Else if all pass → Stage E (or report DONE if E complete)
6. Rewrite session.md before END TURN
```

## Hook awareness (`check-editing-session.sh`)

**Current behavior:** hook enforces micro `Mode:` + `<!-- CHECKS -->` on edit turns.

**Section edits:**

| Turn type | Hook expectation |
|-----------|------------------|
| Stage D (chunk) | Micro CHECKS required — same as micro skill |
| Stages A, B, C | No CHECKS required — `Mode: section-edit · stage:…` |
| Stage E complete | `<!-- SECTION DONE ... -->` recommended; per-chunk CHECKS archived on disk |

**Optional hook extension** (not required for v1):

```bash
# Also recognize section orchestrator turns without micro CHECKS
echo "$input" | grep -qE 'Mode: section-edit · stage:[ABCE]' && exit 0
```

Per-chunk CHECKS enforcement is sufficient for prose quality — the orchestrator never ships unverified chunk prose.

## `/loop` integration

If using Cursor's `/loop` command, configure a prompt such as:

```
Continue physics-paper-editing-section Stage D: read session.md and manifest at
.physics-edit/<slug>/; process exactly one pending chunk; rewrite session.md; END TURN.
```

Replace `<slug>` with the active section slug each session.

## Gitignore

Add to project `.gitignore` when edits are scratch work:

```
.physics-edit/
```

Commit `session.md` + `section-brief.md` + `manifest.json` if you want team-visible progress on long section edits.
