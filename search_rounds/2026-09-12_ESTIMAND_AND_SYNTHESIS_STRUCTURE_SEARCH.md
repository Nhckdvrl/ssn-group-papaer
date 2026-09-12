# 2026-09-12 — Estimand and Synthesis-Structure Search

**Target:** ACL / EMNLP / NAACL Main  
**Rule:** anti-resurrection first; combine multiple reliable literatures; no survivor quota; no compute authorization from this file.

## Serious seeds retained

### L26 — Same PICO ≠ Same Causal Question

**Status:** SERIOUS SEED — DATA / DIRECT-OWNER AUDIT — NO COMPUTE

**Question:** When LLM-assisted evidence synthesis treats trials as answering the same PICO question, does it preserve whether they actually target the same treatment effect / estimand, especially when intercurrent events are handled differently?

**Why this is a real scientific pressure:**
- the estimand framework defines the treatment question an estimate answers, rather than merely its endpoint or numeric result;
- a 255-trial systematic review found that the precise primary estimand was often not recoverable from trial reports, with handling of intercurrent events a major source of ambiguity;
- 2026 methodological work argues that PICO alignment is insufficient for meta-analysis because trials with overlapping PICO elements may target different estimands, changing heterogeneity and applicability;
- current LLM evidence-extraction / automated meta-analysis systems commonly organize evidence around PICO plus extracted numerical outcomes, making this a modern representation/inference question rather than a statistical-terminology quiz.

**Why not pilot yet:** paper-scale expert gold for estimand compatibility is not yet secured. The strongest 255-trial audit has expert adjudication but the row-level extraction data are not obviously released as a ready benchmark. A model-only competence test would be too weak.

**Successful-result space:** whether LLMs preserve estimand distinctions well, collapse them, or only fail under particular intercurrent-event strategies is informative if the downstream question is whether PICO-only evidence representations are sufficient for valid synthesis.

**References:**
- Kahan et al., BMJ 2022, *Evaluating how clear the questions being investigated in randomised trials are: systematic review of estimands*: https://www.bmj.com/content/378/bmj-2022-070146
- Remiro-Azócar et al., Research Synthesis Methods 2026, *Incorporating estimands into meta-analyses of clinical trials*: https://www.cambridge.org/core/journals/research-synthesis-methods/article/incorporating-estimands-into-metaanalyses-of-clinical-trials/6C71B547569F0580F75F438D636B7151

### L27 — Flat Effect Tuples ≠ Independent Evidence Units

**Status:** SERIOUS SEED — OWNERSHIP / NATURAL-GOLD AUDIT — NO COMPUTE

**Question:** Is a flat table of correctly extracted effect-size tuples sufficient for automated evidence synthesis, or can it discard sampling/design dependence that determines how much independent evidence is actually present?

**Scientific pressure:** modern LLM extraction work already shows that reliable role-aware effect tuples are hard to recover, but even perfect tuple extraction does not encode all synthesis structure. Classical meta-analysis distinguishes individual randomization, cluster randomization, crossover/repeated outcomes, shared-control multi-arm studies, and multiple dependent effects because treating dependent observations as independent changes standard errors, weights, confidence intervals, and sometimes conclusions.

**Not K010 / L06:** this is not copied-source dependence or multiple reports of one study. The dependence is induced by experimental/statistical design even when every source is genuine and every number is correct.

**Decisive operation:** find natural studies/reviews where the same visible atomic effect records require different valid synthesis because their covariance / randomization / shared-participant structure differs. If a flat schema makes those cases observationally identical, representation insufficiency follows even before asking whether an LLM fails.

**Why not pilot yet:** need a public paper-scale substrate pairing full text with authoritative design/dependence structure and downstream synthesis quantities; also need a fresh direct-owner search for design-aware LLM meta-analysis rather than generic numerical extraction.

**Reference anchor:** Tan & D'Souza, IRCDL 2026, *Diagnosing Structural Failures in LLM-Based Evidence Extraction for Meta-Analysis*: https://arxiv.org/abs/2602.10881

---

## Compact rejections

### Synthetic-persona marginal fidelity → joint fidelity — KILL
**Question:** Does matching official demographic marginals imply that a synthetic population preserves the real joint distribution?  
**Why not:** a 2026 paper directly owns the claim *Marginal Alignment Does Not Guarantee Joint-Distribution Fidelity* and audits synthetic personas against official references. Direct collision, and synthetic-population work is already crowded.

### Synthetic observational fidelity → intervention validity — DO NOT PROMOTE CURRENT FORM
**Question:** If an LLM-generated population matches observed people, can it be trusted to predict what happens under interventions?  
**Why not:** current social-simulation work already distinguishes observational realism from interventions and exposes intervention-induced latent changes/demand effects. The generic bridge is hot and currently too broad; no quiet, independently identified estimand was found in this pass.

### Semantic similarity → measurement equivalence / jingle-jangle — KILL
**Question:** Can semantically similar construct names/items be treated as measuring the same thing, and different names as different constructs?  
**Why not:** Wulff & Mata, Nature Human Behaviour 2025, already place psychometric items/scales/construct labels in LM embedding space, validate against empirical relations, and use the representation to diagnose taxonomic/jingle-jangle problems. The classical-problem→modern-LM bridge is already built.

Reference: https://www.nature.com/articles/s41562-024-02089-y

### Generic outcome-name harmonization for meta-analysis — KILL CURRENT FORM
**Question:** Are differently worded outcome labels actually measurements of the same outcome?  
**Why not:** LLM-driven outcome alignment/harmonization for automated meta-analysis is already a direct modern task, while the jingle-jangle literature owns the broader construct-equivalence bridge. Another semantic mapper is not a new parent.

### Noninferiority ≠ equivalence — DO NOT REOPEN
**Question:** Does a noninferiority result mean two interventions are equivalent?  
**Why not:** this is a narrow statistical-interpretation cousin of existing K140 (`No Significant Difference ≠ Evidence of Equivalence`) and risks becoming a textbook competence test whose paper value depends on models making the error.

### Legal holding / dicta / current authority — KILL CURRENT FORM
**Question:** Can an LLM distinguish text that appears in a judicial opinion from propositions that actually constitute controlling authority?  
**Why not:** 2026 legal-reasoning work explicitly centers ratio decidendi versus obiter dicta / bindingness, while precedent-aware RAG already models hierarchy, temporal validity, and negative treatment. The modern parent is crowded and system/harness dependent.

---

## Search takeaway

The most promising provenance pattern in this pass is:

> **A mature scientific field proves that a convenient representation is insufficient for valid inference → modern NLP automation adopts that convenient representation → ask whether the representation preserves the load-bearing scientific structure and show a downstream consequence.**

This is stronger than testing whether an LLM knows a classical distinction. The next search should transfer this origin pattern to quieter non-medical domains rather than continue generating neighboring clinical-statistics cells.
