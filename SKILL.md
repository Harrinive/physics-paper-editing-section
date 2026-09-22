---
name: physics-paper-editing-section
description: >-
  Physics-first, capability-adaptive editing for whole LaTeX physics sections or
  passages over 12 sentences. Builds a section physics spine and global object
  ledger, edits argument-sized chunks through physics-paper-editing, and reviews
  the assembled section without forcing every chunk through the same harness.
---

# Physics paper editing — section

Use for a whole `\section{...}` or a passage over 12 typographic sentences. Use
**`physics-paper-editing`** directly for shorter passages. Canon is
**`physics-paper-principles`**.

New sessions use `harness_version: 2`. A section session without that field
resumes through [legacy-v1/LEGACY.md](legacy-v1/LEGACY.md); never migrate a live
version-1 session in place.

## Read order

1. On resume, read `session.md` first, then [cross-skill.md](cross-skill.md).
   For resume automation bounds, also read [automation.md](automation.md).
2. Read [stages.md](stages.md) and [disk-layout.md](disk-layout.md).
3. Before chunk editing, read [chunk-contract.md](chunk-contract.md) and the
   active micro [SKILL.md](../physics-paper-editing/SKILL.md).
4. Read [scope-and-verifiers.md](scope-and-verifiers.md) for Stage B or E review.
5. Before completion, read [test-checklist.md](test-checklist.md).

## Governing design

The section is organized around a **global physics spine** and **global object
ledger** before local prose is optimized. Every chunk inherits them. A chunk
may not introduce a competing normalization, factor convention, duplicate
symbol, or altered scope without reconciling the global ledger.

Chunking remains an attention and persistence mechanism; it does not require
micro-agent ceremony. A strong section editor may author chunks directly. An
economy editor uses the scaffolded micro path. Each chunk is routed separately
by scientific risk.

## Stages

| Stage | Outcome |
|---|---|
| A | Version-2 session, edit intent, model tier, section scope |
| B | Section physics spine, global object ledger, structural plan |
| C | Argument-sized chunks, each at most 12 sentences and LaTeX-safe |
| D | Adaptive editing per chunk; global ledger updated deliberately |
| E | One section-wide physics-story, object-consistency, and formal review |

Do not launch one reviewer per sentence. Do not require an independent worker
for a low-risk chunk. Reopen only spans that fail a required quality axis.

Before the first subagent in a new section session, obtain the user's model
choice using the micro skill's [runtime contract](../physics-paper-editing/runtime-contract.md).
Record the confirmed profile in `session.md` and pass it to every chunk and the
section-wide review. Do not launch a chunk or section reviewer while the choice
is pending.

## Persistence

Section work is normally resumable, so persist the version-2 session, brief,
object ledger, chunk manifest, and quality results under `.physics-edit/` as
specified in [disk-layout.md](disk-layout.md).

## Completion

A section is ready only when all chunks are integrated, no required quality
axis is `FIX` or `USER_DECISION`, and Stage E passes global physics lead and
object consistency. Verification independence is recorded separately from
content quality.

## Out of scope

- Passages of at most 12 sentences
- Inventing missing physical meaning
- Treating chunk boundaries as permission to redefine global objects locally
- Resuming a live version-1 session with version-2 state
