# CT04 — What Can Hybrid Memory Safely Learn? Operation-Level Plasticity in Recurrent-Attention LMs

**Status:** PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Primary target:** ICLR / ICML / NeurIPS; ACL/EMNLP Main is plausible if the story centers language post-training and long-context behavior.  
**Core mode:** exploratory diagnosis first → method only if a stable plasticity boundary exists.  
**Resource envelope:** 4×/8× RTX PRO 6000 96GB; Qwen3.5-0.8B/2B pilot, 4B confirmation; no pretraining from scratch.

---

# 1. Mother question

Modern hybrid LMs such as Qwen3.5 do not have one homogeneous attention block. Most layers maintain a fixed-size recurrent memory using Gated DeltaNet (GDN), interleaved with a minority of full-attention layers.

Recent PEFT evidence creates a puzzle:

- adapting the **whole recurrent backbone** of sequential hybrid Qwen3.5 can be destructive;
- adapting recurrent **state** can nevertheless be extremely effective;
- causal cache interventions show that recurrence and full attention carry sharply different kinds of information.

CT04 asks:

> **Within a pretrained hybrid recurrent memory, which memory operations are plastic under post-training and which are load-bearing?**

For Gated DeltaNet, the question is operational:

> When fine-tuning fails, is the destructive update concentrated in **addressing / read**, **decay / retention**, **erase-write strength**, **content/value write**, or **output/readout** — and can we exploit that structure to obtain better adaptation without corrupting the model's memory contract?

The answer is deliberately not assumed in advance.

---

# 2. Why this question exists now

## 2.1 Native hybrids are now a real post-training object

Qwen3.5-4B has 32 language layers arranged as 8 × [3 × Gated DeltaNet + 1 × full attention], with a native context length of 262K.

Official base and post-trained checkpoints exist at multiple sizes:
https://huggingface.co/Qwen/Qwen3.5-4B-Base

The broader frontier also includes Kimi Linear / KDA and Falcon-H1 / Mamba hybrids.

The practical question is no longer only whether hybrid attention should be pretrained. It is how already-pretrained hybrid memory should be adapted.

## 2.2 Component-level adaptation exposes a real failure

**Where Should LoRA Go? Component-Type Placement in Hybrid Language Models**  
arXiv:2604.22127

Across Qwen3.5-0.8B (sequential GDN + attention) and Falcon-H1-0.5B (parallel Mamba + attention), the paper reports:

- attention-only LoRA is consistently parameter-efficient;
- recurrent-only adaptation is **destructive** in sequential Qwen3.5;
- recurrent-only adaptation is **constructive** in parallel Falcon-H1;
- sequential hybrids exhibit stronger catastrophic forgetting.

But "the recurrent backbone is rigid" is too coarse. GDN contains multiple qualitatively different memory operations.

## 2.3 State-based adaptation gives the opposite signal

**State-offset Tuning: State-based Parameter-Efficient Fine-Tuning for State Space Models** — ACL 2025  
https://aclanthology.org/2025.acl-short.36/

and:

**S0 Tuning: Zero-Overhead Adaptation of Hybrid Recurrent-Attention Models**  
arXiv:2604.01168

show that recurrent state itself is a powerful adaptation surface. S0 Tuning freezes Qwen3.5 weights and tunes recurrent initial states, obtaining large HumanEval gains from very little verified data.

Thus recurrent weight adaptation can be brittle while recurrent computation remains highly adaptable. This suggests a distinction between changing the state / operating point and changing the transition / addressing / write dynamics that define how memory works.

## 2.4 The two memory channels have different functional contracts

**What Attention Recalls and Recurrence Controls in Hybrid Language Models**  
arXiv:2609.04434

uses Split-prefill and State-swap interventions on Qwen3.5 and Falcon-H1 and finds a strong functional split:

- exact retrieval follows the full-attention KV cache;
- language / persona / behavioral mode follows recurrent state much more strongly.

It does not ask which recurrent memory operations can be changed safely during post-training.

## 2.5 Fine-tuning can silently damage hybrid memory

**Attention Amnesia in Hybrid LLMs: When CoT Fine-Tuning Breaks Long-Range Recall, and How to Fix It** — EMNLP 2026  
arXiv:2606.11052

