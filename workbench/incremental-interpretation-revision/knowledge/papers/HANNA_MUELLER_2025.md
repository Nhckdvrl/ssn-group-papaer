# 深读：Hanna & Mueller, NAACL 2025

**论文：** Incremental Sentence Processing Mechanisms in Autoregressive Transformer Language Models  
**正式稿：** https://aclanthology.org/2025.naacl-long.164/  
**范围：** 参考本次打开并核查的正式 PDF 引言、背景、方法与 Fig.1/3/§4.2；关于 QA/faithfulness 的细节依赖既有公共库的正式稿 §6、Appendix B/C/D/H/I 精读记录 [hanna-2024-gp-mechanisms](../../../../library/themes/incremental-language-processing/hanna-2024-gp-mechanisms.md)。本次未独立重新跑作者代码/模型，不将此页称复现。

## 从相关工作重建作者为什么提出这个 idea

心理语言学旧问题是“临时歧义时串行只猜一种，还是并行维护多种；后来的 disambiguator 到底修补还是重新分析？”此前 LM 工作擅长两种近似读数：读时的 surprisal、以及隐藏状态的 parse probing。两者的共同问题是**并不知道这些被 probe 出来的特征有没有被模型实际使用**。对作者而言，直接用一个 SAE 解释一张激活图不足以回答这个问题。

【根据论文论证逆向重建】第一步必须选择某个真正受 parser 影响的任务，把候选续写偏好 m 定义为函数结果。第二步借已有 SAE 及 circuit attribution（AtP-IG）筛取 causally influential features。第三步不止按 activation 词例命名“subject/object”，而要对这些 features 做 up/downweight 干预核对其行为方向。第四步将已经在 continuation 上定位的特征带到 follow-up QA：如果不能决定 QA，便说明“预测时用到的语法特征”不必是“回答时用到的特征”。这四步互相递进，不能只搬其中一张图。

## 主要实验与实际边界

- **数据/模型：** 72基础句、三构式 NP/Z、NP/S、MV/RR；Pythia70M、Gemma2-2B；不同阶段因 next-token choice mass 不足，对 MV/RR 作退出处理，后续 QA 主要在 Gemma。不能把“涵盖72句/三构式”写成全部功能实验等范围。
- **核心可操纵量：** SAE feature 的干预改变两种续写相对概率；其因果意义只对已定义 metric 范围成立。
- **多候选解释：** 不少 causal features 似乎编码主解释，也存在反向解释活跃的 features；不能从同激活立即推出完整概率分布或两个独立 parse graph。
- **后续用途：** 预测得到的语法 features 未充分复用于 QA。但论文自己有重要限制：有限 circuits 的 faithfulness 极低（Pythia NP/S .20 / NPZ 3.48；Gemma NP/S .07 / NPZ .23），不能由选中子集的 QA null 证明所有 syntax 信息从未参与回答。
- **工具与论文强度：** 作者承认需要数百/数千 features 才能接近完整重构。在解释当中，应把“已验证的一部分因果机制”与“完整模型无此机制”明确分层。

## 当前项目的具体参照与反事实

E55/E64 修改的是 GP 与 cue 版本的 **整个 source residual**，包含词面、位置、句法、置信和其他信号，与作者对单 feature 组的干预在科学尺度上不同。source patch 造成 QA 改变并不能反驳作者“某个 syntax feature 没复用”的有限结论，也不能证明源内的“新事件关系”已经形成。

真正模仿本文研究强度的方式是：先以不依赖原题 GoldNo 的 **完整新依赖内容** 证明目标关系确实可生成/可选择，再问它是否可用于独立用途；若能分离，再定位影响 **这个内容和第二用途** 的干预。若找不到特定作用变量，也可有重要的负/测量贡献，但不能让未充分忠实的 feature 介入充当机械发现。

## 逆向实验设计练习

**未知作者结果前：** 如果“parse probe 能读出语法”，下一步哪些解释仍成立？至少：probe 捕捉未使用信息；网络用另一组分布式 features；输出题的标签偏好支配结果。训练一个新的更强 probe 不能消除第一个解释。更好的下一步是对 *已经在续写中证实起作用* 的变量做干预，再测试另一用途。作者实际采用的正是“任务一筛取因果变量 → 任务二验证是否复用”的结构。这种设计方式比“多扫几十层找到一种有效改写”更值得迁移。
