# E03：Trajectory-partition invariance — 同 local transitions，只改 long-pair supervision（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01
- **问题（一句话）：** 当 raw transitions、local one-step windows、environment dynamics 完全相同，只改变 trajectory boundary / long-pair metadata 时，trajectory-supervised reachability/progress geometry 是否随之改变并影响 candidate ordering？
- **设置：** 先用最易做 exact manifest control 的 navigation task。由同一 raw transition store 生成 A/B 两个 dataset view：A 原始 trajectory organization；B 只改变 long-pair/episode metadata，使 RC-aux/TD-JEPA 的 pair label/采样发生预期变化，但 LeWM one-step/local window manifest byte-identical。首轮 1 train seed × 1 task；只有超过 gate 才扩 3 seeds。
- **读数：** local transition hash、one-step window manifest hash、long-pair manifest hash；同 latent pair 的 supervision label/gap distribution；reachability/TD output；encoded-real and predicted candidate ordering；Plan-Real/elite Spearman；fixed-pool regret；closed-loop success（pilot 次要）。
- **阳性对照：** 人工选择一组 pair，使 A/B 的 trajectory-derived label 必然不同；数据 loader 输出必须显示 label shift。LeWM local-prediction negative control 在 A/B 的训练 sample manifest 应完全一致。
- **噪声地板 + MIE：** 相同 dataset view + seed 重建 manifest 应 hash 一致；相同 checkpoint evaluation 重跑给出 geometry/rank 波动。pilot MIE：A/B 差异必须明显超过重复波动，且至少在 candidate ordering 或 regret 上达到足以触发 E04 的量级；具体阈值在 E02 结果后、首次训练前写入日志并冻结。
- **混杂审计：**
  - 禁止改变 raw frame/action bytes；
  - 禁止改变 one-step/local windows；
  - image augmentation RNG 固定/记录；
  - pair 数变化需要 reweight 使总优化步/long-pair exposure 可比较；
  - optimizer/train steps/seed/初始化匹配；
  - A/B goal sampling 与 test set 相同；
  - 若 segmentation 破坏 Markov/context history，另记，不与主要处理混淆。
- **决策表（跑之前写）：** target shift→geometry/rank shift > MIE → E04 行为路径干预；target shift 但 geometry 不动 → 核对 loss weight/optimization 后一次 confirmatory rerun，仍 null 则 PARK I01；local sample hash 不同 → VOID；只有 head output 变而 ranking/decision 不变 → 不升级科学主张。
- **算力预算：** E00 后按单次训练成本填写；首轮最多 A/B + local-predictive control，各单 GPU，可并行但不共享随机读盘。　**实际：** 待运行

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：未运行
- 结果文件：待生成
- 按决策表执行了什么：待运行
- 主张变化：无
- POST-HOC 分析：无