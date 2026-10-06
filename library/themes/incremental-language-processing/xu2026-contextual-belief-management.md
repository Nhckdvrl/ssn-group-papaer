# When Should Models Change Their Minds? Contextual Belief Management in Large Language Models

证据对齐的状态管理：Xu等，EMNLP 2026 main（作者v2注明），arXiv 2605.30219v2，主文§1–7及局限；附录C部分。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
此前卡的阅读范围较窄；2026-10-07已以此处明确的会议/作者版本补足主文。旧缓存保留。

1. **论文形态：** 符号oracle测量与修复方法。
2. **背景与压力：** [正文](https://arxiv.org/abs/2605.30219)。两类有限候选环境、约千级轨迹、3模型；区分应保持、应更新、应忽略；RL/SFT及跨环境迁移。主表是3次轨迹任一次失败，另有单轨迹CI，不能混报。
3. **改变的前提：** 吸收更多上下文不等于按证据管理状态。
4. **idea来源（RECONSTRUCTED）：** 从一般多轮不稳定转到有符号oracle的规范性更新对象。其“latent-output gap”来自另一次提示排名，不是内部线性探针；RL差向量干预只做Qwen，并用vanilla错/RL对样本建立向量。可借有限解释空间和保持/更新对照；现成合成数据无需再逐项用LLM重审，自然GP也不能被这种数据替代。
5. **与近邻的距离：** Belief-R；多轮上下文不稳定；hypothesis/rule discovery与circuit diagnosis；以保持/更新/隔离和有限集合oracle区分。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-7, limitations; part of Appendix C and training table。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
