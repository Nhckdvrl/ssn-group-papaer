# L44 — Local Agent Execution Protocol

**Role:** execution guide for the local research agent  
**Scope:** `L44_REASONING_AUTOMATICITY`, currently authorized only through E01  
**Read first:** `SELECTION.md` and `E01_PREREGISTRATION.md`

---

# 1. Mission

The local agent is responsible for turning the preregistered L44 question into a trustworthy experiment, not for mechanically replaying a brittle list of commands.

The scientific target is:

> **measure how causal dependence on a shared verbalizable workspace changes as an explicitly multi-step reasoning procedure is progressively internalized during training.**

The primary object is the relationship

> `internalization stage -> workspace dependence`.

The experiment is exploratory with respect to the direction and shape of that relationship. A decreasing, increasing, invariant, heterogeneous, or non-monotonic trajectory may all be scientifically meaningful if the quantity is identified cleanly.

The agent should therefore optimize for **valid inference**, not for reproducing a hoped-for curve, a parent-paper number, or a visually attractive mechanistic story.

---

# 2. Researcher mode, not script mode

The preregistration fixes the scientific contract. It cannot predict every implementation issue, library mismatch, GPU constraint, model quirk, data-format problem, or numerical failure.

When reality differs from the document, the agent should diagnose the problem and choose the smallest scientifically safe repair.

Use this rule:

> **Preserve the scientific quantity and comparison; adapt the implementation.**

Do not follow a literal step when doing so would obviously measure the wrong thing. Do not abandon a valid comparison merely because the exact command, tensor location, batch size, public artifact, or parent-paper implementation differs from expectation.

At the same time, flexibility does not permit result-driven redesign. Once outcome-bearing data have been inspected, changes that alter the estimand, treatment, comparison group, evaluation set, or stage definition require explicit re-registration and must not be silently folded into the primary analysis.

---

# 3. Scientific contract: preserve these invariants

These are the load-bearing parts of E01. Engineering decisions may change around them; these should not drift silently.

## 3.1 Question

The experiment must remain about the relationship between **controlled internalization** and **causal workspace dependence**.

Do not turn the project into:

- a descriptive J-lens visualization study;
- another latent-CoT representation paper;
- a benchmark of direct vs CoT prompting;
- a generic post-training feature-drift study;
- an OOD paper before E01 is resolved;
- a search for one spectacular checkpoint transition.

## 3.2 Independent variable

The primary internalization coordinate is the training intervention / scheduled CoT-prefix removal defined in the preregistration.

The agent may repair data parsing, token accounting, or curriculum implementation, but may not relocate registered stages after seeing workspace results.

If the parent implementation makes the nominal `{0,8,16,24,32,39+}` schedule technically inapplicable to the released data/model, preserve the intended progression and document the exact mapping before opening J-space trajectory results. Prefer a principled mapping over forcing nominal numbers that no longer mean the same thing.

## 3.3 Primary causal quantity

Workspace dependence must remain a **selective causal effect relative to a matched non-J perturbation**, not raw damage from deleting activations.

The comparison must continue to answer:

> how much additional task effect is caused by removing J-space directions beyond a perturbation of comparable generic severity?

If the exact control construction proves technically invalid, repair the matching procedure rather than dropping the control.

## 3.4 Longitudinal design

The core evidence is a trajectory across multiple predeclared stages from one controlled training process. An endpoint-only comparison is insufficient unless an unforeseen technical fact makes intermediate checkpoints genuinely unrecoverable; such a change requires re-registration before interpretation.

## 3.5 Held-out evaluation

The frozen GSM8K test set must not be used to tune training, choose workspace layers, choose J-lens settings, select favorable stages, or debug answer extraction after outcome inspection.

Use training/dev/smoke subsets for engineering.

## 3.6 Raw evidence

Raw per-item results are append-only. Never overwrite an inconvenient run. Mark superseded/invalid runs with a reason and keep them available.

---

# 4. What the agent may change autonomously

The following are implementation choices. The agent should use judgment and may change them without asking for approval when necessary, provided the scientific comparison remains intact and the change is logged.

Examples include:

