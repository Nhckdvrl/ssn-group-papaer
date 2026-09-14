# L37 — When Do Label Semantics Break ICL's Inference–Verbalization Boundary?

**Date:** 2026-09-14  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** **PILOT-AUTHORIZED — E01 ONLY**

## 1. Research question

> **When is the standard ICL decomposition into task inference followed by label verbalization actually valid? Can the pretrained semantic meaning of label words penetrate and distort the upstream task representation when it conflicts with the demonstrated mapping?**

This is not a generic label-word paper and not another behavioral test of inverted labels. The scientific object is the **boundary condition of the inference → verbalization factorization** in in-context learning.

A sharper formulation is:

> **Are anti-semantic label failures caused by a model that correctly infers the task but cannot verbalize the answer through a conflicting label channel, or does label semantics contaminate the inferred task representation itself?**

---

## 2. Scientific pressure

### Prior A — remapping behaves like late verbalization

Tao, Chen & Liu (EMNLP Findings 2024), *Inference and Verbalization Functions During In-Context Learning*, causally decompose ICL into an inference function followed by a verbalization function. Their controlled layer-wise interchange interventions show that the inference function is largely invariant to label remapping such as `true/false → cat/dog` across NLI, sentiment, and topic classification.

Primary source: https://aclanthology.org/2024.findings-emnlp.957/

Important scope condition: the remapped labels are semantically arbitrary with respect to the task. Their evidence therefore establishes modularity under **semantically inert label remapping**.

### Prior B — semantically conflicting remapping can become behaviorally impossible

Kumar (2025), *Semantic Anchors in In-Context Learning: Why Small LLMs Cannot Flip Their Labels*, contrasts natural demonstrations with systematically inverted, meaning-bearing labels. Across 8 tasks × 8 open models (1–12B) × 5 seeds, the reported semantic override rate is zero in all tested few-shot conditions: models do not learn coherent anti-semantic classifiers from demonstrations.

Primary source: https://arxiv.org/abs/2511.21038

That paper establishes a strong behavioral failure but does not causally identify whether the failure occurs during task inference or only when the inferred class must be mapped back through the conflicting label vocabulary.

### Mechanistic neighbors

- Sun et al., ACL 2025, *Interpret and Improve In-Context Learning via the Lens of Input-Label Mappings*, identifies task-relevant input-label mappings and causal heads using PC patching. Its experiments deliberately use semantically unrelated / arbitrary labels to reduce semantic interference, so it does not resolve the anti-semantic condition.
- Zheng et al., ACL Findings 2026, *Label Words as Local Task Vectors in In-Context Learning*, shows that each demonstration's answer position forms a local task vector and that these may aggregate into a global task vector. This establishes that label positions participate in task inference; it does not identify whether the **label word's own pretrained meaning** contaminates that task information under conflict.
- Recent geometric work on hidden-state separability/alignment finds early separability followed by later alignment with label unembedding directions and emergence of label semantics. It does not test systematic anti-semantic label conflict.

---

## 3. Why this is not `Prior A + Prior B`

The bridge itself is not the contribution. The unresolved quantity is **where semantic conflict first changes the causal computation**.

Two accounts make different counterfactual predictions.

### Account V — verbalization bottleneck

The model still infers the correct underlying task/class under inverted semantic labels. Failure arises only when that class must be converted into an output token whose pretrained meaning conflicts with the demonstrated mapping.

Prediction:

> An internal state generated under the anti-semantic condition should recover the correct class when routed through a semantically neutral verbalization channel after the inference stage.

This would reinterpret Semantic Anchors: zero behavioral override would **not** imply failure to learn the demonstrated task rule.

### Account I — inference contamination

The semantic meaning of demonstration labels influences formation of local/global task representations themselves. Anti-semantic labels therefore change the inferred rule/class before the final verbalization stage.

Prediction:

> Even when the anti-semantic state is routed through a neutral verbalizer, the inferred class remains corrupted once the relevant task representation has formed.

