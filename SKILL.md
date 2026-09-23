---
name: physics-paper-editing-section
description: >-
  Physics-first editing for whole physics sections of any length or technical
  passages over 12 sentences in LaTeX, Markdown, or plain text.
  Builds a section physics spine and global object ledger, edits argument-sized
  chunks through physics-paper-editing, and reviews the assembled text.
---

# Physics paper editing — section

Use for a whole physics section of any length, a technical note, or any physics
passage over 12 typographic sentences in LaTeX, Markdown, or plain text. Use
**`physics-paper-editing`** directly for shorter non-section passages. Canon is
**`physics-paper-principles`**.

All legacy/version-1 sessions are closed historical records. Never resume them
or count their checks toward current completion. Every new or repeated pass
starts a version-2 editing round with its own round identifier and source
snapshot; see [disk-layout.md](disk-layout.md).

## Read order

1. Before the first user-facing reply, read the micro skill's
   [runtime-contract.md](../physics-paper-editing/runtime-contract.md) and
   [user-communication.md](../physics-paper-editing/user-communication.md).
   Follow the communication policy before every later user-facing reply.
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

Chunking remains an attention and persistence mechanism. A strong section
editor may author chunks directly; an economy editor uses the scaffold. Each
ordinary chunk uses the micro skill's `direct | reviewed` contract. A
source-format-safe unit that cannot be split below 13 sentences remains one
section-owned oversized chunk and uses the reviewed contract directly rather
than violating a definition or equation boundary.

Every chunk must preserve the section's established terminology and notation.
Chunk assembly may not introduce a new clipped label, mathematical alias, or
duplicate name that was absent from the source and global context unless it is
necessary, defined, and reconciled deliberately.

## Stages

| Stage | Outcome |
|---|---|
| A | Version-2 round, immutable source, edit intent, language coverage, role-to-model policy, section scope |
| B | Section physics spine, global object ledger, structural plan |
| C | Source-format-safe argument chunks, normally at most 12 sentences, with a defined oversized-unit fallback |
| D | Direct or reviewed editing per chunk; global ledger updated deliberately |
| E | One section-wide physics-story, object-consistency, and formal review |

Do not launch one reviewer per sentence. A reviewed chunk uses one whole-unit
sentence reviewer and one terminology-and-notation reviewer, plus triggered
specialists.
Do not require a reviewer for a low-risk direct chunk. Reopen only spans that
fail a required quality axis.

In the first user-facing reply, follow the micro skill's
[runtime contract](../physics-paper-editing/runtime-contract.md). If a standing
project or conversation role-to-model policy exists, state its mapping
and continue without asking for confirmation. Otherwise ask and wait. Record
the active mapping in `session.md` and pass it to every chunk and section-wide
review. Chunks do not ask again.

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

Section work is normally resumable, so persist each version-2 round, its
immutable original section text and boundaries, current candidate, brief,
context revision and object-ledger revision, chunk manifest, hashes, and quality results under
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

If any reviewer discovers a scientific defect in the author's source that the
requested task did not already authorize repairing, pause the entire section
round with `needs_user`. Preserve the source and ask one focused question; do
not continue other chunks or convert the defect into a completion-time
limitation.

## Out of scope

- Non-section passages of at most 12 sentences
- Inventing missing physical meaning
- Treating chunk boundaries as permission to redefine global objects locally
- Resuming or reactivating a legacy/version-1 session
