# I10 — Query specialization vs reusable world knowledge

- **Program:** R3
- **Status:** SEED
- **Mother question:** world model 为一个 query/planner 做 decision alignment 时，应该在哪一层接收 query，才能获得 in-query efficiency 又不牺牲 unseen-query reuse？
- **不是:** “query-conditioning有用”；P38、Goal-Aware Prediction、Value Equivalence、Grounded WM都已覆盖 broad claim。
- **研究空间:** 同一 compact visual-WM stack 下，controlled query placement：
  - representation-conditioned；
  - dynamics-conditioned；
  - metric-only；
  - proposal-only；
  - modular proposal-conditioned + query-independent dynamics。
- **核心轴:** seen→unseen query、query dimensionality、candidate distribution、capacity、planning horizon。
- **决定性 evidence:** 不能只看 probe；看 candidate regret / sample efficiency / closed-loop + unseen-query degradation。
- **最强近邻:** What Must a WM Distinguish?；Rank-One Corner；Task-Sufficient WM；WorldTest；Grounded WM。
- **Novelty 生长方式:** 若不同 query placement 形成稳定 specialization↔reuse frontier，并可被 query complexity/capacity预测，再长 modular/selective-conditioning方法。
- **Pilot:** E17。
