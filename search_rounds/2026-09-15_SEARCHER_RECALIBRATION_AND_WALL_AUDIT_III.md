# 2026-09-15 — Searcher Recalibration and Wall Audit III

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS / AAAI  
**Mode:** problem-creator search; no candidate generation unless the mother question survives  
**Outcome:** **0 new L-series; 0 new pilot authorization.**

This round deliberately changed scientific objects several times. The important result is not another killed list. It is a new diagnosis of the searcher: after reducing `behavior → mechanism sequel`, the generator began overproducing a more sophisticated but still mechanical pattern:

> **widely used scalar / quantity X → X is too coarse → propose better quantity Y.**

`wrong quantity` remains an excellent provenance class, but it must not become a topic template. Recent frontier work already aggressively rewrites many obvious quantities. Repeatedly enumerating `tokens`, `loss`, `compute`, `parameters`, `human-likeness`, etc. is another form of successor search.

---

# 1. Fresh calibration event: anomaly validity comes before anomaly mechanism

A particularly useful 2026 calibration event is the debate around ACL 2026 Best Paper **The Imperfective Paradox in LLMs**.

The original paper treats a strong apparent semantic bias as the mother phenomenon. A fresh 2026 critique argues that many benchmark items do not uniquely license the intended semantic inference, that native speakers often accept alternative interpretations, and that lexical-matched minimal pairs / intermediate semantic decisions substantially alter the story.

The transferable lesson is **not** to write benchmark-audit papers. It is a searcher safeguard:

> Before descending from a beautiful anomaly into mechanisms, verify that the anomaly is actually identified by the underlying theory / construct / stimulus.

For semantics, pragmatics, cognition, and other theory-sensitive objects, `stable anomaly` must mean more than numerical replication. It must survive the strongest plausible alternate interpretation of the theoretical gold.

**New hard discipline:**

1. Does the theory uniquely entail the label / contrast being treated as gold?
2. Are alternative interpretations genuinely excluded rather than assumed away?
3. Does the phenomenon survive lexical/template matching when these are theoretical confounds?
4. When human judgments are part of the construct, do they support the intended interpretation?

Only after this audit should `anomaly → mechanism` receive serious search budget.

---

# 2. WALL audit

## W11 — Does a behavior emerging after post-training imply direct optimization pressure for that behavior?

### Question

> If behavior X becomes stronger after RL / post-training, does that mean the reward or gradient directly selected X?

### Pressure

Post-training papers routinely interpret before/after behavioral changes as evidence about what the objective incentivizes. But correlated proxies and policy reorganization can produce a behavioral consequence without direct local pressure on that consequence.

### Modern pressure

ICML 2026 **The Obfuscation Atlas** is a strong example of the research move: observed detector avoidance does not by itself establish direct optimization for activation obfuscation. Broader Goodhart / correlated-proxy / reward-hacking theory already treats this inference explicitly.

### Decision

**CLOSE AS CURRENT TOPIC GENERATOR.**

The linking assumption is scientifically important, but the mother program is occupied. Do not shrink to another detector/reward setting or invent a `direct pressure score`.

**Searcher lesson:** `behavior after optimization` is not automatically `property directly optimized`.

---

## W12 — Does faster learning constitute evidence for an inductive bias?

### Question

> When one pattern is learned earlier / with fewer examples than another, what exactly licenses the claim that the learner is biased toward it?

### Pressure

Syntax acquisition and possible/impossible-language work often use sample efficiency or endpoint perplexity as a bridge from model behavior to claims about learning bias.

### Audit

2026 work directly criticizes sample efficiency / perplexity as a linking hypothesis for human non-attestation and compares alternative evidence such as grammatical sensitivity and generation. This is therefore not an untouched bridge.

### Decision

**CLOSE. Direct linking-hypothesis owner.**

Do not turn this into `better bias metric`.

---

## W13 — Does inability to generate an inference imply absence of the underlying semantic knowledge?

### Question

> If a model cannot reliably produce the reverse / entailed / transformed relation, has it failed to learn the semantic relation itself?

### Pressure

Behavioral semantics work often treats generation failure as evidence of missing semantic structure.

### Audit

ACL 2026 reversal work directly argues that semantic knowledge can coexist with autoregressive order bias. More generally this compresses to the repository's already-killed `capability / representation vs readout` parent (including K174-family routes).

### Decision

**CLOSE / ANTI-RESURRECTION.**

Changing the linguistic phenomenon does not reopen the parent.

---

## W14 — Is inductive bias hypothesis selection, or hypothesis coexistence plus routing/expression?

### Question

> When ambiguous training permits hypotheses A and B but the model behaves like A out of distribution, did training actually select A and eliminate B?

### Pressure

A large generalization literature treats endpoint OOD preference as evidence that the learner selected one structural hypothesis.

### Modern evidence

TACL 2025 **Learning Syntax Without Planting Trees** reports a stronger possibility: within one trained Transformer, subnetworks implementing competing linear and hierarchical rules can coexist even while full-model behavior becomes increasingly hierarchical.

