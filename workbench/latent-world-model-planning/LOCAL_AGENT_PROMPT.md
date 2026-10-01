# Local Agent Prompt — latent-world-model-planning

把下面整段作为本地执行 agent 的启动提示。**它不是让你重新找题；领域 hardening 已做，先读现有地图再执行。**

---

你正在 `Nhckdvrl/ssn-group-papaer` 的 `workbench/latent-world-model-planning/` 工作。

## 你的目标

把这个 workbench 从“文献与设计已硬化、无本地实验”的状态推进到**可复现强基线 + 可复用 measurement harness + 第一轮决定性科研 pilot**。最终目标始终是 ICLR / ICML / NeurIPS / CVPR 级论文，而不是工程 demo、benchmark 刷分或 RC-aux 小改。

### 绝对不要做
- 不从头重新 brainstorm 一堆题；
- 不把“prediction ≠ planning”“latent L2 不好”“long horizon 难”“CEM proposal 差”重新包装成 novelty；
- 不一次下载/装/跑十几个方法；
- 不因为 GPU 多就铺全 Cartesian product；
- 不自行把 workbench 改成 ACTIVE / CLOSED / candidate；
- 不以“有人做过”桌面判死；
- 不隐藏失败 seed、protocol mismatch、checkpoint load warning；
- 不把 trajectory temporal gap / cross-trajectory negative 叫 ground-truth reachability；
- 不把 internal consistency/uncertainty 当 environment executability oracle。

## 第 0 步：必须完整读这些文件

按顺序：
1. 根目录 `AGENTS.md`
2. 根目录 `RESOURCES.md`
3. `workbench/README.md`（确认全局 ACTIVE 容量）
4. 本目录 `README.md`
5. `PAPER_LINEAGE.md`
6. `PROBLEM_METHOD_MAP.md`
7. `POSITIONING.md`
8. `EXPERIMENT_PROGRAM.md`
9. `ASSETS.md`
10. `HANDOFF.md`
11. `CLAIMS.md` / `PAIN_LOG.md`
12. `ideas/I01_behavior_policy_geometry.md`
13. `ideas/I02_optimizer_support_drift.md`
14. `ideas/I03_bottleneck_regime_switch.md`
15. E00–E07 experiment cards

然后运行：

```bash
python3 tools/process/check.py
```

有 ERROR 先修流程/卡片；WARN 要理解，不要机械改。

## 第 1 步：先盘点当前机器资产，禁止重复建设

检查当前节点已有：
- repo clone / commit；
- conda/uv/python env；
- datasets；
- checkpoints；
- simulator dependencies；
- local disk 空间；
- GPU 型号、显存；
- CPU/RAM；
- 已有旧实验/日志。

把真实状态写回 `ASSETS.md`，状态必须区分：
`public entry exists → downloaded+hash → loadable → smoke passed → numeric reproduction`。

**不要为了统一依赖把所有 baseline 强装到一个环境。** LeWM / stable-worldmodel / OGBench 等允许各自 native env，通过 manifest/result schema 比较。

## 第 2 步：E00，只解决“能不能可信地跑”

执行 `experiments/E00_native_baseline_and_resource_preflight.md`：
- 单 GPU；
- 低环境并发；
- 官方小任务优先；
- 测 data wait / train step / planner call / env-render / full episode / peak VRAM；
- 验证 checkpoint、action units、goal、success checker；
- 不直接跑默认 100 epochs；
- 不把 smoke 结果当 scientific claim。

E00 完成后，把**实际**单训/单 episode 成本写回 ASSETS/experiment card，之后所有算力预算基于实测。

## 第 3 步：E01，把一次 baseline 变成之后所有研究共用的 substrate

执行 `E01_baseline_parity_and_candidate_logging.md`：
- 优先 LeWM native protocol；
- TwoRoom 做闭环；
- 再至少一个 contact-rich task（PushT/Cube，按本机资产决定）；
- 官方 checkpoint 与从头训练分开；
- logger 必须旁路，不改变 planner；
- 固定 model/data/config/checkpoint hash。

实现并保存 `EXPERIMENT_PROGRAM.md` S1–S4：
- candidate trace；
- dataset/sample manifest；
- oracle replay harness；
- common result table。

**这是最重要的工程资产。** 后续 I01/I02/I03 都必须复用，不为每个 idea 重建 harness。

## 第 4 步：E02，先复制一个已知 decision-alignment measurement，校准工具

