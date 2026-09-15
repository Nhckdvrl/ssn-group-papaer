# 2026-09-15 — Searcher Recalibration and Wall Audit II

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS / AAAI  
**Mode:** problem-creator search; candidate generation disabled until the Layer-1 question survives  
**Outcome:** **0 new L-series; 0 new pilot authorization.**

This round does **not** interpret zero survivors as evidence that the landscape is empty. The main result is a sharper searcher: several initially attractive questions were closed at the mother-program level, while one pre-existing WATCH gained substantial independent support but simultaneously became **more owner-dense**, not more ready to pilot.

---

# 1. Fresh taste calibration: what changed in the searcher

The round began from strong 2025–2026 papers and award commentary, asking what research move made the work strong rather than copying topics.

Key calibration examples included:

- ACL 2026 Best Paper **Memory Efficiency and Resource-Rational Encoding in Sentence Processing**;
- ACL 2026 Outstanding **Systematicity between Forms and Meanings across Languages Supports Efficient Communication**;
- ACL 2026 **Which Reasoning Trajectories Teach Students to Reason Better? A Simple Metric of Informative Alignment**;
- ICLR 2025 **From Sparse Dependence to Sparse Attention: Unveiling How Chain-of-Thought Enhances Transformer Sample Efficiency**;
- ICML 2024 **The Pitfalls of Next-Token Prediction**;
- NeurIPS 2025 **On the Bias of Next-Token Predictors Toward Systematically Inefficient Reasoning: A Shortest-Path Case Study**;
- NeurIPS 2025 **From Shortcut to Induction Head: How Data Diversity Shapes Algorithm Selection in Transformers**;
- ICML 2026 Honorable Mention **To Grok Grokking: Provable Grokking in Ridge Regression**;
- classical **algorithmic alignment** work, especially **What Can Neural Networks Reason About?**;
- 2026 PAC-style theory of autoregressive reasoning sample complexity.

The important additions to search taste are below.

## 1.1 New provenance: learner-/resource-relative scientific quantities

A quantity that looks like an intrinsic property of the object may actually be a property of:

> **object × learner × resource regime**.

ACL 2026 provides two useful examples.

**Memory Efficiency** does not treat limited memory as generic degradation. It makes memory precision a resource constraint and shows that optimal allocation changes the *kind* of representation that emerges: more compressed and categorical context representations.

**Systematicity** replaces a coarse simplicity notion with learnability of the meaning-to-form mapping. The scientific quantity therefore depends on what a learner can acquire, not just on inventory size or description length.

Transferable search question:

> Are we treating difficulty / complexity / simplicity / efficiency as intrinsic when the relevant scientific object is learner-relative or resource-relative?

This is a provenance lens, not a topic template. The repository already has IP03/IP04/IP06 occupying the broad standing problems.

## 1.2 New provenance: minimal-model / de-specialization test

ICML 2026 Honorable Mention **To Grok Grokking** is a useful search move. Instead of adding another deep-network mechanism for grokking, it asks whether the supposedly exotic phenomenon already appears in ridge regression. It does, with provable two-stage dynamics.

Transferable move:

> Before explaining an apparently LLM-/deep-network-specific phenomenon with a complicated internal mechanism, ask whether a minimal linear / classical model already exhibits it.

If yes, the explanation level should move downward: optimization geometry, factorization, statistics, or measurement may be the scientific object.

This is especially important for preventing the searcher from turning every striking modern anomaly into a mechanistic-interpretability sequel.

## 1.3 New provenance: anomaly-validity audit before mechanism

A strong anomaly is only as strong as the construct that defines it. In semantics, cognition, and evaluation-heavy work, a surprising result can disappear if the supposed gold inference is not actually determined by the stimulus/theory.

Therefore before asking:

> “Why does the model show X?”

first ask:

> “Is X actually the scientific phenomenon we think it is, or did a linking assumption / label / task format create it?”

This is **not** a license for benchmark-audit papers. It is a protection against spending a month mechanismizing an artefact.

## 1.4 Search lens: factorization/interface-relative learnability

