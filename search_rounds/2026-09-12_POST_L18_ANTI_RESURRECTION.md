# Post-L18 Search — Anti-Resurrection Record

**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main  
**Rule:** no survivor quota; record serious rejections and duplicate hits before further search.

This round exposed a process failure: several plausible leads were generated before the killed ledger was checked. Two of them were already explicitly closed parents. `RESEARCH_TOPIC_SEARCH.md` is therefore updated so anti-resurrection precedes lead generation rather than following it.

## Existing kills hit again — do NOT allocate new K IDs

### Duplicate hit: K010 — Dependent/copied-source corroboration

Reconsidered lead:

> Three reports independently supporting X should count differently from three reports copied from one source; does an LLM/RAG system model evidence dependence/provenance rather than count mentions?

This is already K010. The ledger explicitly closes dependent/copied-source corroboration because 2026 RAG work studies copied/dependent evidence being counted as independent support.

**Decision:** duplicate hit on **K010**. Do not reopen by adding provenance metadata, a newer RAG model, or a cleaner dependent-source construction unless a qualitatively different scientific quantity is identified first.

### Duplicate hit: K062 — NIL-Aware Generative Entity Linking

Reconsidered lead:

> A model may know that a real-world entity exists today even though that entity is absent from the target 2019 KB; can it distinguish real-world existence from membership in the specified KB version?

This is still a KB-coverage / NIL-prediction problem. K062 explicitly says not to reopen with another KB-coverage/NIL formulation. BLINKout/NIL-style versioning and emerging-entity work reinforce the collision.

**Decision:** duplicate hit on **K062**. A historical KB version is not by itself new scientific leverage.

## New serious rejections from this round

These are anti-resurrection records for future search. The central point is the dead scientific parent, not the exact title used during exploration.

### L18 — Contextual Entrainment × Word-Meaning Priming Causal Identity

**Status:** KILL CURRENT FORM  
**Primary:** `PAPER_SCALE_FAILURE`  
**Secondary:** `CROWDED_PARENT`, `DECISIVENESS_FAILURE`

RQ:

> Is lexical-specific word-meaning priming causally carried by the same machinery as blind contextual token entrainment, or are they separate contextual-adaptation processes?

Why killed:
- word-meaning priming behavior is already established;
- contextual entrainment and causal entrainment heads are already established;
- 2026 work further separates lexical-form/sense effects, prior-occurrence retrieval, semantic versus mechanical entrainment, and context-dependent sense reinterpretation;
- even the strongest positive result — ablating entrainment heads reduces meaning priming — establishes shared contribution, not causal identity of the two computations.

Reviewer compression:

> “Published word-meaning priming crossed with published contextual-entrainment ablation after lexical/semantic repetition mechanisms have already been factorized.”

**Reopen only if:** a new operation can establish a larger causal law that cannot be reduced to overlap/mediation between two already-owned phenomena.

### Batch Randomness as Online Quota Balancing

**Status:** KILL  
**Primary:** `NOVELTY_PARENT_COLLISION`  
**Secondary:** `CROWDED_PARENT`

RQ:

> When an LLM produces a batch that matches a target distribution better than repeated one-shot calls, is it sampling, or actively balancing the visible prefix to make the list look random?

Why killed:
- ACL 2026 makes batch-versus-independent random generation salient;
- earlier subjective-randomness work already analyzes LLM sequences through running-average / higher-order Markov structure and reproduces streak suppression with a window-average mechanism;
- negative lag-1 autocorrelation / gambler's-fallacy-like behavior is already documented.

Reviewer compression:

> “Existing LLM subjective-randomness control law applied to the newer dice benchmark.”

### Whole-Correct / Atom-Wrong NLI as a New Measurement Object

**Status:** KILL CURRENT FORM  
**Primary:** `NOVELTY_PARENT_COLLISION`  
**Secondary:** `CROWDED_PARENT`, `OUTCOME_FRAGILITY`

RQ explored:

> If the whole NLI hypothesis is correct while a necessary atomic probe is wrong, is the whole answer non-compositional, or did atomization change the inference problem by stripping context?

Why killed:
- atomic NLI/decomposition is already a direct modern object;
- decomposition/decontextualization work already establishes that fully atomic claims can lose needed context and alter evaluation;
- Atomic Inference already composes atomic predictions into whole labels;
- a positive non-compositional result is interesting, but the opposite outcome collapses to the already-crowded “isolated atom probes underestimate contextual competence” parent.

**Do not reopen** by changing the critical-atom perturbation unless the operation identifies a qualitatively new inference beyond decomposition validity/compositionality.

### Source-Aware vs Draft-Only LLM Translation Refinement

**Status:** KILL  
**Primary:** `NOVELTY_PARENT_COLLISION`

RQ:

> During translation refinement, is the LLM genuinely rereading the source to repair adequacy, or mainly polishing the draft toward its own target-language distribution?

Why killed:
- classic automatic post-editing already directly compares source-aware and target-only refinement;
- the established result is essentially the strongest result we could hope for: target-only improves fluency, while source access is needed for adequacy improvements.

Reviewer compression:

> “Classic source-aware APE repeated with modern LLM refinement.”

### Multi-Turn Temporal Scope: Lost State vs Current-Knowledge Override

**Status:** KILL CURRENT FORM  
**Primary:** `PAPER_SCALE_FAILURE`  
**Secondary:** `CROWDED_PARENT`, `L12_FAILURE_MODE`

RQ:

> When a historical time established in turn 1 is omitted in later turns and the model drifts back to the present, did it lose the discourse temporal state or retain it but fail to use it against current-world priors?

