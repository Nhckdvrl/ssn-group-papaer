# Sample Complexity and Representation Ability of Test-Time Scaling Paradigms

纠错的表达能力：Huang等，ICLR 2026会议稿，主文§1–7；附录D局限。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 理论与合成/真实任务检验。
2. **背景与压力：** [正文](https://proceedings.iclr.cc/paper_files/paper/2026/hash/592729d610953abb6d16065773316d00-Abstract-Conference.html)。理论分别分析重复采样和带verifier的在线专家选择；3-SAT/字符串实验10k训练、512测试，另有AIME实验。
3. **改变的前提：** 单任务表达能力不足以解释多任务测试时学习。
4. **idea来源（RECONSTRUCTED）：** 从单任务Transformer表达能力发展到多任务组合与推理时学习。best-of-n优势要求正确答案概率最大且verifier能正确排序；自纠错构造是更宽的attention-only网络和广义位置编码，不是现有LLM自然学会该算法的证明。可借反馈是否真正改变后续尝试分布的问题，不能用可表达性代替已学得机制，也不能用无反馈重读的阴性否定此理论。
5. **与近邻的距离：** self-consistency；best-of-n；online bandit专家选择；已有Transformer单任务表达理论；实现构造不等于自然学得。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-7; Appendix D limitations; proofs not rederived。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
