# S08 — Is Metacognitive Control Shared?

**Status:** KILL — registration cancelled after significance/taste re-audit (2026-09-21)  
**Registered:** 2026-09-18  
**Target venues:** ACL / EMNLP / NAACL Main  
**Scientific type:** mechanistic interpretability / metacognitive control / causal dissociation

## 1. Stable parent question

Language models can internally represent confidence and use it to decide whether to answer or abstain. Reasoning models must make additional metadecisions: whether to keep thinking, verify, backtrack, reflect, or terminate.

The stable parent question is:

> **Is internal confidence a shared metacognitive control variable reused across different model behaviours, or do different metadecisions rely on policy-specific control states?**

The first concrete comparison is **answer/abstain vs continue/terminate reasoning**.

A shorter formulation is:

> **Is metacognitive control shared?**

This is not a paper about predicting reasoning length, building a better early-stopping method, or discovering a “stopping neuron.”

## 2. Scientific pressure

Several recent findings establish pieces of the architecture but do not agree on a single control variable.

- Kumaran et al. (Nature Machine Intelligence 2026), *Causal evidence that language models use confidence to drive behaviour*, show that internal confidence causally controls answer-vs-abstain decisions. Confidence steering changes abstention, and the paper separates confidence formation from the policy that maps confidence to action. The study deliberately avoids explicit chain-of-thought and identifies reasoning-time metacognitive control as an open question.
- Qiao et al. (EMNLP 2025 Main), *ConCISE*, distinguish **Confidence Deficit** from **Termination Delay**: a reasoning model can continue reflecting even after reaching a verified, confident answer. Their formulation itself requires a changing termination threshold/policy in addition to confidence.
- *Beyond the Commitment Boundary* finds that a model can continue generating substantial reasoning after the answer is already effectively fixed.
- *From Latent Signals to Reflection Behavior* (2026) identifies a causal trajectory from a latent thinking-budget/control direction through pivot cues to overt reflection behavior.
- Reflection/termination steering and exit-neuron work further show that reasoning-control signals can be causally manipulated independently of ordinary task accuracy.

These observations create a natural unresolved architectural question:

> **Does the same confidence representation govern multiple metadecisions, with different thresholds/policies, or is reasoning control implemented by a distinct internal state?**

This question is independently motivated by the longstanding cognitive-science distinction between domain-general confidence and domain-/policy-specific metacognitive control.

## 3. Competing worlds

### World A — Shared confidence controller

A common internal confidence state is upstream of both abstention and reasoning termination.

Predictions:
- confidence steering changes answer/abstain behavior **and** the propensity to stop reasoning;
- termination-related signals largely reflect a downstream threshold/readout of confidence;
- perturbing a pure downstream termination policy need not change confidence.

### World B — Shared monitor, policy-specific control

Confidence is available to multiple behaviours, but reasoning termination depends on an additional policy/control state that is not reducible to confidence.

Predictions:
- confidence can affect termination, but much less completely than abstention;
- a residual termination state predicts/controls stop-vs-continue after matching confidence and reasoning depth;
- steering this residual control state changes reasoning effort without proportionally changing confidence.

### World C — Metadecision-specific control / double dissociation

Abstention and reasoning termination are controlled by largely distinct internal variables.

Predictions:
- confidence steering strongly changes abstention but has little causal effect on native reasoning termination;
- termination/thinking-control steering changes reasoning length, reflection, or </think> probability while leaving answer confidence/abstention largely unchanged.

A coupled or bidirectional result is also informative and would imply feedback between monitoring and control rather than a simple one-way architecture.

## 4. Nearest-prior ownership boundary

S08 does **not** claim:

- first evidence that LLMs represent confidence;
- first confidence-based early-stopping method;
- first evidence that confidence predicts reasoning length;
- first ability to steer reflection or reasoning length;
- first discovery of a reasoning termination signal;
- first evidence that models can learn when to think.

Those objects are already occupied.

The surviving reviewer-level knowledge delta is:

> Existing work has causally established confidence-guided **abstention** and separately identified/controlled **reasoning termination/reflection** states. S08 asks whether these metadecisions share one internal metacognitive control variable or are implemented by separable monitor/control states, using causal cross-interventions in the same model.