shows that CoT-SFT can dramatically damage long-context recall in distilled hybrid LMs and localizes much of the failure to W_Q/W_K drift in retained softmax-attention layers.

This is a key precedent: adaptation failure can be highly localized inside a memory mechanism.

---

# 3. The recurrent memory is not one module

A simplified Gated DeltaNet update is:

S_t = alpha_t (I - beta_t k_t k_t^T) S_{t-1} + beta_t k_t v_t^T,
and o_t = S_t^T q_t.

This exposes distinct operations:

- **k / addressing:** which memory direction is corrected or written;
- **q / read:** how the recurrent state is queried;
- **v / content:** what is written;
- **alpha / retention:** how much old state survives;
- **beta / erase-write strength:** update strength;
- **output/gating path:** how recurrent readout enters the residual stream.

Qwen3.5 exposes partially separable projection paths including fused in_proj_qkv, decay-related in_proj_a, write-strength in_proj_b, in_proj_z, and out_proj.

Because q/k/v are fused, a serious experiment must use slice-specific low-rank updates or gradient masks rather than calling the fused projection one scientific variable.

---

# 4. Exact novelty boundary

CT04 is **not**:

- the first PEFT method for SSMs;
- the first study of LoRA placement;
- the first state-based PEFT method;
- the first paper showing attention and recurrence have different functions;
- the first paper showing fine-tuning can hurt recall;
- a generic module sweep;
- a new hybrid architecture.

The paper only becomes interesting if it establishes something like:

> **Recurrent memory is non-uniformly plastic: task adaptation can safely modify some memory operations while perturbing others corrupts a stable memory function / retention contract.**

A stronger outcome is:

> **the operation-level plasticity pattern predicts both target-task learning and collateral forgetting, and therefore gives a better adapter-placement rule than component identity alone.**

---

# 5. Dangerous nearest priors

## 5.1 Where Should LoRA Go? — strongest immediate prior

Owns component-level placement and the destructive recurrent-adaptation phenomenon.

It does not currently own:

- operation-level decomposition inside GDN;
- causal localization to retention/address/write/read dynamics;
- recurrent-state memory diagnostics;
- a mechanism-derived safe recurrent adaptation method.

Reviewer danger:

> "This is the same paper with GDN split into more module names."

If CT04 ends as a table of more LoRA placements, **KILL**.

## 5.2 Parameter-Efficient Fine-Tuning of State Space Models — ICML 2025

Owns PEFT benchmarking for Mamba-style SSMs, broad parameter targeting, and Sparse Dimension Tuning / SDLoRA.

Boundary:

> CT04 studies **native sequential hybrid Gated DeltaNet memory**, and its central object is causal plasticity of distinct memory operations and their collateral memory effects.

If the final result is merely "some dimensions are better to tune," novelty collapses.

## 5.3 State-offset Tuning / S0 Tuning

Own state-space / recurrent-state adaptation.

Boundary:

> they modify state or state offsets while freezing transition weights. CT04 asks why state adaptation can work while weight adaptation is brittle, and which transition/read/write operations are responsible.

## 5.4 Attention Amnesia — EMNLP 2026

Owns CoT-SFT-induced recall degradation and W_Q/W_K localization in retained **softmax attention** of distilled hybrids.

Boundary:

> CT04 studies recurrent-state dynamics in **native hybrid GDN** and does not assume the same Q/K mechanism.

If the only result is "GDN q/k also drift, freeze q/k," re-audit.

## 5.5 What Attention Recalls and Recurrence Controls

Owns the functional division of labor between attention KV and recurrent state at inference.

Boundary:

> CT04 studies post-training plasticity inside the recurrent mechanism.

## 5.6 Gated DeltaNet-2 / FG2-GDN

These architecture papers explicitly separate decay, erase, and write because they are different memory operations.

They are pretraining/architecture work, not post-training plasticity work, but they make a monolithic "GDN block" scientifically unnatural.

---

# 6. Competing hypotheses

The pilot must not presuppose a winner.

## H1 — retention dynamics are brittle

Updating decay / retention parameters changes effective memory horizon and drives collateral forgetting.