The same input-output function can become a different learning problem depending on how the computation is factorized into autoregressive steps, what intermediate states are supervised, and how outputs are serialized.

This looks promising as a *search lens*, but this round found that it is already adjacent to several mature theoretical programs. It must not be promoted merely because the phrase sounds new.

---

# 2. WALL audit

The goal was not to generate fifty candidates. Each wall was entered at the mother-question level and closed rather than shrunk when the mother program was already owned.

## W1 — Is “amount of training data” the wrong quantity?

### Layer-1 question

> If two corpora contain the same number of tokens but radically different redundancy / information, why should token count be the scientific measure of data scale?

### Pressure

Scaling laws and training prescriptions often speak in tokens/examples, while duplicates, noise, and correlations change effective information.

### Audit

This is already a direct active program: recent scaling-law work explicitly introduces data quality, redundancy, effective sample size, and related information-sensitive quantities.

### Decision

**CLOSE AS CURRENT TOPIC GENERATOR.**

Do not rename `effective information`, `effective tokens`, or `independent evidence` and reopen. The mother-level quantity rewrite is already owned.

---

## W2 — Do resource constraints create qualitatively different algorithms/representations?

### Layer-1 question

> Does restricting memory / context / compute merely make a learner worse, or can it systematically change what representation or algorithm is learned?

### Pressure

The default engineering expectation is monotone resource benefit. Resource-rational work predicts structured reorganization rather than simple degradation.

### Audit

This is already **IP04** in the standing portfolio, and ACL 2026 strengthens it rather than creating a new paper opening.

### Decision

**KEEP AS ACTIVE STANDING PROBLEM; NO CANDIDATE.**

A future project needs a natural resource constraint plus a theory predicting a qualitative reorganization. Another bottleneck/noise ablation is not enough.

---

## W3 — What determines which equivalent computation an autoregressive learner actually learns?

This wall began from the existing WATCH:

> `local predictability vs global execution efficiency`.

The important update is that it now has **multiple independent lineages**, but also much higher owner density.

### 10-second question

> **When multiple algorithms compute the same function, what determines which one an autoregressive learner actually learns?**

### Pressure

Expressivity says both algorithms are representable. Classical runtime complexity says which algorithm is efficient *after it is known*. Neither necessarily predicts which computation gradient-based autoregressive training can discover from finite data.

### Convergent evidence

#### A. NeurIPS 2025 — inefficient shortest-path reasoning

**On the Bias of Next-Token Predictors Toward Systematically Inefficient Reasoning** compares optimal bottom-up dynamic-programming traces with longer valid backtracking traces under the same training-token budget. The longer traces generalize better. Arbitrary redundancy does not reproduce the benefit; generalization correlates with confidence in next-token prediction.

This is the strongest direct evidence for the original WATCH hypothesis:

> globally worse execution can be locally easier to model.

But it is still one controlled shortest-path setting.

#### B. ICLR 2025 — CoT changes sample complexity via dependency structure

**From Sparse Dependence to Sparse Attention** shows that CoT can reduce parity-learning sample complexity from exponential to polynomial even when expressivity is already sufficient. The proposed reason is that CoT decomposes the target into sparse sequential dependencies.

This establishes that a computation's **factorization into learnable dependencies** can matter even when capacity is not the bottleneck.

#### C. ICML 2024 — teacher forcing creates a distinct local-prediction failure

**The Pitfalls of Next-Token Prediction** separates inference-time autoregression from teacher-forced training and gives a minimal planning task where teacher forcing permits a locally successful but globally useless solution.

This is not the same phenomenon as shortest-path inefficiency, but it independently says:

> local next-token fit is not equivalent to learning the desired global computation.

#### D. NeurIPS 2025 — data distribution selects the learned algorithm

**From Shortcut to Induction Head** proves a transition between a positional shortcut and an induction-head algorithm as a function of the training distribution's diversity. Two representable solutions exist; the distribution determines which gradient training selects.

This strongly supports the broader standing question while weakening any attempt to tell a one-factor `local predictability alone` story.

