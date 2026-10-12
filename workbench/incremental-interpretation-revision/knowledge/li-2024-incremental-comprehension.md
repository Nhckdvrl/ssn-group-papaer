# Incremental Comprehension of Garden-Path Sentences by Large Language Models（CogSci 2024）`[证据级别：正文 Methods–Discussion]`

[论文](https://arxiv.org/abs/2405.16042)。评审、展示形式与分数未核对。

1. 论文形态：心理语言学理论 + 逐段受控测量。
2. 背景与压力：surprisal能检测困难，却不直接说明模型最终支持什么解释。
3. 改变的前提：把人的comprehension问答搬到LLM，逐chunk测initial proposition，并用parse/attention补证。
4. idea来源（DOCUMENTED）：Christianson 2001和Patson 2009的lingering与comma效应；作者试图在相同刺激上直接比较解释。
5. 与近邻距离：相对Jurayj 2022几何，增加语义问答；相对经典人类研究，增加模型内部parse与attention；相对surprisal论文，追踪最终理解而不仅难度。Amouyal 2025随后进一步拆plausibility/verbtype。
6. 方法/数据：24 NPZ；五chunk；GP/comma；GPT2/LLaMA2/FlanT5/RoBERTa；GPT2/RoBERTa训练parse probe。论文预检final问句成功，后续主要initial问句；不能将其预检结果当成我们数据的保证。
7. 证据与短板：comma改善和部分parse-shift/spillover；不同任务最像人的模型不同。样本小，attention指标不是因果机制；将Yes/No当正确/错误解释时需保留未蕴含与逻辑假的区别。
8. 可迁移动作：同刺激上的不同读数，定位证据到达前后发生的变化；但先检查final读数，不只观察No概率上升。
9. 对我们：双解释、逐段变化、comma本身都有owner。E01是measurement，不能把这些现象写成new story；若读数分离，要追具体干预为何改变某一读数。

## 2026-10-12 独立精读补记（作者v1 HTML；表1数字核对）

24句Christianson材料分5块呈现；两类题：误读题“Did the man hunt the deer?”与正确读题“Did the deer run…?”，**预测试中所有模型都答对正确读题，故分析只看误读题**。无逗号时四模型在消歧块后“继续支持误读”；有逗号时LLaMA（p=.003）、GPT-2（p=.05）下降，只有LLaMA切换到正确语义。parse probe结构切换率：GPT-2无逗号到块5仅16.67%、有逗号50%；RoBERTa 45.83/62.50；人类35.4/73.4（Christianson）。注意力只有定性热图。
**对我们**：他们的“正确读题”是主句事实（“deer ran”），不是替代依赖（“man hunted [himself/intransitively]”），所以“都答对”不与我们的0–12%矛盾；他们没有问替代依赖题。idea来源是Christianson+Patson的材料直接迁移到四个旧模型；尺度小（24句、4模型）。
