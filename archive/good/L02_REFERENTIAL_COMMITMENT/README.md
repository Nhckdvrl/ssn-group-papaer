# L02 — Semantic Role Completion and Referential Commitment

**2026-09-08 decision: NO-GO for the current NAACL Main research route.**

The original DNI/INI-to-fill/null mapping is not valid candidate-support gold.
Completed diagnostics do not establish a new extraction or system-selection
consequence beyond the closest literature. Preserve all evidence; do not promote
interpretation classification into a hallucination claim.

[Research verdict](RESEARCH_VERDICT.md) contains the reasoning, comparisons,
results and substantive redesign needed to reopen the route. H01–H03 remain
untested, not empirically refuted. No claim is made that all future implicit-
argument research is impossible.

| Evidence | Entry point |
|---|---|
| E000: original SemEval | [580 omissions, source labels and links](experiments/E000_data_audit/RESULTS.md) |
| E000b: revised UCCA | [391 typed participants / 116 review IDs](experiments/E000b_ucca_audit/RESULTS.md) |
| E000c: coreference | [1,198 source edges and visibility limits](experiments/E000c_coreference_audit/RESULTS.md) |
| E001a: 32B / 24B likelihood probe | [336 records; label-order sensitivity](experiments/E001a_interpretation/RESULTS.md) |
| E001b: direct native labels | [168 records; full-context DNI bias](experiments/E001b_native_labels/RESULTS.md) |

- [Claim ledger](CLAIMS.md) and [experiment log](EXPERIMENT_LOG.md)
- [Follow-up literature alignment](literature/FOLLOWUP_ALIGNMENT_20260908.md)
- [Support contract and resource admission](data/SUPPORT_CONTRACT.md)
- [Reproduction instructions](REPRODUCE.md)
- [Four-run provenance verification](runs/verification_models_20260908.json)

All four model runs completed: 504 prediction records over the same 42 distinct
development examples, not a 504-example independent test set. The original
proposal is retained as [historical material](experiments/E001_pilot/PROPOSAL_HISTORY_20260908.md);
its optimistic five-gate verdict and necessity claims are superseded.
