# Automation & resume

**For agents:** Start with [SKILL.md](SKILL.md) § Agent read order. **Read when** resuming a section edit or arming an optional file watcher. Resume boot: [cross-skill.md](cross-skill.md) § ON RESUME.

## After a Stage D launch

Return control once the piece is marked and verification is scheduled asynchronously. Do **not** wait for `PASS`. Do **not** ask the user to reply **continue**.

The next turn reads:

- **`session.md`** first
- `section-brief.md` + `manifest.json`
- `jobs/<id>/` for any `checking` chunk (wake protocol before a new piece)

## Resume commands

| User says | Action |
|-----------|--------|
| anything, while a job is `checking` | Wake protocol first (related hashes → interrupt → harvest → merge) |
| **next piece** | Draft the next `pending` chunk (second mark OK) |
| **stop** | Request stop for running verifiers; harvest; do not start a new piece |
| (no command — just an edit) | Same as wake |

## Context compaction recovery

If the chat was summarized or the user asks about an in-progress section edit:

1. **Read `session.md` first.**
2. Follow **Next action** and **Hard rules**.
3. Do not re-run job or pace intake.
4. Honor **User special requests**.
5. Do **not** launch verifier jobs without a confirmed, inherited, or recorded no-interaction-fallback profile.
6. Do **not** improvise the old wait-until-PASS loop.

## Optional file watcher

Silent editor edits are invisible until a chat message or a wave finishes, unless a debounced watcher (~5–10s after last write) wakes the parent and runs the same hash check ([coworker-loop.md](../physics-paper-editing/coworker-loop.md)). Arm only if the user wants that; do not mention the watcher in the narrative.

## Hook awareness (`check-editing-session.sh`)

| Turn type | Hook |
|-----------|------|
| `verify:running` / `verify:partial` / `draft-ready` | Legal without CHECKS |
| Stages A, B, C, E | No micro CHECKS required |
| `verify:complete` | CHECKS in the audit drawer; **no** FAIL reloop |

## Gitignore

```
.physics-edit/
```
