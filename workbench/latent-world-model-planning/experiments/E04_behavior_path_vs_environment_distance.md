# E04：Behavior path length vs environment shortest distance（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01
- **问题（一句话）：** 在相同 environment transition graph / 尽量匹配 local edge support 时，仅让 behavior policy 走 shortest-ish、detour/loop、route-mixture 三种轨迹，trajectory-derived planning objective 会不会把 behavior 时间结构写进 latent geometry，并伤害真实最短可达 planning？
- **设置：** 仅在 E03 通过后运行。首选 TwoRoom/maze 类可精确计算 directed shortest steps 的环境；生成 matched start-goal 与三种 behavior dataset。通过 reweight/subsample 匹配 state occupancy / local edge support；训练 LeWM（negative control）、RC-aux，TD-JEPA 代码稳定时加入。train/test episode 完全分离。
- **读数：** environment oracle (d^*(s,g))、(R_h^*=1[d^*le h])；behavior temporal gap (Delta_eta)；label disagreement；head/latent distance 对 (Delta_eta) vs (d^*) calibration；fixed-candidate ranking/regret；novel-route/stitch goals；closed-loop success。
- **阳性对照：** 构造一组同 start-goal、detour 明确比 shortest path 长的 trajectory，必须满足 (Delta_eta>d^*)；oracle BFS/shortest path 与 simulator 简单可达 case 一致。
- **噪声地板 + MIE：** 同 dataset seed 的 repeated training/eval；pair-level calibration 以 start-goal bootstrap；closed-loop 以 paired episode CI + train-seed variance。MIE：不仅 label calibration 变，还必须在 fixed-candidate ordering/regret 或 control 上超过 E02 重复波动，才升级。
- **混杂审计：**
  - local edge/state occupancy 匹配程度作为结果报告，不隐去；
  - dataset size/optimization steps 相同；
  - goal-distance distribution 相同；
  - behavior detour 不同时改变视觉外观/physics；
  - cross-trajectory negative construction 单独记录；
  - shortest oracle 只在导航 exact setting 声称；
  - 扩到 continuous task 时不再称“ground-truth shortest path”。
- **决策表（跑之前写）：** behavior route 改变→geometry→decision 连锁成立 → 设计最小 structural correction 并另立方法卡；只 label/head 变 → I01 降级；LeWM 同样大幅变化 → 说明 dataset control 仍改变 local learning，先修匹配；effect 只在 one toy 且 continuous/contact task 无 counterpart → 不升顶会主张。
- **算力预算：** E03 后按实际单训成本决定；先 1 seed 做识别，再 3–5 train seeds confirmatory；不同 dataset variant 独立单 GPU。　**实际：** 待运行

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：未运行
- 结果文件：待生成
- 按决策表执行了什么：待运行
- 主张变化：无
- POST-HOC 分析：无