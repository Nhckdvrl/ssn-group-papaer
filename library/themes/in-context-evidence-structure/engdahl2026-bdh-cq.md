# BDH-CQ: In-Context Learning with Recurrent Latent Reasoning（2026-08预印本，接受状态未核对）

**证据级别：正文§1–4、6–9，附录未完整读。** [作者原文v1](https://arxiv.org/html/2608.09888v1)。不依据聚合站摘要推机制。

1. **形态：** 新模型/系统＋有界行为解释，非公开权重的LLM机制论文。150M系统将demo更新记忆与query latent迭代分开；精确实现/维数仍proprietary，不能用这份材料独立复现其内部算法。
2. **最强参照与压力：** scratchpad/latent reasoning、HRM/TRM、ARC task训练；区分一条query偶然正确与同规则对多个新input一致执行。能力不压缩为参数数目或一条difficulty曲线。
3. **改变的前提：** “记住新映射”不自动保证与其它operation组合；但组合失败也可能来自原子operation没有可靠学会。
4. **idea来源（RECONSTRUCTED）：** ConceptARC分组暴露不同失败 → freeze后生成oracle任务 → 固定测试输入，仅加匹配复杂度demo区分支持不足与执行困难 → 原子/组合和layout交叉。作者整理的论证不是完整发现日志。
5. **距离：** Coconut/looped latent systems提供新架构参照，ConceptARC提供概念分组，ICL任务记忆提供学习参照；本文有模型/成本贡献。ICES不能仅借它的“组合”名字，就把metadata条件分类改称新缺陷。
6. **实验：** 2–8新颜色绑定96/96第一候选正确；reflection与rotation原子72/72，relocation组合分别47/72、72/72；color swap原子26/72、组合0/72。后者两个shuffled layout原子各1/24，作者明确不能将其组合失败完全归composition。相同长ordering输入增加目标复杂度支持0/24→13/24，nested19/24→24/24；不是凡low accuracy都capacity不足。
7. **短板：** “rank one”是返回候选排名第一，**不是rank-1内部记忆模块**。pass@2有些records只有一个candidate，不是各query两个独立样本；identifier与batch混合一起换，不能分别归因。私有系统、模型选择/训练暴露与机制仅概念层面，不能将图式S/H当已验证电路。
8. **迁移动作：** 配对byte-identical测试，改变示例支持；在同layout下先验证原子操作，再解释组合；报告完整task与pair精确率、错误结构和多候选预算，而不是制造一个抽象能力分数。
9. **对ICES：** E66 single失败所以不能说独有composition；E72正控截断不能说binding；E74任意函数空间未执行所以先E75gate。E76用熟悉±1但context指定Source参数，检验能否获得raw阳性，之后才问rule关系与word carriers。该文是方法/反例参照，不证明我们的机制或novelty。
