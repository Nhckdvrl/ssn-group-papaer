# L27 — Flat Effect Tuples ≠ Independent Evidence Units

**Status:** **SERIOUS SEED — OWNERSHIP / NATURAL-GOLD AUDIT — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## One-sentence RQ

> **Is a flat table of correctly extracted effect-size records sufficient for automated evidence synthesis, or does it erase design-induced dependence that determines how much independent evidence the records actually contain?**

## Plain example

A trial reports treatment A vs shared control C and treatment B vs the same control C. A flat extractor can perfectly recover two effect rows. But those two rows are not two independent experiments: they share participants/control information. Treating them as independent can give the study too much weight and understate uncertainty.

The same issue appears with cluster-randomized trials, crossover/repeated-measure designs, multiple outcomes from the same participants, and multiple effect sizes from one study.

## Scientific pressure

Two mature literatures meet here:

1. **LLM evidence extraction:** current work converts papers into role-aware study/effect records and already shows that binding the right variables/methods/numbers into tuples is hard.
2. **Meta-analysis/statistics:** correctly extracted effect sizes are still not sufficient if the synthesis ignores covariance, unit of randomization, shared controls, repeated participants, or other dependence structures. Unit-of-analysis errors can alter study weights, standard errors, confidence intervals, and p-values.

The candidate therefore asks whether the *output object* used by automated extraction is scientifically sufficient, not merely whether extraction accuracy is high.

## Prior work owns

- numerical and PICO/effect extraction from scientific papers;
- structural tuple-binding failures in LLM extraction;
- classical methods for cluster trials, shared controls, repeated outcomes, dependent effect sizes, and multilevel/multivariate meta-analysis;
- generic warnings that multiple reports/effects may be dependent.

## Potential unowned bridge

Whether **flat LLM-extracted effect schemas make valid downstream synthesis non-identifiable even when every atomic field is correct**, and what minimum design-aware representation restores identifiability.

This differs from K010 / L06: the dependence here is induced by experimental/statistical design, not copied sources or multiple publications of one study.

## Decisive operation

Find natural study/review cases where atomic effect tuples are correct but valid analysis differs because of design/dependence metadata. The cleanest test should hold atomic effect information fixed while varying or revealing:

- shared vs independent controls;
- participant overlap / repeated measures;
- cluster vs individual randomization;
- multiple dependent outcomes/effects.

If two scientifically different synthesis states collapse to the same flat representation, representation insufficiency follows without needing an LLM failure effect.

Then test whether full-text LLMs can reconstruct the missing dependence graph/design state and whether an explicit representation restores the correct synthesis decision.

## Successful-result test

- **Flat schemas lose load-bearing structure:** direct wrong-object diagnosis with downstream inference consequence.
- **Full-text models recover structure, flat schemas do not:** interface/schema bottleneck rather than capability failure; still strong.
- **Current structured extractors already preserve enough information:** preservation result only matters if we can specify a minimal sufficient representation and show why it works across design families.
- **Heterogeneous:** identify which study designs can safely collapse to flat tuples and which require relational/covariance structure.

The candidate does not need models to make many mistakes.

## Main blockers before pilot

1. Find a public paper-scale corpus pairing full text with authoritative design/dependence annotations or reproducible meta-analysis inputs.
2. Fresh direct-owner audit for design-aware LLM meta-analysis / covariance extraction.
3. Avoid expanding into the entire statistics of meta-analysis; the NLP object must be the sufficiency of the extracted evidence representation.
4. Make the downstream consequence executable/programmatic rather than author-judged.

## Kill conditions

- a recent paper already directly studies design/dependence-aware LLM extraction for meta-analysis and shows downstream synthesis effects;
- no scalable natural substrate can connect source text → dependence structure → valid analysis;
- the candidate reduces to generic `LLMs make extraction errors`;
- the only demonstration needs hand-built toy trials rather than natural scientific records.

## Anchor

- Tan & D'Souza, IRCDL 2026, *Diagnosing Structural Failures in LLM-Based Evidence Extraction for Meta-Analysis*: https://arxiv.org/abs/2602.10881
