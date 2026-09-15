# L44 — Does Internalization Produce Automaticity?

**Status:** `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`  
**Date:** 2026-09-15  
**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS

## RQ

> **As training compresses an explicitly multi-step reasoning procedure into fewer or no overt reasoning steps, does the learned computation become less causally dependent on the model's shared internal workspace — or does deliberation merely move from visible tokens into latent workspace state?**

Short form:

> **When reasoning disappears, does it actually become automatic?**

The scientific object is a relationship between two notions that recent work often conflates:

1. **behavioral / computational internalization** — the same task is executed with fewer generated reasoning steps, lower runtime, or a direct answer;
2. **mechanistic automaticity** — the task no longer causally depends on a shared flexible-reasoning workspace.

The project asks whether these quantities co-vary during learning.

---

# 1. Why this is an important standing problem

Skill acquisition has long distinguished deliberate, resource-demanding computation from practiced computation that can run automatically. LLM research has independently begun using the same vocabulary:

- *Distilling System 2 into System 1* calls successful direct generation after System-2 distillation `System 1`;
- stepwise / implicit-CoT work calls the disappearance of explicit intermediate tokens `internalization`;
- *Scaling Competence, Shrinking Reasoning* interprets the late disappearance of reasoning tokens during task-specific fine-tuning as task internalization;
- *Learning through Internalization* formally defines internalization as reconfiguring a slow multi-step procedure into a faster program in the same hypothesis class.

These are meaningful notions of compression, but they do not identify whether the resulting computation is **automatic** in a mechanistic sense.

A direct one-pass answer could arise in at least two qualitatively different ways:

- **latent deliberation:** the model still assembles and manipulates intermediate state in a shared internal workspace, but no longer externalizes it;
- **compiled / automatic computation:** training has moved the operation into a specialized route that no longer needs the shared workspace.

The distinction matters before introducing any particular interpretability tool. It determines what researchers are entitled to infer from phrases such as `System 1`, `internalized reasoning`, `compiled reasoning`, and `direct answer`.

---

# 2. Why now: a missing causal quantity became measurable

## A. Internalization trajectories already exist

Deng et al. (2024), *From Explicit CoT to Implicit CoT: Learning to Internalize CoT Step by Step*  
https://arxiv.org/abs/2405.14838

starts from explicit CoT and progressively removes intermediate steps during fine-tuning. This gives an unusually clean **training axis** from externalized reasoning toward direct computation.

Huang et al. (2026), *Transformers Provably Learn to Internalize Chain-of-Thought*  
https://arxiv.org/abs/2605.28600

provides theory and experiments showing reasoning can be progressively absorbed into hidden computation across training stages.

Tsilivis et al. (2026), *Learning through Internalization*  
https://arxiv.org/abs/2606.20937

formalizes internalization as replacing a slow procedure with a faster program, studies how representations change, finds that wider architectures can internalize better than deeper ones, and shows internalization can reduce OOD performance through shortcut solutions.

These works establish the **internalization axis**, but not workspace dependence.

## B. J-space supplies an operational causal definition of automaticity

Gurnee et al. (2026), *Verbalizable Representations Form a Global Workspace in Language Models*  
https://transformer-circuits.pub/2026/workspace/index.html

identifies a small shared J-space used for reportable, flexible, and silent reasoning. The paper explicitly proposes **J-space independence as an operational definition of automaticity in a language model**.

Its most important clue for L44 is that GSM8K answered **directly** is substantially more vulnerable to J-space ablation than the same problems solved with explicit CoT. The authors interpret the explicit steps as externalizing information that the direct-answer model would otherwise need to carry in its internal workspace.

Therefore:

> **fewer visible reasoning tokens do not imply less internal deliberation.**

The paper is cross-sectional. It does not ask how workspace dependence changes as a skill is learned or internalized.

## C. Open-weight instrumentation now exists

Anthropic released the Jacobian-lens reference implementation:

