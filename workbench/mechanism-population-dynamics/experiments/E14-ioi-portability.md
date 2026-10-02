# E14 — Claim portability for the IOI circuit across independent runs（2026-10-02）

- **状态：** RUNNING（预测提交于任何 E14 结果之前）
- **类型：** CLAIM（C03 的第三个机制，前瞻检验）
- **对应：** C03、E15；Tigges et al. 2024（单 run 中 IOI 成分随训练更替、算法保持）；IOI sign-flip（ICML 2026 MIW；发育事件在 PolyPythia 变体上复现）
- **阳性对照：** canonical `pythia-160m` / `pythia-410m` 应有 IOI 行为（Tigges：≥160M 学会 IOI），且名称移动头（name mover）的群体消融显著降低 logit 差
- **噪声地板 + MIE：** 每个 run 200 条 IOI 提示的 bootstrap；20 组随机头对照；实验单位 = run（每个尺寸 10 个）
- **决策表（跑之前写）：** 见下方
- **问题：** C03 的分层（角色 / 角色整体必要性可迁移；具体成分不可迁移）是否在第三个、谱系最成熟的电路上成立？

## 设置
- 模型：`pythia-160m` + `seed1..9`、`pythia-410m` + `seed1..9`，step 143000（已过 R0）。
- 数据：Tigges 官方 `data/ioi_dataset.py`（curt-tigges/circuits-over-time@803038e4eb；Wang et al. 2022 生成器），`prompt_type="mixed"`，N=200，`random.seed(0)`；ABC 对照集按原作者方式用 `gen_flipped_prompts` 生成，用于均值消融参照。
- **行为：** END 位置 logit 差 = logit(IO) − logit(S)；准确率 = logit 差 > 0 的比例。
- **名称移动角色（NMH）：** 每个头在 END 位置对（IO − S）unembed 差的直接贡献（DLA）；NMH = DLA ≥ 全部正 DLA 之和的 10%，且 END→IO 注意力 > END→S 注意力。
- **消融：** 在 END 位置把头输出 z 替换为其在 ABC 集上的 END 位置均值；群体 = 全部 NMH；单体 = DLA 最大的 NMH；对照 = 20 组同大小、排除 NMH 的随机头。

## 陈述类型与预测（预注册）
| 代号 | 陈述 | 预测 |
|---|---|---|
| I1 行为存在 | IOI 准确率 ≥ 0.8 | 不预测（作为前提报告） |
| I2 角色存在 | 至少一个 NMH | 可迁移性 ≥ 0.9 |
| I3 角色整体必要性 | NMH 群体消融使 logit 差下降 ≥ 50% 且超过全部随机组 | ≥ 0.9 |
| I4 成分编号 | 参照 run 的 top NMH（层.头）在目标 run 中也是 NMH | ≤ 0.3 |
| I5 近似深度 | top NMH 层差 ≤ 1（占总层数比例换算后报告严格同层） | ≥ 0.7 |
| I6 单成分必要性 | top NMH 单独消融 ≥ 群体效应的 50% | 不预测 |
| I7 行为强度 | logit 差与参照 run 相差 ≤ 0.5 | 不预测 |

## 决策表
- **C03 跨三机制成立：** I2、I3 ≥ 0.9 且 I4 ≤ 0.3（两个尺寸都满足）→ C03 扩展到三个机制，考虑升级（需混杂审计与独立校对）。
- **部分：** I2/I3 只在一个尺寸满足，或 I4 > 0.3 → 按实际结果收窄 C03。
- **不成立：** I2 或 I3 < 0.7 → “角色可迁移”不是一般规律，C03 只保留 induction / 仲裁上的结论。