- code organization, modules, scripts, CLI layout and file names;
- PyTorch / Transformers / CUDA implementation details;
- eager vs compiled kernels;
- FlashAttention availability;
- tensor-parallel, FSDP, DeepSpeed, DDP or single-node execution;
- micro-batch size, gradient accumulation, activation checkpointing;
- dataloader workers, caching, sharding and local staging;
- checkpoint serialization format;
- mixed-precision details needed for numerical stability;
- chunk size used to fit the Jacobian lens;
- equivalent APIs for hooks or residual-stream access;
- exact implementation of deterministic answer parsing, provided the rule is frozen before primary outcomes are opened;
- smoke-test sample sizes;
- retrying failed jobs;
- fixing off-by-one token alignment, masking, padding, EOS, BOS or chat-template bugs;
- correcting a parent-code incompatibility with the current library version;
- replacing a missing public artifact with a faithful local reproduction;
- using a smaller engineering subset before the registered full run;
- changing non-scientific logging/monitoring infrastructure;
- memory-saving transformations that are numerically checked against a small reference run.

When choosing among equivalent implementations, prefer the one that is easiest to audit and rerun, not the cleverest one.

---

# 5. What the agent may repair, but must document carefully

Some problems sit between engineering and science. The agent may resolve them, but must explicitly write the rationale in the local decision log before using the repaired procedure for primary results.

Typical examples:

### 5.1 Parent recipe does not reproduce on Qwen3-8B

Do not mechanically insist on a learning rate or batch schedule that clearly fails because the parent used a different architecture/data implementation.

First diagnose whether the failure is caused by:

- tokenization / target construction;
- optimizer-scale mismatch;
- effective batch mismatch;
- sequence truncation;
- instruction/chat formatting;
- loss masking;
- wrong reset semantics;
- numerical instability;
- genuine model-family sensitivity.

Engineering and optimization repairs may be selected on train/dev data only. The goal is to obtain a real controlled internalization trajectory, not to reproduce the parent's exact accuracy.

If multiple reasonable recipes work, choose one before opening workspace-trajectory results and freeze it.

### 5.2 Released Stepwise data differ from the description

Inspect the actual dataset. Reconstruct the intended variable: progressive removal of externally visible intermediate reasoning while preserving the question/final target relation.

Do not blindly treat a token count as meaningful if the release encodes steps differently.

Record:

- original format;
- transformation performed;
- number of affected examples;
- examples before/after transformation;
- hash of the final frozen training data.

### 5.3 J-space tensor location differs from reference code

Use the semantically corresponding residual-stream state in Qwen. Verify on a small batch that the hook location reproduces the expected forward pass exactly when no intervention is applied.

A hook with non-zero no-op error is a bug until explained.

### 5.4 Norm matching is imperfect

Improve the matched-control construction until generic perturbation severity is genuinely comparable. Exact equality is not always numerically possible; quantify residual mismatch instead of pretending it is zero.

If control construction changes, rerun the affected calibration measurements under the same new construction.

### 5.5 Stage-specific traces become very short

The preregistered relative-position local analysis assumes enough non-answer positions exist. If late stages contain fewer usable positions, do not fabricate duplicate positions merely to retain eight samples.

Choose a deterministic rule before inspecting J effects, for example using all distinct eligible quantile positions and reporting the count. Preserve equal weighting across items/stages as much as possible and add a sensitivity analysis on the common set of available quantiles.

### 5.6 Exact-answer parsing fails on real outputs

Fix parsing using clean outputs only, preferably on train/dev examples. Freeze the parser before reading intervention comparisons. Keep raw strings so every score can be audited.

---

# 6. Changes that require re-registration before interpretation

If a change alters what scientific statement the experiment estimates, stop and write a short amendment before proceeding with outcome-bearing analysis.

Examples:

- changing the primary model after seeing its L44 trajectory;
- replacing GSM8K with a different task as the primary trajectory;
- changing the internalization intervention from stepwise removal to a qualitatively different training method;
- choosing checkpoints because their J-space result looks interesting;
- selecting workspace layers using GSM8K intervention outcomes;
- changing the main causal comparison from J-vs-matched-control to another estimand;
- removing the matched control;
- changing the primary evaluation split after viewing results;
- changing the primary outcome because another metric gives a cleaner curve;
- adding a second model/task and then redefining the original study around whichever one looks strongest;
- defining a subgroup only after discovering an effect concentrated there and treating it as confirmatory.

For an amendment:

1. freeze and commit all data already observed;
2. state the problem that forced the change;
3. state which original inference is no longer valid;
4. define the new procedure before viewing new primary outcomes;
5. keep old and new analyses separately labeled.

The local agent may author this amendment itself. It does not need to stop working merely because the original document was incomplete; it does need to preserve provenance.

---

# 7. Result-independent debugging discipline

When something fails, debug against **mechanical invariants**, not against the desired scientific result.

