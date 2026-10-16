# Physics paper section editing skill

The active workflow is version 2: establish the section's physics architecture
and global object ledger, then edit argument-sized chunks through the direct or
reviewed contract. It covers whole sections of any length and long LaTeX,
Markdown, and plain-text physics passages. Reviewed chunks receive sentence and
terminology checks, independently when the host and user permit, and the
assembled section is checked again before completion. Start with
[SKILL.md](SKILL.md).

The bookkeeping of a round is a program, `scripts/check_edit_round.py`; the
skill lists when the agent runs which command. The project's role-to-model policy
is the file `physics-edit-policy.json` at the repository root; the skill stores no
default.

Version-1 sessions are closed historical records. Repeated work starts a fresh
version-2 round with explicit language coverage, an immutable original source,
current candidate snapshots, and dependency revisions.
