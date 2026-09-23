# Resume automation

Automation may locate the section state and detect stale snapshots, but it must
not choose scientific meaning or alter routing silently.

If the round is `needs_user` because of a newly discovered source-level
scientific defect, automation may refresh evidence but must not resume editing
other chunks until the author responds.

On resume:

1. locate `.physics-edit/<section-slug>/CURRENT` and resolve the active round;
2. if no active version-2 round exists, leave any legacy artifacts closed and
   create a fresh round rather than resuming them;
3. read the immutable original section and boundaries, current candidate,
   brief, object ledger, manifest, coverage contract, and next action;
4. compare the live section and dependency revisions with the reviewed
   candidate, chunk anchors, context revision, and ledger revision;
5. mark obsolete review output stale and recheck affected axes; under either
   language mode, changed or renumbered checked sentences need fresh evidence,
   and exhaustive coverage still requires every sentence;
6. update the current candidate and its hash only after all live spans and
   dependencies have been reconciled. Never overwrite the immutable original.

Host hooks are optional. Disk state remains sufficient for recovery.