Good debugging targets:

- clean logits match before/after installing a no-op hook;
- gradients/loss masks match a small hand calculation;
- checkpoint stage labels match actual removed-token schedules;
- J projection mathematically removes the intended component;
- control projection removes comparable norm;
- deterministic decoding reproduces bit-for-bit or within documented numerical tolerance;
- answer parser matches human inspection;
- lens fitting uses exactly the frozen corpus IDs;
- train/dev/test contamination checks pass;
- public/reference examples reproduce at least at the level required to validate the implementation.

Bad debugging target:

> keep changing the setup until `W_direct > W_CoT`, until `W_s` decreases, or until a paper-like curve appears.

A scientifically surprising pattern is data, not a bug, once implementation invariants pass.

---

# 8. How to handle unexpected findings

Unexpected results are expected in this project. Use the following decision procedure.

## Case A — obvious implementation inconsistency

Example: no-op hooks change logits, control norms are wrong, answer extraction fails.

**Action:** repair and rerun. Mark previous runs invalid with a concrete reason.

## Case B — parent-paper number does not replicate, but our measurement is internally valid

Example: direct-vs-CoT ordering differs from Anthropic while J ablation still shows selective causal effects beyond matched controls.

**Action:** do not force replication. Treat the parent result as calibration evidence and continue if the workspace-dependence construct remains identifiable. Record the discrepancy.

## Case C — intervention causes broad generic destruction

**Action:** investigate strength, hook location, output-token exclusion and control matching using calibration data only. If no selective causal axis can be established, stop the J-space route. Do not interpret generic damage as automaticity.

## Case D — internalization trajectory behaves differently from the parent

Example: performance rises then falls, direct stage is weaker, removal occurs at a different rate.

**Action:** first determine whether a genuine internalization manipulation occurred. If there is a usable multi-stage reduction in visible reasoning with retained competence, the exact parent curve need not replicate. If task competence collapses, repair the training route or mark it unresolved.

## Case E — `W_s` is flat

**Action:** quantify precision. A precise flat trajectory is a substantive outcome; a wide interval is unresolved. Do not search for a new layer band or metric solely to manufacture variation.

## Case F — `W_s` is non-monotonic

**Action:** preserve the full registered trajectory. Check whether the pattern survives the preregistered measurement-sensitivity analyses. Do not reduce it to a chosen pair of checkpoints.

## Case G — one control reveals a new confound not anticipated in the preregistration

**Action:** characterize the confound on data that do not require opening new primary outcomes. Add the minimal control needed to separate the competing explanations. Label it as an amendment/sensitivity analysis depending on whether it changes the primary estimand.

The agent is encouraged to add controls when they close a real identification hole. It should not add arbitrary analyses merely because the current result is aesthetically weak.

---

# 9. Execution order is a dependency graph, not a ritual

The nominal sequence is:

> `E00-A implementation -> E00-B Stage 0 -> E00-C measurement calibration -> E01 trajectory`.

Preserve the **logical dependencies**, but the agent may interleave engineering work when efficient.

For example:

- download/freeze datasets while J-lens code is being validated;
- write training and evaluation infrastructure in parallel;
- smoke-test J-lens fitting on 100 sequences before S0 is ready;
- validate answer parsing on clean base-model outputs early;
- precompute frozen corpus IDs and hashes before training.

Do not open E01 trajectory outcomes before the calibration choices that depend on `S0` are frozen.

The important ordering constraint is epistemic:

> decisions that define the measurement must be made before seeing the results that those decisions could favor.

---

# 10. Suggested local workspace

The agent may alter this layout if the repository already has a better convention, but keep provenance clear.

```text
candidates/L44_REASONING_AUTOMATICITY/
  SELECTION.md
  E01_PREREGISTRATION.md
  AGENT_EXECUTION.md
  notes/
    AGENT_DECISIONS.md
    E00_A_REPORT.md
    E00_B_REPORT.md
    E00_C_REPORT.md
    E01_REPORT.md
  configs/
  scripts/
  src/
  data_manifest/
  results/
    raw/
    derived/
  runs/
```

`raw/` should be immutable per run ID. `derived/` can be regenerated.

The agent should create `notes/AGENT_DECISIONS.md` on first execution and append short timestamped entries for nontrivial deviations.

Suggested entry format:

```markdown
## YYYY-MM-DD HH:MM — short decision title

Observed:
...

Diagnosis:
...

Decision:
...

Scientific invariant preserved:
...

Could this affect interpretation?
...

Files/runs affected:
...
```

