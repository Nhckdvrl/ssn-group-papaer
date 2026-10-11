# Beyond Single-shot Writing: Deep Research Agents are Unreliable at Multi-turn Report Revision

多轮报告修订的损伤：Chen等，ACL 2026 main，主文§1–8及局限；附录C.3/E.5。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 纵向任务与失败模式测量。
2. **背景与压力：** [会议原文](https://aclanthology.org/2026.acl-long.609/)。MR DRE复用3个专家清单数据集，5个DRA、3种反馈；多轮/反馈数量实验用75题，两个作者审核100条反馈。分开覆盖、反馈采纳、原覆盖破坏与引用；主表内容反馈break平均约31%，格式约21%，与摘要16–27%不能混报。统计是按题配对单侧t检验，不是所有观察都显著；break大于0的检验因量本身非负，信息量有限。
3. **改变的前提：** 单次报告质量不说明用户修改后仍可靠。
4. **idea来源（RECONSTRUCTED）：** 从单次报告benchmark转到用户修改的真实使用循环，发现高采纳率掩盖对其他内容和过去编辑的破坏。相对ResearchRubrics/RigorousBench/ResearcherBench及迭代起草，增量是有反馈的修订对象和纵向保持测量。模型/scaffold信息与成本不齐、清单/judge质量和报告长度影响读数，原因尚未解释；局部prompt/独立reviser有改善而非“完全无效”。对I04的压力：一般“修订有副作用”也已有明确证据，必须找到结构性失败边界及可迁移机制，不能把名称改为关系就算novelty。
5. **与近邻的距离：** ResearchRubrics；RigorousBench；ResearcherBench；迭代起草/外部反馈修订；增量是反馈范围外及历史编辑的保持。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-8 and limitations; Appendix C.3 feedback validation and E.5 statistics。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
