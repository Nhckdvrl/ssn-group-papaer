# I08 — Explicit rollout vs implicit predictive abstraction

- **状态：** SEED / broad problem mine
- **母问题：** reward-free offline learning中，predictive structure 应保存为可任意 rollout 的 explicit action-conditioned dynamics，还是 amortize 成 long-horizon successor/policy-conditioned implicit representation？何种 regime 决定选择？
- **领域依据：** TMLR'26 *What Drives Success in Physical Planning with JEPA-WMs?* 已明确区分 explicit 与 implicit，并把 training-cost / inference-cost / generalization trade-off 的 direct comparison 留作 future direction。Bagatella **TD-JEPA** (2510.00739) 是 implicit canonical example；DINO-WM/PLDM/JEPA-WM/LeWM 是 explicit side；TD-MPC2等为 hybrid。
- **不是：** 两篇论文横向抄主表、单纯 latency benchmark、泛泛“hybrid更好”。
- **必须找的 scientific object：** 少数 regime variables 能否预测 explicit / implicit / hybrid 的优势与失败，例如：
  - reward/goal redefinition；
  - unseen objective composition；
  - environment dynamics/layout shift；
  - horizon；
  - data coverage；
  - deployment search budget；
  - arbitrary supplied-action counterfactual query需求。
- **最小 pilot：** common offline data + common real utility + matched train/test task definitions；native protocols保留，另加 common-audit protocol；同时记录 train compute 与 deployment model calls。
- **升级条件：** 至少一个跨 task family稳定的 regime boundary，且不是总compute差异；最好能在未用于拟合的 regime 预测 intervention ranking。
- **可能的方法形态：** adaptive/hybrid allocation、explicit short-horizon + implicit tail、query-dependent compute placement；仅在 boundary成立后设计。
- **命名警告：** Bagatella TD-JEPA ≠ Bai/Xiong Temporal-Distance JEPA；后者历史 config 也叫 `td_jepa`。
- **对应：** E13 → conditional cross-regime confirmation。
