# E35 — Is mechanistic component identity set by initialization or by training data? A crossed 3-init × 25-data census（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前）
- **类型：** PILOT（territory 核心问题的新维度：成分身份的来源）
- **对应：** C01（induction 成分身份在 PolyPythias seed 间不可复现；但 seed 同时改变初始化与数据顺序）；C03；Pre-carved Niches（2609.01170：单模型，主张初始化在相当程度上决定特化）；Bali 2026（头稳定性）；Olsson 2022
- **前提（已核实）：** DataDecide 中同一 seed 名在所有配方间共用完全相同的 step0 权重（6 个配方 × 3 seed 的 step0 safetensors sha256 逐一相同；不同 seed 不同）→ 1B 的 75 个最终模型构成 **3 初始化 × 25 训练数据** 的完全交叉。
- **阳性对照：** (a) 同一模型两半探针数据上的图相关（测量信度上限）≥ 0.8；(b) induction 图中至少一个头的 induction 分数 > 0.5（每个模型）
- **噪声地板：** 配对相似度的 bootstrap（按配方重采样）
- **问题（只回答这个）：** 对 induction、previous-token、attention sink、上下文取回四类头，模型间“哪个头扮演该角色”的相似度，是“同初始化、不同数据”时更高，还是“同数据、不同初始化”时更高？

## 读数（每个模型；全部保存 [层 × 头] 图）
- **M1 induction 图：** 200 条 2×128 重复随机 token 序列（E24 同），第二遍对“上一次出现 + 1”的平均注意力。
- **M2 previous-token 图：** 50 篇自然文本（Pile eval 固定子集解码后用 OLMo 分词器重新编码，各取前 256 token），对 t−1 的平均注意力。前 25 / 后 25 篇各算一次（信度）。
- **M3 sink 图：** 同上自然文本，对位置 0 的平均注意力。
- **M4 上下文取回图：** E28 的 300 条 c1_decl / c1_qa 提示，末位对干扰首 token 的平均注意力（两格式平均）。
- 标量：每类图的最大值、超过阈值（M1 > 0.3，M2 > 0.5，M3 > 0.5，M4 > 0.2）的头数；复制保真度（第二遍 loss）。

## 分析
- 对每类图：所有模型对的 [层×头] 图 Spearman 相似度；按对的类型平均：**SI**（同初始化、不同数据，3 × C(25,2) = 900 对）、**SD**（同数据、不同初始化，25 × 3 = 75 对）、**DD**（两者都不同）。另算 top-5 头集合的 Jaccard。
- 标量的二因素方差分解（初始化 3 水平 × 数据 25 水平，无重复 → 主效应 + 残差）。
- 附加（只报告）：3 个 step0（初始化本身）的图与训练后模型图的相关——初始化是否已“预刻”角色位置。

## 判据（每类图独立）
- **初始化决定身份：** mean(SI) − mean(SD) > 0.1，且按配方 bootstrap 的 95% CI 不含 0，且 mean(SI) > mean(DD) + 0.1。
- **数据决定身份：** mean(SD) − mean(SI) > 0.1，CI 不含 0，且 mean(SD) > mean(DD) + 0.1。
- **两者都不决定（身份偶然）：** SI 与 SD 都在 DD ± 0.1 内。
- 其余为“混合”，如实报告各量。
