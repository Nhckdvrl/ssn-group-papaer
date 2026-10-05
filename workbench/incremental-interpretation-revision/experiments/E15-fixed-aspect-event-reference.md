# E15：固定 continued 拆分活动指向与先前活动预设（2026-10-05）

- **状态：** PLANNED
- **类型：** EXPLORE（E14 异常后的语言干预，不做模型/prompt sweep）
- **对应：** P10；C01/C02 的解释边界。不是预设 paper idea。
- **问题（一句话）：** E14 的 same−separate 变化，来自活动指向不同，还是 continued/began 与先前活动预设同时变化？
- **设置：** 本地 pinned Qwen3-8B，frozen FP32/SDPA、TF32=false，普通 raw text，无 chat/question/instruction；seed=0，batch=4。只新增 176 条 continued-a-separate 原句变体，复用 E14 已冻结的 528 条。22 author source clusters × 2 original NP options × GP/comma × 2 target continuations。主切片沿用事前独立审出的 7 episodic sources；全部22、两个NP选项、原source blocks及eligible/clear-reference分项均报告。
- **材料：** E14 began-a-separate 桥中仅 began→continued，所有其余字符、actor、activity NP、目标替代词与词数不变；机械校验完整字符串单词差异及目标跨度。176 条经独立 GPT Luna 审查，全部acceptable/clear separate；无 semantic gold。所有版本/cache/hash 见 `results/D0-E15-preparation-v1.json`；原文/衍生句不进 git。审核者的 prior-activity support 用了未来S2，明确不进入因果预测或筛选。
- **读数：** R = 初始患者NP目标总bits − 原self/reciprocal目标总bits；D = R_GP−R_comma。A = D_continued-same−D_continued-separate；B = D_continued-separate−D_began-separate。逐source验证 A+B=E14 原interaction。两个NP先在source内均值，paired bootstrap 10,000、seed20261005；报告95%CI与每个source，无独立变体伪重复。替代短语长度不同，因此绝对R不是准确率；GP/comma配对固定短语，长度影响在相减中抵消。
- **阳性对照：** E14 原interaction保留且原材料/hash锁定；不同target causal-context token相同，首batch手工span损失与HF masked loss核对。E14的无桥baseline与E13同句2168词最大差5.51e−5bits。这里不新加选择性重复，也不以control设自动科学gate。
- **噪声地板 + MIE：** 已知FP32词级数值漂移约1e−5bits；主要不确定性为source异质性与7组主样本。以分解结果的大小、方向、CI及逐项一致性改变解释，没有预先任意效果门槛。
- **混杂审计：** A固定continued，仍改变that particular/a separate（活动指向与determiner语义不能完全分开）；B固定a separate，continued同时引入先前进行中的另一活动，可能是预设accommodation而非纯aspect。跨anchor的桥长相同；S1原样；所有audited变体均评分。新旧run检查权重manifest、precision、attention、batch、库版本一致。独立scope标记来自E14原后文，保持不随结果改动。词汇预测/文本repair仍是竞争解释，单次分解不能证明内部event graph。
- **决策表（跑之前写）：** A保留大部分负interaction而B小 → 活动指向条件下的旧绑定使用仍值得追，随后控制determiner与指向清晰度；A小而B负 → 当前桥变化主要与continued的活动预设有关，不能讲event identity；A/B均明显 → 混合解释，先找分别响应的source结构；CI宽或源组反向 → 报告异质性并追具体材料，不加模型/prompt sweep。任何结果都不自动关闭territory或宣布novelty。
- **算力预算：** 一张空闲H20、预计≤0.03 GPU·时；只176新输入，528旧输入仅统计复用。**实际：** 待运行。
- **命令：** `source scripts/env.sh` 后运行 `$IIR_PYTHON scripts/event_identity_infer.py --experiment E15 --data $IIR_CACHE/E15-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E15`；分析用 `scripts/aspect_reference.py --old $IIR_CACHE/runs/E14 --new $IIR_CACHE/runs/E15 --cache $IIR_CACHE --out results/E15-summary.json`。以上路径在本workbench内执行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行。C01/C02维持L0。
