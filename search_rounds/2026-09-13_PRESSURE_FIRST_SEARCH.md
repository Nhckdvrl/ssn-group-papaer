# 2026-09-13 — Pressure-First Search

This rolling log follows the corrected provenance doctrine:

> **scientific pressure first → matched/stress test → phenomenon second**

Do not default to mining already-published anomalies. Search old laws, widely used assumptions, evaluation/deployment mismatches, and causal explanations whose evidence is weaker than their influence.

Only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic is user-facing.

---

## Hook P1 — Is the benefit of easy→hard curriculum really ordering, or learning-rate timing?

**Status:** `DROP / DIRECT CAUSAL SUCCESSORS`

### Pressure

Curriculum learning is commonly motivated as an ordering effect: presenting easier examples before harder ones is supposed to improve optimization or learning. In modern LLM training, however, data order is mechanically coupled to optimizer time; under learning-rate decay, later hard/high-quality examples receive smaller updates.

A clean pressure-first question was therefore:

> **After matching effective update opportunity, does easy→hard order itself still help, or is part of the modern curriculum effect just where examples land on the LR schedule?**

### Why it dies

This is already too directly occupied. A 2025 study, *How Learning Rate Decay Wastes Your Best Data in Curriculum-Based LLM Pretraining*, explicitly identifies the incompatibility between ascending-quality curricula and decaying LR and shows that constant/matched LR can restore gains. A 2026 successor, *Understanding Curriculum Learning in LLMs via Cross-Difficulty Optimization Dynamics*, further analyzes curriculum schedules through transfer across difficulty levels and develops a schedule around that dynamics.

ACL 2026 work on mathematical-reasoning curricula also finds no universal forward/reverse ordering rule, reinforcing that the simple curriculum-order premise is already under active re-identification.

### Reviewer compression

> `Curriculum order is confounded with optimizer time + existing LLM studies already manipulate LR/data-order coupling and cross-difficulty transfer = our matched test.`

### Anti-resurrection

Do not reopen as `easy→hard only works because examples occur at high LR`, `match LR across curriculum stages`, or generic forward-vs-reverse curriculum unless a qualitatively new same-quantity contradiction emerges.

---

## Hook P2 — Does post-training create the LLM “hivemind,” or is common error structure inherited from pretraining?

**Status:** `DROP / PUBLIC DIRECT DECOMPOSITION ALREADY EXISTS`

### Pressure

ICML 2025 *Correlated Errors in Large Language Models* challenges a widely used assumption: diversity of providers, architectures, and training should yield meaningfully diverse mistakes. It finds high error correlation across hundreds of models. NeurIPS 2025 Best Paper *Artificial Hivemind* further establishes broad model-output homogeneity.

A natural matched-stage question was:

> **Is this convergence already present in base models, or does instruction/post-training make independently pretrained models converge toward the same behavior?**

The attractive E01 would compare matched base↔instruct checkpoints and then separate weight changes from chat-format effects.

### Why it dies

A public August-2026 study, *Where the Hivemind Comes From: Geometry, Tuning and Format, Separated on Open Weights*, already performs almost exactly this decomposition on six matched open-weight base/instruct pairs. It reports that base models do not reproduce the high homogeneity regime, instruction tuning contributes some increase, and applying the model's trained chat template to the same instruct weights produces a much larger shift; in their reported decomposition the format effect is roughly 4.6× the tuning effect.

The source is a public research article rather than a flagship-conference paper, but this project explicitly treats strong public work/blogs as novelty evidence. We should not pretend the direct experiment is open merely because it has not yet appeared in ACL/ICML.

### Reviewer compression

> `ICML/NeurIPS establish LLM homogeneity + the August-2026 open-weight study already separates base, instruction-tuned raw prompting, and chat-template prompting = proposed stage-localization study.`

### Anti-resurrection

Do not reopen as `does RLHF/SFT homogenize models`, `base vs instruct error correlation`, or `chat templates cause hivemind` without a different scientific quantity that the existing decomposition cannot answer.

---

## Hook P3 — If instruction tuning changes MoE routing, is the router actually what learned?

**Status:** `DROP / ROUTER–BODY DECOMPOSITION ALREADY CROWDED`

### Pressure

ICLR 2024 *Mixture-of-Experts Meets Instruction Tuning* reports a useful internal tension: instruction tuning benefits MoE models disproportionately and changes expert usage, yet freezing gate/router parameters during instruction tuning does not hurt the reported average and can slightly improve it, while freezing experts is clearly harmful.

That creates a natural computational question:

> **When post-training changes expert selection, is the routing policy learned in router weights, or induced by changing hidden states fed into essentially the same router?**

A clean conceptual decomposition is `route = topk(W_router h)`: compare router-weight changes with representation/body changes rather than equating changed routing decisions with learned router parameters.

### Why it dies

By 2026 the router-versus-body space is already too directly occupied. Public/academic work now includes:

- gate/body swap experiments across post-trained MoE checkpoints showing that swapping routers can change many routing decisions while producing little capability change, whereas body/expert changes carry much more of the capability shift;
- router-prior work showing that preserving useful pretrained routing structure during post-training can matter more than forcing uniform balancing;
- router–expert coupling analyses showing that routing geometry is learned jointly with hidden/expert representations rather than as an isolated policy;
- RL/post-training studies that explicitly track router drift and module-wise change.

Combined with the ICLR-2024 freeze-gate ablation, the likely strongest result — routing can change mainly because upstream representations/body change even when router weights do not — is already strongly implied. An exact `W_router × h` cross-combination experiment would be tidy, but reviewer compression is too strong.

### Reviewer compression

> `freeze-gate instruction tuning + gate/body swaps + router/expert geometric coupling = routing-change need not mean router-weight learning.`

### Anti-resurrection

Do not reopen as `router weights vs hidden states`, `where MoE routing adaptation lives`, `freeze router but routing still changes`, or generic post-training router specialization unless a new same-quantity contradiction appears.

---

## Hook P4 — Are sparse RL weight updates caused by the RL objective, or merely by on-policy data support?

**Status:** `DROP / PARENT + SUCCESSOR ALREADY SEPARATE THE MAIN CAUSE`

### Pressure

NeurIPS 2025 *Reinforcement Learning Finetunes Small Subnetworks in Large Language Models* reports that large behavioral changes under seven RL algorithms can be carried by sparse coordinate subsets that overlap strongly across seeds, datasets, and algorithms. The tempting explanation is that RL's objective creates a sparse update mechanism.

A pressure-first matched question was:

> **On the same self-generated trajectories, would token-level imitation/CE produce similarly sparse parameter updates, or is sparsity genuinely specific to policy-gradient/reward optimization?**

### Why it dies

The parent already does much of the identification. In-distribution / rejection-sampling SFT is also highly sparse, while out-of-distribution SFT/DPO updates are much denser; online/offline RL details, clipping, and related optimizer differences do not explain the broad pattern. A 2026 on-policy-distillation follow-up then shows that dense teacher supervision can still yield coordinate-sparse updates when the training distribution is on-policy.

Thus the strongest likely conclusion of a same-rollout RL-vs-CE experiment — **distribution/support relative to the current policy is more load-bearing than the nominal RL objective** — is already largely implied by parent plus successor.

### Reviewer compression

> `RL update sparsity + in-distribution SFT is also sparse + out-of-distribution SFT is dense + on-policy distillation stays sparse = sparsity follows policy-relative data support more than RL objective.`

### Anti-resurrection

Do not reopen as `RL vs SFT update sparsity`, `same rollout policy gradient vs CE`, or `why RL only tunes a subnetwork` without a qualitatively different quantity not predicted by current on-policy evidence.

---

## Hook P5 — Does architecture-invariant loss-to-loss scaling survive post-training?

**Status:** `DROP / LAW ALREADY FRACTURED + DIRECT POST-TRAINING ARCHITECTURE EVIDENCE`

### Pressure

ICML 2025 *LLMs on the Line* reports a striking pretraining-era law: when pretraining data are controlled, loss-to-loss scaling is driven mainly by the data, while tokenizer, optimizer and even substantial architecture differences such as Llama/Transformer versus Mamba have limited impact on the scaling trend. This invites a modern-regime question:

> **If architectures reach comparable pretrained loss under controlled data, does applying the same instruction/post-training preserve that architecture invariance, or does post-training expose architecture-specific learnability?**

The route initially looked feasible because NVIDIA released controlled 8B Mamba-2 and Transformer models trained on the same data and hyperparameters for roughly 3.5T tokens.

### Why it dies

The broad law is already too fractured to make the post-training extension a clean new parent. April-2026 *Nexus* demonstrates that models can reach essentially the same pretraining loss yet differ substantially in downstream generalization because optimizer-induced solution geometry differs, so equal loss is not itself a strong common-state guarantee. More directly, an ICLR-2025 study instruction-tunes Mamba/Mamba-2 and Transformer families under a common recipe and reports that instruction tuning changes their ICL behavior and can move Mamba-2 past Transformer baselines. Hybrid/SSM post-training work likewise already treats architecture-specific adaptation as an empirical object.

Therefore the strongest plausible positive result — post-training breaks the apparent architecture invariance observed in base-model loss scaling — is no longer surprising enough or uniquely attributable. The project would mostly fit another quantitative curve through a phenomenon already expected from known architecture-specific ICL/copying behavior plus evidence that same pretraining loss can hide distinct solutions.

### Reviewer compression

> `LLMs on the Line: architecture has limited effect on pretraining loss-to-loss scaling + Nexus: same pretraining loss need not imply same downstream solution + controlled Mamba/Transformer instruction tuning already changes relative ICL behavior = post-training architecture invariance can break.`

### Anti-resurrection

Do not reopen as `same pretraining loss, different SFT response`, `does post-training break loss-to-loss architecture invariance`, or a Mamba-vs-Transformer SFT scaling sweep unless a new same-quantity law supplies a sharper prediction than generic architecture-specific post-training behavior.
