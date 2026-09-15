# L37 — When Do Label Semantics Break ICL's Inference–Verbalization Boundary?

**Date registered:** 2026-09-14  
**Date revoked:** 2026-09-15  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** **ARCHIVED / NO-GO — PILOT AUTHORIZATION REVOKED**

## Revocation decision

L37 is closed before pilot execution.

The original selected question was:

> Under anti-semantic labels, does the model still infer the correct underlying class and fail only in downstream verbalization, or does label semantics contaminate the inferred task representation itself?

The original novelty audit was insufficient because it searched mainly under our own terminology (`semantic labels`, `inference/verbalization`, `task vectors`) and failed to perform an answer-ownership search over alternative literatures describing the same computation.

## Direct ownership collision

The decisive missed owner is **Halawi et al., ICLR 2024, _Overthinking the Truth: Understanding how Language Models Process False Demonstrations_**.

That work studies false / permuted demonstration labels and already reports the load-bearing qualitative answer that L37 hoped to discover:

- intermediate layers can favor the truthful / underlying answer;
- later computation increasingly follows the false demonstrated mapping;
- late-layer false-induction mechanisms are implicated causally;
- semantic label choices such as `Positive/Negative` versus semantically uninformative `A/B` are explicitly compared.

This substantially owns the scientific distinction behind the proposed `inference survived, late label-following/verbalization failed` outcome.

A second central owner is **Tao, Chen & Liu, EMNLP Findings 2024, _Inference and Verbalization Functions During In-Context Learning_**, which already supplies the explicit inference→verbalization factorization and controlled layer-wise interchange intervention that L37 proposed to reuse.

Together, these owners create the fatal reviewer compression:

> false/permuted-label work already shows a truthful intermediate state followed by late override, and Tao et al. already provide the causal inference/verbalization decomposition; L37 mainly applies the latter instrument to a more explicitly anti-semantic label setting.

Recent follow-up work on shuffled meaningful labels, label-conditioned task representations, and in-context fixation further reduces the independent answer space.

## Why the old authorization is invalid

The original selection treated this as an unresolved bridge:

> arbitrary remapping preserves inference; anti-semantic labels fail behaviorally; therefore locate whether semantic conflict breaks inference or verbalization.

That is not enough. The correct novelty gate is whether the **strongest successful conclusion** is already substantially owned under different terminology or experimental framing.

For L37, the strongest positive result would be approximately:

> the model can represent the correct class before later label-following computation overrides it.

That conclusion is no longer independently novel enough for the target contribution.

## Final status

```yaml
status: ARCHIVED_NO_GO
authorization: REVOKED
pilot: NONE
reason: ANSWER_OWNERSHIP_COLLISION
central_missed_owner: HALAWI_ICLR_2024_OVERTHINKING_THE_TRUTH
method_owner: TAO_EMNLP_FINDINGS_2024_INFERENCE_VERBALIZATION
reviewer_compression: FATAL
resurrection: FORBIDDEN_WITHOUT_NEW_PAPER_IDENTITY
```

Do **not** execute the previously proposed `ANTI -> OPAQUE` interchange pilot under L37.

A future project about scale/training-dependent emergence of semantic-override ability would be a **new candidate** and must restart Search + Selection; it is not an authorized reconstruction of L37.