Why killed:
- ChronoScope already frames the failure as correct knowledge bound to the wrong temporal frame and shows explicit temporal restatement can recover performance;
- the remaining natural route is probe/patch “representation present but unused,” which is exactly the representation-versus-use/readout failure mode already learned from L12;
- no independent decisive operation was found that creates a new scientific object.

### Semantic Leakage as Entity/Feature Binding Failure

**Status:** KILL CURRENT FORM  
**Primary:** `CROWDED_PARENT`  
**Secondary:** `PAPER_SCALE_FAILURE`

RQ:

> Does semantic leakage follow associative activation regardless of discourse owner, or arise because the model binds an activated feature/value to the wrong entity or slot?

Why killed:
- semantic leakage / irrelevant-information sensitivity is already crowded;
- transformer entity/relational binding now has mature mechanistic accounts and causal interventions, including binding IDs, ordering IDs, and relational-cell style representations;
- combining the two leaves a narrow bridge: “this leakage instance is a known binding failure.”

Reviewer compression:

> “Semantic Leakage + existing entity-binding mechanism.”

### Table DRE: Wrong Cell Retrieval vs Value Contamination During Reasoning

**Status:** KILL CURRENT FORM  
**Primary:** `CROWDED_PARENT`  
**Secondary:** `PAPER_SCALE_FAILURE`

RQ:

> When a table reasoner references the wrong value, did it fail to retrieve the correct cell, or retrieve it and then corrupt/bind the value incorrectly during later reasoning?

Why killed:
- the mother error is real, but cell selection, cell-level rationale, faithful TableQA auditing, structured attribution, and value/entity binding are already active objects;
- the proposed mechanism decomposition reviewer-compresses to applying existing evidence-selection/value-binding tools to the DRE failure taxonomy.

### Coherent World Update / Dependency-Directed Belief Contraction

**Status:** KILL  
**Primary:** `NOVELTY_PARENT_COLLISION`

RQ explored:

> When a premise is replaced or withdrawn, can an LLM retract exactly the conclusions that depended on it while preserving unrelated beliefs, rather than locally patching one fact?

Why killed:
- TRACK/MQuAKE and knowledge-update work already cover propagation/interdependence;
- more decisively, ICLR 2026 AGM-Bench directly operationalizes AGM and iterated belief revision, including Preservation/Inclusion-style failures.

Reviewer compression:

> “AGM-Bench belief revision/preservation with another dependency graph.”

### Surface Contamination vs Semantic Memorization

**Status:** KILL CURRENT FORM  
**Primary:** `CROWDED_PARENT`

RQ explored:

> Does benchmark contamination require recognizable surface form, or does semantically equivalent rephrasing/cueing still retrieve memorized evaluation content?

Why killed:
- 2026 contamination work already separates surface matching from semantic/cue-controlled memorization and studies memorization beyond literal overlap.

**Do not reopen** with another paraphrase family unless it changes a downstream scientific conclusion rather than adding a detection cell.

### Scientific-Summary Population/Scope Generalization

**Status:** KILL CURRENT FORM  
**Primary:** `NOVELTY_PARENT_COLLISION`  
**Secondary:** `CROWDED_PARENT`

RQ explored:

> Does an LLM turn a result established for a bounded population/condition into an unrestricted claim when summarizing scientific evidence?

Why killed:
- PICO/scope factuality and scientific generalization-bias work already directly studies population/scope overgeneralization in generated scientific/biomedical claims.

### Reasoning Trap Follow-Up: Feasibility Recognition vs Action Licensing

**Status:** KILL CURRENT FORM  
**Primary:** `CROWDED_PARENT`  
**Secondary:** `PAPER_SCALE_FAILURE`

RQ explored:

> When reasoning makes a model call an unavailable or inappropriate tool, did it fail to recognize that the task/tool configuration was infeasible, or recognize the constraint and nevertheless license an impossible action during planning?

Why killed:
- ACL 2026 *The Reasoning Trap* already establishes increased tool hallucination under reasoning enhancement, including same-weight Qwen3 Think-On/Off effects;
- 2026 *Do Agents Know What They Can't Do?* directly studies feasibility awareness under removed critical tools and whether agents recognize infeasibility and stop;
- 2026 *Looking Is Not Picking* directly separates attending to the correct tool from selecting it and localizes many failures to decision readout rather than recognition;
- the surviving cross — when reasoning changes feasibility recognition versus action selection — is not obviously owned verbatim, but reviewer-compresses to combining three already-established axes rather than a new scientific object.

Reviewer compression:

> “Reasoning Trap’s Think-On effect + FeasiGen feasibility awareness + Looking-Is-Not-Picking decision readout.”

**Reopen only if:** a qualitatively new intervention establishes a general law about reasoning-induced action licensing that predicts behavior beyond tool selection/feasibility and cannot be reduced to recognition-versus-readout.

## Investigated but NOT killed / NOT pilot-authorized yet

These should not be mistaken for survivors. They remain unresolved leads only and require a fresh anti-resurrection + ownership pass before any pilot:

1. **Temporal forgetting during training:** strong checkpoint-level learn→forget→relearn phenomenon, but no discriminating operation beyond generic interference/optimization accounts has yet survived review. No pilot authorized.
2. **ICRL local credit assignment:** whether scalar rewards are bound to the action/step that caused them versus used as trajectory-quality labels. Direct bandit ICRL explanations already remove the broader “is reward really RL?” framing. No pilot authorized.

## Search procedure change made in this round

`RESEARCH_TOPIC_SEARCH.md` now requires an anti-resurrection check **before** lead generation/deep search:

> scientific object + estimand + decisive operation + synonyms → search `KILLED_LEDGER` / archived candidates / relevant `Interpretability-try` history → if matched, write `Not KXXX because ...` or discard.

This is specifically intended to prevent the two duplicate hits above (K010 and K062) from recurring under new wording.
