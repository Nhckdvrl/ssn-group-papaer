# L44 E01 Preregistration — Internalization and Workspace Dependence

**Status:** `AUTHORIZED — E01 ONLY; NOT MAINLINE`  
**Date revised:** 2026-09-16  
**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS

---

# 1. Research question

> **As an explicitly multi-step reasoning procedure is progressively internalized during training, how does the model's causal dependence on a shared verbalizable workspace change?**

The experiment follows one controlled training trajectory from explicit reasoning to increasingly internalized reasoning and measures workspace dependence at multiple predeclared stages.

The central object is a **relationship**, not a directional prediction:

> `degree of internalization -> causal workspace dependence`.

The trajectory may decrease, increase, remain stable, or change non-monotonically. Each resolved pattern has a distinct scientific interpretation.

This question is motivated by a tension across recent work:

- Stepwise Internalization shows that an explicitly supervised reasoning procedure can be compressed into fewer or no visible CoT tokens while retaining substantial task performance.
- Global-workspace work identifies a small J-space that is causally important for flexible reasoning while many routine computations proceed with little dependence on it.
- Recent latent-reasoning work shows that a silent reasoning interface can sometimes act more as training-time scaffolding than as a load-bearing inference-time scratchpad.

The missing quantity is how **workspace dependence itself evolves during internalization**.

---

# 2. Scientific quantities

## 2.1 Internalization stage

Training follows Stepwise Internalization (Deng, Choi & Shieber, 2024): starting from explicit CoT supervision, progressively remove a prefix of intermediate reasoning tokens while keeping the input question and final answer fixed.

Let `s` denote the number of CoT tokens scheduled for removal.

For E01, save checkpoints at the following predeclared stages:

> `s in {0, 8, 16, 24, 32, 39+}`

where `39+` is the paper's GSM8K convention for removing all remaining CoT tokens.

Define the normalized manipulated coordinate

> `I_s = min(s / 39, 1)`.

This is the primary internalization coordinate because it is fixed by the training intervention rather than inferred from the model's later behavior.

At every stage also record:

- exact-answer accuracy;
- emitted non-answer tokens;
- emitted reasoning-token count;
- generation latency / tokens to final answer;
- format compliance.

These behavioral quantities describe how much visible reasoning remains, but they do not define the stage retrospectively.

---

## 2.2 Causal workspace dependence

Workspace dependence is measured with the Jacobian-lens / J-space intervention introduced by Gurnee et al. (2026).

At each relevant activation, identify the most active J-lens directions and remove their projection, while excluding directions corresponding to tokens the clean model is imminently trying to output. The intervention is always compared against a layer-, count-, and removed-norm-matched non-J control.

For an evaluation score `Y`, define the selective causal effect at stage `s`:

> **`W_s = Y_s(ctrl) - Y_s(J)`**

where larger positive `W_s` means greater selective dependence on the J-space.

The primary scientific object is the curve

> **`{I_s, W_s}` across all registered stages.**

No single endpoint comparison is sufficient for E01.

---

# 3. Primary model and data

## 3.1 Model

Primary model:

> **`Qwen/Qwen3-8B-Base`**

Reasons for choosing it:

- open weights and feasible full-parameter / distributed SFT on available hardware;
- standard decoder Transformer architecture;
- Qwen3-8B already has public Jacobian-lens fits and independent J-lens tooling, reducing implementation risk;
- using the base checkpoint makes the explicit-CoT -> internalized trajectory easier to interpret than starting from a model already strongly optimized for direct mathematical answering.

The exact Hugging Face revision hash must be frozen in the run manifest before training.

No model shopping is permitted after E01 results are visible.

---

## 3.2 Internalization data

Primary task:

> **GSM8K using the augmented Stepwise-Internalization training data released by Deng et al.**

Use the published data construction and split. The paper reports approximately:

- `378k` training examples;
- `0.5k` development examples;
- `1.3k` test examples;
- training sequences restricted to at most 150 tokens for the GSM8K experiments.

The dataset is chosen because the internalization procedure is already demonstrated on the same scientific object and because question, reasoning trace, and final answer remain fixed while the visible reasoning prefix is removed.

The frozen held-out test split is never used for learning-rate selection, stage selection, J-lens fitting, workspace-band selection, or stopping decisions.

