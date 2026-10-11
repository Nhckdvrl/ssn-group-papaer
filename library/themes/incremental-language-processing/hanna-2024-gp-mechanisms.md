# Incremental Sentence Processing Mechanisms in Autoregressive Transformer Language Models（2024 v1）`[证据级别：正文 §1–7]`

[全文](https://arxiv.org/abs/2412.05353)、[代码](https://github.com/hannamw/GP-mechanisms/)。本文读取v1；最终会刊现已核对为NAACL2025；评审分数未核对。

1. 论文形态：受控行为 + 因果mechanistic解释。
2. 背景与压力：能从hidden states解码syntax，不等于模型真的用它处理歧义。
3. 改变的前提：从GP continuation的causal features入手，再检验同组features是否支配后续QA。
4. idea来源（DOCUMENTED）：serial/parallel、repair/reanalysis的心理语言学争论，加上SAE/因果circuits以提高功能证据。
5. 与近邻距离：比Jurayj几何更强调因果；比Li parse probe更强调功能；比经典surprisal工作追问计算路径；QA结果又区分predicting与answering。
6. 方法/数据：72基础句适配三类构式；Pythia70M/Gemma2-2B；局部词汇强制两种阅读；SAE + AtP-IG + feature intervention + action probe；MV/RR因continuation choice mass限制退出后续部分分析。
7. 证据与短板：同一部分前缀可激活两种句法features；Gemma问答circuits与预测circuits的IoU约0–0.2%，syntax组干预几乎不改QA。repair/reanalysis结论依赖选中的features与读数，其结果不能扩成所有模型没有任何修订机制。
8. 可迁移动作：把一组功能已验证的解释用到第二任务，检查能否真的解释后者；对“代表什么”和“用于什么”分别提出可干预预测。
9. 对我们：泛泛的多parse共存、representation/use gap已有owner。当前不执行SAE/probe；E01若发现任务改变cue作用，需要一个更具体、更自然的问题，而不是给已有gap换个名称。

## Final NAACL2025核对

[出版PDF](https://aclanthology.org/2025.naacl-long.164.pdf)的§6及B/C/D/H/I附录已重读，独立hash见ledger。QA IoU NP/S=0%、NP/Z=.2%及“不广泛复用”保留。重要范围：Pythia QA常constant50%，因此只对Gemma做后续功能结论。QA阳性题也存在，不是单一No评分。Appendix C回收faithfulness：Pythia NP/S .20、NP/Z3.48；Gemma NP/S .07、NP/Z.23，作者承认需要数百/数千features才能近1。因此有限feature组没有效果不足以彻底排除其他syntax用途；这是研究范围，不是桌面否定已有工作。Appendix H跨construct非特异干预改变NPZ约10pp也一并报告，不能写所有干预严格零。泛泛predicting/QA gap仍是明确owner；不以发现证据限制直接宣称我们的novelty。

## 2026-10-06 复读要点
RQ3 原话：LM 既不修补先前的结构预测，也不通过重分析生成新的句法特征。Gemma-2-2B 的 GP 问答主要由与句法无关的 Yes/No 倾向特征驱动（例如在 "Certainly / Of course" 上激活的特征）。作者把"识别歧义"留作未来工作。对 C1 来说，这意味着：小模型的问答读数会被回答倾向污染，所以必须选真实缺陷大的中等规模模型，并用复述和蕴含状态分层的读数。

## 2026-10-07：针对当前干预的复核

重读正式稿引言、§3/§4.1/§4.2开头、§6–7与limits。作者的repair定义是消歧之后输出依赖原有reading-specific特征；reanalysis依赖reading-agnostic旧特征，并可能构建新的reading-specific特征。这些定义不是“答案更正确/干预有正效应”就自动满足。主要72句/3构式是预测部分，MVRR因next-token choice mass退出后续分析；QA只分析Gemma2-2B，不能扩大为所有现代模型/构式。基础QA阳性、正负问题平衡与源特征组选取的范围都保留。

E55/E63与它的具体距离尚未成立：我们用自然cue的整个源残差，能改变后续源句计算和查询计算，不是它已解释的有限syntax feature组。整体cue替换的正效应不能直接反驳其限定结论，也不能证明“消费者选错了已经正确的源关系”。要区分编码过程和已存表示的使用，可借Feng冻结其余context的动作：让后续源位置保持原GP计算，只改变已有源位置的表示，观察不同用途的变化。此动作是下一候选，待E63完整角色结果决定是否值得执行，不再扫描同一mask窗口。全量词替换仍含句式/位置/置信等多因素，最终须有具体关系变量与保持性控制。