https://github.com/anthropics/jacobian-lens

It fits the lens on open-weight decoder-only Transformers and includes Qwen examples. This makes a longitudinal checkpoint study technically possible without relying on closed Claude activations.

---

# 3. Closest-owner audit

## Distilling System 2 into System 1 (Yu et al., 2024)

Owns the behavioral / efficiency statement:

> System-2 outputs can be distilled so the model responds directly without intermediate reasoning tokens.

It operationalizes System 1 by the absence of the intermediate sequence, not by an internal causal computation criterion.

**Does not own:** whether the direct computation still depends on a shared reasoning workspace.

## From Explicit CoT to Implicit CoT (Deng et al., 2024) + implicit-CoT lineage

Owns stepwise removal of overt reasoning while preserving task performance and explicitly aims to move reasoning into hidden states.

**Does not own:** whether those hidden states use a shared flexible workspace or a workspace-independent automatic route.

## Scaling Competence, Shrinking Reasoning (Singh et al., 2025)

Owns the natural training trajectory `reasoning grows -> becomes effective -> shrinks`, with performance retained after overt reasoning is removed.

**Does not own:** where the computation goes internally after the reasoning tokens disappear.

## Transformers Provably Learn to Internalize CoT (Huang et al., 2026)

Owns a theoretical / algorithmic account in which implicit reasoning is absorbed into deeper hidden computation.

**Does not own:** a causal automatic-vs-workspace distinction in trained LLMs.

## Learning through Internalization (Tsilivis et al., 2026) — strongest owner risk

This is the most serious parent. It already asks how network representations evolve during internalization and whether explicit reasoning is mirrored vertically or replaced by shortcuts / parallel computation. It also uses automaticity as motivating intuition and shows an OOD cost of deeper internalization.

However its formal quantity is **runtime / step compression**: a new program internalizes the old one if it agrees with the slow procedure and executes faster. Its empirical mechanism questions concern vertical representation, architecture, shortcuts, and OOD generalization.

It does **not** identify whether the final fast program remains causally dependent on a globally shared flexible-reasoning workspace.

L44 therefore does not ask another version of `what representations emerge during internalization?`. It asks a sharper relation between two independently defined quantities:

> **Does computational internalization imply mechanistic automaticity?**

## Global Workspace / J-space (Gurnee et al., 2026)

Owns the causal distinction between J-space-dependent flexible reasoning and J-space-independent automatic computation, including the direct-vs-explicit GSM8K dissociation.

Its training experiments study post-training effects on workspace contents and reflection training. It does not trace a skill as it is progressively internalized.

## J-CoT / latent-working-memory methods (2026)

Use J-space or other latent memory as a *method* for reasoning without overt CoT.

They reinforce the possibility that hidden deliberation survives token removal. They do not measure whether ordinary skill internalization moves computation toward or away from workspace dependence.

### Novelty verdict

> **NO EXACT OWNER FOUND as of 2026-09-15.**

But the space is close to two very recent frontiers. The paper identity is valid only if it remains the **relationship between runtime internalization and causal workspace dependence**. It must not collapse into `apply J-lens to implicit CoT` or `visualize hidden reasoning during training`.

---

# 4. Why this is exploratory rather than a phenomenon gamble

Let internalization stage be `s` (for example the fraction / number of explicit CoT steps removed during a fixed curriculum).

At each checkpoint define a causal workspace-dependence quantity:

> `W_s = task damage from J-space ablation - damage from matched non-J perturbation`.

The primary object is the **trajectory / relationship `W_s` as reasoning is internalized**, not the existence of one lucky anomaly.

Every resolved direction is scientifically interpretable:

1. **W decreases with internalization**  
   Training genuinely automatizes the computation: compressed reasoning migrates away from the shared workspace.

2. **W increases with internalization**  
   Overt reasoning disappeared, but deliberation became *more* internally workspace-dependent. `Direct` / `System 1` behavior is not mechanistic automaticity.

