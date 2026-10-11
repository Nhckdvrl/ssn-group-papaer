# L11 — Related Work and Paper-Level Novelty

**Candidate:** Task Gradient ≠ Learning Pressure  
**Freshness:** 2026-09-09

This file records the current ownership boundary. It should be refreshed whenever the central narrative changes.

---

## 1. Direct parent

Wu et al., Findings of EACL 2026  
**“Imbalanced Gradients in RL Post-Training of Multi-Task LLMs.”**  
https://aclanthology.org/2026.findings-eacl.164/

Owns:
- task-level gradient imbalance in multi-task LLM RL;
- evidence across multi-domain and same-domain mixtures;
- the mismatch between gradient magnitude and task learning gain;
- checks showing that simple reward/advantage/length statistics do not explain the whole gap;
- the high-level observation that task-specific optimization geometry can differ;
- motivation for gradient-level correction.

L11 must therefore start from:
> **the anomaly is known; its concrete LLM-level source and measurement meaning remain unresolved.**

---

## 2. Classic multi-task balancing

Chen et al., ICML 2018  
**GradNorm**  
https://proceedings.mlr.press/v80/chen18a.html

Owns:
- task gradient magnitude imbalance as a generic multi-task optimization problem;
- adaptive gradient normalization.

Therefore:
> unequal gradient norms are not new by themselves.

L11 must not be a renamed GradNorm paper.

---

## 3. Gradient conflict / surgery in LLM RL

Cai et al., 2026  
**“Advancing General-Purpose Reasoning Models with Modular Gradient Surgery.”**  
https://arxiv.org/abs/2602.02301

Owns:
- cross-domain interference;
- gradient-direction conflict;
- module-level surgery to reduce conflict.

Important distinction:
- **direction conflict** asks whether two task updates disagree;
- **magnitude/gain miscalibration** asks why one task is much louder and whether that loudness means more useful learning.

The project must preserve this distinction.

---

## 4. Curvature-aware multi-domain RL

ICLR 2026 work such as **Curvature-Guided Policy Optimization (CGPO)** uses task geometry/curvature to improve multi-domain RL.

Representative source:
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/f0bb0cc7cd2a027cff5f237f28def7eb-Abstract-Conference.html

This blocks a weak novelty claim such as:
> “different tasks have different curvature.”

Curvature can still be part of our explanation if it participates in a broader new empirical story about what task pressure means.

---

## 5. Gradient-based data selection

Findings of ACL 2026 work such as **LearnAlign** uses gradient alignment for RL data selection.

Representative source:
- https://aclanthology.org/2026.findings-acl.2009/

This owns:
- gradient structure as a data-selection signal;
- some normalization/confound awareness.

It does not by itself answer:
> **why cross-task gradient magnitude is misaligned with actual learning gain.**

---

## 6. Gradient norm as a training signal

Findings of ACL 2026 work such as **VIGOR** uses gradient-norm information as an intrinsic signal and explicitly handles length-related biases.

Representative source:
- https://aclanthology.org/2026.findings-acl.1606/

This makes the measurement question more consequential:
> if gradient norm is used to allocate learning, when is it comparable?

But L11 should not become only a critique or extension of VIGOR.

---

## 7. Broader optimization geometry

Natural-gradient / Fisher literature already tells us that raw Euclidean parameter-gradient magnitude is not a universally invariant quantity.

Therefore the following is not a sufficient contribution:

> “Parameter norm depends on parameterization.”

The new scientific work must connect the mismatch to a concrete language-model training mechanism or natural task/output structure and demonstrate the consequence empirically.

---

## 8. What can still be ours

The candidate’s current paper-level ownership is:

1. begin from the established multi-task gradient/gain paradox;
2. identify a concrete source of task optimization loudness in LLM policy-gradient computation;
3. distinguish raw parameter loudness from meaningful policy/function movement;
4. validate the explanation causally using a natural matched manipulation;
5. derive a consequence for task comparison, mixture construction, or training measurement.

Related work may own pieces of this chain. The full chain must remain recognizably ours.

---

## 9. Reviewer compression

### Attack: “Imbalanced Gradients + more plots”
Wins if the work stays descriptive.

### Attack: “GradNorm for RL”
Wins if balancing/performance is the main contribution.

### Attack: “Modular Gradient Surgery”
Wins if the center becomes gradient conflict.

### Attack: “Natural gradient in an LLM setting”
Wins if the final contribution is only a generic geometry fact.

A strong final paper needs its own scientific narrative, not an ingredient novelty claim.

---

## 10. Novelty flexibility

Do **not** over-kill the topic because a paper shares:
- a gradient metric;
- a task;
- a normalization trick;
- an optimizer;
- a curvature concept.

Do kill/reconstruct if one or a small number of papers can accurately compress the **entire final paper**:
> framing + decisive operation + central conclusion + consequence.

That is the repository’s authoritative paper-level novelty standard.

---

## 11. Current verdict

**PASS for pilot authorization, guarded by a fresh literature check before mainline promotion.**

The novelty corridor is real but should remain mechanism/measurement-centered.
