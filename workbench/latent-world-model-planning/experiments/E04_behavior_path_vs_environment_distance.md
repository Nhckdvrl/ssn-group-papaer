# E04：Natural behavior routing vs environment distance（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01
- **前置：** E03 必须建立至少 decision-level 的 trajectory-factorization sensitivity；否则不运行 E04 扩大故事。
- **问题（一句话）：** 在相同 environment dynamics 与尽量匹配的 local transition support 下，shortest-ish、detour/loop、route-mixture 三种**自然 behavior policy**是否把不同 routing statistics 写入 trajectory-supervised planning geometry，并导致对真实 environment controllability 的不同决策？

## 设置

首选 TwoRoom/maze 类能精确求 directed shortest-step distance (d^*(s,g)) 的环境。

生成 matched datasets：
1. **Shortest-ish:** 偏向短路径；
2. **Detour/loop:** 对相同/匹配 start-goal 系统性走更长但合法路线；
3. **Route-mixture:** 多条可行路线的 mixture，控制 route frequency。

通过 reweight/subsample 尽量匹配：
- dataset size；
- state occupancy；
- local directed edge occupancy/support；
- start/goal distribution；
- action marginal；
- observation rendering/physics。

绝对匹配做不到时，把 residual imbalance量化并作为 covariate/限制，不写“完全 controlled”。

## 方法

- RC-aux；
- TD-JEPA；
- LeWM negative control；
- 至少一个不使用 long-range behavior-gap target 的 local-geometry baseline（优先 Temporal Straightening 或 CGS，代码可用性决定）。

## Oracle 与读数

导航 exact setting：
- environment shortest distance (d^*(s,g))；
- finite-budget oracle (R_h^*(s,g)=mathbf{1}[d^*(s,g)le h])；
- observed behavior gap (Delta_eta(s,g)) 的 distribution。

比较：
- target disagreement: (Delta_eta) / proxy label vs (d^*,R_h^*)；
- learned head/geometry 更贴近 (Delta_eta) 还是 environment oracle；
- fixed-candidate rank / elite rank；
- selected-action flips；
- candidate-set regret；
- unseen route / stitching goals；
- closed-loop success。

**continuous/contact-rich 扩展：** 不声称 ground-truth shortest path。改做 paired behavior dataset + same candidate real execution consequence，并报告只有 navigation有 exact oracle。

## 阳性对照

预先构造若干 matched start-goal：
[
Delta_{	ext{detour}}(s,g) > Delta_{	ext{short}}(s,g) ge d^*(s,g)
]
且环境 (d^*) 完全相同。BFS/graph shortest oracle先用 trivial cases验算。

## 噪声地板 + MIE

- 每个 behavior dataset先 1 paired seed；
- start-goal pair bootstrap；
- closed-loop episode CI 与 train-seed variance分开；
- **升级 gate：** 不仅 target/head calibration 变化，而且 fixed-candidate rank/regret或control consequence超过 E02 noise floor；
- 只有通过后才 3–5 train seeds + contact-rich扩展。

## 混杂审计

- local edge/state occupancy mismatch显式报告；
- goal-distance distribution相同；
- dataset size / optimizer steps / pair exposure相同；
- detour policy不同时改变 visual appearance/physics；
- cross-trajectory negatives另记；
- behavior policy生成器不看 test outcome；
- method hyperparameters在 validation选，不按哪一组更有利重调。

## 决策表

- **behavior routing → proxy/geometry → decision chain成立，local controls稳** → 新建方法卡：优先 dynamics/local consistency / quasimetric / multi-route aggregation；
- **只 target/head变，decision null** → I01 降级，不做大 seed；
- **LeWM/local geometry也同幅变化** → data matching仍有 confound，回 data construction；
- **navigation成立但 contact-rich没有任何 counterpart** → 限制 scope，不直接升顶会主张；
- **simple quasimetric/Bellman baseline已经完全恢复 invariance** → 这是好结果：可把 paper重点变成“识别 + 强简单基线”，而不是强行造复杂方法。

- **算力预算：** E03 后基于实测；variant×seed独立单 GPU，数据 node-local staging。  
- **实际：** 待运行

## 结果
未运行。