---

## 3.3 J-lens fitting corpus

Fit the Jacobian lens on a task-independent generic corpus:

> **WikiText-103 raw train, 1,000 frozen sequences of 128 tokens.**

Follow the released `anthropics/jacobian-lens` estimator:

- average input-output Jacobian;
- first 16 positions excluded as attention-sink positions;
- same tokenizer and sequence IDs for every checkpoint;
- same fitting code, source layers, target layer, dtype, and reduction rule across stages.

A 100-sequence fit may be used only as an engineering smoke test. All registered E01 measurements use the 1,000-sequence fit.

The fitting corpus is independent of GSM8K and of all calibration/evaluation prompts.

---

# 4. Experiment structure

E01 has three phases. Phase A is an implementation replication, Phase B establishes the causal measurement on the actual Stage-0 checkpoint, and Phase C measures the internalization trajectory.

---

# 5. Phase A — implementation replication

Before any L44 training result is examined, verify that the intervention code reproduces basic J-lens behavior on an existing public Qwen3-8B setup.

Use:

- `Qwen/Qwen3-8B`;
- a public Qwen3-8B Jacobian lens fitted with the Anthropic reference implementation;
- released Anthropic prompt sets where possible.

This phase is an engineering check, not an L44 result.

Minimum checks:

1. J-lens readouts contain sensible intermediate concepts on released multi-hop examples.
2. The ablation implementation can project out the clean pass's top active J-lens directions.
3. matched random/non-J controls remove the same number of directions and comparable activation norm.
4. output-token exclusion works exactly as specified.
5. repeated runs with deterministic decoding reproduce identical clean and intervention scores.

Failure here means the implementation must be repaired before proceeding. It does not supply evidence about the L44 research question.

---

# 6. Phase B — validate the workspace measurement on Stage 0

## 6.1 Stage-0 checkpoint

Train the Qwen3-8B-Base model on the full explicit-CoT target first. This produces checkpoint `S0`, the starting point of the internalization curriculum.

The Stepwise-Internalization procedure then continues from this checkpoint; `S0` is not a separately chosen model.

Use the parent procedure as the default training recipe:

- AdamW;
- bf16;
- effective batch size 32;
- learning rate `1e-5` for the 7B-class GSM8K regime;
- removal smoothing `lambda = 4`;
- optimizer state reset whenever the scheduled removal count increments;
- removal rate `Delta = 8` for the large-model GSM8K regime.

Any necessary engineering deviation must be recorded before the affected run and cannot be chosen using J-space results.

---

## 6.2 Measurement validation set

Use two independent components.

### A. Flexible-reasoning positive control

Use the released Anthropic two-hop / multi-hop prompt set (`probe-swap` / released multi-hop evaluation material), restricted only by a predeclared clean-performance rule.

A prompt is retained if `S0` gives the correct clean answer under the frozen decoding protocol. The retained set is frozen before interventions are run.

Measure:

- clean answer score;
- J-space ablation answer score;
- matched non-J control answer score.

The construct is supported if J-space removal has a reproducible selective causal effect on this flexible-reasoning set beyond the matched control.

### B. General-processing control

Use held-out WikiText-103 sequences disjoint from the J-lens fit corpus.

Measure:

- next-token NLL;
- top-1 agreement with the clean model;
- response/continuation coherence where generation is used.

This quantifies generic model damage from the same intervention.

### C. Direct-vs-explicit GSM8K characterization

On a frozen subset of held-out GSM8K items, evaluate both:

- direct final-answer generation;
- explicit step-by-step generation.

The published workspace paper reports greater robustness for explicit CoT than direct answering on GSM8K. We record whether this qualitative relation reproduces on `S0`, but the ranking is **descriptive calibration**, not a requirement for the later trajectory.

The role of Phase B is to establish that `W_s` has a usable causal interpretation on the actual model family and intervention stack.

---

# 7. J-space intervention protocol

Primary intervention follows the published global-workspace ablation as closely as possible.

At every intervened `(token position, layer)`:

1. compute the clean activation;
2. rank J-lens directions by activation;
3. take the top `k = 10` eligible directions;
4. exclude any direction corresponding to a token in the clean model's top-10 imminent output tokens;
5. project out the activation component along the selected J directions;
6. continue the forward pass.