#### E. ACL 2026 — trajectory suitability is learner-relative

**Which Reasoning Trajectories Teach Students to Reason Better?** finds that stronger-teacher trajectories need not teach better students and proposes Rank–Surprisal Ratio, combining student-relative alignment and informativeness. Across five students and 11 teachers it reports average Spearman 0.86 with downstream reasoning performance.

Again, this is not an algorithm-selection law, but it shows that the usefulness of a reasoning trace is partly a property of the *learner–trace pair*.

#### F. PAC/online autoregressive-learning theory is emerging

2026 theory studies the sample complexity of learning autoregressive computations under final-answer versus full-chain supervision. Full CoT supervision can remove generation-length dependence that appears under end-to-end supervision in the analyzed regimes.

Thus `autoregressive learnability` itself is no longer an untouched conceptual space.

### The decisive owner collision: algorithmic alignment

The broadest tempting formulation is **not new**.

**What Can Neural Networks Reason About?** already asks why equally expressive network structures have different generalization/sample complexity and defines **algorithmic alignment** between network computation structure and the reasoning algorithm. Better alignment yields better sample-complexity bounds.

Therefore we must not claim novelty for:

> “Which of two algorithms is easier for a neural network to learn?”

The 2025–2026 autoregressive results update the regime, but `algorithm learnability` has a real intellectual parent.

### Current state

**WATCH+ / IMPORTANT — CONVERGENT EVIDENCE, NO ATTACK YET.**

This is a genuine upgrade from the previous state. It is no longer a shortest-path curiosity supported by one lineage. But that does **not** authorize a paper.

A better standing formulation is:

> **Autoregressive learnability of equivalent computations:** what property of an algorithm's factorization/dependency structure predicts whether next-token training will select and generalize it?

The old phrase `local predictability vs global execution efficiency` should now be treated as **one live hypothesis**, not the title or conclusion.

### What would actually unlock a project

Do not pilot merely by inventing a second synthetic algorithm family.

A future route should require at least one of:

1. a **single, independently motivated quantity** that predicts algorithm selection across genuinely different task families, beating existing alignment / likelihood / horizon / diversity explanations out of sample;
2. a **natural foundation-model phenomenon** where two independently identifiable computations solve the same task and existing theories make conflicting predictions;
3. a theorem or counterexample showing that a currently load-bearing quantity (algorithmic alignment, trace likelihood/surprisal, horizon, dependency sparsity, etc.) is systematically insufficient in the autoregressive regime.

Until then, remain WATCH.

### Forbidden next moves

- another shortest-path variant;
- `DP vs backtracking` on a new graph distribution;
- making traces longer/shorter and calling length the variable;
- `Paper A sparse dependence + Paper B shortest path = our theory`;
- inventing a new scalar on synthetic tasks and only checking in-distribution correlation;
- interpreting any next-token-confidence correlation as causality;
- immediately designing patching/probes to locate the bias.

---

## W4 — Is task difficulty representation/serialization-relative rather than intrinsic?

### Question

> Can the same underlying problem become easy or hard solely because the representation changes the dependencies the learner must acquire?

### Audit

This is scientifically real but broad, and current work already studies presentation order, tokenization/vocabulary, structured serialization, CoT decomposition, and representation-dependent generalization. It is also partly a restatement of IP03 and W3.

### Decision

**DO NOT CREATE A SEPARATE CANDIDATE.**

Use representation-relative difficulty as a search lens inside IP03/W3. Do not paperize the generic claim.

---

## W5 — Is reasoning-token count the wrong measure of inference-time compute?

### Question

> Do 10,000 generated tokens represent 10,000 units of useful computation?

### Audit

2025–2026 reasoning work already separates token length from useful depth/breadth/effective computation and actively proposes alternative allocation and accounting schemes.

### Decision

**CLOSE AS CURRENT TOPIC GENERATOR.**

This is an attractive wrong-quantity question whose mother surface is already mature.

---

## W6 — Does supervision granularity choose the learned algorithm?

### Question