This would place a real boundary condition on Tao et al.'s modular factorization: inference is invariant to arbitrary remapping, but not to remapping whose labels carry strong conflicting task semantics.

### Hybrid outcome

Semantic conflict may initially alter late alignment but, past some depth or conflict strength, feed back into the causal task representation. A hybrid result is acceptable only if it is pre-registered as a depth-dependent mixture of V and I, not invented after seeing results.

---

## 4. Decisive operation

Use the **same task items, same demonstrations, same model, same number/order of examples**. Only the label regime changes.

Recommended first substrate: SST-2 or another binary classification task shared by the relevant prior work, on an open model family supported by Tao et al. (preferably Mistral-7B-v0.3 / a directly compatible checkpoint after reproduction audit).

Three label regimes:

1. **CONGRUENT** — semantically natural labels, e.g. `positive` / `negative` with normal mapping.
2. **OPAQUE** — task-neutral labels, e.g. arbitrary single-token symbols/words, fully counterbalanced.
3. **ANTI-SEMANTIC** — the same meaning-bearing label words with their mapping inverted.

Behavioral correctness must distinguish:

- the underlying task class;
- the prompt-required output token under the demonstrated mapping.

### Core causal test

Reuse Tao-style layer-wise interchange interventions to separate a source prompt's inferred state from a target prompt's verbalization function.

For each layer boundary `l`, construct a counterfactual in which the query representation formed under `ANTI-SEMANTIC` demonstrations is inserted into an otherwise `OPAQUE` verbalization context, with symmetric controls (`CONGRUENT→OPAQUE`, `OPAQUE→OPAQUE`, and reverse-direction swaps where diagnostic).

Primary estimand:

> **ANTI→OPAQUE class recovery as a function of layer**, relative to OPAQUE and CONGRUENT causal controls.

Interpretation:

- If an intermediate ANTI state routed through OPAQUE produces the correct underlying class despite direct ANTI behavioral failure, the failure is downstream / verbalization-dominant.
- If ANTI states already produce the wrong underlying class through a neutral target verbalizer across the post-inference region, semantic conflict contaminated inference/task representation.

A complementary intervention at demonstration answer positions / local task vectors is permitted only if it is needed to distinguish where contamination enters; it must not replace the primary interchange test with probe-only evidence.

---

## 5. E01 gates

E01 is bounded and must stop if the instrument does not identify the object.

### Mother gates

Before causal interpretation:

1. `CONGRUENT` accuracy must be high enough to establish the task is solved reliably.
2. `OPAQUE` remapping must be learnable enough to reproduce Tao-style inference/verbalization separation.
3. `ANTI-SEMANTIC` must show a material semantic-override failure relative to OPAQUE on the same content.
4. Results must survive at least two counterbalanced semantic label pairs / arbitrary-label assignments; no single-word artifact.

Exact numeric thresholds are to be frozen after a no-claim reproduction/power audit and before confirmatory causal runs.

### Instrument gates

1. Reproduce a Tao-style counterfactual swap in the OPAQUE condition: source inference + target verbalization must yield the predicted remapped output in a contiguous layer region.
2. Symmetric same-condition swaps must preserve behavior; arbitrary cross-prompt representation replacement must not itself destroy task accuracy.
3. The neutral/opaque verbalizer must decode underlying class independently of the anti-semantic token meaning.
4. If no layer region cleanly supports inference→verbalization interchange on the chosen model/task, **STOP**. Do not model-shop after confirmatory evaluation.

---

## 6. Ownership / reviewer compression

Strongest reviewer compression:

> `Tao et al. (neutral label remapping) + Semantic Anchors (inverted semantic labels fail) + label-anchor/task-vector papers = obvious combination.`

This compression is fatal **unless** the causal experiment answers the unresolved localization question.

What prior work owns:

- arbitrary remapping can leave inference causally invariant while changing verbalization;
- meaning-bearing inverted labels can cause severe behavioral failure;
- label positions carry task information and input-label mappings can be localized causally.

