# CTRL-RAG：可归因概率不自动等于忠实内容（arXiv2026，ANT Med-AQ，未核接收） `[证据级别：主文精读，范围如下]`

- 阅读时间：2026-10-08T06:36:08.611429+08:00
- 原文：[tan2026-ctrl-rag](https://arxiv.org/abs/2603.04406v1)；本地/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07/tan2026-ctrl-rag.pdf，SHA a0ab6ae768baf7ce8a49e607e1f0da892a758dabc7372d5e4e800a27c1b64285。
- 范围：Author v1 main1-6 pp1-8 all, AppA-C pp12-13 all; tables/curves pp7-8 visual. Code and acceptance unverified.

1. **形态/压力：** 失败模式→奖励方法→训练；RAG correctness/citation reward稀疏或可投机，而self-confidence不识别文档依赖。
2. **idea来源（RECONSTRUCTED）：** 从归因/leave-one-out沿文本概率扩为训练信号，不把概率高等同正确；共享已有GRPO而改变reward对象。新轴是有/无支持文档的答案likelihood差，不是重建观察。
3. **与近邻距离：** Self-RAG/RAft调检索或SFT；RAG-RL/PA-RAG以外部correctness/citation；self-certainty/NOVER以内部置信度；本文增加支持文档贡献及correctness gate。一般对比likelihood、token credit、gate已有owner。
4. **方法：** 全文档LP减删除最关键支持doc后的LP；除sqrt(output length)，threshold1，乘accuracy。必须知道support doc，不能叫完全无监督。固定观察长度的我们不能靠length normalization改变candidate rank，这点由算术决定，不需要额外ablation。
5. **规模/基线：** Dense8B/MoE30B-A3B；74109 SFT，约10000 RL按pass@8/LP方差选；Hotpot/MuSiQue训练、7评测；group8、同SFT conventional rewards、公版模型。异构40H800，非低成本单卡实验。
6. **结果/边界：** 主表有改善但不是所有cell；min/avg差小、乘gate并非所有任务更优。Table2 PRGB加gate80.0而乘79.3；“全面超过3点”等强措辞不完整由表支持。PPL文字exp(-sum)缺常见长度归一化，图值解释不直接当严格信息定律。训练删KL是实现观察，不是KL必导致崩溃的理论证明；code未公开核。
7. **可迁移动作：** 让反馈比较可辨别的证据依赖，再看训练结果与长度投机；既有benchmark自然优先。
8. **对我们：** 一般内部reward有误/归因/归一化/gate都不足novel。E101分解固定target的前后相反credit，E103/E105若显示真实proposal选择随预算变坏，才有具体修订机制距离。不能借本文局限自动判死或把其没测GP叫创新。