Do not log every shell command. Log decisions a future reviewer would need in order to understand why the actual experiment differs from the preregistration.

---

# 11. Run discipline

Every non-smoke run should have a stable run ID and machine-readable manifest.

At minimum record:

- git commit;
- dirty working-tree diff or explicit `clean=true`;
- hostname / GPU type;
- model/tokenizer revision;
- dataset IDs/hashes;
- seed;
- training stage;
- all optimizer/scheduler parameters;
- exact command/config;
- lens hash;
- fit-corpus IDs;
- hook location;
- workspace layers;
- intervention `k` and exclusion rules;
- control construction and random seed;
- decoding config;
- output parser version;
- raw-output path.

Do not rely on memory or terminal history.

Before deleting a checkpoint or large artifact for disk reasons, preserve the manifest, code revision, metrics and enough information to regenerate it. Registered S0–S5 weights should be preserved until E01 is reviewed unless storage makes this impossible.

---

# 12. Compute and efficiency judgment

Use cheap information first.

Before launching expensive training or lens fitting, run the smallest test that can reveal:

- shape mismatch;
- hook incompatibility;
- broken masking;
- parser failure;
- non-determinism;
- numerical instability;
- impossible memory use;
- obviously incorrect curriculum behavior.

Scale only after these pass.

The agent may change the compute implementation aggressively to fit available hardware, including distributed strategy and micro-batching. Do not change the scientific sample or comparison merely to make a job convenient unless the corresponding power/precision consequence is explicitly assessed.

If a planned full measurement becomes much more expensive than expected, estimate the achievable confidence interval / resolution before spending the compute. A route that cannot resolve the registered effect scale should be reported as a feasibility problem rather than run blindly.

---

# 13. Literature and code lookup during execution

The agent is allowed and encouraged to inspect:

- official parent repositories;
- current library documentation;
- open issues / implementation notes;
- exact model configs;
- newer papers that directly affect the validity of the instrument or design.

Use new literature to repair interpretation or catch an owner/validity problem. Do not continuously redesign E01 around every new paper.

If a new paper published during execution directly owns the L44 scientific statement, or invalidates J-space as the intended construct, stop interpretation and return to Selection before spending more compute.

---

# 14. Completion criteria for each phase

## E00-A complete when

The J-lens code path is mechanically trustworthy: clean/no-op equivalence, projection math, matched control, output exclusion and deterministic rerun have all been audited on the public setup.

Exact reproduction of every parent effect size is not required.

## E00-B complete when

A frozen S0 exists with a documented explicit-CoT training recipe and sufficient GSM8K competence to support the planned causal measurement.

If S0 is weak, diagnose the training implementation on dev data before proceeding.

## E00-C complete when

The actual S0 model has a usable selective workspace-dependence measurement: J-space intervention is distinguishable from matched generic damage on the frozen reasoning calibration set, generic-language damage is quantified, and all measurement choices needed for E01 are frozen.

The direct-vs-explicit ordering is descriptive calibration, not an admission criterion.

## E01 complete when

All usable registered stages have:

- frozen checkpoint identity;
- clean behavioral measurements;
- checkpoint-specific lens fit;
- clean / J / matched-control task measurements;
- `W_task`;
- exposure-normalized `W_local`;
- raw per-item records;
- registered uncertainty analyses.

Then write `E01_REPORT.md` from raw results before starting any new model/task/OOD expansion.

---

# 15. What counts as a route failure

A route failure is an **identification or feasibility failure**, not an inconvenient scientific answer.

Examples:

- the J-space intervention cannot be separated from generic matched damage;
- the model cannot be trained into a usable multi-stage internalization trajectory after reasonable, dev-only repair;
- the measurement is too noisy to distinguish meaningful changes at the available sample/compute scale;
- the trajectory is qualitatively determined by arbitrary lens-transport choices;
- a newly discovered technical fact means `W_task/W_local` no longer measure the intended construct.

If this happens, produce a concise failure report with reusable assets and return the mother question to Selection/standing-problem status.

Do not invent a nearby paper from whichever incidental anomaly appeared during debugging.

---

# 16. Final operating principle

When uncertain, ask:

> **If I make this change, am I improving our ability to estimate the same scientific relationship, or am I changing the question after seeing the answer?**

If it is the first, make the repair, document it, and continue.

If it is the second, freeze what has been observed and re-register before proceeding.

The preregistration is a protection against outcome-driven reasoning. It is not a substitute for scientific judgment.