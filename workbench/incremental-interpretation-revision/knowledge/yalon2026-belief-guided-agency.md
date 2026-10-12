# Indications of Belief-Guided Agency and Meta-Cognitive Monitoring in Large Language Models

内部信念与行动：Yalon等，NeurIPS 2026，arXiv 2602.02467v1，主文§1–8及讨论。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 动态内部读出与干预。
2. **背景与压力：** [正文](https://arxiv.org/abs/2602.02467)。Llama70B/Gemma27B，CounterFact和代词消歧；Patchscopes解码竞争概念，操纵来源/指令，再注入未选概念。干预的66.7–85.4%是logit-margin按预期移动率，不能当答案翻转率。
3. **改变的前提：** 功能性belief需要预测行动而不只解码真值。
4. **idea来源（RECONSTRUCTED）：** 从真值探针转向功能性的行动引导，并追踪生成全过程。与Marks、Ji-An、知识冲突和CoT定位的距离是动态操作化。限制：名称解码可能反映提及，WS概念缠绕，且未定位收敛/更新回路。可借跨输入→状态→行为的因果链，不能借“belief”一词省去角色语义验证。
5. **与近邻的距离：** Marks真值探针；Ji-An等内部belief；Patchscopes；Butlin等意识指标；不把功能证据扩成意识证明。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-8, discussion and limitations。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
