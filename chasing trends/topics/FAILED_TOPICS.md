# Failed Topics Ledger

这里记录 **已经锁定并完成审计、最终 KILL 的 chasing-trends 候选**。

目的只有两个：

1. 防止下一轮换标题复活；
2. 保留真正有用的 kill evidence / paper-growth lesson。

不记录：
- 随手 brainstorm；
- 读两篇就放弃的 seed；
- 还没有 nearest-prior audit 的想法。

每条使用：

## CT-KILL-YYYYMMDD-N — Short name

- **Mother question:**
- **Lineage / pressure:**
- **Nearest covering prior:**
- **Kill reason:**
- **Kill category:** novelty / identification / data / compute / recipe / evaluation / width / experiment explosion / other
- **Anti-resurrection:** 哪种换名版本仍然是同一死法。
- **Useful lesson:** covering work 或失败教会了什么。

---


## CT-KILL-20260919-1 — Relevant but Invalid / validity-aware reasoning-history reuse

- **Mother question:** When later information invalidates dependencies used by a model's earlier reasoning, should that historical reasoning still be replayed into the next turn?
- **Lineage / pressure:** multi-turn reasoning history, context pollution, belief revision, feedback/correction.
- **Nearest covering prior:** Huang et al. (2026), *Do LLMs Benefit From Their Own Words?*; Choi et al. (EMNLP 2026), *In-Place Feedback: Reliable Refinement for Multi-Turn Expert-LLM Collaboration*; SWE-AGILE (ACL 2026 Findings). Belief-R remains the nearest behavioral dataset but not a clean validity instrument.
- **Kill reason:** The controlled object collapses from "cached computation" to replayed model-generated token context; the exact valid-vs-invalid interaction remains untested but is narrow relative to existing context-pollution/state-repair work. Belief-R does not provide objective explicit premise invalidation, while a clean synthetic replacement task would make the result less natural and more obvious. A nontrivial method requires dependency extraction/state repair and causes the project to expand into context-management infrastructure.
- **Kill category:** width / data / novelty-convergence / other (scientific-object collapse).
- **Anti-resurrection:** Renaming this as stale-CoT removal, validity-aware `preserve_thinking`, reasoning-cache invalidation, or dependency-aware thought pruning does not fix the blocker. Reopen only if the object becomes actual non-text persistent computation/state reuse, or if a natural dynamic domain supplies objective dependency ground truth and creates a distinct unresolved relation.
- **Useful lesson:** A product knob can establish real deployment pressure without defining a deep academic object. Serialized historical reasoning should not be called a computation cache unless the experiment controls something beyond replayed textual context.



## CT-KILL-20260921-1 — Context Utility Rankability / set-dependent sparse attention

- **Mother question:** Can sparse-attention context utility be represented by a single scalar ranking, or is marginal utility intrinsically set-dependent?
- **Lineage / pressure:** learned sparse attention, causal context routing, redundancy/complementarity, multi-hop evidence selection.
- **Nearest covering prior:** *Learning What Matters: Supervising Sparse Attention Routing with Causal Evidence Sets* (2026), plus SAS / R-KV and adjacent set-aware selection work.
- **Kill reason:** The exact nestedness/rank-reversal formulation remains distinguishable, but recent causal/set-aware routing work already occupies most of the same scientific narrative. Proving a sufficiently stronger structural separation would require nontrivial intervention engineering while still leaving high reviewer-compression risk.
- **Kill category:** novelty / width / resource allocation.
- **Anti-resurrection:** Renaming as non-additive utility, budget-conditioned ranking, submodular sparse attention, set-conditioned routing, or “Top-K is insufficient” does not fix the novelty distance.
- **Useful lesson:** A mathematically cleaner formulation is not automatically a sufficiently distinct paper claim when nearby work already owns the underlying relational/causal selection story. Prefer topics where the new method or causal object creates a wider reviewer-visible gap.


## CT-KILL-20260922-1 — Counterfactual Credit for MoE Routing

