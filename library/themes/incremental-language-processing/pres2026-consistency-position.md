# Position：以跨输入关系作为优化对象（ICML2026，作者组接收页核；所读为March5作者稿） `[证据级别：主文精读，范围如下]`

- 阅读时间：2026-10-08T06:36:08.611429+08:00
- 原文：[pres2026-consistency-position](https://time-for-consistency.github.io/assets/pdfs/Consistency_Pos_Paper.pdf)；本地/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07/pres2026-consistency-position.pdf，SHA 8f66cf6ba005e7193f8172f842d2189d02c8e104c7d2fc6d889255aefddbe2ae。
- 范围：Author March5 PDF main1-5 pp1-9 all and AppA-C pp15-19 all; ICML2026 confirmed author lab page, official final/reviews not checked.

1. **形态/背景：** position整合+开放研究问题，非新方法大实验；逐input/output独立打分无法定义sycophancy、知识变更传播、self-description等跨输入性质。
2. **idea来源（RECONSTRUCTED）：** 对多类失败抽取共同关系约束，借equivariance/graphical structure与posterior regularization，但将对象移到可扩展的行为层；自己承认基本结构优化非新思想。
3. **最近邻：** paraphrase/bias invariance、deductive closure/updatability、CoTfaithfulness与calibration，RLAIF等被统一为instance-instance/meta-instance；position的尺度是新组织视角，不是一条benchmark gain。
4. **方法/证据：** 关系phi、hard/soft/posterior三路径和8case study；self-redteam/AIscience是提议，不当已跑实验。AppC讨论数据生成/推断筛选/训练。公式正负号与“hard必须推断”强表述须谨慎，未复核code。
5. **边界：** 一致性不是truth/透明保证；缺边界data、vacuous fixedpoint、rigidity/tradeoff已有讨论。self-report发现unsafe之类是潜在接口，不当无限可靠监测证明。
6. **可迁移动作：** 不拘泥方法创新：从常见失败重新定义评价关系、明确不同实现可共用的新问题；仍须落到能观察到功能后果的phi。
7. **对我们：** 宽泛语义一致性、局部真实/全局不一致、跨输入解释均不是novel。GP解释credit的prefix-vs-revision冲突必须提供新预测/选择后果，而不是把所有研究归为一个新词。E104结构then-cut非真正语义证据oracle，不能直接作通用机制反证；未建立跨域证据，禁止机械迁移边界。