3. **W is non-monotonic**  
   Skill acquisition may pass through a latent-deliberation stage before later compilation into an automatic route.

4. **W stays precisely constant despite large behavioral internalization**  
   Runtime/token compression and workspace dependence are largely orthogonal properties.

5. **task-dependent slopes**  
   Some computations are compilable into automatic routes while others remain workspace-bound; this creates a second-stage question about what task structure predicts automatizability.

The pilot fails only if the internalization trajectory is not behaviorally real, the J-space intervention cannot be validated on the chosen open model, or the causal estimate is too noisy to resolve the relationship.

---

# 5. Scientific consequences

## If direct/internalized reasoning remains workspace-dependent

- current behavioral uses of `System 1` and `automatic` need a mechanistic qualification;
- latent CoT and compiled reasoning should be distinguished rather than grouped as the same phenomenon;
- reducing visible reasoning tokens may reduce latency without reducing internal deliberative computation;
- the disappearance of CoT cannot be used as evidence that reasoning has become routine or specialized.

## If workspace dependence falls during internalization

- the System-2-to-System-1 metaphor gains a concrete causal substrate;
- training can reorganize a computation from shared flexible workspace use into specialized automatic processing;
- this provides a mechanistic account of why practiced skills can execute cheaply.

## If automaticity predicts OOD/flexibility loss

A strong C2 would connect the J-space result that shared workspace supports flexible computation with the internalization result that OOD performance can degrade. This could yield a broader law:

> **automaticity trades flexible reuse for cheap execution.**

This is a second-stage hypothesis, not part of the E01 pass condition.

---

# 6. Instrument / validity risk

This is the candidate's largest risk.

The original global-workspace results were established primarily on Claude. Anthropic's open implementation supports open-weight decoders, and independent open-model replications exist, but the full **causal automatic-vs-deliberate dissociation** must be demonstrated on the exact model before any longitudinal claim is trusted.

There is also at least one independent open-model replication reporting that some claimed J-lens legibility advantages weaken under matched controls. That does not refute the causal J-space result, but it is enough to forbid treating the instrument as automatically validated.

Therefore **E01 begins with an instrument gate** rather than with the training experiment.

---

# 7. Main-level growth path

E01 is only a falsification / identification pilot.

A credible Main-level paper would need:

1. a validated causal workspace measure on at least one open model;
2. a controlled internalization trajectory showing a resolved `internalization -> workspace dependence` relation;
3. replication on a second task or second independently trained trajectory;
4. if supported, a principled account of when automaticity emerges and whether it trades off with flexible/OOD use.

The full-paper identity must survive removing all visualizations of J-space contents. The core result is causal dependence, not interpretability aesthetics.

---

# 8. Selection verdict

| criterion | verdict |
|---|---|
| Independent importance | **PASS** — distinguishes two scientific notions of learned skill compression |
| Scientific consequence | **PASS** — changes what `System 1` / `internalized reasoning` means mechanistically |
| Genuine uncertainty | **PASS** — recent parents support both latent-workspace and compiled-shortcut accounts |
| Why now | **PASS** — controlled internalization trajectories + causal workspace intervention now coexist |
| Exploration vs gamble | **PASS** — estimates a trajectory; positive/zero/negative/non-monotonic are interpretable |
| Exact owner | **NO EXACT OWNER FOUND**, with Tsilivis et al. 2026 as strongest adjacent owner |
| Instrument validity | **OPEN RISK — MUST PASS FIRST** |
| Feasibility | **HIGH for E01**, provided J-space positive controls reproduce |
| Main-level growth | **PLAUSIBLE**, not yet established |

## Decision

> **L44 — `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.**

The authorized experiment is specified in `E01_PREREGISTRATION.md`. Do not broaden into generic latent-CoT interpretability, System-1/System-2 benchmarking, or another post-training feature-drift study.