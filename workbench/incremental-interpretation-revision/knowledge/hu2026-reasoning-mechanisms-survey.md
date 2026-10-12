# Towards a Mechanistic Understanding of Large Reasoning Models: A Survey of Training, Inference, and Failures

推理机制：Hu等，ACL 2026，主文§1–5及局限。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 机制综述。
2. **背景与压力：** [原文](https://aclanthology.org/2026.acl-long.889/)。将训练、推理行为和失败三个对象连接，整理SFT/RL、反思/回溯、CoT忠实性及过度思考。多处结论存在相反实证，不宜把综述中的总括句当作定律。
3. **改变的前提：** 训练配方、执行行为与失败须联系起来理解。
4. **idea来源（RECONSTRUCTED）：** 强推理配方出现后，问题从“能否推理”转成“哪些计算产生收益、哪些产生失败”。相对一般RL/LRM综述，重心转向内部机制。给我们的启发是把成功和失败的计算路径放在同一实验里，并问机制能否预测、改善新情形；不能只增加可读特征和漂亮热图。
5. **与近邻的距离：** 一般LRM/RL综述、CoT忠实性、反思/回溯研究；具体claim ownership逐篇见正文，未完成统一定位判决。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main sections 1-5, limitations; truncated page 5 reread separately。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
