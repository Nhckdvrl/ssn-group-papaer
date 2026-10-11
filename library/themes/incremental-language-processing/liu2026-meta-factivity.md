# From Factuality to Meta-Factivity（ACL2026 short，position）

`[证据级别：正式主文精读]` [原文](https://aclanthology.org/2026.acl-short.7/)。HUST外语学院；正式PDF8页，SHAffbc4dd629951d95f2ebd07915f8a1262400d436ed452b2bf60fe6e34e60a234；main1–5/limitations/ethics pp1–5全部、Table3 p3视觉，refs pp6–8未逐篇核。不把接受的position稿当大规模机制实验。

1. **形态/idea来源（RECONSTRUCTED）：** EFP的head/tail不平衡、高分无对应理由、discriminative/generative差距→借factivity、QUD/common-ground更新、meta-cognition建立新的评价对象。贡献是从静态事件标签转向commitment reasoning/regulation的roadmap，不是新训练算法。
2. **近邻距离：** Jiang/de Marneffe、MAVEN-FACT等已测factuality/pragmatics、evidence不一致；MFF组织recognition/reasoning/regulation及output/process/grounding对应维度。一般“答对不等于知道/会用”“动态belief更重要”已有owner，不能作为I06–08独占贡献。
3. **证据尺度：** 两张旧benchmark再分析表、一个DeepSeekV3.2 probe四文本×10runs；Q1 9Uncertain/1Factual，Q3 10Factual，Q2 10Uncertain，Q4 6/4，作者给共同Factual Gold。没有跨多模型的大benchmark、白盒干预或实际regulation训练，作者limitations明确框架尚待实现。
4. **判断边界：** 更强模型head/tail差更大不能单由此推过拟合；CoT文字不是唯一internal causal理由，探针/SAE“ultimate knows”与RLHF物理优先compliance是论点/引用解释，不是四例实验所证明。医生did-not-deny例中的truth commitment受语用约定影响，不能把本文一句Factual当普遍形式蕴含；本文自身也强调factivity/context梯度。
5. **可迁移动作：** 留住operator/content依赖及source commitment，区分源中被某人认知/报告的p与直接世界p；现成FactBank/CommitmentBank/UDS与MegaVeridicality可作为后续数据入口，不因此bulk审计或现在切换领域。
6. **对我们：** E107只测GP修订后的关键依赖承诺，不是全面meta-factivity。I07潜在增量是完整观察重建如何给具体关系修订相反credit；E107明确/隐式两种支持及条件排名能检验这个对象，普通evaluation taxonomy或truth monitoring不是我们的新方法。position尺度说明视角/研究对象也可有贡献，但需要自身的重要问题和证据，不能复述泛框架。