- **Mother question:** Can a pretrained sparse MoE router receive useful token-level credit for unexecuted experts without rerunning the downstream model for many alternative routes — and can that credit be turned into a better router?
- **Lineage / pressure:** *When Are Experts Misrouted?* (counterfactual routing diagnostic, final-layer EPO existence probe); ERL, ProbMoE, ERC, CoR, AdapMoE, RoMA.
- **Nearest covering prior:** RoMA (ICLR 2026) already owns "router-only post-training improves an MoE LLM", which is the effect that actually survived here. The parent owns the counterfactual diagnostic itself.
- **Kill reason:** The **estimator** half held up under every test: proxy fidelity rho 0.698 on OLMoE and cross-family replication on Qwen3-30B-A3B including renormalised routing; exact utilities near-additive at calibrated layers (R² .87/.97/.999); proxy potential tracking the exact one (rho .90/.98); the shallow-layer limit localised to finite-step estimation rather than expressiveness; ~130x supervision-cost advantage with a break-even near 6 candidates/sequence. The **method** half never closed. Binary pairwise distillation (C0) fit a margin-collapse shortcut that random labels fit slightly faster, and its route-regret metric turned out invalid. KL-regularised Counterfactual Potential Distillation (CPD v1) — mass-preserving target, exactly KL-matched shuffled control — gained a significant +5.8 points over base in real greedy free generation on 120 locked problems, but could not be separated from either control (vs shuffled +3.3 ns, vs Router-CE +1.7 ns), showed **no measurable alignment between the learned score correction and the exact counterfactual utility** (A_delta and A_z indistinguishable from zero for every arm and layer), and produced **worse** fixed-support route value than ordinary router-only CE tuning. Three independent lines therefore point the same way: the gain is most parsimoniously router-only adaptation, not counterfactual content.
- **Kill category:** novelty-convergence / identification (the central mechanism is unattributable) / experiment explosion (each repair added a branch rather than removing one).
- **Anti-resurrection:** Do not reopen as a nonlinear or MLP router head, on-policy / "actionable" credit gated by entropy, margin or gold probability, a second-order estimator, more training data, a second MoE family, or by adding EPO / RoMA baselines. All of those grow branches around a claim whose centre — that counterfactual content buys something over ordinary router adaptation — has no supporting evidence. Reopen only if some *other* project independently needs the estimator, or if a genuinely different action mechanism for the missing signal appears that is not router-logit distillation.
- **Useful lesson:** **A beautiful, cheap, cross-model diagnostic or estimator does not imply that a Main-level intervention method exists downstream of it.** CT03's first half went unusually smoothly and that success set the default expectation that a method would grow out of it. The question that should have been asked at selection time — and was not — is whether the missing signal has an obvious, natural, deployable *action mechanism*. Ask it before authorising the pilot, not after two distillation formulations have failed. A secondary lesson: once every proposed next step is a rescue ("try X, if it works the topic lives"), the topic is already decided, and the cost of the individual experiment is irrelevant to that judgement.
- **Final post-kill mechanism audit (2026-09-23):** E08 showed the cheap proxy can screen the parent's full Gumbel top-K action space (`R_2=0.938/0.976` at L36/L44), but exact EPO at L47/L36 changed essentially every completion without a resolved downstream accuracy gain. The decisive frozen-target probe then separated objective success from deployed action: parent-style preference training could drive preference accuracy very high while target overlap collapsed, and direct slot attribution showed **80.8% of executed experts belonged to neither `r+` nor `r-`**. A target-directed rank control could move overlap toward `r+`, so linear-gate capacity alone is not the explanation, but it did not solve exact adoption and is not a replacement method. The final diagnosis is an **objective/action mismatch**, not estimator failure. Canonical archive: `candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING/FINAL_POSTMORTEM.md`.
- **Final anti-resurrection:** Do not rename this mismatch into a new CT topic merely by importing top-k/listwise/hinge/KPO/Plackett-Luce/soft-top-k losses, running a second MoE family, or searching for a pass@K delta. Those are new method-search branches after the original information-to-action chain has already failed. A genuinely new topic would require an independently motivated mother question and a fresh nearest-prior audit.

## CT-KILL-20260927-1 — CT05 Shape-blog exploration lineage (historical CT05–CT09 consolidated)

- **Status:** ARCHIVED / KILLED LINEAGE. Historical CT06–CT09 are no longer independent registry entries; their artifacts live under `candidates/CT05_EXACT_MEMORY_DEMAND/lineage/`. Their old labels remain only as provenance, and IDs CT06–CT09 are free for future registrations.
- **Mother neighborhood:** Alex Zhang's *Language Model "Shape"* agenda applied to hybrid attention/recurrent memory, agent-history representation, query-timed exact access, RLM information hiding, and cross-channel handoff.
- **Why the lineage is closed:** every branch began from a plausible Shape intuition before a stable, manipulable mother phenomenon was established in our own regime. The decisive tests were informative, but repeated first-gate failures show this is not a productive source of new CT registrations without independent external pressure.
- **Original CT05:** on 182 SWE-smith / APIGen-MT checkpoints, Qwen3.5-9B recurrence did not substitute for historical KV: `rho_2=-0.005 [-0.034,0.024]`, hybrid-specific leverage `-0.03 [-0.07,0.03]`, median recurrence carry `0.001 nats`. Copy tokens were ~11% of output but ~60% of damage; recurrence restored ~1% of copy damage. Exact demand was concentrated, but future-query selection reduced to already-occupied query-aware KV work.
- **Historical CT06 branch:** killed at selection. SWAX / Rethinking already own the broad training-pressure story; “continued-train a pretrained hybrid until rho moves” was a recipe search, not an observed phenomenon.
- **Historical CT07 branch:** intra-action query timing failed. Pre-value recovery was only `0.13–0.22`; useful source lookup emerged during value generation itself, not at a deployable tool/key boundary.
- **Historical CT08 branch:** RLM visibility decomposition was not identifiable in the affordable regime. On 400 OOLONG-synth items, trained RLM-Qwen3-8B scored `0.274`, untrained same-harness Qwen3-8B `0.346`, flat full-context `0.515`; the published RLM transfer effect lives at much larger RL/length scale than the visibility manipulation.
- **Historical CT09 branch:** its frozen continuation gate failed (`H=0.108 [0.104,0.112] < 0.20`), but this was **not a null effect**. POST after one attention lookup and then all-KV removal was `1.79 nats` vs NOREAD `0.03`; POST−NOREAD was positive on 399/400 items (median ~1.72 nats). This is preserved as a robust partial retrieval-triggered recurrent trace, with carrier/persistence unresolved; it is not promoted into a new topic.
- **Anti-resurrection:** do not reopen by changing backbone/scale/prompt/budget, adding KV-dropout training, turning CT07 into two-stage tool filling, repairing the 8B RLM until the published large-scale effect appears, or sweeping CT09 carrier/layers/models in hope of a larger magnitude. A genuinely new topic requires an independently observed behavior/failure first.
- **Useful lesson:** blog/design intuition is not mother evidence. Future Shape work should begin from a strong open baseline or already-established empirical tension, accumulate exploratory failure gradients, and only then register an RQ. Separate scientific findings from investment thresholds.

Canonical consolidated summary: `candidates/CT05_EXACT_MEMORY_DEMAND/README.md`.
