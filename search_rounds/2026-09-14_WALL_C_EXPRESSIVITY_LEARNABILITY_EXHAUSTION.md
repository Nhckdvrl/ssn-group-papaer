# 2026-09-14 — WALL-C / IP03 Expressivity → Learnability → Learned Algorithm Exhaustion Audit

**Target:** ACL / EMNLP / NAACL Main, calibrated against TACL / ICLR / ICML / NeurIPS / AAAI  
**Mode:** one-WALL historical reconstruction → theory-owner audit → same-quantity contradiction search  
**Result:** **WALL CURRENTLY EXHAUSTED FOR A PRACTICAL MAIN-LEVEL DESCENDANT — NO NEW L-SERIES — NO PILOT**

This does **not** mean the scientific problem is solved. The standing question remains fundamental:

> A Transformer can represent many computations. Why does gradient-based learning select one of them, and which representable computations are actually learnable and reusable?

The conclusion is narrower: the most natural descendants we can currently identify are already active theory programs, and the apparently strongest cross-paper tensions collapse because the papers study different complexity quantities or different input/output objects.

---

## 1. Historical mother problem

Formal expressivity is not a learning theory. A construction showing that a model *can* implement an algorithm does not imply that realistic training will find it, prefer it, or retain it OOD.

This gap has a long ancestry in learning theory, implicit regularization, minimum-description-length / flat-minima arguments, formal-language modeling, and more recent Transformer theory.

The relevant scientific chain is:

`representable computation -> geometry / optimization / data interaction -> selected computation -> generalization`

A good descendant would need a quantity that makes rival selection accounts disagree on the **same target computation**, not another architecture leaderboard or formal-language benchmark.

---

## 2. Major active selection theories found

### 2.1 Input-space sensitivity / parameter-space geometry

Hahn & Rofin, ACL 2024 Best Paper, *Why are Sensitive Functions Hard for Transformers?*, show that high input-space sensitivity implies isolated / sharp Transformer solutions, helping explain low-sensitivity bias and PARITY length-generalization failures.

A 2026 follow-up, *Understanding the Parameter Space Geometry of Transformers Encoding Boolean Functions*, pushes this program further: sensitive functions can occupy vanishingly small parameter-space regions and random initialization is unlikely to land near them.

**Implication:** `expressible but hard to learn because the solution is geometrically inaccessible` is already a direct theory program.

### 2.2 Globality / correlation structure

Abbe et al., NeurIPS 2024, *How Far Can Transformers Reason? The Globality Barrier and Inductive Scratchpad*, introduce globality as a learnability quantity distinct from formal expressivity and show particular scratchpads can break the barrier.

**Implication:** `reasoning target is expressive but globally unlearnable unless decomposed` is occupied.

### 2.3 Program simplicity / RASP-L / C-RASP

ICLR 2024 *What Algorithms can Transformers Learn?* relates length generalization to RASP-L program simplicity. Later work formalizes this further using C-RASP / limit-transformer frameworks.

Most directly, the July 2026 paper *From Expressivity to Sample Complexity: Narrow Teachers for Transformers via C-RASP* explicitly attempts to move from expressivity constructions to sample-complexity bounds.

**Implication:** `formal construction -> practical learnability` is now itself an explicit theory program, not an empty bridge.

### 2.4 Succinctness

Bergsträßer, Cotterell & Lin, ICLR 2026 Outstanding, *Transformers are Inherently Succinct*, replace binary expressivity with representation succinctness.

Zhao, Findings ACL 2026, *Do Transformers Grok Succinct Algorithms?*, immediately asks whether GD actually finds the predicted succinct counting circuit and reports a grokking / weight-norm complexity-collapse transition.

**Implication:** `succinct representability -> learned algorithm` already has a direct empirical successor.

### 2.5 Training-data geometry / diversity

Kawata et al., NeurIPS 2025, *From Shortcut to Induction Head*, prove a data-distribution phase transition: the same shallow Transformer selects a positional shortcut or an induction head depending on diversity of trigger distances.

