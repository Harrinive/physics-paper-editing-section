# The rulings file

A project may keep the author's decisions in `RULINGS.md` at the repository root.
Rulings for the whole paper that are general rules belong in the project's writing
guide; `RULINGS.md` holds decisions about particular objects and claims. A project
without the file works as before.

**Who reads it.** The agent that weighs the findings reads the whole file once per
round: `digest` and `stage-e merge` print it. Reviewers stay cold; no reviewer packet
carries it. A round may still quote a few rulings by hand in its section brief or
in `reviewer-context.md`; those are the only rulings reviewers see.

**A ruled decision is settled.** The rule is in
[quality-contract.md](../physics-paper-editing/quality-contract.md).

## Keeping the file

The file holds the owner's current decisions, not their history.

- **File by subject, not by place.** Entries are grouped by the object, claim, or
  topic they concern. Each states the decision and its reason, so that it holds
  wherever the text moves, and cites no section number or position.
- **Revise, do not append.** Before adding a ruling, find the entries on the same
  subject. Merge it into one it extends; rewrite or delete one it replaces.
- **Story rulings stand apart.** Rulings on the order of the paper or the role of a
  section sit in one block, because a reorganization changes exactly those.
- **Follow the text.** When a change alters what the paper says about a subject,
  reread that subject's entries in the same change. Delete an entry only when the
  owner has replaced it or its subject has left the paper. If unsure, ask the owner.
- **Move what has grown general.** A ruling that now holds for the whole paper moves
  to the writing guide.

The file stays Markdown, with one heading per subject, so that the headings can
serve as a list of keys if it ever grows too long for one read.