## Matched control

For each J intervention, construct a non-J control with:

- identical layers;
- identical token positions;
- identical number of removed directions;
- removed activation norm matched to the J intervention;
- directions sampled from the orthogonal / non-J residual component under a frozen random seed.

A sham/no-op condition is also logged for implementation auditing.

## Workspace layers

The primary layer band is fixed independently of the GSM8K trajectory.

For Qwen3-8B, public J-lens fits place the main workspace-like middle region approximately in layers `9–27` of the 36-layer model. E01 therefore uses:

> **primary fixed band: layers 9–27**

for all stages.

This prevents selecting a different favorable layer range after seeing task effects.

Because fine-tuning may shift the structural workspace, a preregistered secondary analysis estimates a checkpoint-specific band using the same frozen structural criterion and generic corpus. The scientific result must be qualitatively stable to this transport choice; a trajectory that appears only after selecting stage-specific favorable bands is unresolved.

---

# 8. Internalization trajectory

Continue training from `S0` using the published token-removal curriculum.

Save immutable checkpoints when the scheduled CoT-prefix removal first reaches:

| Stage | Scheduled removed CoT tokens | Normalized `I_s` |
|---|---:|---:|
| S0 | 0 | 0.000 |
| S1 | 8 | 0.205 |
| S2 | 16 | 0.410 |
| S3 | 24 | 0.615 |
| S4 | 32 | 0.821 |
| S5 | 39+ / all | 1.000 |

Do not move checkpoint locations based on validation curves or J-space behavior.

For every stage, freeze and store:

- model weights;
- optimizer state;
- training step / epoch;
- exact removed-token schedule;
- clean dev accuracy;
- mean/median generated reasoning length;
- final-answer format compliance.

---

# 9. Manipulation check: did internalization actually occur?

E01 requires a usable internalization trajectory before the mechanistic relation can be interpreted.

The following are manipulation checks, not directional hypotheses about workspace behavior.

A usable trajectory should show:

1. substantial reduction in visible reasoning across stages;
2. at least four registered stages with enough task competence to estimate causal damage;
3. the final stage producing answers with little or no explicit reasoning;
4. final-stage answer accuracy retaining a substantial fraction of Stage-0 performance.

Operationally, flag the trajectory as inadequate if either:

- `S5` retains less than 75% of `S0` exact-answer accuracy; or
- fewer than four of the six registered stages retain at least 70% of `S0` accuracy.

These thresholds are chosen to prevent interpreting intervention effects on checkpoints that have simply lost the task.

If the manipulation is inadequate, the Stepwise-Internalization implementation/training route is unresolved for this model. Do not reinterpret the collapse as evidence about automaticity.

---

# 10. Controlling the output-length confound

The stages deliberately differ in how many reasoning tokens they emit. Applying an intervention at every generated token therefore changes the number of intervention opportunities across stages.

E01 records two complementary causal quantities.

## 10.1 Task-level workspace dependence

Run the published-style J-space ablation throughout the model's stage-specific execution and score final-answer accuracy.

For stage `s`:

> **`W_task(s) = Acc_s(ctrl) - Acc_s(J)`**

This answers the operational question:

> how much does the task, as actually executed at this internalization stage, depend on J-space?

Because execution length is itself part of the learned procedure, this is scientifically meaningful, but it may combine per-step dependence with the number of opportunities for intervention.

## 10.2 Exposure-normalized local dependence

To separate those factors, run a second analysis with **single-position interventions**.

For each frozen evaluation trace:

- teacher-force the clean stage-specific trace;
- select eight preregistered relative positions at quantiles `{0.10, 0.20, 0.30, 0.40, 0.60, 0.70, 0.80, 0.90}` of the available computation trace, excluding the final answer token;
- at one selected position at a time, intervene across the full workspace layer band;
- compare J-space removal with the matched non-J control;
- measure change in the log probability of the next gold token.

For item `i`, stage `s`, position `p`:

> `d_{i,s,p} = logP_ctrl(next_gold) - logP_J(next_gold)`.

Define:

> **`W_local(s) = mean_{i,p} d_{i,s,p}`**.

Every stage contributes the same number of sampled positions per retained example, so `W_local` is not mechanically reduced by having a shorter visible chain.

