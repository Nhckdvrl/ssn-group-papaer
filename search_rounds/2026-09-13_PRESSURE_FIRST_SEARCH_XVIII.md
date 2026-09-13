# 2026-09-13 — Pressure-First Search XVIII

Continuation after `PRESSURE_FIRST_SEARCH_XVII.md`. This batch deliberately keeps switching objects before deciding whether P73 deserves Selection. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## P90 — Metaphor comprehension: literal-first reinterpretation vs direct figurative access

**Status:** `PRESSURE ONLY — NOT SELECTION — NO COMPUTE`

### Pressure
Human metaphor research has a long-standing, intuitive process distinction: indirect/literal-first accounts say the comprehender initially accesses literal meaning and only later revises when context makes it inadequate; direct-access / graded-salience accounts allow figurative content to be accessed immediately, especially for conventional metaphors or supportive contexts. This is scientifically live rather than a textbook-closed distinction.

A tempting LM question is whether a decoder model's successful metaphor interpretation actually passes through a causally load-bearing literal interpretation or reaches figurative meaning without constructing a complete literal proposition first.

### Why not promoted
The selective operation is still missing. Showing that literal lexical/semantic features are present, or even causally useful, does **not** establish a staged `construct literal proposition → reject/revise` route: direct-access and graded-salience accounts also allow literal lexical features to remain active. Conversely, deleting a literal-related direction would alter semantic ingredients needed by both accounts. Current LM-side metaphor work is much thinner than the human theory, but low owner density is not enough when the proposed causal test does not identify the process distinction.

**Blocker:** find a temporal or path-specific operation that can remove a *completed literal-compositional route* while preserving the lexical semantic material shared with figurative interpretation, plus a conventionality/context negative control. Until then, no GPU.

**Anti-resurrection:** do not promote `literal meaning is decodable during metaphor`, `patch literal features`, or `context changes metaphor interpretation` as the paper.

---

## P91 — Referential opacity under modern LLM scale: did the old semantic learnability failure disappear?

**Status:** `DROP CURRENT FORM / OLD-LAW RETEST COLLAPSES TO COMPETENCE`

### Pressure
TACL 2023 *Transparency Helps Reveal When Language Models Learn Meaning* linked a formal learnability condition (strong transparency) to empirical failure on referential opacity, using GPT-2/BERT-era models. Modern base LMs are vastly larger and trained differently, so this superficially fits `old empirical law → changed modern regime`.

### Why dead in current form
The strongest cheap experiment is still `do modern models now succeed on opacity?`, which is an old-task competence rerun. If they succeed, the interesting next question becomes whether the model stores separate epistemic files / reconstructs attitude-holder-relative identity — a scientific skeleton already covered by recent project work and the killed representation/reconstruction families. If they fail, the 2023 law merely persists. No independent causal quantity has been identified that makes both outcomes Main-level before seeing the result.

**Anti-resurrection:** do not reopen as `GPT-2 failed opacity but Llama/Qwen might pass`, or another probe/similarity benchmark. A future return needs a genuinely new changed-regime prediction about the *computation*, not the score.

---

## P92 — Uniform Information Density as a modern-generation law

**Status:** `DROP / DIRECT 2026 MODERN-REGIME OWNERS`

### Pressure
UID is a classic psycholinguistic production law and looked like a possible `old human empirical law → RLHF/reasoning generation` pressure.

### Why dead
CoNLL 2026 already directly compares pretrained and post-trained LLM outputs under an information-theoretic UID lens and reports superhuman uniformity plus post-training shifts. Findings ACL 2026 separately revisits UID in LLM reasoning with step-level information-density measurements. The modern-regime question is already active and direct; a new `does RLHF/reasoning alter UID?` paper would be a neighbor, not a fresh parent.

**Anti-resurrection:** do not reopen with another model family, decoding temperature, or reasoning benchmark unless a new causal quantity survives these 2026 owners.

---

## P93 — Are induction heads still the mechanism of ICL in modern LMs?

**Status:** `DROP / CHANGED-REGIME QUESTION ALREADY OWNED`

### Pressure
The original induction-head story is an influential mechanistic law from smaller Transformers: prefix matching / copying heads emerge with in-context learning. A natural modern-regime stress test is whether large pretrained LMs still use induction heads as the dominant ICL machinery.

