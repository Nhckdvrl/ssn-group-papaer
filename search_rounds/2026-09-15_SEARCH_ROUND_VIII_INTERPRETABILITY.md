# Search Round VIII — Interpretability Focus — 2026-09-15

## Status

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS  
**Search preference:** interpretability / mechanism, avoiding already-crowded RLVR / CoT / optimizer / attention-microchoice walls

**Result:** **1 NEW E01-AUTHORIZED SURVIVOR**

> **L43 — Do Backup Circuits Provide Natural Robustness?**  
> `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`

No other new candidate was promoted.

---

# 1. Search behavior in this round

This round deliberately did **not** search for another `feature X in model Y` or `use SAE/patching on behavior Z` paper.

The search started from long-lived interpretability pressures:

- Are discovered mechanisms properties of the model or artifacts of the intervention / coordinate system?
- Is redundancy only an interpretability nuisance, or does it have a functional role?
- Are intrinsically interpretable / sparse models mechanistically representative of ordinary dense models?
- Does a model have one mechanism for a behavior or multiple causally sufficient alternatives?
- Which recent tools make those old questions newly identifiable?

Recent papers were used as a **leverage bank first**, owner bank second.

---

# 2. Survivor — L43

## Question

> **Are the dormant backup circuits that repair a Transformer after artificial ablation also recruited by ordinary, answer-preserving input stress in the intact model?**

Short form:

> **Is artificial self-repair the same mechanism as natural robustness?**

Package:

- `candidates/L43_NATURAL_BACKUP_ROBUSTNESS/SELECTION.md`
- `candidates/L43_NATURAL_BACKUP_ROBUSTNESS/E01_PREREGISTRATION.md`
- `candidates/L43_NATURAL_BACKUP_ROBUSTNESS/OWNER_AUDIT_ADDENDUM.md`

## Why the question existed before the new method

The Hydra / self-repair lineage establishes that downstream components can compensate after attention-head ablation.

Rushing & Nanda, ICML 2024, *Explorations of Self-Repair in Language Models*:

https://proceedings.mlr.press/v235/rushing24a.html

extends the phenomenon across model families and the full pretraining distribution, decomposes some repair into LayerNorm rescaling and sparse learned components, and explicitly ends with the unresolved question of **why self-repair exists**.

The conceptual ambiguity is old:

> Is self-repair a robustness architecture the intact model actually uses, or a response to an unnatural off-manifold internal intervention?

## Why now

Gong et al. 2026, *Conditional Co-Ablation: Recovering Self-Repair Backups in Transformer Circuits*:

https://arxiv.org/abs/2607.01940

provides the missing leverage. CoAx identifies dormant backup components that ordinary intact-state first-order scoring misses. On GPT-2-small IOI it raises published-backup recovery from roughly `0.33` to `0.91` ROC-AUC and verifies that the recovered heads really carry the repair after primary ablation. The same conditional idea transfers to induction across multiple model families.

That gives, for the first time, a frozen independently defined set of:

> **components whose role is specifically `backup after primary failure`.**

We can now ask whether that counterfactual role predicts natural causal necessity.

## Identification

E01 uses GPT-2-small IOI because it has the strongest available ground truth:

- canonical primary Name Movers;
- eight published backup Name Movers;
- public CoAx reproduction;
- published answer-preserving `DoubleIO` / `TripleIO` stress variants;
- cheap exact head-level interventions.

The primary quantity is not `do backup heads change attention?`.

It is a difference-in-differences:

> does ablating the **predefined backup set** hurt intact stressed inputs more than BASE, **relative to a BASE-importance-matched ordinary late-head set**?

The prereg also requires an intact-forward-pass recruitment signature. If only post-ablation effects move, the result is labeled `INTERVENTION-ONLY`, not natural recruitment.

## Strongest owner risk

Nainani et al. 2024, *Adaptive Circuit Behavior and Generalization in Mechanistic Interpretability*:

https://arxiv.org/abs/2411.16105

already studies DoubleIO / TripleIO. It rediscovers their circuits and finds canonical Name Movers remain important; no other individual head has enough direct causal effect to be added as a new Name Mover. It also discovers `S2 Hacking`, an adaptation of the **knockout circuit** that is not how the full intact model works.

This is a serious adjacent owner, not something to hide.

But its circuit search is first-order / individual. CoAx's central result is that exactly this class of redundant backup can be invisible to intact-state first-order scoring. Nainani therefore supplies a strong prior, but does not measure whether the **already-defined backup set is jointly and selectively necessary under natural stress**.

CoAx itself also reports template-robust backup recovery, but the primary circuit is still internally removed before backups are scored. That is robustness of the *counterfactual backup relationship*, not natural recruitment.

## Status

> **PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE.**

The project is killed if E01 degenerates into:

- a descriptive attention shift;
- another prompt-specific circuit diagram;
- `canonical circuit changes across prompts`;
- or a backup effect that cannot beat the frozen matched control.

The full-paper identity requires the stronger distinction:

> **counterfactual repair capacity vs naturally used robustness mechanism.**

---

# 3. Serious idea not promoted — sparse interpretable models vs dense-model algorithms

## Question

> **If we train a Transformer to be intrinsically sparse / interpretable, does it learn the same algorithm an ordinary dense Transformer would have learned for the same behavior?**

