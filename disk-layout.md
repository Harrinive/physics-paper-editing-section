# Version-2 section state

```text
.physics-edit/<section-slug>/
├── session.md
├── section-brief.md
├── object-ledger.md
├── manifest.json
├── reviews/
└── jobs/
    └── <job_id>/
```

## session.md

Store:

- `harness_version: 2`;
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
completion, and snapshot identifier when reviewed.

Direct chunks need no `jobs/` entry. Create a job directory only for a
persistent guided/independent review or concurrent file edit.

## Version boundary

If an existing session lacks `harness_version: 2`, read the version-1 layout in
[legacy-v1/disk-layout.md](legacy-v1/disk-layout.md). Do not rewrite its schema.
