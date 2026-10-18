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
editor may author chunks directly; an economy or unknown editor uses the scaffold. Each
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
all 16 sentence checks, and every sentence in newly drafted text counts as
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

## Compliance gate

The bookkeeping of a round is a program, `scripts/check_edit_round.py` (run it
with `python3`; it needs no packages; `--root` defaults to the top level of the
current git repository). It keeps the verdicts per sentence, issues reviewer
packets with the hash of the text they show, records reviewer reports, and decides
with `check` whether the round may be reported as ready. It calls no LLM and
changes no manuscript text. The project's role-to-model policy is the file
`physics-edit-policy.json` at the repository root; the skill stores no default,
so ask the owner when it is missing and write the answer with `policy set`.

Commands: `policy`, `init`, `chunks`, `rechunk`, `pending`, `prompt`, `record`,
`digest`, `waive`, `stage-e`, `status`, `snapshot`, `defect`, `revision`, `gc`, `check`
(`--help` lists the options). Run these at the moments below. **Must** means the
program refuses the next step or `check` fails without it.

| # | Moment | Run | |
|---|---|---|---|
| 1 | Start of a round | `policy show` (if missing: ask the owner, then `policy set`), `init`, fill brief and ledger, `check` | must: policy, `init`; should: `check` (only brief, ledger and attestations should be open) |
| 2 | Resume in a new session or after compaction | `status`, `pending`, `check` | must. `status` lists packets issued but not recorded: record or drop them before launching new ones |
| 3 | A bullet is split, merged, moved or added | `rechunk`, `chunks` | must. A chunk with at least half of its sentences already reviewed keeps its id |
| 4 | After each edit batch, once the editor's own canon check is done | `record --role editor_closure`, then `digest` (no accepted finding may be unapplied), `pending`, `prompt` | must: the closure (`prompt` refuses without it). A FIX that you decide not to apply: `waive --reason` |
| 5 | Launching a reviewer | the model and effort that `prompt` prints | must |
| 6 | A reviewer result | `record --packet pNNN --report FILE --model M --effort E` | must. It enforces model and effort, revision, and a verdict for every scoped sentence. Sentences that changed since the packet was issued are reported, not rejected: their verdicts simply no longer match |
| 7 | A sentence review with principle hits `FIX` | `prompt --role specialist --principles ...` before the repair | must (the gate owes a specialist per hit) |
| 8 | A batch is recorded | `pending`, `digest` | should |
| 9 | Nothing pending in a chunk | `prompt --scope close` for the sentence and the terminology reviewer, then repairs by rows 4 to 8 | must: `check` needs a close review per role |
| 10 | After the last edit | `snapshot` | must (`check` fails until the snapshot equals the live text) |
| 11 | Before Stage E | `check` shows no line that begins with a chunk id | must: `prompt --role holistic\|formal` refuses otherwise |
| 12 | A Stage E round (at most two) | `prompt --role holistic` and `--role formal` once per reviewer (3 per role in round 1, 2 in round 2; the program refuses more), each launched as a new agent that gets only the printed line; `record --packet` for each; `stage-e merge`; `stage-e rule --cluster K.. --as applied\|waived\|deferred --reason ...` | must. A cluster is must when one reviewer calls it a claim defect or two reviewers raise it; `applied` is accepted only when its sentences changed; round 2 is required when round 1 applied a claim or global cluster; there is no round 3; one-sentence wording items are `local` and go back to the chunk loop |
| 13 | An owner ruling, a Stage E repair, or a move between chunks | `defect rule` if a defect was logged; `pending` for the blast radius; `revision --yes` only if the spine, the ledger or the conventions that reviewers judge against changed | must for `defect rule`. A bump prints and discards every current verdict and rejects packets still out. An edit of the ledger, the brief or `reviewer-context.md` without a bump is only warned about when a packet is recorded |
| 14 | Before every report to the owner | `check`; quote its last line; end with "Deviations from the skill:" | must |
| 15 | At the end of a round, or when asked about disk use | `gc` | should. It lists rounds past retention and deletes nothing; `gc --compact` removes the bulk of expired rounds (raw reports, packets, sentence maps, snapshots) and only with the owner's agreement |

## Completion

A section is ready only when all chunks are integrated, every required result
matches the current chunk and section snapshots, the declared language
coverage is complete, no required quality axis of a chunk is `FIX` or
`USER_DECISION`, and Stage E is adjudicated: at most two rounds of independent
blind reviewers, every must cluster applied or waived (none open, none deferred
to the owner). Verification independence is recorded separately from content
quality.

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
