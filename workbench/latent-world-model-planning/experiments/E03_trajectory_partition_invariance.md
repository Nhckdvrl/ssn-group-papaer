# E03：Valid trajectory refactorization invariance（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01
- **问题（一句话）：** 当 environment 与 raw local transition multiset 完全相同，只把 transition 在共享 junction 处重新组成不同的**合法 trajectories**时，trajectory-supervised RC-aux / TD-JEPA 是否学出不同 long-range planning geometry，并改变 fixed-candidate decisions？

## 设置

首选可精确知道 state/junction 的 navigation task（TwoRoom / maze family），先 1 train seed 做 identification。

从同一 raw store 构建：

- **A original factorization：** 原 trajectory decomposition；
- **B valid cut-and-splice：** 只在相同/容差内等价 junction state 处切开并交换 suffix，使拼接后的每条相邻 transition 都是原 store 中真实 transition；
- **C split-only（可选 sanity）：** 只切 episode 不跨 route 拼接，测试 logging-boundary sensitivity。

### 必须满足的 hard invariants

A/B：
- raw `(o_t,a_t,o_{t+1})` multiset hash 相同；
- local transition count 相同；
- LeWM 用到的 fixed-history/one-step training window multiset hash 相同；若 history=3，splice junction 附近会改变 history window，则必须**排除 junction-crossing windows或构造 matching views**，直到 hash 可证明一致；
- image/action bytes 不改；
- train/test split 不改；
- dataset size、batch exposure、optimizer steps、augmentation policy相同；
- 只允许 long-range within-trajectory pair membership / observed gap / cross-trajectory status 改变。

若做不到这些，E03 不叫 identification experiment，只能降级成普通 data perturbation。

## 被测方法

首轮：
1. RC-aux；
2. TD-JEPA（official repo 已核对，包含 LeWM/RC-aux variants）；
3. LeWM one-step local-prediction negative control。

有现成实现再加一个**local geometry control**（Temporal Straightening 或 CGS），不因“完整”先实现。

## 读数

### Data-level
- raw-transition hash；
- one-step/history-window manifest hash；
- long-pair manifest hash；
- pair membership change rate；
- same pair 的 (Delta_β) / reachability label change；
- cross-trajectory-negative status flip rate。

### Model-level
- RC-aux (R_phi(z,z',h)) / TD-JEPA (d_psi) 对同一 evaluation pair 的 paired shift；
- 与 environment shortest-distance/reachability oracle 的 calibration（只在 exact nav setting）；
- representation pairwise distance / local geometry only as secondary diagnosis。

### Decision-level
复用 E02 固定 candidate pool：
- Plan-Real / elite-stage rank；
- selected action flip rate；
- candidate-set regret；
- predicted vs encoded-real endpoint score；
- closed-loop success 只作 pilot consequence，不用少量 episode夸大。

## 阳性对照

预注册至少一组 junction splice，使某些远状态 pair：
- A 中 same trajectory、gap = (Delta_A)；
- B 中 gap = (Delta_B
eqDelta_A)，或变成 cross-trajectory；
同时它们之间的 environment shortest path (d^*) 不变。

loader 必须显示 target shift；否则 treatment 没真正作用。

## 阴性对照

- LeWM local prediction在 A/B 的 sample manifest和loss exposure相同；
- raw transition prediction smoke 差异应落在训练随机性范围；
- local geometry method（若加入）不读取 altered long-pair metadata。

## 噪声地板 + MIE

- 同一 view/seed 重建 manifest hash 必须确定性一致；
- same checkpoint / candidate pool 重复评测，bootstrap over start-goal pairs；
- **pilot gate：** 不以 head-output shift 为 MIE。至少一个 decision-level量（rank / selected flip / regret）要超过 E02 的 repeat floor，并方向与 target→geometry prediction一致，才进入 E04。
- 数值阈值在 E02 结果出来后、E03 第一条训练命令之前写到 run log，之后不改。

## 混杂审计

- junction matching tolerance：预注册；离散状态优先 exact；
- history windows：必须 hash 等价，不能只说 raw transitions相同；
- pair exposure：A/B total pair count/weight/optimizer steps匹配；
- cross-trajectory negatives：单独统计，不让 positive-gap 与 negative-status 两个 treatment 混在一起而不报告；
- data ordering / augmentation RNG：固定或记录；
- model init / train seed：paired；
- goal/eval manifest：完全相同；
- test data不参与 trajectory refactorization选择。

## 决策表（跑之前写）

- **A：target shift + model geometry shift + decision shift > MIE，LeWM/local controls稳** → E04；
- **B：target/head shift明显，decision-level null** → I01 暂不升级；一次 optimization/weight sanity 后仍 null 则 PARK；
- **C：RC-aux/TD-JEPA 都基本 invariant** → 记录强 robustness；检查机制，不强行制造更极端 splice；
- **D：LeWM/local control也变或 history-window hash不同** → VOID，修数据 construction；
- **E：仅 split-only 有效、valid splice 无效** → 标 logging-boundary artifact，不进入主 story，除非真实数据 pipeline有广泛影响。

- **算力预算：** E00/E01 实测速率后填；首轮 A/B × {RC-aux, TD-JEPA, LeWM} 可独立单 GPU；不要共享盘同时随机读，先 node-local stage。  
- **实际：** 待运行

## 结果
未运行。