If a direct prior is found that identifies both internal confidence and native reasoning-control representations in the same model and performs cross-steering/double-dissociation tests between them, the novelty claim must be re-audited.

## 5. Minimum pilot

Use one open reasoning model with a native thinking mode, preferably a checkpoint that can also answer directly (for example, a Qwen3-family model).

Use reasoning tasks with known discrete answers so confidence can be measured without a separate judge.

### Step 1 — Obtain matched reasoning-prefix states

Generate native reasoning traces. At several prefix locations **before natural termination**, fork the same prefix into two branches:

1. **forced-answer branch:** close/exit thinking and measure the answer distribution, giving a prefix-level answer-confidence label;
2. **native branch:** allow reasoning to continue and record whether the model naturally terminates soon, continues, reflects, or backtracks.

Because both branches share the identical prefix state, this avoids comparing unrelated “thinking” and “non-thinking” prompts.

### Step 2 — Identify the two internal variables

At matched prefix positions:

- identify a confidence representation from high- vs low-confidence prefix states;
- identify a termination/control signal predicting imminent native stop-vs-continue **after controlling/matching for confidence, token depth, correctness, and task**.

Do not assume linear orthogonality in advance. First measure overlap. If needed for causal identification, isolate the termination component remaining after confidence is accounted for.

### Step 3 — Causal cross-intervention

Perform two cross-steering tests at the same prefix states:

**Confidence → reasoning control**
- steer confidence up/down;
- measure forced-answer confidence and answer/abstain behavior to validate the intervention;
- measure native </think>/termination probability, remaining reasoning length, reflection/backtracking.

**Termination/control → confidence**
- steer the residual termination/control state toward stop/continue;
- verify that reasoning termination/reflection changes;
- measure forced-answer confidence and, where applicable, answer/abstain behavior.

The core result is the **cross-causal matrix**, not a benchmark score.

## 6. Pilot discipline

- one open model first;
- one or two compact reasoning datasets with discrete ground truth;
- no fine-tuning required for the first pilot;
- no model zoo;
- no need to reproduce an entire early-exit method;
- compare interventions at matched reasoning depths;
- treat answer confidence, stopping, reflection, and correctness as separate variables;
- do not define the two vectors from different model families or unrelated prompting modes if avoidable.

## 7. What would count as knowledge gain?

- **Shared-control result:** supports a reusable internal confidence variable that coordinates multiple model behaviours; reasoning control may be another thresholded readout of the same metacognitive state.
- **Hierarchical result:** confidence is a shared monitor, but each behaviour has its own policy/control state; this generalizes the confidence→policy decomposition beyond abstention.
- **Double dissociation:** “knowing how certain I am” and “deciding whether to keep computing” are distinct computations in reasoning models.
- **Bidirectional coupling:** metacognitive monitoring and reasoning control recursively alter one another rather than forming a static monitor→policy pipeline.

All outcomes change the functional architecture we assign to LLM metacognition.

## 8. Zhao/Cho-style mechanistic path

Mechanism is secondary to the mother question.

If the pilot survives, the natural chain is:

1. **Representation:** locate/characterize confidence and termination-control states;
2. **Computation:** determine whether the same state is read by both action policies or whether one state transforms into another;
3. **Causal dissociation:** cross-steer the two states and measure the two metadecisions;
4. **Optional component localization:** only then identify pathways/components implementing the mapping.

Do not begin by hunting neurons, heads, or vectors.

## 9. Claim boundary

Do not turn S08 into:

- an efficient-reasoning method paper;
- another “when to think” benchmark;
- confidence calibration;
- verbal-confidence analysis;
- a stopping-neuron/circuit catalog;
- “longer reasoning is unnecessary.”

The stable object is the **functional architecture relating internal confidence to distinct metacognitive control decisions**.

## 10. Promotion status

**PILOT-AUTHORIZED.**

The pilot is authorized because:

- the mother question is broader than any single recent method/future-work item and has independent cognitive-science pressure;
- current LLM evidence supports at least two plausible architectures;
- the same-model prefix-fork design avoids the largest mode-distribution confound;
- causal cross-intervention cleanly distinguishes shared, hierarchical, and dissociated control architectures;
- the pilot is small, training-free, and not evaluation-centric;
- every principal outcome produces a meaningful computational conclusion.

