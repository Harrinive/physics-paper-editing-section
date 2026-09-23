---
name: physics-paper-editing-section
description: >-
  Physics-first, capability-adaptive editing for whole physics sections or
  technical passages over 12 sentences in LaTeX, Markdown, or plain text.
  Builds a section physics spine and global object ledger, edits argument-sized
  chunks through physics-paper-editing, and reviews the assembled text.
---

# Physics paper editing — section

Use for a whole physics section, a technical note, or any physics passage over
12 typographic sentences in LaTeX, Markdown, or plain text. Use
**`physics-paper-editing`** directly for shorter passages. Canon is
**`physics-paper-principles`**.

All legacy/version-1 sessions are closed historical records. Never resume them
or count their checks toward current completion. Every new or repeated pass
starts a version-2 editing round with its own round identifier and source
snapshot; see [disk-layout.md](disk-layout.md).

## Read order

1. Before the first user-facing reply, read the micro skill's
   [runtime-contract.md](../physics-paper-editing/runtime-contract.md) and
   [user-communication.md](../physics-paper-editing/user-communication.md).
   Before later replies, reread the communication policy as needed.
2. On resume, resolve the active version-2 round through `CURRENT`, read that
   round's `session.md`, then [cross-skill.md](cross-skill.md).
   For resume automation bounds, also read [automation.md](automation.md).
3. Read [stages.md](stages.md) and [disk-layout.md](disk-layout.md).
4. Before chunk editing, read [chunk-contract.md](chunk-contract.md) and the
   active micro [SKILL.md](../physics-paper-editing/SKILL.md).
5. Read [scope-and-verifiers.md](scope-and-verifiers.md) for Stage B or E review.
6. Before completion, read [test-checklist.md](test-checklist.md).

## Governing design

The section is organized around a **global physics spine** and **global object
ledger** before local prose is optimized. Every chunk inherits them. A chunk
may not introduce a competing normalization, factor convention, duplicate
symbol, or altered scope without reconciling the global ledger.

Chunking remains an attention and persistence mechanism; it does not require
micro-agent ceremony. A strong section editor may author chunks directly. An
economy editor uses the scaffolded micro path. Each chunk is routed separately
by scientific risk.

Every chunk must preserve the section's established terminology and notation.
Chunk assembly may not introduce a new clipped label, mathematical alias, or
duplicate name that was absent from the source and global context unless it is
necessary, defined, and reconciled deliberately.

## Stages

| Stage | Outcome |
|---|---|
| A | Version-2 round, edit intent, language coverage, model tier, section scope |
| B | Section physics spine, global object ledger, structural plan |
| C | Argument-sized chunks, each at most 12 sentences and source-format-safe |
| D | Adaptive editing per chunk; global ledger updated deliberately |
| E | One section-wide physics-story, object-consistency, and formal review |

Do not launch one reviewer per sentence. Do not require an independent worker
for a low-risk chunk. Reopen only spans that fail a required quality axis.

In the first user-facing reply of every new conversation that invokes this
skill, ask which models to use if subagents are needed, following the micro
skill's [runtime contract](../physics-paper-editing/runtime-contract.md). Ask
before substantive editing, even if the section may ultimately need no
subagents. A standing preference may be offered as the recommended choice but
does not replace the question. Record the user's explicit answer in
`session.md` and pass it to every chunk and the section-wide review. Chunks do
not ask again. Do not begin substantive editing or launch a reviewer while the
choice is pending.

Every round also declares `language_coverage: selective | exhaustive`.
Selective coverage audits changed or diagnosed sentences plus chunk-level
prose. Exhaustive coverage gives every sentence in every current chunk a
current-snapshot language verdict. Do not infer exhaustive coverage merely
from the existence of old chunk artifacts; ask when the requested coverage is
ambiguous. Detail: the micro skill's
[language-coverage.md](../physics-paper-editing/language-coverage.md).

Coverage selects sentences, not principles. Every in-scope sentence receives
all 15 sentence checks, and every sentence in newly drafted text counts as
changed.

## Persistence

Section work is normally resumable, so persist each version-2 round, its brief,
object ledger, chunk manifest, source hashes, and quality results under
`.physics-edit/` as specified in [disk-layout.md](disk-layout.md). Historical
rounds remain immutable evidence and never satisfy a later round.

## User-facing language

Keep the exact version, round, snapshot, routing, and status vocabulary in the
persisted records, where it is needed for correctness. In conversation, follow
the shared [user-communication policy](../physics-paper-editing/user-communication.md):
describe what is happening in ordinary language and never present an internal
label without immediately explaining what it means for the author's text.

## Completion

A section is ready only when all chunks are integrated, every required result
matches the current chunk and section snapshots, the declared language
coverage is complete, no required quality axis is `FIX` or `USER_DECISION`, and
Stage E passes global physics lead, object consistency, and assembled-text
terminology and notation. Verification independence is recorded separately
from content quality.

For a scoped section copyedit, inherit the micro skill's completion boundary:
an untouched pre-existing violation outside the authorized change scope may be
recorded as a limitation rather than repaired. Stage E must still check the
assembled section, and every violation introduced, changed, or left unresolved
inside the required coverage blocks completion. A section completed under this
exception must not be described as fully compliant with the canon.

## Out of scope

- Passages of at most 12 sentences
- Inventing missing physical meaning
- Treating chunk boundaries as permission to redefine global objects locally
- Resuming or reactivating a legacy/version-1 session
