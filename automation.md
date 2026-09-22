# Resume automation

Automation may locate the section state and detect stale snapshots, but it must
not choose scientific meaning or alter routing silently.

On resume:

1. locate `.physics-edit/<section-slug>/CURRENT` and resolve the active round;
2. if no active version-2 round exists, leave any legacy artifacts closed and
   create a fresh round rather than resuming them;
3. read the active round's brief, object ledger, manifest, coverage contract,
   and next action;
4. compare the live section hash and chunk anchors with reviewed snapshots;
5. mark obsolete review output stale and recheck affected axes; under
   exhaustive language coverage, any changed or renumbered sentence needs a
   fresh language verdict;
6. update the round's current source hash only after all live spans have been
   reconciled.

Host hooks are optional. Disk state remains sufficient for recovery.