This differs from classical **underspecification**, where different training runs may realize different compatible predictors. Here the ambiguity may persist **within one model**.

### Decision

**NO CANDIDATE. Strengthens standing IP12.**

The scientific distinction is real, but the repository already maintains the broader problem: when is a single learned algorithm an adequate explanation, and when is a mixture/state-dependent family the real computational object?

Do not make a successor paper by searching for competing subnetworks on another task.

**Standing update:** IP12 gains strong language-learning evidence.

---

## W15 — Is a token the correct unit of learning pressure?

### Question

> Does one token of sequence loss correspond to one comparable unit of supervision?

### Pressure

Sequence loss sums/averages token terms even though tokens can differ radically in novelty, difficulty, causal role, and predictability.

### Audit

NeurIPS 2024 **Rho-1: Not All Tokens Are What You Need for Pretraining** already attacks uniform-token training directly, and 2025–2026 work extends token significance / capability-aware loss / token-level RL heterogeneity.

### Decision

**CLOSE. Active quantity-rewrite program.**

Do not propose another token-importance scalar as the paper.

---

## W16 — Does a nonce / unseen form provide clean evidence of rule generalization in foundation models?

### Question

> Can a Wug-style stimulus still be treated as genuinely novel when the learner was pretrained on web-scale text and subword relatives?

### Pressure

Classic productivity experiments rely on novelty to rule out direct lexical experience.

### Audit

Strong modern work already explicitly checks zero occurrence of nonce forms / derivatives in known pretraining corpora. With closed models the residual becomes unverifiable provenance / contamination rather than a satisfying scientific object.

### Decision

**CLOSE.**

Modern pretraining complicates the assumption, but this route becomes data-provenance auditing rather than the kind of model-science paper currently sought.

---

## W17 — Does test-time reasoning compute create capability or merely improve search over existing support?

### Question

> When more inference-time compute raises accuracy, did the model gain access to new successful behavior or merely sample / search existing behavior more effectively?

### Pressure

This is the inference-time analogue of the important `score ≠ capability boundary` distinction used in RLVR analysis.

### Audit

2026 work already distinguishes average-success improvements from pass@K support and explicitly decomposes `test-time scaling` into sequential deliberation, parallel sampling, and partial-state search. These are different statistical objects, not one scalar compute axis.

### Decision

**CLOSE AS CURRENT TOPIC GENERATOR.**

`tokens ≠ compute` and `accuracy ≠ expanded support` are already direct active questions. Do not shrink to another reasoning benchmark.

---

## W18 — Is human-likeness a scalar property of a language model?

### Question

> If one model better predicts one human measure but worse predicts another, what does it mean to call it `more human-like`?

### Pressure

LM cognitive-model papers often compress reading times, neural responses, surprisal fit, grammatical preferences, and other observables into a broad human-likeness narrative.

### Audit

TACL 2023 inverse-scaling work, later internal-layer analyses, and 2025–2026 cognitive-modeling studies already show that different behavioral/neural measures can track different model layers and scaling trends.

### Decision

**NO CANDIDATE. Strengthens IP07.**

The searcher should treat `human-likeness` as a family of linking hypotheses, not a scalar quantity. A future project must target one consequential bridge whose validity changes a substantive human-language theory.

---

## W19 — Is token entropy the right uncertainty object for language-model meaning?

### Question

> Does uncertainty over token strings measure uncertainty over answers / meanings?

### Audit

Semantic entropy and its extensions already make `token-space uncertainty ≠ meaning-space uncertainty` the center of an active uncertainty-estimation program.

### Decision

**CLOSE.** Also low-priority metric/UQ territory for the current search.

---

## W20 — Is pretraining loss a sufficient state variable for learning progress?

### Question

> If two models have nearly identical held-out cross-entropy, are they at scientifically equivalent stages of learning?

### Pressure

Scaling work often uses validation loss as a compact state variable linking scale, data, compute, and downstream capability.

### Audit

ICML 2025 loss-to-loss scaling shows data-dependent mappings; ICLR 2026 work reports downstream differences even at matched training loss; ACL 2025 work already decomposes token loss by capability salience. The community is actively disputing and replacing the scalar state variable.

### Decision

**CLOSE.**

Do not invent a new `capability-weighted loss` successor.

---

## W21 — How does absence become evidence in language learning?

### Question

> How can a learner infer that a form is disallowed from the fact that it repeatedly fails to appear where an alternative does?

### Pressure

Negative evidence / statistical preemption is a classic acquisition problem that is difficult to manipulate over a human learner's complete experience. Controlled LM training appears to provide genuinely new leverage.

### Audit

2026 **Do Language Models Know What Not to Say? Causal Evidence for Statistical Preemption in LLMs** already uses controlled intervention to separate statistical preemption from entrenchment across alternations.

### Decision

**CLOSE AS CURRENT TOPIC GENERATOR.**

This is exactly the kind of old problem + modern leverage we should like, but the obvious scientific attack has already been made. Do not descend to a finer mechanism merely because the mother problem is excellent.

---

## W22 — Is parameter count the right notion of architecture scale?