Why it matters:

OpenAI's 2025 *Weight-sparse transformers have interpretable circuits* makes de-novo sparse models dramatically easier to reverse engineer. But its use as a model organism for ordinary LLMs depends on whether sparsity preserves the relevant computation rather than selecting a different, easier-to-interpret algorithm.

The paper itself explicitly notes that the main results are on de-novo sparse models and that confidence in sparse↔dense mechanistic analogy would increase their value; it provides only preliminary bridges.

Why it was **not** promoted:

1. **Successor-paper risk is high.** The motivating uncertainty is stated almost directly by the leverage paper itself.
2. **Universality is already an explicit interpretability program.** ICLR 2025 work compares mechanisms across Transformer / Mamba-like architectures and finds both shared abstract algorithms and architecture-specific implementation differences.
3. **Identification is weak.** `same algorithm` lacks a clean invariant unless the task is reduced to a toy regime, at which point the paper identity weakens.
4. A realistic best-case paper risks being compressed to `validate OpenAI's sparse model organisms`, rather than answering a broader independent foundation-model question.

**Verdict:** `SERIOUS-LOOK — NO PILOT / HOLD-REJECT`.

Do not revive by merely comparing sparse/dense circuit overlap or feature cosine similarity.

---

# 4. Other interpretability walls killed in this round

## VIII-1 — Does post-training preserve or rewire pretrained circuits/features?

**KILL — overcrowded.**

ACL 2025 / ICML 2025 / ACL 2026 already study circuit stability, fine-tuning circuit dynamics, and feature evolution under SFT/RL. A new SAE/patching study would be another instance, not a new question.

## VIII-2 — Is there a unique circuit / unique mechanism for a behavior?

**KILL as mother question.**

ICLR 2025 formal identifiability work already shows mechanistic explanations can be non-unique; later theory continues the line. The broad philosophical statement is owned.

The more concrete `how many interchangeable sufficient routes does a real LLM use?` was explored but not promoted because circuit multiplicity is already becoming an explicit research object and measuring multiplicity across scale is strongly confounded by model capacity / unit count.

## VIII-3 — Do different random seeds learn the same circuit?

**KILL — active universality/stability line.**

Prior work studies universal neurons across refits, head stability, and alignment up to rotations / Procrustes. `run more seeds on another task` is not enough.

## VIII-4 — Is a dense Transformer actually conditionally sparse / an implicit MoE?

**KILL — crowded and instrument-sensitive.**

Sparse Feature Circuits, activation-sparsity work, and recent dense-vs-sparse computation studies already make conditional computational sparsity an explicit object. A new SAE-based answer would also risk confusing explanation sparsity with computation sparsity.

## VIII-5 — Does superposition provide robustness / generalization?

**KILL — suddenly crowded.**

2025–26 work already causally manipulates superposition and adversarial robustness, including results where adversarial training changes effective feature counts and theory addressing why robustness changes superposition.

## VIII-6 — Is unlearned knowledge erased or merely hidden / masked?

**KILL — mature 2025–26 mechanistic-unlearning line.**

Do not reopen with another probe / SAE / activation-patching instrument.

## VIII-7 — Can mechanistic signatures distinguish memorization from generalization?

**KILL — crowded.**

Many 2025–26 works study memorization localization, generalization circuits, training dynamics and causal signatures. The generic parent question is no longer scarce.

## VIII-8 — Does knowledge distillation preserve the teacher's internal computation?

**KILL — exact owner.**

TMLR 2026 *Distilled Circuits: A Mechanistic Study of Internal Restructuring in Knowledge Distillation* directly studies how distillation reorganizes internal circuits while behavior is preserved.

## VIII-9 — Generic activation patching / mediator failure

**DO NOT GENERATE TOPICS FROM THE METHOD ALONE.**

2026 *The Curse of Multiple Mediators* already formalizes hidden interaction effects in activation patching and shows how components can be invisible or artificially inflated. This is important leverage and a warning for L43, not a reason to propose `a better patching metric` paper.

---

# 5. Main lesson from this interpretability round

Interpretability is not uncrowded. The most obvious questions are now heavily occupied:

- feature stability;
- circuit universality;
- post-training rewiring;
- SAE faithfulness;
- superposition;
- unlearning;
- activation-patching estimator corrections.

The better search surface is one level deeper:

> **What scientific claim are we currently inferring from interpretability interventions that the intervention itself may not identify?**

L43 survived because it is not about finding another circuit. It challenges a scientific inference already being made from a mature phenomenon:

> `we observe a backup after damage` **does not automatically imply** `the intact model has a naturally useful backup mechanism`.

The 2026 leverage is unusually good because CoAx now names the counterfactual backup set in advance, allowing the natural-use claim to be tested without inventing the mechanism after seeing the stress condition.

That search pattern should be retained, but **not** turned into a template such as `every intervention may be an artifact`. The next interpretability search should move to another long-standing scientific inference and ask whether a new tool/regime finally makes its key distinction identifiable.

---

# 6. Current portfolio delta

New this round:

> **L43 — Do Backup Circuits Provide Natural Robustness?**  
> `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`

Unchanged:

> **L42 — Does Scale Reward Syntax?**  
> `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`

No Mainline project is declared by this search round.