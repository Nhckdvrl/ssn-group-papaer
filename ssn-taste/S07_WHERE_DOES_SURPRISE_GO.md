# S07 — Where Does Surprise Go?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  
**Target venues:** ACL / EMNLP / NAACL Main  
**Scientific type:** belief/model revision / epistemic credit assignment / controlled sequential inference

## 1. Stable parent question

When a language model encounters an observation that conflicts with what it expected, **what does it decide was wrong?**

The same prediction error can, in principle, be explained at different levels:

1. the **current world state** was misestimated;
2. the **observation process / source** was unreliable;
3. the **transition rule / dynamics model** governing how the world changes was wrong.

The stable parent question is:

> **How do language models allocate epistemic surprise across state, observation/source, and transition/rule revision?**

A shorter formulation is:

> **Where does surprise go?**

The object is not generic Bayesian reasoning, source-trust benchmarking, or changepoint detection. The object is the **locus of model revision after an ambiguous prediction error**.

## 2. Scientific pressure

Several strong recent lines establish the component abilities separately, without answering the revision-allocation question.

- *Large Language Models Develop Belief State Geometry In-Context* (2026) finds that open LLMs can represent and causally use near-Bayesian posterior belief states for HMM-like sequences when the generative process is fixed.
- *Information Discernment in Large Language Models* (2026) studies how models use source reliability and truth-direction information, and finds severe failures of source discernment.
- *In-Context Learning Under Regime Change* (2026) studies adaptation to changes in the underlying data-generating dynamics.

These literatures usually hold the other explanatory layer fixed. They therefore do not answer what happens when **one residual can be absorbed by multiple parts of the model**.

This is the scientific pressure behind S07:

> **A prediction error does not uniquely specify which part of the model should be revised.**

## 3. Competing worlds

### World A — State absorption

The model primarily treats anomalous evidence as information about the **current hidden state**.

Prediction: the anomaly strongly changes current-state belief, but after a trusted state reset its effect should largely disappear; trust in the source and beliefs about future transitions remain mostly unchanged.

### World B — Observation/source revision

The model treats the anomaly as evidence that the **observer/source is unreliable**.

Prediction: after the world state is reset or independently established, the anomaly continues to reduce the influence of future reports from the same source.

### World C — Transition/rule revision

The model treats the anomaly as evidence that the **world's dynamics/rule changed**.

Prediction: even after a trusted state reset, the anomaly changes predictions about how the state will evolve on the next transition.

### World D — History-sensitive joint credit assignment

The model can allocate surprise among the three levels according to prior history/precision rather than using one fixed default.

Prediction: the same anomalous observation leads to different persistent downstream fingerprints when prior histories make state uncertainty, source unreliability, or rule change differentially plausible.

World D is not “the desired answer”; a systematic bias toward A/B/C would also be a substantive finding.

## 4. Nearest-prior ownership boundary

S07 does **not** claim:

- first evidence that LLMs can perform Bayesian state inference;
- first evidence that source reliability matters;
- first evidence of changepoint/regime adaptation;
- first evidence that LLM belief updating is non-normative;
- first POMDP/world-model benchmark.

The surviving reviewer-level knowledge delta is:

> Existing work studies posterior state inference, source weighting, and dynamics adaptation largely as separate inference problems. S07 asks which **model component is revised when the same anomalous observation is compatible with more than one explanation**, and identifies the revision locus from its persistent downstream consequences.

If a direct prior is found that places state uncertainty, source/observation reliability, and transition uncertainty in one matched LLM experiment and identifies which component absorbs the same prediction error, the novelty claim must be re-audited.

## 5. Minimum pilot

Use one very small natural-language sequential world with:

- a binary hidden state;
- a simple, learnable transition rule;
- one named observer/source whose reliability can be learned from history;
- an occasional anomalous report.

The **anomalous report itself is held identical** across conditions. Only the preceding history changes which explanation is more plausible.

### Core sequence

1. Establish a short history of state transitions and source reports.
2. Present one report that conflicts with the model's current prediction.
3. Measure the immediate current-state belief.
4. Provide a **trusted state reveal/reset** that removes uncertainty about the present state.
5. Test two persistent consequences separately:
   - how strongly the model uses the **same source's next report**;
   - what state the model predicts after the **next transition** when no report is available.

This gives three distinct fingerprints:

- effect disappears after reset -> state revision;
- effect persists only in future same-source weighting -> source/observation revision;
- effect persists in transition prediction after reset -> dynamics/rule revision.

### Prior manipulation

Create matched histories that independently vary:

- confidence in the current-state prediction;
- earned reliability of the source;
- stability of the transition rule.

Include an ambiguous condition where all three explanations remain plausible.

The pilot should use log-probability or forced-choice readouts, not ask the model to verbally explain “what changed.”

## 6. Pilot discipline

- one open model first;
- tens to low hundreds of controlled sequences, not a benchmark;
- no training required;
- no large synthetic dataset;
- no explicit request for Bayesian arithmetic;
- one semantic instantiation is enough for go/no-go; a second surface realization is only a robustness check;
- primary result is the **revision fingerprint**, not deviation from an ideal posterior score.

## 7. What would count as knowledge gain?

- **State-dominant:** LLMs absorb surprise locally rather than revising generative assumptions; apparent adaptability may hide rigid source/dynamics models.
- **Source-dominant:** models preferentially explain contradiction by distrust, changing how later evidence is interpreted.
- **Rule-dominant:** models rapidly revise dynamics, potentially over-generalizing one anomaly into a regime shift.
- **History-sensitive allocation:** models perform a richer form of hierarchical epistemic credit assignment, revising different model components according to prior evidence.

Any stable asymmetry is scientifically meaningful because it predicts how later observations will be interpreted.

## 8. Claim boundary

Do not turn S07 into:

- another source-reliability benchmark;
- a changepoint-detection benchmark;
- a general “LLMs are/are not Bayesian” paper;
- a large POMDP evaluation;
- an agent-memory or RAG system;
- a terminology-transfer paper from active inference/control.

The stable object is **which explanatory layer absorbs prediction error and how that choice changes later inference**.

## 9. Promotion status

**PILOT-AUTHORIZED.**

The pilot is authorized because:

- the mother question is independent of any single trigger paper;
- state/source/rule revision are qualitatively different possible worlds;
- nearest priors establish the components but do not identify the same revision-allocation law;
- a single anomaly followed by reset/source/transition probes gives a small and direct identification strategy;
- the experiment need not become a benchmark or model zoo;
- all major outcomes provide interpretable knowledge gain.

---

## 2026-09-19 execution-risk re-audit — KEEP / PILOT-AUTHORIZED

S07 survives strongly. The key variables are manipulated at inference time in one controlled sequential world, and the trusted-reset/source-reuse/transition-prediction fingerprints directly separate revision loci. No training recipe is part of the causal claim.

### Tightened execution gate

Run one semantic instantiation first, but require the three diagnostic readouts to separate cleanly:

- immediate state belief;
- same-source influence after trusted state reset;
- next-transition prediction after reset.

**KILL immediately** if:
- reset does not actually isolate current-state uncertainty;
- source and transition fingerprints remain behaviorally inseparable;
- results are dominated by explicit lexical cues rather than history-dependent revision;
- the project starts requiring a large POMDP benchmark to make the effect visible.

A second surface realization is a robustness check only after a clean first signal.

**Final status: KEEP — PILOT-AUTHORIZED.**