**Implication:** `same architecture + same broad task, different training distribution -> different selected algorithm` is directly owned.

### 2.6 Initialization

Abbe et al., ICLR 2025, *Learning High-Degree Parities: The Crucial Role of the Initialization*, prove learnability of almost-full parities can reverse under different initialization distributions.

This does not produce a clean contradiction with the sensitivity theory; recent parameter-space geometry work makes initialization accessibility a natural part of the same broader explanation.

### 2.7 Optimizer implicit bias

NeurIPS 2025, *The Rich and the Simple: On the Implicit Bias of Adam and SGD*, proves that GD/SGD and Adam can favor qualitatively different feature solutions on the same problem: SGD is more simplicity-biased while Adam can learn richer nonlinear structure.

**Implication:** `optimizer chooses the learned function/feature complexity` is a mature ML parent.

### 2.8 Feature competition / gradient starvation

Pezeshki et al., NeurIPS 2021, *Gradient Starvation*, formally explains how learning one predictive feature can suppress gradients for other predictive features. Related representation-learning work shows easy features can suppress harder, more predictive features.

**Implication:** `early easy solution blocks later alternative algorithm/feature` is not a new Transformer law.

### 2.9 Pretraining as a learned architectural prior

NeurIPS 2025, *Born a Transformer — Always a Transformer?*, directly asks how theoretical architectural abilities appear after pretraining. It finds an induction/anti-induction asymmetry connected to circuit strength and shows targeted fine-tuning can remove some learned asymmetry without removing fundamental length-generalization constraints.

**Implication:** `architecture vs learned/pretraining bias` is already a direct object.

---

## 3. Attractive tensions that were killed

### 3.1 `Succinct but sensitive` is not itself a new contradiction

Hahn, Jurafsky & Futrell (TACL 2021) already explicitly note that sensitivity is orthogonal to Kolmogorov / description complexity. PARITY is the canonical example: very short description, very high sensitivity.

Therefore:

> `simple algorithm, but hard for Transformer`

is not a newly discovered paradox. It is an established construct split.

A project merely crossing two complexity metrics would reviewer-compress to a head-to-head benchmark of already-known non-equivalent notions.

### 3.2 `Short description vs parameter-space accessibility`

This looked deeper: perhaps the missing law is that algorithmic simplicity is distinct from how much parameter volume implements it.

But this is the old flat-minima / MDL / Bayesian-volume lineage, continued by modern sensitivity geometry. Hochreiter & Schmidhuber already linked flat regions to short weight descriptions; modern work formalizes flatness, parameter volume, and sensitivity-related accessibility.

**Verdict:** mature theory parent, not a clean new question.

### 3.3 `CoT makes high-sensitivity tasks learnable`

Initially attractive as a causal link:

`global high-sensitivity target -> sharp landscape -> stepwise low-dependence intermediates -> easier training`.

This is directly occupied:

- NeurIPS 2024 globality / inductive scratchpad;
- ICLR 2025 *From Sparse Dependence to Sparse Attention*, showing CoT turns parity learning from exponential to polynomial sample complexity by introducing sparse sequential dependencies;
- Kim & Suzuki parity-with-CoT theory;
- ICML 2025 lower bounds for CoT explicitly connect scratchpads to sensitive tasks such as PARITY;
- 2026 ICoT theory internalizes intermediate computations.

**Verdict:** direct parent collision.

### 3.4 `Initialization defeats sensitivity bias`

This initially looked like a contradiction: if sensitive solutions are inherently sharp, why can special initialization make full parity learnable?

But the 2025 initialization result plus 2026 parameter-space geometry naturally form one story: initialization changes whether optimization begins in/near the tiny relevant region. There is no clear same-quantity reversal of the sensitivity theory.

**Verdict:** not a contradiction.

### 3.5 `Shortcut selection is not intrinsic simplicity; data diversity flips it`

This is true but already mature. NeurIPS 2020 *Pitfalls of Simplicity Bias* emphasizes that the precise notion of simplicity is vague and that networks can overcommit to simple predictive features. AISTATS/NeurIPS work subsequently studies how data distribution and optimization alter simplicity bias. Kawata 2025 gives a Transformer-specific algorithm-selection law.

