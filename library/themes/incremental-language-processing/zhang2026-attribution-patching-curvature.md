# When Attribution Patching Lies: Diagnosis and a Second-Order Correction

因果定位估计何时不可靠：Zhang/Wang，NeurIPS 2026名单核对，arXiv 2606.09899v1，主文§1–5。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 估计误差诊断与方法。
2. **背景与压力：** [正文](https://arxiv.org/abs/2606.09899)。5模型族至9B，事实补全/IOI/greater-than；用真实activation patching作单组件干预参照，比较first-order attribution、HVP/MS-HVP、IG/IH/GIM。大步二阶校正仍可过冲，分步界依赖局部三阶光滑；公式可核对，完整附录证明未重新推导。
3. **改变的前提：** 局部非线性不能代表整个下游响应曲率。
4. **idea来源（RECONSTRUCTED）：** 便宜归因分数给错误回路→误差来自下游网络曲率而非局部激活→诊断与有成本的校正。与AtP*/GIM/IG距离是误差对象和网络级二阶项，不是“patching从此可直接证明语义”。独立组件效应之和不等于联合patch；参考干预的因果值也依赖替换选择/指标。文内有25GPUh总计与大模型多GPUh、Gemma激活类型等表述矛盾，不能照抄成本/普遍收益。我们的首轮直接做有限patch，避免用gradient近似的null筛掉位置；以后扩组件时才考虑筛选工具。
5. **与近邻的距离：** AtP*；GIM；Integrated Gradients；Integrated Hessians；以真实单组件干预为参照而非语义oracle。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-5; boundary omitted by mixed byte/character slices reread; proofs not rederived。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
