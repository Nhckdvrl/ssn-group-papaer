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
