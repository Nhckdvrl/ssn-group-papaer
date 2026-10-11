# Reason, Then Re-reason: Cross-view Revisiting Improves Spatial Reasoning

跨视角再验证：Ma等，ICML 2026（PMLR核对），arXiv 2606.11683v1，主文§1–6及局限。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 结构诊断与推理协议。
2. **背景与压力：** [接收与论文](https://proceedings.mlr.press/v306/ma26z.html)。ReRe在VSI-Bench（5000余QA/288视频）和STI静态子集上，用初始8帧产生假说、VGGT重建后生成8帧新视角再检验；9模型/4族。Qwen3VL8B约+5.2pp，但各子任务存在退步；无主文重复seed/CI。positive/negative flips是QA加权，与任务宏平均收益不相等。
3. **改变的前提：** 相机轨迹约束下答案需要能由互补证据再验证。
4. **idea来源（RECONSTRUCTED）：** 固定相机视角下单次答案常用语义先验补不足，几何特征注入又依赖训练；因此把几何变成原接口可消费的反证，比较单新视角、同视角重看、concat/interleaved和不同轨迹。重要边界：重建用1fps/默认100帧而初始模型仅8帧，且VGGT提供额外先验，不能称原信息完全相同或纯纠错机制；joint与sequential也未严格等生成算力。论文的“重看原视角变差”与我们的压力相通，但这个阴性不单独证明partial observability是唯一瓶颈。可借“什么证据能推翻旧假说”的设计，而非把一次重读升级成方法。
5. **与近邻的距离：** Video-R1；See&Trek；VGGT几何注入；concat/interleaved多视角；增量在可消费视觉反证，信息/算力仍混杂。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main sections 1-6, limitations and impact; appendix not read。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
