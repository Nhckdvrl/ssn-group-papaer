# Learn from Your Mistakes: Self-Correcting Masked Diffusion Models

训练误差恢复而非只放开重写：Schiff等，NeurIPS 2026名单核对，arXiv 2602.11590v2，主文§1–7及局限。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 错误分布训练与生成方法。
2. **背景与压力：** [正文](https://arxiv.org/abs/2602.11590)。ProSeCo将模型完整预测当误差噪声，以同权重第二forward预测干净文本；推理交替unmask/correct。LLaDA8B SFT约40B tokens、4数学/代码集，另QM9及OWT（1Msteps/5000生成）；同SFT配方vanilla、ReMDM/PRISM/AR对照。HumanEval48.17→62.20是带采样纠错的最佳配置，不是相同forward数的纯训练收益；仅新loss而无纠错采样为52.44。
3. **改变的前提：** 放开重写不代表学会恢复自身生成错误。
4. **idea来源（RECONSTRUCTED）：** 冻结已生成token/分布漂移→不是只重mask，而是学会修正自身特有错误→保持接口、权重共享并评测速度/质量前沿。与self-conditioning、unrolled部分mask轨迹、ReMDM及Hollow Transformer距离，是训练输入的误差分布和已decoded位置纠错。增加训练forward，NFE也不是硬件wallclock速度；各benchmark选择不同纠错预算、无主文跨seedCI。输入句不能像生成答案一样任意替换；可借“已学得错误恢复”与“具有未来访问”必须分开的认识，不因E54 null否定可训练修订。
5. **与近邻的距离：** self-conditioning；unrolled denoising；ReMDM；PRISM；Hollow Transformer；增量在同权重错误恢复训练。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main 1-7, limitations and impact; appendix not read。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