## H2 — addressing is brittle

Changing k and/or q remaps which stored associations are written/read.

## H3 — content path is plastic

Value/content write or output projection absorbs task adaptation while preserving pretrained memory dynamics.

## H4 — write strength is task-dependent

Beta-like update strength may help some domains and hurt others, implying no universal safe module list.

## H5 — no localized plasticity exists

Destruction is diffuse, parameter-count driven, or caused by high-order interactions among operations.

---

# 7. Minimum pilot

## 7.1 Models

Primary:

- Qwen3.5-0.8B-Base for the cheapest factorial;
- Qwen3.5-2B-Base for confirmation.

Only move to 4B after a stable effect appears.

## 7.2 Reproduce the parent phenomenon first

Use one or two settings from Where Should LoRA Go?:

- GSM8K / math adaptation;
- optionally CodeAlpaca or UltraChat.

Reproduce:

- attention-only LoRA;
- all-GDN LoRA;
- broad all-eligible LoRA.

If recurrent-only adaptation is not destructive under a faithful reproduction, stop and re-audit before finer mechanistic claims.

## 7.3 Operation-level matched interventions

Within GDN, test parameter-budget-matched adapters for:

1. read query q;
2. write/address key k;
3. content value v;
4. retention / decay path;
5. write-strength beta path;
6. output gate / readout;
7. only the strongest predicted combinations.

Parameter count, steps, data, and effective LR must be matched.

Do not run an uncontrolled adapter zoo.

---

# 8. Measure more than target accuracy

The topic dies if it is only "which target_modules get highest GSM8K."

For every intervention measure:

## A. Target learning

- GSM8K / MATH-style accuracy;
- HumanEval or code if code is used.

## B. Collateral retention

- MMLU / ARC / HellaSwag or comparable general retention;
- RULER / NIAH / selected LongBench diagnostics.

## C. Memory-function diagnostics

### Split-prefill / State-swap

Ask whether fine-tuning changes:

- exact-retrieval dependence on attention KV;
- behavioral/language dependence on recurrent state.

### Retention horizon

Track GDN decay statistics and empirical state-survival timescales.

DASC (arXiv:2608.30386) shows different GDN/KDA heads/channels have markedly different retention horizons. CT04 uses this as a diagnostic, not as a serving contribution.

### State-write / read sensitivity

Track changes in:

- state update magnitude;
- state survival;
- query/read sensitivity;
- causal contribution of recurrent state.

The desired output is a **plasticity map tied to memory function**, not a benchmark rank table.

---

# 9. Stronger controlled experiment

If the initial map survives, manipulate training dependency structure.

Create matched versions of the same underlying examples where information required for the answer is:

- local / near;
- distant / long-range;
- behavioral/instruction-like rather than exact-retrieval-like.

Keep semantic target and token budget as matched as possible.

Ask:

> does the safe/brittle operation change when supervision requires a different memory contract?

Possible worlds:

- one universal plasticity map;
- dependency-distance-dependent plasticity;
- task-type-dependent plasticity;
- strong interactions between operation and dependency structure.

The answer is empirical.

---

# 10. Method path — only after the map exists

## World A — a stable safe subset exists

Example hypothetical result:

- value/readout plastic;
- decay/addressing brittle.

Then use **operation-aware LoRA**: adapt only the safe recurrent operations, optionally together with attention LoRA.

Compare against:

- attention-only;
- GDN-only;
- all eligible;
- S0 / state-based PEFT where compatible.

The contribution is not the hand-written target-module list; it is the validated memory-plasticity mechanism that predicts it.

## World B — plasticity is task-dependent

Then static placement is insufficient.

Use a cheap calibration stage to estimate a per-operation score such as:

plasticity score = target-learning signal / memory-contract sensitivity.

Allocate adapter rank or enable LoRA only where target gradient is high and collateral memory sensitivity is low.

## World C — recurrent transition weights are broadly brittle

Then the method may combine:

- state-based adaptation;
- attention-path adaptation;
- frozen recurrent transition dynamics.

This world is only strong if the mechanism explains the boundary and improves over simple attention-only placement.

---

# 11. Benchmark path

