# E23 — Does corpus repetition structure predict a recipe's copy-vs-recall prior?（2026-10-03，CPU + 网络）

- **状态：** REGISTERED（判据提交于计算之前；登记时已看过 23 个 default seed 的配方均值（见 logs/2026-10-03.md “E20 描述性查看”），尚未计算任何语料统计量）
- **类型：** PILOT（数据 → 倾向；为后续“数据 → 机制 → 倾向”中介检验做准备）
- **对应：** E20、E22；Chen, Luo, Pan 2026（重复结构催化 induction 头）；Chen et al. ACL 2024（平行结构 → ICL）；Kim et al. 2025（文档内重复 → 依赖上下文）
- **阳性对照：** 统计量的方向性检查——tulu/flan 集合的 S1 应显著高于普通网页集合（falcon、c4）；否则统计量没有测到“平行结构”，主检验不可判定
- **噪声地板：** 配方均值用 3 seed 平均；统计量按文档 bootstrap
- **问题（只回答这个）：** 25 个 DataDecide 配方的语料“可复制性”（文档内重复结构）能否预测该配方在 Substitution 冲突（“X is Y. X is ___”）上的平均采信边际？

## 语料统计（每个数据集合取一个分片开头 ~25M token，经 HTTP Range；配方值 = 按集合 token 量加权平均）
- **S1 induction 可预测率：** 文档内 token t_j 满足“前两个 token 组成的二元组此前在同一文档中出现过、且其后接的正是 t_j”的比例。
- **S2 长程逐字重复率：** 处于文档内重复 8-gram 中的 token 比例。
- **S3 问答格式密度：** 每千 token 中行首 “Question:/Answer:/Q:/A:” 的次数。

## 判据（实验单位 = 配方，n = 25；E20 的 3 seed 平均）
- 主检验：Spearman(S1_recipe, Substitution 平均采信边际) ≥ 0.5 且置换 p < 0.05 → 语料可复制性预测复制先验。
- 区分：S3 只应预测 Coherent × World Capital（唯一带问答格式的条件）；若 S3 对 Substitution 的预测强于 S1，说明是“指令格式”而非“重复结构”。
- 混杂：对配方均值 clean 边际（知识强度）做偏相关，结论需在偏相关下保持（|变化| < 0.15）。
- |ρ| < 0.2 → 语料重复结构不能解释配方差异；如实报告，不追加统计量。
