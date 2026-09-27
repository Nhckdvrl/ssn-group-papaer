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


## CT-KILL-20260927-1 — Exact vs compressed memory allocation for hybrid-LM agents

- **Mother question:** Given that a hybrid LM's recurrent state has already absorbed an agent's history, which past events still need exact attention KV at a decision, and is that "exactness demand" (as opposed to importance) predicted by existing signals? The intended method was a decision-aware fidelity router that allocates KV budget between the two native memory channels.
- **Lineage / pressure:** Alex Zhang, *Language model "shape"* (2026 blog, recurrent history + dense local context for agents); *What Attention Recalls and Recurrence Controls* (2609.04434); HAM (2603.22325), HOLA (2607.02303), DeltaS (2609.27470), NHA (ACL 2026); agent KV eviction (AgentKV, MemDecay, RoleKV, SideQuest).
- **Nearest covering prior:** 2609.04434 owns the retrieval-vs-control channel split. AgentKV / Quest / Lookahead Q-Cache own query-aware KV selection for what remains. SWAX (2509.24552) and learnable-eviction hybrids (2510.20787) own training hybrids so that recurrence carries long-range memory.
- **Kill reason:** Pre-registered Kill A fired in E01 (`candidates/CT05_EXACT_MEMORY_DEMAND/docs/E01_RESULTS.md`). The data were 182 natural SWE-smith / APIGen-MT decision checkpoints on Qwen3.5-9B, with Qwen3-8B as the Transformer control. Evicting old events' KV hurt as much as deleting their text: rho_2 = −0.005 [−0.034, 0.024], hybrid-specific leverage −0.03 [−0.07, 0.03], median per-event recurrence carry 0.001 nats. The dependence sits on verbatim copying: copy tokens are 11% of the target but carry 60% of the damage, and recurrence restores 1% of it (26% on the other tokens). The proposal's own motivating case, a policy system prompt, needs its exact KV in 95% of checkpoints. Exactness demand *is* highly structured (top 10% of events hold 92%), but only the future action's own queries predict it (99% / 93% of the oracle). Hybrid-native signals do worst: DeltaS drift 9% / 2%, surprisal negative. With the recurrent channel empty, "allocation between two channels" reduces to query-aware KV retrieval on a Transformer, which is owned.
- **Kill category:** identification / novelty-convergence (the scientific object, recurrence-supplied compressed influence on agent decisions, is ~0 in current hybrids).
- **Anti-resurrection:** Do not reopen as a decision-aware / fidelity / exactness router on Qwen3.5-class models, per-role recurrent streams, DeltaS- or HAM-style signals for agent KV retention, a "predict which strings the agent will copy" eviction policy (AgentKV / lookahead-query territory), or by re-running on Falcon-H1, larger Qwen3.5, or free-running own actions in hope of a nonzero rho. Each adds a condition to a claim whose central quantity is zero on the pre-registered model. Reopen only if a hybrid trained under KV scarcity (SWAX-style stochastic windows, or eviction-aware agent post-training) first shows rho >= 0.3 on the same E01 harness. Only then does the allocation question have an object.
- **Useful lesson:** Measure the leverage of the cheaper channel before designing an allocation between channels. The whole proposal rested on "recurrence already remembers everything, compressed", which a single KVWIN-vs-TEXTWIN contrast falsified in about an hour of compute. Methodological residue: Qwen3 needs its attention-sink tokens and gated-attention Qwen3.5 does not, so cross-family KV interventions must protect the sink. Without that, the Transformer control looked +36.7 nats worse on the system prompt for purely artefactual reasons.


## CT-KILL-20260927-2 — Training pressure × hybrid memory specialization (killed at selection)

- **Mother question:** Is the "attention recalls, recurrence controls" split in hybrid LMs architectural, or produced by training-time access to attention? Can memory-pressure continued training make a pretrained hybrid's recurrence back up exact agent history (rho > 0, copy-token carry > 0)?
- **Lineage / pressure:** CT05 E01 (rho ≈ 0, copy carry 1%); SWAX; *Rethinking the Role of Efficient Attention in Hybrid Architectures*; *Functional Component Ablation* (2603.22473) lists the question as future work.
- **Nearest covering prior:** SWAX (2509.24552, ICLR 2026) shows that short or stochastic windows make recurrence learn long-range recall (NIAH ~30% vs ~0% at 131k), which settles "learned vs architectural" behaviourally. Rethinking (2606.15378) shows efficient layers store little long-range information when full attention exists, and that architecture gaps shrink with sufficient training (speed, not endpoint).
- **Kill reason:** The only uncovered residual is post-hoc re-specialization of a pretrained full-attention hybrid, measured by channel-level carry on agent copy tokens. That is a conditional recipe question ("does some continued-training schedule move rho off 0?") facing the fixed-state copy-capacity bound. It had no natural observation behind it, only a hoped-for capability. `candidates/CT06_TRAINING_PRESSURE_MEMORY_SPECIALIZATION/README.md` keeps the audit and the unrun Gate 0.
- **Kill category:** novelty (SWAX / Rethinking) / width (recipe search).
- **Anti-resurrection:** Do not reopen as KV-dropout / stochastic-window / event-dropout continued training of Qwen3.5-class models, "eviction-robust hybrids", or "memory-pressure curriculum", and not on another backbone. Reopen only if an independently observed phenomenon (not a desired capability) shows pretrained recurrence carrying copy-level history somewhere.
- **Useful lesson:** A reopen condition written into a kill record ("if some training makes rho >= 0.3") is not a research question by itself. It names a capability to hope for, and SWAX had already shown the behavioural half.
- **Also not registered (same day):** *value liveness* (when an old tool value can be dropped). SideQuest already trains on last-use indices, StateComp frames "safe to replace", and Execution Provenance / linear decodability of tool-call dependency graphs cover the dataflow side.