---

## 2026-09-19 execution-risk re-audit — KEEP / PILOT-AUTHORIZED

S08 survives the recipe audit because the first decision is training-free and same-model. Its real risk is **mechanistic construct validity**: independently decoded confidence and termination directions must correspond to causally meaningful states rather than convenient linear separators.

Recent work causally establishes confidence→abstention but explicitly leaves extended reasoning open; confidence-guided termination methods motivate, rather than settle, the shared-vs-separable-control question.

### Tightened execution gate

One open reasoning model only. Build matched-prefix labels, then require a genuine cross-causal matrix:

- confidence steering must first validate on confidence/abstention;
- termination-control steering must validate on native stop/continue;
- then test both cross-effects at the same prefixes.

**KILL immediately** if:
- either direction is only decodable but not steerable;
- cross-effects depend sensitively on arbitrary layer/vector choices;
- “termination control” disappears after matching confidence/depth/correctness;
- the project requires head/neuron archaeology before establishing the functional dissociation.

Do not add models or fine-tuning to rescue an ambiguous first cross-steering result.

**Final status: KEEP — PILOT-AUTHORIZED.**

---

## 2026-09-19 data-path audit

**Data burden: VERY LOW.**

Reuse existing discrete-answer reasoning datasets such as MATH-500, GSM8K and AIME-style problems. Ground-truth correctness is already available. Prefix-level confidence labels come from forced-answer forks; termination labels come from the model's native reasoning trace.

No new dataset, human annotation or judge model is required.

**KILL on data grounds** if:
- the experiment starts requiring manually labeled reflection/backtracking quality;
- confidence must be judged from free-form verbal explanations instead of a direct answer distribution;
- success depends on curating a special task set where stopping behavior looks clean.



---

## Final significance / Sasano-taste audit — KILL

**This section is authoritative and supersedes all earlier pilot-authorization language.**

S08 is killed not because the experiment is impossible, but because the strongest plausible result is not important enough under the current Sasano/Main taste bar.

### Mother question under review

> Is internal confidence a shared metacognitive control variable reused across answer/abstain and reasoning continue/terminate decisions, or do these behaviors rely on separable control states?

### Why the topic is killed

1. **The strongest positive result is too easy to compress into an architectural detail.**
   - Shared result: the same confidence state is read by multiple policies.
   - Separate result: abstention and termination use different control states.
   Neither conclusion by itself substantially changes how we understand reasoning, learning, or language understanding.

2. **The “so what?” problem survives even under clean causal identification.**
   A reviewer can reasonably ask why two distinct decision policies should have been expected to share one controller in the first place. Demonstrating double dissociation may therefore feel like mechanistic confirmation of an unsurprising possibility rather than a new scientific law.

3. **Nearby behavioral work already weakens the surprise.**
   Existing work distinguishes confidence deficits from termination delay and shows reasoning can continue after the answer is effectively committed. S08 would then risk compressing to:
   > prior work separated the behaviors; we show the internal control signals are separable too.
   That is too close to a behavior-known → mechanism-follow-up pattern.

4. **Broadening the question to universal metacognition creates experiment explosion.**
   A genuinely larger claim would require multiple metadecisions such as abstention, verification, retrieval, tool use, backtracking, and help-seeking. This would multiply tasks, readouts, interventions and confounds, violating the small-decisive-experiment preference.

5. **The topic also retains construct risk.**
   Before comparing architectures, the project must first establish reliable causal confidence and termination-control handles in the same model. Thus the first pilot partly validates the instrument rather than directly answering the scientific question.

### Final verdict

**KILL.**

### Anti-resurrection rule

Do not revive S08 by:
- adding more metadecisions to claim a universal metacognitive controller;
- adding more models or datasets;
- hunting heads, neurons, SAEs or cleaner steering vectors;
- reframing the work as an early-exit or efficiency method;
- arguing that causal double dissociation is sufficient significance by itself.

### General lesson

> “Do A and B share an internal mechanism?” is not automatically an important mechanistic question. Before selecting such a topic, ask what major understanding changes in the shared world versus the separate world. If the answer is only “the architecture is different,” the mother question is usually too weak.
