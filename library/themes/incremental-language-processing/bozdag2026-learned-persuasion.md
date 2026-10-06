# Learning to Persuade Exposes How Easily LLMs Abandon Correct Beliefs

正确答案被说服：Bozdag等，NeurIPS 2026，arXiv 2608.11624v1，主文§1–7。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 失败模式与优化压力测试。
2. **背景与压力：** [正文](https://arxiv.org/abs/2608.11624)。TruthfulQA训练2886个目标实例，5个评测集、多个攻击/目标模型、5seeds；评价限于目标最初答对的题。训练目标还含格式和长度奖励，不能理解为只有一个二元奖励。
3. **改变的前提：** 固定弱攻击者低估容易被改变的范围。
4. **idea来源（RECONSTRUCTED）：** 静态提示只测受限攻击者，转用优化寻找更强压力，再看跨模型/任务迁移。接近93.7%的单集PSR不代表所有目标；GPT-5-mini跨集均值约3%。作者不区分深层信念改变与表面服从。对我们可借的是同时检验合理改正与错误影响，不能仅以更容易改变答案认证更强修订。
5. **与近邻的距离：** 静态说服提示；多模型辩论；RL说服者；TruthfulQA/强目标跨集比较；深层belief未直接测。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-7 including limitations。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