Start narrow.

Pilot:

- GSM8K or MATH-derived SFT;
- one general-retention suite;
- RULER/NIAH diagnostic.

Full method after survival:

- MATH-500;
- AIME 2024/2025 if model scale supports it;
- HumanEval/MBPP or executable code;
- IFEval;
- RULER and selected LongBench diagnostics.

Do not create a new benchmark.

The strongest final plot is a **target-gain vs collateral-forgetting / long-context-retention frontier**.

---

# 12. Compute / data audit

Stage 1:

- Qwen3.5-0.8B;
- LoRA only;
- a few thousand existing SFT samples;
- multiple operation placements;
- 2–3 seeds only for decisive conditions.

Stage 2:

- Qwen3.5-2B / 4B;
- confirm the discovered mechanism;
- reduce condition count to the strongest competing hypotheses.

4× PRO 6000 is already ample. 8× mainly accelerates seeds, long-context diagnostics, and 4B confirmation.

No pretraining, large RL run, agent environment, or new data collection is required.

---

# 13. Hard kill conditions

KILL CT04 if:

- the destructive recurrent-LoRA phenomenon does not reproduce;
- operation-level differences disappear after parameter-count / LR matching;
- no stable pattern appears across seeds or at least two tasks;
- benchmark differences have no corresponding memory-functional / retention diagnostic;
- all GDN operations are similarly destructive and no principled repair follows;
- the only effect is exactly the same Q/K drift already captured by Attention Amnesia;
- operation-aware LoRA cannot beat or complement simple attention-only LoRA on a meaningful target-vs-retention frontier;
- a direct paper already causally localizes GDN post-training brittleness to the same operations and derives the same adapter rule;
- the final story reduces to "we tried more LoRA target_modules."

Do not rescue with a giant module grid, dozens of benchmarks, a new dataset, from-scratch training, or opaque loss stacking.

---

# 14. Reviewer compression tests

## "This is Where Should LoRA Go? with more rows."

Valid unless CT04 shows:

1. operation-level adaptation has a reproducible causal effect on memory function;
2. the same diagnostic predicts collateral forgetting;
3. the resulting method beats coarse component placement.

## "This is ICML 2025 SSM PEFT on Qwen3.5."

The distinction must remain:

> GDN is a key-addressed recurrent **memory update rule inside a native hybrid**, and CT04 explains the plasticity of its memory operations and their interaction with the full-attention channel.

If the work becomes a generic PEFT benchmark, kill it.

## "This is Attention Amnesia for recurrent layers."

CT04 survives only if recurrent-state dynamics contribute a distinct failure mode / plasticity structure beyond softmax QK routing drift.

## "Just freeze recurrence and tune attention."

That is already a strong baseline.

CT04 matters only if it explains when that rule is unnecessarily conservative and finds a recurrent adaptation surface that improves the achievable trade-off.

---

# 15. Expected knowledge sentence

The paper must earn a sentence like:

> **Hybrid recurrent memory is not uniformly fine-tunable: post-training gains and forgetting are controlled by which memory operation is changed. [Operation X] is a plastic adaptation surface, whereas perturbing [operation Y] shifts the pretrained retention/addressing contract and causes collateral failure. Exploiting this asymmetry yields safer and stronger adaptation than component-level LoRA placement.**

If no stable sentence emerges, CT04 should die.

---

# 16. Verdict

> **PILOT-AUTHORIZED**

Why:

- it starts from a documented failure rather than an invented phenomenon;
- strong papers create an unresolved tension: recurrent-weight adaptation can be destructive, recurrent-state adaptation can be strong, and recurrent state has a distinct causal role;
- the answer cannot be inferred from equations alone;
- the first experiment is cheap and highly discriminative;
- the method path depends on what the pilot discovers rather than being pre-written;
- it fits 4×/8×96GB comfortably;
- if the effect survives, it can become a method paper with benchmark gains rather than stopping at mechanistic analysis.

**First task:**

> reproduce the Qwen3.5 recurrent-LoRA failure, then perform a parameter-budget-matched operation-level GDN adaptation study while simultaneously measuring target learning, collateral forgetting, and recurrent-memory diagnostics.
