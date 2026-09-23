# Section-wide review

Section review exists to catch relationships that local chunks cannot see.

## Stage B focus

- Is the physics spine faithful to the manuscript's promised result?
- Are the physically native quantities identified before formal helpers?
- Do object scopes and factor conventions remain coherent across the section?
- Are any scientific choices unresolved before prose is reorganized?

Low-risk direct chunks may be self-only. Reviewed chunks use the mandatory
sentence and terminology-and-notation reviewers plus the triggered specialists
defined by the micro skill.

## Stage E focus

- Does the assembled section follow one physical argument?
- Does each object keep the same category, scope, normalization, and factors?
- Does the assembled section preserve established terminology and notation,
  with every new technical term or symbol necessary and defined?
- Do chunk boundaries preserve cause, implication, and claim strength?
- Are formal statements consistent across chunks?

Run one holistic reviewer. When relevant formal content is present, add one
formal reviewer with an explicit scope: `changed`, `dependency_closure`, or
`all_in_scope`; otherwise record `none`. Use `all_in_scope` for the affected
unit under the high-risk profile. Use the micro conflict adjudicator only for
an actual incompatible scientific recommendation.

Record section-level quality axes, affected spans, reviewed snapshot, reviewed
context revision and applicable object-ledger revision, formal-review scope,
applicable canon revision, and actual model metadata. Stage E does not emit
sentence results: declared sentence coverage belongs to each Stage-D chunk and
must already be current.
Do not launch one reviewer per sentence. Rerun a clean chunk when its snapshot or
a recorded dependency from the global context or ledger has changed.
