# Resume automation

Automation may locate the section state and detect stale snapshots, but it must
not choose scientific meaning or alter routing silently.

On resume:

1. locate `session.md` from the target section;
2. route sessions without `harness_version: 2` to legacy documents;
3. read the version-2 brief, object ledger, manifest, and next action;
4. compare live anchors with any reviewed snapshot;
5. mark obsolete review output stale and recheck only affected axes.

Host hooks are optional. Disk state remains sufficient for recovery.
