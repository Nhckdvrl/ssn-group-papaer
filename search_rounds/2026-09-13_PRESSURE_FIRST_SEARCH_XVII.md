# 2026-09-13 — Pressure-First Search XVII

Continuation after `PRESSURE_FIRST_SEARCH_XVI.md`. This batch deliberately moves away from the surviving no-compute pressures P69/P73/P79 and records owner assassinations in reasoning/RL, interpretability instruments, PEFT, and ICL regime-change. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## P85 — Belief bias in logical reasoning: valid structure absent, or present but plausibility wins?

**Status:** `DROP / DIRECT 2025–2026 CAUSAL OWNER PROGRAM`

### Pressure
Human reasoning has a classic belief-bias dissociation: conclusions can be logically valid but implausible, or invalid but believable. A tempting model-science question is whether LMs fail because the validity computation itself is corrupted by world-knowledge plausibility or because a valid structural state survives and loses only at decision time.

### Why dead
Findings ACL 2025 *Reasoning Circuits in Language Models: Mechanistic Interpretation of Syllogistic Inference* already identifies causally necessary/sufficient reasoning circuitry and commonsense-related attention that contaminates syllogistic decisions. Findings ACL 2026 *How Language Models Conflate Logical Validity with Plausibility* goes further: validity and plausibility are geometrically aligned and steering those representations causally changes logical decisions. The central representational/causal interaction is already owned.

**Anti-resurrection:** do not reopen as `logic present but belief wins`, `belief bias is readout rather than representation`, or validity-vs-plausibility steering with another syllogism set/model.

---

## P86 — RLVR improves reasoning by generating new algorithms or selecting/verifying pre-existing ones

**Status:** `DROP / DIRECT MECHANISM OWNER + ACTIVE 2026 VERIFICATION PROGRAM`

### Pressure
A natural post-training A/B asks whether verifiable-reward RL creates genuinely new reasoning procedures or mainly changes which pre-existing trajectories the policy samples and endorses.

### Why dead
2025 *On the Mechanism of Reasoning Pattern Selection in Reinforcement Learning for Language Models* directly argues that much RLVR gain comes from selecting among reasoning patterns already present in the base policy, with individual-pattern performance comparatively stable. 2026 work simultaneously develops the opposite/boundary side through self-verification and capability-support analyses. The generator/selector/verifier decomposition is therefore an active parent, not an empty pressure.

This also lies adjacent to already killed generic RLVR capability-boundary / entropy / mode-collapse / self-correction families.

**Anti-resurrection:** do not reopen generic `RL learns vs selects`, `generator vs verifier`, or `base support vs post-RL policy` with another reward/model/task. A future return needs a new scientific quantity not already reducible to support selection or verification.

---

## P87 — Does a logit/tuned lens reveal the model's current belief, or only decode an intermediate coordinate system?

**Status:** `DROP / FOUNDATIONAL OWNER ALREADY TESTS CAUSAL FIDELITY`

### Pressure
Interpretability papers often narrate intermediate decoded logits as a model progressively changing its mind. The identifying question is whether the decoded quantity is actually causally used by later computation rather than merely readable.

### Why dead
Belrose et al. (2023), *Eliciting Latent Predictions from Transformers with the Tuned Lens*, was explicitly designed because the raw logit lens is unreliable under representational drift. It does not stop at decodability: it evaluates stimulus-response fidelity and causal basis extraction, showing that ablating directions prioritized by the tuned lens disproportionately affects model behavior. Generic `lens output != belief` or `decodable intermediate logits != causal state` is therefore not a fresh parent.

**Anti-resurrection:** do not reopen with another task/layer/model or a generic patching audit. A new lens paper would need a distinct causal estimand/identification failure that survives the tuned-lens fidelity program.

---

## P88 — Why can low-rank adaptation work: does LoRA create new task features or only reshape/amplify existing ones?

**Status:** `DROP / 2025–2026 THEORY + CAUSAL/GEOMETRIC OWNERS`

### Pressure
The striking structural fact behind PEFT is that a very low-rank parameter update can produce substantial behavioral specialization. A tempting A/B is `new representational directions are learned` versus `pre-existing features are merely reweighted/read out differently`.

### Why dead
By 2025–2026 this is already a dense mechanistic/theoretical program: COLT/ICML work analyzes when low-rank tuning performs feature learning versus lazy adaptation and gives optimization guarantees; ICML 2025 circuit analysis studies how fine-tuning changes causal computation; LREC 2026 *From Behavior to Geometry: A Causal and Geometric Analysis of LoRA-Based Domain Adaptation* directly studies emergence versus reshaping of discriminative directions. `Why low rank suffices / new vs reused features` is no longer an unowned parent.

**Anti-resurrection:** do not reopen with a different rank, adapter placement, domain, or model family unless a new invariant/estimand exists beyond feature emergence vs reshaping.

---

## P89 — After an in-context task switch, does the LM forget the old rule or perform mixture/change-point inference over regimes?

**Status:** `DROP / DIRECT 2026 REGIME-CHANGE + INTERFERENCE PROGRAM`

### Pressure
A matched ICL sequence can contain one mapping/rule and then abruptly switch to another. The intuitive scientific question is whether failures after the switch reflect persistent interference/forgetting or a rational latent-regime posterior that has not yet moved to the new task.

### Why dead
2026 work already treats this exact object as regime-change inference and in-context continual learning: *In-Context Learning Under Regime Change* formalizes change-point/model-averaging behavior, while *Understanding Generalization and Forgetting in In-Context Continual Learning* decomposes attention-induced inter-task interference and forgetting; *When Context Sticks* empirically studies persistent ICL interference. A new switch-point experiment would enter an existing parent rather than create one.

**Anti-resurrection:** do not reopen as `ICL forgets vs averages`, `old demonstrations contaminate the new task`, or `task switch detection` with another synthetic mapping.

---

## P73 ownership delta — prediction-error-weighted ICL

**Status remains:** `SERIOUS AUDIT TARGET — NOT SELECTION — NO COMPUTE`

A May 2026 closest owner materially sharpens, but does not obviously close, the gap: *Causal Interventions on Continuous Variables: A Case Study on Verb Bias in Steering Vectors for In-Context Learning* causally edits verb-bias information in structural-priming steering vectors and shifts structural preferences. Importantly, it reports that error-signal-like aspects encoded in those vectors are **not naturally causally used in downstream production**, and explicitly leaves connecting continuous variables to the ICL update unresolved.

This strengthens the need for P73's distinguishing operation rather than authorizing it: causally change **pre-outcome expectation**, then present the **same observed prime**, and measure whether the later update changes after subtracting direct intervention carryover. The owner audit must still determine whether another 2025–2026 paper already performs this `do(expectation) → same observation → update size` experiment, and Selection must prove a selective first stage before GPU.

---

## Round checkpoint

**New survivor: 0.**

This is not a closeout. Continue switching scientific objects. Current no-compute pressures P69/P73/P79/P54/P62/P47 remain pressures only and must not monopolize the search.