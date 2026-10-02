# I12 — What experience is worth collecting for an actionable world model?

- **Program:** R1
- **Status:** SEED
- **Mother question:** 在固定 interaction / transition budget 下，什么数据组成最能提高 counterfactual planning utility？
- **候选 data roles:**
  - broad state coverage；
  - conditional action excitation；
  - route/trajectory diversity；
  - same-reset action branches；
  - active disagreement / uncertainty probes；
  - failure / recovery transitions；
  - query-targeted probes。
- **不是:** “多样数据更好”或“active exploration更好”。PLDM/P94/Task-Sufficient WM/Do-JEPA/FIRM等都已给出局部答案。
- **真正目标:** 分解 **每单位 transition 的 planning value**，找出环境/任务 regime 决定哪种 experience 最值钱；最好出现 data-composition law，而非单策略winner。
- **readout:** counterfactual action fidelity、fixed-candidate regret、closed-loop success、unseen-query/goal transfer；prediction MSE只是 guard。
- **升级条件:** data strategy排序随可解释 regime变量系统变化，或出现一个原有 data heuristic漏掉的高价值 data type。
- **Pilot:** E16。
