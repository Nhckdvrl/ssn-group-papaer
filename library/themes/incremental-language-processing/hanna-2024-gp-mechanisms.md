# Incremental Sentence Processing Mechanisms in Autoregressive Transformer Language Models（2024 v1）`[证据级别：正文 §1–7]`

[全文](https://arxiv.org/abs/2412.05353)、[代码](https://github.com/hannamw/GP-mechanisms/)。本文读取v1；最终会刊、评审分数未核对。

1. 论文形态：受控行为 + 因果mechanistic解释。
2. 背景与压力：能从hidden states解码syntax，不等于模型真的用它处理歧义。
3. 改变的前提：从GP continuation的causal features入手，再检验同组features是否支配后续QA。
4. idea来源（DOCUMENTED）：serial/parallel、repair/reanalysis的心理语言学争论，加上SAE/因果circuits以提高功能证据。
5. 与近邻距离：比Jurayj几何更强调因果；比Li parse probe更强调功能；比经典surprisal工作追问计算路径；QA结果又区分predicting与answering。
6. 方法/数据：72基础句适配三类构式；Pythia70M/Gemma2-2B；局部词汇强制两种阅读；SAE + AtP-IG + feature intervention + action probe；MV/RR因continuation choice mass限制退出后续部分分析。
7. 证据与短板：同一部分前缀可激活两种句法features；Gemma问答circuits与预测circuits的IoU约0–0.2%，syntax组干预几乎不改QA。repair/reanalysis结论依赖选中的features与读数，其结果不能扩成所有模型没有任何修订机制。
8. 可迁移动作：把一组功能已验证的解释用到第二任务，检查能否真的解释后者；对“代表什么”和“用于什么”分别提出可干预预测。
9. 对我们：泛泛的多parse共存、representation/use gap已有owner。当前不执行SAE/probe；E01若发现任务改变cue作用，需要一个更具体、更自然的问题，而不是给已有gap换个名称。
