# CoRe: Context-Robust Remasking for Diffusion Language Models

修订目标的选择：CoRe，ICML 2026（PMLR核对），arXiv 2602.04096v1，主文§1–6；附录D。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 缺陷诊断与解码方法。
2. **背景与压力：** [接收与论文](https://proceedings.mlr.press/v306/zhai26b.html)。LLaDA8B、5个推理/代码集，128基础+8辅助forward；随机/低margin修订和等136forward对照。相对ReMDM的旧confidence，先在更新后的上下文中联合mask候选，再选择不稳定token。
3. **改变的前提：** 旧confidence不是新上下文下的稳定性。
4. **idea来源（RECONSTRUCTED）：** 允许重写还不够，需要知道哪些旧决定该重写。单模型、代码收益较大，不能称普遍改善推理；“被选token instability高”的图因选择规则而自然成立，不足以证明错误检出precision。对GP可借针对关系依赖的诊断和等算力控制，但不能把输入token改写等同于内部解释修订。
5. **与近邻的距离：** ReMDM；confidence/margin remasking；随机重mask；LLaDA原解码；是否能修与知道修哪处分开。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-6; Appendix D stochastic controls and selected examples; omitted method/results text reread separately。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