What it does **not** currently establish:

> whether pretrained label semantics under direct conflict acts only at the downstream label-alignment/verbalization stage or changes the upstream inferred task/class representation itself.

That distinction is load-bearing. The two outcomes revise different strong claims in the literature, and neither is implied by the behavioral failure alone.

Fresh repository anti-resurrection search on 2026-09-14 found no existing candidate centered on semantic label conflict breaching the inference–verbalization boundary.

Current ownership verdict: **PLAUSIBLE INDEPENDENT CONTRIBUTION**.

---

## 7. Successful-result chain

### Outcome A — inference survives, verbalization fails

Observation:

> Direct anti-semantic ICL cannot output the demonstrated inverted mapping, but its intermediate state yields the correct underlying class when passed through an opaque verbalizer.

Inference:

> The model learned the task/class despite apparent zero semantic override; the bottleneck is downstream semantic commitment / label verbalization.

Consequence:

> Behavioral anti-semantic failure is not sufficient evidence that ICL cannot learn a conflicting rule. `task learning` and `expressibility through a semantically anchored label channel` must be separated.

### Outcome B — semantic conflict corrupts inference

Observation:

> Anti-semantic states already encode / causally drive the wrong underlying class when read through a neutral verbalizer, in a region where opaque remapping preserves inference.

Inference:

> Label meaning penetrates task representation formation. Tao-style inference→verbalization modularity is conditional on the label space being semantically inert with respect to the task.

Consequence:

> The ICL computation is not generally modular with respect to the output vocabulary; pretrained semantics can alter the upstream function that demonstrations induce.

### Outcome C — no selective difference

If ANTI behaves exactly like OPAQUE once lexical/mapping controls are matched, the proposed semantic-boundary claim is unsupported. **STOP / KILL** rather than moving to another label set or task until a positive appears.

---

## 8. Main-level growth path

Only after E01 passes:

- **C1 — causal identification:** inference vs verbalization locus of anti-semantic failure.
- **C2 — conditional law:** vary independently pre-registered label–task semantic conflict strength and test whether it predicts the depth/onset of causal contamination. The scientific quantity should be stated concretely as a conflict-conditioned change in causal transfer, not as a vague `semantic permeability` metaphor.
- **C3 — consequence:** test whether making the output vocabulary semantically inert restores modularity / prompt learnability without changing task evidence, and whether the same law predicts which label spaces are easy vs impossible to remap.

No model zoo, new benchmark, prompt-optimization paper, or generic ICL task-vector atlas is authorized.

---

## 9. Feasibility

This route is inexpensive relative to training projects:

- no model training is required for E01;
- Tao et al. provide an existing interchange-intervention design/code path;
- Semantic Anchors provides inverted-label behavioral setups/code;
- SST-2 and other standard classification tasks provide independent gold;
- the main cost is forward passes / cached activations across layers.

Main risks are identification, not compute.

---

## 10. Verdict

```yaml
natural_question: PASS
mother_phenomenon: PASS_STRONG_BUT_MUST_REPRODUCE_SAME_MODEL
anti_resurrection: PASS
same_quantity_pressure: PASS_AFTER_SCOPE_CORRECTION
closest_owner_density: MEDIUM_HIGH
central_owner: NOT_FOUND
reviewer_compression: SERIOUS_BUT_SURVIVABLE_ONLY_WITH_CAUSAL_LOCALIZATION
identification: PASS_CONDITIONAL_ON_INTERCHANGE_GATE
successful_result_upper_bound: PASS
outcome_identity: PASS
resolution: FAVORABLE
compute_cost: LOW
pilot: E01_ONLY
verdict: PILOT_AUTHORIZED_E01_ONLY
```

**Authorization:** one bounded E01 reproducing the three label regimes and the causal interchange gate on one predeclared model/task substrate. No breadth or mechanism expansion before this gate passes.