**Verdict:** old simplicity/feature-learning parent + direct Transformer owner.

### 3.6 `Easy algorithm learned first makes alternative algorithms unreachable`

This collapses to gradient starvation / feature suppression, already a mature learning-dynamics mechanism.

**Verdict:** not a new parent.

### 3.7 `LargeCounter grokking contradicts sensitivity theory`

This comparison fails the SAME-QUANTITY test. Succinct LargeCounter concerns compact representation of a recursive sequence/counter computation; Hahn–Rofin sensitivity concerns input-string-to-output behavior under a particular sensitivity definition and associated parameter geometry.

Without first showing that the **same LargeCounter input/output function** is high-sensitivity in the relevant theorem's sense, the apparent conflict is semantic only.

**Verdict:** no contradiction established; do not revive by analogy.

---

## 4. Why not propose a unified complexity metric?

The field already contains multiple quantities because they answer genuinely different questions:

- sensitivity;
- degree / globality;
- RASP-L/C-RASP program structure;
- representation succinctness;
- parameter-space sharpness / volume;
- predictive information / data structure;
- initialization alignment;
- optimizer-specific implicit bias.

A new `unified score` would need an independent scientific reason to exist and a theorem/empirical law showing that prior quantities fail on the **same tasks under the same learning setup**. We do not currently have that contradiction.

Without it, creating another metric would be method-first/theory-first novelty rather than question-first science.

---

## 5. Reviewer compression of likely descendants

> “Hahn & Rofin sensitivity geometry, but on another formal task.”

> “Globality / RASP-L / C-RASP with another notion of task complexity.”

> “Kawata’s algorithm-selection phase transition with another training knob.”

> “Zhao’s succinct-algorithm grokking on another algorithm.”

> “Gradient starvation / simplicity bias, instantiated inside a Transformer.”

> “Adam-vs-SGD implicit bias, but measuring circuits instead of features.”

> “Born-a-Transformer, but another pretraining-induced algorithm asymmetry.”

All of these are scientifically legitimate follow-ups; none currently gives us an independently owned Main-level parent.

---

## 6. Outcome robustness / feasibility problem

The remaining intellectually strongest question is something like:

> **Is there a common selection law predicting which representable computation gradient training will choose across naturalistic tasks?**

That is a genuine open problem, but it is:

- theorem-heavy;
- ML-owned;
- far broader than one ACL Main experiment;
- unlikely to be resolved by our compute budget or a small empirical pilot;
- highly vulnerable to becoming `yet another task-specific law` if narrowed.

Shrinking it until we can run it would violate the project rule demonstrated by L19: do not narrow a high-value question until it fits available compute/technical reach.

---

## 7. Anti-resurrection fence

Do not reopen IP03 merely because a new paper/task offers:

- another formal language;
- another optimizer;
- another initialization;
- another curriculum/data order;
- another RASP program;
- another grokking transition;
- a new mechanistic circuit;
- a new complexity metric;
- a new architecture family;
- a new claim that CoT makes a task easier.

Reopen only if one of the following appears:

1. **same-computation contradiction:** two mature selection theories make opposite predictions for the same target computation, architecture, data, objective, and optimizer;
2. **new natural estimand:** a quantity with independent meaning predicts algorithm choice across multiple natural computations and succeeds exactly where existing quantities disagree;
3. **regime change:** a new training regime invalidates a load-bearing premise of an established selection law, not merely changes its parameters;
4. **identifiable cross-task law:** a simple intervention produces a pre-specified algorithm-selection crossover across qualitatively different tasks that no current local theory predicts.

---

## 8. Final state

**NO NEW L. NO PILOT. WALL-C/IP03 CURRENTLY EXHAUSTED FOR THIS SEARCH.**

The scientific problem remains one of the strongest in modern model science, but the accessible descendant space is currently too densely occupied by active 2024–2026 theory programs. The correct action is to preserve the standing problem and wait for a genuine contradiction or new identifying leverage, not manufacture another local law.