### Question

> At equal parameter budget, can depth / width / recurrent composition change what computations are learnable, rather than merely efficiency?

### Pressure

NeurIPS 2025 Best Paper **1000 Layer Networks for Self-Supervised RL** makes depth itself a dramatic empirical variable, while common scaling discussions collapse architecture to parameters/FLOPs.

### Audit

Classical depth separation plus current transformer depth–width tradeoffs, architecture-conditioned scaling, and variable-width work already form a direct program.

### Decision

**CLOSE.**

`parameter count is too coarse` is correct but no longer an available parent.

---

## W23 — Superposition: beneficial capacity mechanism or harmful interference mechanism?

### Apparent contradiction

NeurIPS 2025 argues superposition can produce robust neural scaling; ACL 2026 uses feature-superposition geometry to explain harmful emergent misalignment.

### Audit

This is **not a scientific contradiction**. The foundational superposition story already contains the tradeoff: storing more features than dedicated dimensions increases effective capacity at the price of interference.

### Decision

**CLOSE AS FALSE CONTRADICTION.**

Do not create a `when is superposition good vs bad?` paper unless a natural quantity violates an explicit prediction of the existing tradeoff theory.

**Searcher lesson:** opposite-looking conclusions from strong papers do not constitute a contradiction if the old theory already allows both simultaneously.

---

## W24 — Same endpoint performance, different training history: is the final model state enough?

### Question

> Can models with similar endpoint behavior/loss embody systematically different computations because they arrived there through different developmental paths?

### Pressure

Dense checkpoint release makes formation history observable in a way it historically was not.

### Audit

`Developmental interpretability` has now become an explicit research program, including training-time singular-learning-theory analyses and dedicated reviews/agendas.

### Decision

**CLOSE AS GENERIC FORM.**

Revisit only if a substantive older scientific inference relies on **path independence** and the modern regime supplies evidence that breaks that exact inference.

---

# 3. New searcher failure mode: WRONG-QUANTITY AUTOCOMPLETE

This round caught a new generator drift.

After learning from `expressivity → succinctness`, `score → capability boundary`, `memorization → information capacity`, etc., the searcher began producing:

- token count is not information;
- token length is not compute;
- cross-entropy is not learning state;
- parameter count is not architecture scale;
- human-likeness is not scalar;
- entropy over tokens is not semantic uncertainty.

Many are scientifically correct. But correctness is not provenance.

If several leads in a row have the form:

> **X is a commonly used scalar → X is too coarse → replace X with richer Y**

then **STOP GENERATION**.

Ask instead:

1. What standing scientific disagreement remains unresolved *because* X collapses two causal regimes?
2. Is there already an active literature proposing Y-like replacements?
3. Does changing X alter a load-bearing conclusion, or merely improve prediction/correlation?
4. Would the question still matter if no new metric were proposed?

If the answer is mainly `we can define a better quantity`, switch scientific object.

---

# 4. Stronger contradiction discipline

`Paper A says X helps` and `Paper B says X hurts` is not enough.

Before treating two results as a contradiction, require:

1. **SAME-QUANTITY:** same scientific object, observable, estimand, intervention meaning, and relevant regime;
2. **THEORY-INCOMPATIBILITY:** the best existing theory cannot naturally make both results true under different conditions already represented in that theory.

Superposition is the warning case: capacity benefit and interference harm look directionally opposed but are already the two sides of the same old tradeoff.

A useful contradiction should force a theory revision, not merely a boundary condition the theory already contains.

---

# 5. Portfolio consequences

**New L-series:** 0.  
**New pilot authorization:** 0.

Standing updates only:

- **IP12 strengthened:** TACL 2025 provides concrete evidence for within-model coexistence of competing rules, not only across-run underspecification.
- **IP07 strengthened:** human-model correspondence must be specified at the level of a particular observable / timescale / linking hypothesis; `human-likeness` is not a sufficient scalar construct.
- **Autoregressive-learnability WATCH from the previous round remains WATCH+.** Nothing in this round provides the missing cross-task quantity or natural contradiction needed to unlock it.

No new standing problem was added merely to create progress.

---

# 6. Next-round instruction

Do **not** continue by enumerating more common scalars that may be too coarse.

Do **not** return to the walls closed above through a narrower model/task/mechanism.

The next round should switch discovery mode again. Prefer:

- a long-standing theory whose **shared premise** is broken by the foundation-model regime;
- a natural phenomenon for which two mature theories make genuinely incompatible predictions on the **same quantity**;
- a standing important problem where a new 2025–2026 method changes what can be inferred rather than merely measuring it better;
- an apparently model-specific effect that disappears or becomes theoretically simpler in a minimal classical model;
- a field-level inference that depends on path independence, exchangeability, stationarity, identifiability, or another assumption that modern training/deployment concretely violates.

Most importantly, keep the searcher's own generator under observation:

> **The goal is not to replace one autocomplete pattern with a smarter autocomplete pattern.**

A healthy search round can end at zero when the mother problems were genuinely examined and the generator itself became better calibrated.