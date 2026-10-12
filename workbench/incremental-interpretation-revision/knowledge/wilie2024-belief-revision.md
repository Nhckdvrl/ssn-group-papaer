# Belief Revision: The Adaptability of Large Language Models Reasoning

更新与保持的直接近邻：Wilie等，EMNLP 2024 main，主文§1–9及局限。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
此前卡的阅读范围较窄；2026-10-07已以此处明确的会议/作者版本补足主文。旧缓存保留。

1. **论文形态：** 新评估对象与benchmark。
2. **背景与压力：** [会议原文](https://aclanthology.org/2024.emnlp-main.586/)。Belief-R由ATOMIC种子经GPT-4生成，1912个基础题、1744个加入前提的题；5人多数标注、保留至少4/5一致的项目，AC1从.573到.697。约30模型及direct/CoT/plan-and-solve；BREU均衡更新/保持两类，不等于条件于每项初始答对的修订成功率。
3. **改变的前提：** 静态前提推理不等于新前提下的保持或更新。
4. **idea来源（RECONSTRUCTED）：** 静态推理评测未测新前提如何改变原结论，借Byrne suppression task构造additional/alternative条件，继而发现更新与保持的行为权衡。关键距离是动态评测对象与可重复数据，不是新纠错算法。这里把“if r then q”读成隐含必要条件，是常识/语用任务，严格经典蕴含并不会因增加此前提而撤回q；作者明确承认这一解释。MP人工标注推到MT，部分不合逻辑的人工答案并入unknown。我们不能用它证明自然语法角色更新机制，也不能再把一般更新/保持权衡当全新叙事。数据来自社区基准时先尊重其任务定义，不机械重审整集。
5. **与近邻的距离：** Byrne suppression task；ATOMIC；BoardgameQA；PropInd；静态冲突解决与动态前提任务区分。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main sections 1-9, limitations and ethics; appendix not read。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
