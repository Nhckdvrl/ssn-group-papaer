# E000b — UCCA resource suitability

Executed `scripts/audit_ucca_resource.py` on the original authors' repository,
commit `432bac16527299b389a0f964e34abf040e000f7c`. `report.json` records hashes
of all 395 repository data/document files and the executed script. No labels edited.

Reproduced IWPT 2021 Table 2 exactly:

| Native type | Count |
|---|---:|
| Deictic | 107 |
| Generic | 86 |
| Genre-based | 147 |
| Type-identifiable | 6 |
| Arbitrary/Nonspecific | 36 |
| Iterated/repeated/set | 9 |
| Total | 391 |

There are 393 graph segments grouped into 116 review/document IDs. An additional
28 nodes marked implicit have other/unrefined incoming labels; they are retained
in the audit counts and excluded from the six-type count, not silently relabeled.

82 parent scenes contain typed implicit participants of different categories.
For example, `139152-0002`, “Very good hospitality offered.!”, contains both
Genre-based and Generic participants. They share the broad UCCA Participant edge
`A`; the release does not supply frame-specific role names (provider versus
recipient). Graph IDs alone cannot tell a language model which semantic role a
question targets. Manually inferring role names would be new annotation.

Admission: suitable for a native graph/type inventory and potential independent
annotation sampling. **Not admitted as an automatic replacement for L02's primary
filler-support gold.** The audit exports null `role_identity_gold` and
`candidate_specific_support_gold` fields explicitly. Category → unsupported
specific filler mapping remains unvalidated, as it was in SemEval.

Scientific consequence: this route broadens natural source material beyond Doyle,
but does not, without new annotation, solve the principal measurement problem.
This is not evidence that the semantic distinction is trivial or that models fail.
