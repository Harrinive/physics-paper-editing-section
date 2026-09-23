# Version-2 section state

```text
.physics-edit/<section-slug>/
├── CURRENT
├── legacy-*/                    # closed, read-only history
└── runs/
    └── <round-id>/
        ├── session.md
        ├── source-original.txt
        ├── source-boundaries.json
        ├── candidate-snapshot.txt
        ├── section-brief.md
        ├── object-ledger.md
        ├── manifest.json
        ├── reviews/
        └── jobs/
            └── <job_id>/
```

`CURRENT` contains the relative path of the active version-2 round. A new
round gets a new directory. Never overwrite, reactivate, or use a historical
round's quality results to satisfy the current round.

`source-original.txt` stores the immutable round-start section text.
`source-boundaries.json` stores its section and chunk anchors.
`candidate-snapshot.txt` stores the current reviewed candidate. Hashes identify
these artifacts but never replace them; disk recovery must not depend on Git or
conversation memory.

## session.md

Store:

- `harness_version: 2`;
- unique `round_id` and `round_status: active | needs_user | ready | closed |
  superseded`;
- `language_coverage: selective | exhaustive`;
- identifiers for the immutable original and current candidate snapshots;
- source file and section anchors;
- edit intent, model tier, tier source, user constraints, and the active
  role-to-model policy with its choice, source, and standing/user-selected
  status;
- current stage and next action;
- section-level quality and verification independence.

## section-brief.md

Store the section purpose, promised result, physics spine, neighboring context,
and manuscript conventions. Do not duplicate the full principles files.

## object-ledger.md

For every story-bearing object, store role/category, scope, dimensions/scaling,
included factors, normalization, first use, later payoff, and current
disposition. Give the ledger a content hash or monotonic revision. Record each
deliberate change, the affected chunks, and the resulting revision.

## manifest.json

Each chunk stores order, original and live anchors, sentence count, edit intent,
risk, object dependencies, reviewed context and ledger revisions, execution
path/profile, formal-review scope, verification independence, all five quality
axes, completion, current snapshot identifier, stable sentence IDs, checked
sentence IDs, principle hits, language coverage results, terminology review,
triggered specialists, and per-review model metadata. Under exhaustive coverage,
the checked-sentence evidence includes every sentence.

An ordinary synchronous direct chunk needs no `jobs/` entry. Create a job
directory whenever lifecycle or evidence requirements demand persistence,
including a resumable or concurrent direct edit and reviewed work whose results
must survive context loss.

## Snapshot invalidation

A review is usable only when its recorded candidate snapshot, context revision,
and relevant object-ledger dependencies match the live state. Preserve
mismatched reviews as stale evidence. A changed sentence invalidates its
language verdict; a split, merge, reorder, or renumbering invalidates the
affected sentence map. A context-revision or applicable object-ledger-revision
change invalidates every dependent review even when chunk text is unchanged.
Never promote stale PASS state.

`context_revision` identifies the inherited section spine, neighboring text,
and manuscript conventions. It excludes the object ledger, whose applicable
revision is stored separately.

## Legacy boundary

Any session without `harness_version: 2` is closed historical evidence. Do not
resume or migrate it in place. Keep it read-only, mark it closed when practical,
and create a fresh version-2 round with all quality fields pending.