> Does SFT/process supervision/RL improve reasoning because it teaches a different computation, rather than merely improving the same capability?

### Audit

Direct current programs already compare supervision regimes, algorithmic behavior, sample efficiency, exploration, and policy support. Combined with W3's owner map, this route quickly becomes a successor factorial.

### Decision

**CLOSE.**

Do not turn SFT-vs-RL into the experimental instantiation of W3 merely because checkpoints are accessible.

---

## W7 — Can passive next-token prediction identify what matters for action/planning?

### Question

> If two latent states predict the same passive observations but imply different actions, can passive prediction alone learn the distinction needed for planning?

### Audit

This is a deep standing issue, but causal-world-model / passive-vs-active / token-predictor-vs-planner work now forms a direct program.

### Decision

**CLOSE AS CURRENT TOPIC GENERATOR.**

Do not shrink to another toy POMDP or causal-state cell.

---

## W8 — Does KL divergence actually measure “stay behaviorally close” in RLHF?

### Question

> If two token distributions have small/large KL, does that mean the policies are semantically or behaviorally close/far in the way alignment relies on?

### Audit

The question has excellent wrong-quantity taste, but 2026 semantic-aware Wasserstein regularization work directly attacks the token-index KL limitation and proposes semantic transport-based alternatives.

### Decision

**CLOSE.** Direct quantity owner.

---

## W9 — Does a scalar reward model imply a coherent scalar preference?

### Question

> When human preferences are contextual, multidimensional, or cyclic, what justifies treating them as samples from one transitive scalar utility?

### Pressure

Scalar reward models inherit strong utility-representation assumptions that are easy to forget once preference learning becomes an engineering pipeline.

### Audit

This is a very good old-assumption-under-modern-regime question, but the mother issue is already explicit in modern RLHF theory/practice discussions and recent cyclic-preference / beyond-scalar reward work.

### Decision

**CLOSE AS CURRENT TOPIC GENERATOR.**

Keep as an example of a good search provenance whose project surface is occupied.

---

## W10 — What linking hypothesis lets LMs serve as scientific models of human language?

### Question

> When does an LM result genuinely bear on a theory of human learning/processing rather than merely reproduce a human behavioral pattern?

### Pressure

LMs permit exact training histories and interventions impossible in humans, but behavioral similarity alone does not identify shared mechanism or pressure.

### Audit

This is already repository **IP07** and is now an explicit live debate in linguistics/cognitive science. Recent work directly questions whether perplexity/sample-efficiency/behavioral matching are valid linking variables for human claims.

### Decision

**KEEP AS ACTIVE STANDING PROBLEM; NO CANDIDATE.**

A future project needs one concrete, load-bearing linking claim whose failure changes how a substantive literature is interpreted. Generic `human vs LM` comparison remains banned.

---

# 3. Searcher diagnosis after this round

The main scarcity is **not important mother problems**. This round easily found important questions:

- what is effective data;
- how resource constraints shape representation;
- what makes one computation learnable;
- whether difficulty is representation-relative;
- what counts as inference-time compute;
- whether passive prediction yields action-relevant state;
- whether KL is the right behavioral distance;
- whether scalar rewards represent preference;
- when LMs bear on human-language theory.

The scarcity is:

> **an unowned, consequential uncertainty for which modern foundation-model work provides genuinely new leverage without shrinking the mother problem into a leftover cell.**

This is exactly why zero survivors is acceptable here.

The searcher should therefore make two corrections.

## Correction A — do not confuse evidence convergence with paper availability

W3 is the clearest example. Independent evidence made the standing problem *more credible*, but the same convergence revealed a theory program and reduced open ownership.

> More evidence for the mother problem can make a new paper **less** available.

## Correction B — perform explanation-level checks before mechanistic descent

Before saying `stable anomaly -> internal mechanism`, ask:

1. Is the anomaly's construct valid?
2. Does a minimal/classical model already reproduce it?
3. Is there an old theory that already names the mother quantity?
4. Is the phenomenon actually a consequence of factorization/optimization/measurement rather than an LLM-specific representation?