### Why dead
ICML 2025 *Which Attention Heads Matter for In-Context Learning?* directly separates induction heads from function-vector heads and finds larger-model few-shot ICL is driven much more strongly by function-vector heads, with many early induction heads transitioning toward FV roles during training. NAACL 2025 and other 2025 work causally test induction mechanisms in Llama/InternLM, and 2026 work continues cross-architecture ICL mechanism analysis. The attractive old-law update has already happened.

**Reviewer compression:** `Olsson induction heads → ICML 2025 FV-vs-induction causal comparison = modern ICL is not simply induction-head dominated.`

**Anti-resurrection:** do not reopen as `induction heads are not enough`, `which heads really do ICL`, or induction-vs-function-vector localization on another model.

---

## P94 — Function-vector heads are one coherent causal class

**Status:** `DROP / DIRECT 2026 OWNER`

### Pressure
Function-vector work often ranks heads by magnitude of causal contribution and treats the selected set as a single functional class. A clean identifying pressure is whether magnitude hides opposing causal signs.

### Why dead
June 2026 *Function-Vector Heads Are Two Populations: Writers and Cancellers in In-Context Learning* directly makes this move: sign-preserving attribution plus path patching splits the apparent FV class into causal writers and cancellers. This is another useful **provenance template** — inspect the identifying statistic behind a widely used mechanistic category — but the topic itself is occupied.

---

## P73 — Does prediction error causally set the in-context update size?

**Status:** `ADVANCE TO FULL SELECTION AUDIT — STILL NO COMPUTE IN THIS LOG`

### Pressure sharpened
NAACL 2025 uses the inverse-frequency effect (IFE) in structural priming to conclude that LLM ICL is error-driven and that an error signal is implicitly computed in the forward pass. That diagnostic is not uniquely identifying: classic ACT-R/base-level models of structural priming also reproduce inverse-frequency interactions, and the human literature contains residual-activation / implicit-learning / Bayesian alternatives.

A May 2026 closest owner causally edits continuous verb bias in steering/function vectors and finds error-signal-like information, but reports that those error-related aspects are not naturally causally used in downstream production and explicitly leaves the connection from continuous variables to ICL unresolved.

The remaining estimand is therefore not `does IFE exist?` and not `is an error vector decodable?`:

> **If the model sees exactly the same prime, does the amount it learns from that prime change solely because its own expectation immediately before the structural evidence was causally changed?**

Short form:

> **Does surprise causally set the in-context learning rate?**

### New selective-operation candidate: READ-ONCE

A cleaner causal cut than post-hoc vector subtraction is possible in an autoregressive decoder.

1. At the prime verb / last shared pre-diagnostic state, causally edit a cross-fitted continuous verb-bias coordinate so the model expects PD more or less strongly. First-stage leverage is measured directly on the model's PD-vs-DO continuation odds.
2. Keep the edited source K/V available **only while the first construction-diagnostic evidence is processed**. This is `READ-ONCE`.
3. Immediately after that evidence has been read, restore the prime-verb/source K/V to the clean cache. The later target can therefore no longer directly attend to the edited expectation source. Any surviving effect must have been written into the diagnostic/post-diagnostic states while the observation was processed.
4. Compare to a `TOO-LATE` arm where the same calibrated edit becomes available only after the diagnostic evidence has already been processed, and is likewise removed after the matched propagation window. This measures generic state/carryover effects that do not require the expectation to exist when the evidence arrives.

This operation directly exploits causal timing: in a standard decoder, the previous softmax probability is not fed back as a variable. If current expectation matters to online adaptation, its representation must be available when the observed token/span is processed and must leave a downstream causal trace.

### Why Selection is now warranted

The question has a strong mother, an exact closest successor, a live identification gap, and a plausible same-checkpoint temporal cut. The strongest reviewer compression (`NAACL 2025 IFE + 2026 causal verb-bias/error directions = already known`) does not entail the answer because neither work estimates `do(pre-observation expectation) → same observation → later native update`, and the 2026 paper's negative natural-use result makes that link explicitly nontrivial.

This log does **not** authorize compute. Promotion requires a separate Selection document to audit first-stage selectivity, direct-path completeness, evaluation resolution, null value, and Main-level growth without claiming that a positive result uniquely proves gradient descent.

---

## Round checkpoint

**New survivor in this rolling log: 0.**

P73 is the only object advanced to full Selection audit. This is not a search closeout: independent pressure-first search remains active regardless of the Selection verdict.