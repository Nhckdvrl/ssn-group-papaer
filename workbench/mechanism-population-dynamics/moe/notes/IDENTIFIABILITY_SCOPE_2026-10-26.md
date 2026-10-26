# 总函数约束、可识别性与当前实验范围（2026-10-26）

> **2026-10-26 后续整理：** 本文的条件性命题与历史范围讨论保留；当前研究使用的局部跨输入算子、有限 cohort 重组关系及预测读出边界统一见 [RESEARCH_DIRECTION](../RESEARCH_DIRECTION.md)。其中有额外假设的可识别性讨论不能直接当作实际学生的全局保证或方向关闭依据。

这份概念校正不新增实验/主张，不提出理论原创性。当前应问：**固定语言计算要求，在有限训练中哪些实际计算分解会重复出现，额外分配信息是否约束它们？** “sum-only监督必然不可识别”不是可用前提。

## 一个条件性的充分条件（自主推导；已由独立审读核对）

在连通开域D上，共同gate logits g_e及两套expert函数f_e、f'_e均实解析，0<k<E。对每个实际出现且具有非空strict top-k开区域的subset S，假定两套模型aggregate在整个D严格相同。共用正分母可消去（全softmax no-renorm及共同selected-renorm均可），得到该区域内

`sum_{e in S} exp(g_e(h)) [f'_e(h)-f_e(h)] = 0`。

每个左边在D解析，故由恒等延拓在D处处为0。令A为这些subset的0/1 incidence矩阵。如果A列rank=E，逐h有Aq(h)=0，且exp(g)>0，因而每个expert函数相同。它不保证神经参数唯一。

充分实现条件之一：中心化线性gate的rank为E−1，且输入域允许logit像覆盖全部零和空间，则全部strict k-subsets可实现；任意i/j的subset行差生成e_i−e_j，再由一行非零和k补齐常数方向，incidence满rank。仅有generic logits或有限样本mask满rank不足以推出以上域覆盖与严格函数等式。

## 为什么它不能替当前实验下结论

语言隐藏态有限/离散或位于受限支持；只有近似fit；actual gate与计算有BF16量化；没有每个open region内的精确等式，也没有解析延拓的稳定恢复界。即便理想函数可识别，有限数据/优化仍可能产生共享近似偏差与模型间变异；反过来，共享误差也不能当非唯一分解证据。E138正是把这两者分开，E139将检验额外分配信息的有限cohort作用，不证明全域唯一性或数学不可识别性。

## 已有理论ownership与距离

- [Nguyen et al., 2402.02952v2](https://arxiv.org/html/2402.02952v2)：确定性dense softmax回归中，在紧参数域/strong identifiability等条件下联系总函数估计与expert恢复。标题不能替代假设核对。
- [Nguyen et al., 2309.13850v2](https://arxiv.org/html/2309.13850v2)：top-K条件Gaussian混合密度的MLE理论；条件密度可识别性不能直接用于确定性神经块加权和，其激活gate也归一化。

两篇只核对所记录章节，未复核全部证明；详细论文卡在根library的EXPERT_ALIGNMENT_PAPER_CARDS_2026-10-26.md。没有进行理论新颖性穷尽搜索，不称新定理。当前唯一新增GPU问题仍是E139配对free cohort。
