# L26 — Same PICO ≠ Same Causal Question

**Status:** **SERIOUS SEED — DATA / DIRECT-OWNER AUDIT — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## One-sentence RQ

> **When automated evidence synthesis decides that trials address the same PICO question, does it preserve whether those trials actually target the same treatment effect / estimand, or can it pool semantically similar studies that answer different causal questions?**

## Why this question exists

This is not created by an LLM benchmark. Trial methodology already distinguishes the treatment *question* from the observed endpoint and numerical estimate. Intercurrent events such as treatment discontinuation, rescue medication, or death can make two otherwise similar trials target different effects depending on how those events are handled.

A systematic review of 255 RCTs found that the precise primary estimand was often not recoverable from trial reports. In parallel, 2026 evidence-synthesis methodology argues that PICO alone can miss estimand incompatibility and that pooling different estimands can distort heterogeneity and applicability.

Modern LLM evidence synthesis makes the old issue newly consequential because systems commonly retrieve/match by PICO and then convert papers into structured outcome/effect records for downstream synthesis.

## Prior work owns

- estimands and intercurrent-event strategies in clinical trials;
- the inadequacy of PICO alone for some evidence-synthesis decisions;
- LLM extraction of PICO/outcomes/numerical trial results;
- generic automated meta-analysis and study matching.

## Potential unowned bridge

Whether **LLM-era semantic matching / structured extraction preserves treatment-question identity**, and whether adding estimand structure changes which studies are legitimately comparable or poolable.

The paper must stay on this representation/inference bridge. `Can GPT identify estimand labels?` is not enough.

## Decisive operation

Prefer natural expert-adjudicated trial pairs or review sets where PICO is closely aligned but the estimand differs because of intercurrent-event handling. Compare:

1. PICO-only / flat evidence representation;
2. full-document model judgment;
3. explicit estimand-aware representation;
4. authoritative compatibility / synthesis consequence.

The strongest version demonstrates that the omitted estimand information changes a legitimate synthesis decision rather than only a classification score.

## Successful-result test

- **Models collapse different estimands:** current evidence representations are scientifically insufficient; identify which attributes are lost and the downstream synthesis consequence.
- **Models preserve them from full text but PICO schemas lose them:** the diagnosis shifts from model competence to interface/schema insufficiency, still a strong paper.
- **Models preserve them reliably even under compressed schemas:** important preservation result only if it establishes which minimal representation is sufficient and changes how automated evidence systems should be designed.
- **Heterogeneous:** identify which intercurrent-event strategies or reporting regimes make treatment-question identity recoverable.

The paper must not require a dramatic raw error rate.

## Main blockers before pilot

1. Secure paper-scale natural/expert gold for estimand attributes and pairwise compatibility.
2. Fresh search for any 2025–2026 NLP/biomedical NLP paper that directly evaluates estimand-aware evidence synthesis.
3. Define a downstream synthesis consequence that is identified without inventing a normative pooling rule ourselves.
4. Keep the paper from collapsing into clinical statistical competence.

## Kill conditions

- no usable natural/expert gold without major bespoke annotation;
- a direct recent owner already evaluates PICO-vs-estimand compatibility in LLM evidence synthesis;
- the best outcome is only `LLMs sometimes misclassify estimand labels`;
- valid downstream pooling/compatibility cannot be determined independently of author judgment.

## Anchors

- Kahan et al., BMJ 2022, *Evaluating how clear the questions being investigated in randomised trials are: systematic review of estimands*: https://www.bmj.com/content/378/bmj-2022-070146
- Remiro-Azócar et al., Research Synthesis Methods 2026, *Incorporating estimands into meta-analyses of clinical trials*: https://www.cambridge.org/core/journals/research-synthesis-methods/article/incorporating-estimands-into-metaanalyses-of-clinical-trials/6C71B547569F0580F75F438D636B7151
