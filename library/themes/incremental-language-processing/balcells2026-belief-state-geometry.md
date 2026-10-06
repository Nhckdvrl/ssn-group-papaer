# Large Language Models Develop Belief State Geometry In-Context

信念状态几何：Balcells等，NeurIPS 2026，arXiv 2609.17376v1，主文§1–9。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 构念测量与因果干预。
2. **背景与压力：** [正文](https://arxiv.org/abs/2609.17376)。6个开放模型、40个选定低熵HMM、每项10条20k-token序列。线性探针、短后缀/输出分布对照及因果干预检验状态几何；部分小模型/参数区间不成立。
3. **改变的前提：** 当前输出不足以确定潜在状态。
4. **idea来源（RECONSTRUCTED）：** 从Xie的生成过程推断、Shai的专门训练toy模型，走到生产模型在上下文中推断过程及状态。关键距离是用发射矩阵的零空间区分信念状态与当前输出：有些状态差异不改变当前预测。局限是选定HMM和线性坐标，不能直接称自然语言已维护全局世界。可借的是为“解释”设计当前输出看不见、后续用途看得见的检验。
5. **与近邻的距离：** Xie等ICL过程推断；Shai等toy模型状态几何；Transformer/HMM filtering工作；自然语言belief工作，不能混成同一对象。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-9, discussion and limitations; extensive appendices not read。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