The primary mechanistic interpretation of the trajectory uses `W_task` together with `W_local`:

- a change present in both is strong evidence that causal workspace reliance per unit computation changed;
- a change only in `W_task`, tracking response length while `W_local` stays stable, indicates that execution compression changed total exposure more than local dependence.

---

# 11. Measurement invariance across checkpoints

The J-lens itself can drift after fine-tuning. A fixed direction set from `S0` cannot be assumed to remain a valid measurement basis.

Primary procedure:

- fit a new Jacobian lens for every registered checkpoint;
- use the exact same 1,000 generic sequences and fitting code;
- keep the primary layer band fixed at 9–27;
- measure functional causal effects, not vector cosine similarity.

Two sensitivity analyses are preregistered:

1. **fixed-lens transport:** apply the `S0` lens where technically valid across later checkpoints;
2. **stage-specific structural band:** use the same independent band-identification criterion at every stage.

A trajectory that reverses sign or disappears under minor reasonable lens-transport choices is reported as measurement-sensitive rather than assigned a mechanistic interpretation.

---

# 12. Evaluation set and decoding

Primary trajectory evaluation uses the frozen GSM8K test set.

Before any J-space intervention result is viewed, freeze:

- prompt template;
- tokenizer version;
- greedy decoding configuration;
- maximum generation length;
- numerical-answer extraction regex;
- handling of commas, decimal forms, signs, units and malformed outputs.

Primary task score:

> **exact numerical final-answer accuracy.**

Continuous secondary score:

> final-answer token/string log probability under teacher forcing where well-defined.

No post-hoc switch from accuracy to log probability is allowed because one yields a more attractive trajectory. Both are logged from the start; accuracy is the primary behavioral endpoint and log probability supplies resolution for local intervention analyses.

---

# 13. Statistical analysis

All uncertainty is over independent problem instances.

Use paired item bootstrap with `10,000` resamples for:

- `W_task(s)`;
- `W_local(s)`;
- stage-to-stage differences;
- endpoint differences;
- the full stage curve.

The six stages are treated categorically in the primary analysis. A linear trend is reported as a compact summary, not assumed as the data-generating shape.

## Global relationship test

Test the null that workspace dependence is constant across registered stages using a paired permutation / bootstrap omnibus statistic over the six stage means.

## Meaningful-effect scale

After Phase B but before Phase C results are examined, define the smallest mechanistically meaningful change as:

> **`delta = 0.20 × |W_calibration|`**

where `W_calibration` is the selective J-space effect on the frozen flexible-reasoning positive control.

This ties resolution to the measured strength of the instrument instead of inventing an arbitrary percentage-point threshold.

The `delta` value is frozen before opening the internalization-trajectory results.

---

# 14. Outcome interpretation

The registered outcome space is deliberately broad.

## A. Workspace dependence decreases

A resolved decrease in `W_task` and `W_local` indicates that practice/internalization has shifted the task toward computation that is less reliant on the shared J-space.

This supports a form of mechanistic automaticization.

## B. Workspace dependence increases

A resolved increase indicates that visible reasoning can disappear while the computation becomes more reliant on silent workspace processing.

This would show that behavioral compression can move deliberation inward rather than compile it away.

## C. Non-monotonic trajectory

For example:

> low -> high -> low workspace dependence

would be consistent with a multi-stage transition in which explicit reasoning is first moved into latent workspace computation and only later compiled into a more automatic route.

A non-monotonic interpretation requires an interior stage to differ from both endpoints by at least `delta` with uncertainty resolving those contrasts.

## D. Resolved invariance

If internalization changes strongly while the entire workspace-dependence curve remains within the preregistered `±delta` equivalence region, behavioral internalization and workspace dependence are separable dimensions in this regime.

## E. Heterogeneous / measurement-sensitive trajectory

If effects differ substantially across items, lens transport choices, or task subfamilies without a resolved overall relation, report the heterogeneity. Do not force it into one of the four simple narratives above.

---

# 15. Route-stopping conditions

The scientific question remains meaningful across positive, negative, zero, and non-monotonic relations. The current experimental route becomes unusable when the relevant quantity cannot be identified.

Stop the registered route if any of the following occurs:

