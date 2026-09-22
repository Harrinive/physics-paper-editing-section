# Version-2 section state

```text
.physics-edit/<section-slug>/
├── CURRENT
├── legacy-*/                    # closed, read-only history
└── runs/
    └── <round-id>/
        ├── session.md
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

## session.md

Store:

- `harness_version: 2`;
- unique `round_id` and `round_status: active | needs_user | ready | closed |
  superseded`;
- `language_coverage: selective | exhaustive`;
- starting and current SHA-256 identifiers for the target section snapshot;
- source file and section anchors;
- edit intent, model tier, tier source, user constraints, and the reviewer
  model profile with its choice, source, and `user_confirmed` value;
- current stage and next action;
- section-level quality and verification independence.

## section-brief.md

Store the section purpose, promised result, physics spine, neighboring context,
and manuscript conventions. Do not duplicate the full principles files.

## object-ledger.md

For every story-bearing object, store role/category, scope, dimensions/scaling,
included factors, normalization, first use, later payoff, and current
disposition. Record deliberate ledger changes with the affected chunks.

## manifest.json

Each chunk stores order, anchors, sentence count, edit intent, risk, object
dependencies, execution path, verification independence, quality axes,
completion, current snapshot identifier, stable sentence IDs, language coverage
status, and per-review model metadata. Under exhaustive coverage, it also
stores one current-snapshot verdict per sentence.

Direct chunks need no `jobs/` entry. Create a job directory only for a
persistent guided/independent review or concurrent file edit.

## Snapshot invalidation

A review is usable only when its recorded chunk or section snapshot matches the
live source. Preserve mismatched reviews as stale evidence. A changed sentence
invalidates its language verdict; a split, merge, reorder, or renumbering
invalidates the affected chunk's sentence map. Never promote stale PASS state.

## Legacy boundary

Any session without `harness_version: 2` is closed historical evidence. Do not
resume or migrate it in place. Keep it read-only, mark it closed when practical,
and create a fresh version-2 round with all quality fields pending.
