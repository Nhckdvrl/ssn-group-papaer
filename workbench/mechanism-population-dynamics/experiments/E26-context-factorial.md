# E26 — Which property of a context does pretraining Flan make models rely on?（2026-10-03）

- **状态：** REGISTERED（判据提交于计算之前；提示构造已在 CPU 上检查，见下）
- **类型：** PILOT（因子化拆解；E25 的必要后续）
- **对应：** E20、E25；审计（logs/2026-10-03.md）：Coherent vs Substitution 同时混杂 问答格式（100% vs 0%）/ 干扰出现次数（2–4 vs 1）/ 篇幅（84–110 vs 13–23 词）。Xie et al. 2023（连贯证据更有说服力）；Du et al. ACL 2024（相关 / 肯定语气的上下文说服力更高）
- **阳性对照：** 所有模型中，出现次数效应（cK − c1）> 0（更多次提及 → 更多采信），否则操纵无效
- **噪声地板：** 每配方 3 seed；SE = 配方内 seed SD × √(1/3 + 1/3)，SD 在 4 个配方（dolma1_7、no_flan、c4、dclm-baseline，各 3 seed，自由度 8）上合并估计；c4 与 dclm-baseline 只用于估计 SD
- **问题（只回答这个）：** 预训练中加入 Flan 所带来的采信增加，主要随上下文的哪一个属性出现——问答格式、干扰答案的出现次数、支持性论述（相同出现次数下）、还是篇幅？

## 设置
- 模型：dolma1_7-1B 与 dolma1_7-no-flan-1B × 3 seed（step69369）；另 c4-1B、dclm-baseline-1B × 3 seed 仅用于 seed SD。共同条目只在前两个配方的 6 个模型上取（SD 配方在各自 3 seed 的共同已知条目上计算）。
- 条目：ParaConflict 6 类，在 6 个模型都已知（clean：lp(答案) > lp(干扰)）的共同条目上。
- 每条目由数据集自身文本构造：S = Substitution 的首句（“<陈述> <干扰>.”）；P = Coherent 中 “Question:” 之前的段落（含干扰 k 次，k ∈ {2,3,4} 随类别）；q = Coherent 中的问句；stem = Coherent 中 “Answer:” 之后的陈述开头（所有单元统一使用）。F = 固定的中性填充文本（无实体、无数字），按词数截断使 F + S 与 P 词数相同。
- 上下文：c1 = S；cK = S 重复 k 次；cP = P；cF = F + S。结尾：decl = 上下文 + “ ” + stem；qa = 上下文 + “ Question: ” + q + “ Answer: ” + stem。共 8 个单元。
- 读数：采信边际 lp(干扰) − lp(答案)（首 token 前加空格、EOS 起始，与 E20 相同）。

## 对比（每个模型，共同条目均值）
- 格式 = mean_ctx(qa − decl)；次数 = cK − c1（decl 与 qa 平均）；论述 = cP − cK（同次数）；篇幅 = cF − c1。
- Flan 效应 Δ_X = mean_3seed(dolma1_7) − mean_3seed(no_flan)，对每个对比 X 以及对 8 个单元本身分别计算。

## 判据
- 阳性对照：6 个模型的“次数”对比全部 > 0。
- 对每个 X ∈ {格式, 次数, 论述, 篇幅}：Δ_X > 2·SE_X 记为“Flan 增强该属性的作用”。
- **归因：** 若恰有一个 X 满足且其 Δ_X 至少是其余的 2 倍 → Flan 效应归因于 X。若多个满足 → 如实报告为多因素。若没有一个满足、而单元层面的 Flan 主效应显著 → Flan 是整体性的采信增加，不随这些属性变化。
- 不追加单元；不改读数。

## 提示构造检查（CPU，登记前完成）
- 2146 / 2146 条 Coherent 提示恰有一个 “Question:”，其后含 “Answer:”（结构一致）。
- `--check`：2146 条全部通过（各单元干扰出现次数 c1=1、cK=cP=k、cF=1；k 均值 3.22，范围 2–4）；cP 92.0 词、cF 91.7 词（填充在句末截断，|差| ≤ 10 词）；c1 18.0 词、cK 41.1 词。填充文本不含任何答案 / 干扰词。