1. the J-space intervention cannot be distinguished from matched generic perturbation on the frozen flexible-reasoning calibration set;
2. J-space ablation causes such broad language-model destruction that a selective reasoning effect cannot be separated from generic damage;
3. the internalization curriculum fails the manipulation checks in Section 9;
4. confidence intervals remain wider than the preregistered meaningful-effect scale despite the planned frozen evaluation set;
5. the apparent trajectory depends qualitatively on one arbitrary lens-transport / workspace-band convention.

A route stop returns the mother question to the standing-problem bank. It does not turn an unresolved measurement into a substantive null result.

---

# 16. Minimal initial experiment sequence

Run in this order.

## E00-A — J-lens engineering smoke test

**Model:** `Qwen/Qwen3-8B`  
**Lens:** public pre-fitted Qwen3-8B J-lens  
**Data:** released Anthropic multi-hop examples + held-out generic text

Deliverables:

- clean / J-ablation / matched-control outputs;
- removed activation norm audit;
- output-token exclusion audit;
- deterministic rerun hash.

No training.

## E00-B — build Stage 0

**Model:** `Qwen/Qwen3-8B-Base`  
**Training:** explicit-CoT GSM8K stage using the frozen Stepwise-Internalization data and recipe.

Deliverables:

- Stage-0 checkpoint;
- clean dev/test accuracy;
- reasoning-token distribution;
- exact training manifest.

## E00-C — fit Stage-0 J-lens and validate the causal axis

Fit the 1,000-sequence lens on `S0`.

Run:

- frozen multi-hop positive control;
- held-out WikiText general-processing control;
- frozen direct-vs-explicit GSM8K characterization.

Freeze `W_calibration` and therefore `delta`.

## E01 — internalization trajectory

Continue the single training run and save `S1`–`S5` at the registered removal counts.

For each stage:

1. fit its J-lens on the identical generic corpus;
2. run clean / J / matched-control task evaluation;
3. compute `W_task`;
4. run the eight-position local intervention protocol;
5. compute `W_local`;
6. bootstrap the six-stage trajectory.

No second task, model family, RL stage, OOD experiment or model-zoo expansion is authorized by this preregistration.

---

# 17. Closest-work boundary relevant to E01

These works constrain interpretation and are recorded before running the experiment.

### Gurnee et al. (2026) — Verbalizable Representations Form a Global Workspace in Language Models

Provides the J-lens/J-space measurement and evidence that flexible reasoning is selectively J-space-dependent while routine processing can proceed with much less dependence.

### Deng, Choi & Shieber (2024) — From Explicit CoT to Implicit CoT

Provides the controlled internalization trajectory used here. It leaves probing the internal process across internalization stages as an open direction.

### Wu et al. (2026) — J-CoT: Chain-of-Thought in J-Space

Shows that J-space itself can be used as a recurrent latent reasoning interface. It strengthens the plausibility that J-space can carry hidden intermediate reasoning, while leaving the training trajectory of ordinary autoregressive internalization unmeasured.

### Kshirsagar (2026) — The Weight of Silence

Causally intervenes on latent thought vectors before/after an RL stage in a chess model and finds that latent thoughts can behave more like training scaffolding than an inference-time scratchpad. This makes causal dependence, rather than mere latent-state presence, essential for E01.

The registered claim remains the relationship between a controlled explicit-to-implicit training trajectory and dependence on an independently defined shared workspace.

---

# 18. Reproducibility contract

Every run must write a machine-readable manifest containing:

- git commit;
- model and tokenizer revision;
- dataset hashes / example IDs;
- stage / removed-token schedule;
- optimizer and scheduler state;
- random seeds;
- lens-fit corpus IDs;
- fitted-lens hash;
- workspace layers;
- intervention `k`;
- random-control seed;
- decoding settings;
- raw per-item clean/control/J scores.

Raw results are append-only. Summary scripts must regenerate every reported table and interval from those raw records.

---

# 19. Decision after E01

E01 does not authorize a full paper automatically.

If the relationship is resolved, return to Selection and ask whether the result has sufficient scientific magnitude and independence to justify a broader study. Candidate expansions may include an independent natural reasoning task, another internalization route, or testing whether reduced workspace dependence trades off against flexible recombination/OOD behavior.

Those are future selection questions, not part of this preregistration.