执行 `E02_decision_audit_replication.md`：
- random / mid-CEM / elite candidate；
- Plan-Real / CEM-stage rank；
- real endpoint latent cost vs predicted endpoint latent cost；
- candidate margin；
- fixed-pool regret；
- bootstrap 单位是 start-goal pair，不是 candidate。

如果已知 effect 测不到，不许跳过直接宣布新 phenomenon；先核对 protocol。

## 第 5 步：主探索优先 I01，不要先发明方法

### I01：behavior-policy geometry contamination
执行顺序：

```text
E03 trajectory-partition invariance
        ↓ 只有通过
E04 behavior path vs environment distance
        ↓ 只有建立 geometry→ranking/control consequence
最小 correction / new C## / confirmatory multi-seed
```

E03 最关键的识别要求：
- raw transitions 一样；
- local one-step window manifest 一样；
- 只让 long-pair/trajectory metadata 改；
- hash 证明，而不是口头说“一样”。

E04 最关键：
- environment dynamics 相同；
- shortest-ish / detour / route-mixture；
- 尽量匹配 local edge/state support；
- navigation 使用真正 environment shortest-distance oracle；
- continuous manipulation 不伪称 shortest path。

如果只看到 reachability head 输出变、planner 不变：**降级，不包装。**

### I02 可以在独立节点并行，但必须等 candidate logger 可信
执行 E05：
- stage-wise support；
- model optimism；
- false elite；
- real regret；
- action magnitude/smoothness controls；
- PLDM-style uncertainty / ACID 等只按需要接。

offline model exploitation 是经典问题；只有完整 `support drift → optimism → false elite → environment regret` 链以及现有控制解释不了，才值得升级。

### I03 在 E02 后作为“统一矿图”推进
E06 oracle ladder → E07 interaction。
不要做方法大排名。目标是找**可预测 bottleneck 的 regime variable**；如果只能每任务单独解释，就 park。

## 第 6 步：如何使用很多 GPU

你可以并行：
- 不同 train seeds；
- eval groups；
- planner budget/horizon；
- fixed candidate audits；
- paired dataset variants；
- confirmatory runs。

但先：
1. dataset stage 到 node-local disk；
2. 测 1 job data_wait；
3. 再少量并发；
4. 并发增大导致 GPU idle / data_wait 上升就停。

跨节点不做梯度同步。不同地点默认不搬内部数据/私有 checkpoint。只交换代码、小 config、metrics、manifest。

## 第 7 步：方法什么时候允许出现

从一开始允许方法，但它必须来自真实证据：
- P## 痛点；
- E## anomaly；
- strong baseline unexpected success；
- near-neighbor tension。

例如 I01 如果成立，优先比较：
1. local-transition / Bellman / quasimetric consistency；
2. temporal-gap label 从 point estimate 改 interval/lower bound；
3. multi-route aggregation；
4. graph-local/connectivity objective。

**不是先选一个好看的 loss 再找解释。**

## 第 8 步：每次运行后的写回

每次实验：
1. 跑前 experiment card 已存在，若改 setting 先写 amendment；
2. raw 大文件留节点，只把 manifest/path/hash 写仓库；
3. 更新 experiment card Result；
4. 有真实现象才在 `PAIN_LOG.md` 建 P##；
5. 有证据才在 `CLAIMS.md` 建/升级 C##；
6. 更新 `logs/YYYY-MM-DD.md`；
7. 小步 commit + push。

主张升级按 `workbench/EXECUTION.md`；L2 前混杂审计，L3 前独立校对。

## 第 9 步：什么时候回来请求人审

不要每个实验来问用户。满足任一才汇报决策：
- E04 建立或否定完整 behavior→geometry→decision 链；
- E05 建立 stable support-drift chain；
- E06/E07 找到跨任务可预测 regime；
- 首个科学 C## 到 L2；
- 需要改变 ACTIVE 状态 / 抢占另一条线资源；
- 两个 lead 连续被平凡 baseline/直接近邻吸收，需要重新审 territory。

汇报格式：
```text
1. 已跑什么（E##，commit/hash）
2. 核心数字 + CI / train-seed variance
3. 哪个 C## 升/降级
4. 已排除哪些平凡解释
5. 最近近邻对 novelty 的压力有没有变化
6. 下一组最便宜且决定性的实验
7. 只列真正需要人决定的事
```

## 研究原则

本 workbench 的目标不是“跑完 E00–E07”，而是让强 baseline、oracle decomposition、paired data interventions 和大量独立实验共同逼出一个**顶会尺度的新认识**。任何 experiment 如果不会改变下一步科学判断，就不要因为卡空闲而跑。