Only descend into hidden mechanisms after these checks survive.

---

# 4. Portfolio update

**New L-series:** 0  
**New pilot authorization:** 0

### Standing WATCH update

Upgrade:

> `local predictability vs global execution efficiency`

from a weak shortest-path-supported WATCH to:

> **WATCH+ — Autoregressive learnability of equivalent computations**

with `local predictability` retained as one hypothesis.

Reason for upgrade:

- shortest-path evidence;
- sparse-dependence CoT theory;
- teacher-forcing failure theory;
- data-diversity-driven shortcut/algorithm selection;
- learner-relative trajectory suitability;
- emerging PAC theory of autoregressive reasoning.

Reason **not** to promote:

- classical algorithmic-alignment ownership;
- current autoregressive learnability is already an active theory surface;
- no single new quantity yet makes cross-family predictions;
- a second synthetic task would be breadth, not a scientific reframing.

### No resurrection

This round does not reopen scaling-law origins, predictive-state/world-model identifiability, process supervision, update scope, minimal grounding, positional memory, or other mother programs closed in earlier rounds.

---

# 5. Source anchors

- ACL 2026 Best Paper Awards: https://2026.aclweb.org/program/best_papers/
- Xu, Dillon & Futrell, ACL 2026, *Memory Efficiency and Resource-Rational Encoding in Sentence Processing*: https://aclanthology.org/2026.acl-long.1550/
- Osmelak et al., ACL 2026, *Systematicity between Forms and Meanings across Languages Supports Efficient Communication*: https://aclanthology.org/2026.acl-long.1340/
- Yang et al., ACL 2026, *Which Reasoning Trajectories Teach Students to Reason Better?*: https://aclanthology.org/2026.acl-long.1950/
- Wen et al., ICLR 2025, *From Sparse Dependence to Sparse Attention*: https://proceedings.iclr.cc/paper_files/paper/2025/hash/fa6d4d2020aac4bd8f7cdb2771fc1ae2-Abstract-Conference.html
- Bachmann & Nagarajan, ICML 2024, *The Pitfalls of Next-Token Prediction*: https://proceedings.mlr.press/v235/bachmann24a.html
- Alberghi et al., NeurIPS 2025, *On the Bias of Next-Token Predictors Toward Systematically Inefficient Reasoning*: https://proceedings.neurips.cc/paper_files/paper/2025/hash/090298ec38fee9b8ced6dad1e1c3a7d8-Abstract-Conference.html
- Kawata et al., NeurIPS 2025, *From Shortcut to Induction Head*: https://proceedings.neurips.cc/paper_files/paper/2025/hash/6499b639e8a4b5c9a780d9b88c09722f-Abstract-Conference.html
- Hanneke, Mehalel & Moran, 2026, *Sample Complexity of Autoregressive Reasoning: Chain-of-Thought vs. End-to-End*: https://arxiv.org/abs/2604.12013
- Xu et al., 2019/2020, *What Can Neural Networks Reason About?*: https://arxiv.org/abs/1905.13211
- ICML 2026 Awards / *To Grok Grokking*: https://blog.icml.cc/2026/07/05/announcing-the-icml-2026-awards/
- Xu, Vardi & Safran, 2026, *To Grok Grokking: Provable Grokking in Ridge Regression*: https://arxiv.org/abs/2601.19791

---

# 6. Instruction for the next search pass

Do **not** immediately continue W3 with experiments.

Return to broad landscape search. Favor problem frames where one of these happens:

- a load-bearing quantity changes once learner/resource/factorization is treated as part of the scientific object;
- a modern anomaly survives construct audit but collapses to a simpler classical mechanism, changing the explanation level;
- an old theorem/inference loses a load-bearing assumption under the foundation-model regime;
- a standing important problem suddenly receives genuinely new leverage rather than a new benchmark or intervention.

If W3 re-enters the search, require the unlock condition above. Otherwise leave it incubating.

**Final state:** healthy zero-survivor round; searcher improved; one standing problem strengthened but intentionally not paperized.
