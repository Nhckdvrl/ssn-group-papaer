# Erased, Rerouted, or Rescaled?（2026-10-04最新作者预印本v1）

`[证据级别：主文精读＋方法附录]` [原文](https://arxiv.org/abs/2610.05292v1)。Tokyo/HKUST/RWTH/HIT Shenzhen；22页，SHA4035b9c3be2bdeb308222a030633945333842cda8bb50c6ef628f59224f29ebf。接收/代码未核；不凭姓名误认作者组。

1. **形态/问题：** post-training是否压缩belief的问题被拆成可恢复R、因果使用U、方差占用A；用精确HMM reward-null kernel使三者可辨识，再看训练与开源LM。视角/对象的贡献大于新RL算法。
2. **idea来源（RECONSTRUCTED）：** rank下降/固定probe失败常被解释成信息丢失，但坐标变换和readout改变能产生同样诊断。从known Bayesian belief state中构造任务粗化，使“reward忽略什么”精确已知，检验表示、使用、尺度三种竞争解释；两条原预测被结果推翻并保留。
3. **近邻距离：** belief geometry/representation change已有；KL tilt保留等reward output的reference odds也是已有结论。本文把它转为belief-state保护条件和可测因果quotient，新增anchor/state-filter/optimization分工；一般“保留但不用”和“谱不等于信息”不属于我们独有。
4. **理论：** kernel为任务读出M的零空间与simplex tangent交集，并分next-token visible/invisible。anchor保护reference已区分的tied outputs，filter保护未来reward-relevant更新所需的信息；剩余方向由优化决定。不是所有被忽略信息都会删去，也不是无KL必压缩/坍塌的定理。
5. **方法/规模：** 4层128宽transformer与2层GRU；pretrain4万步近Bayes loss，post-train5000步/3种子，50k强weight-decay stress主要1seed。twins16384、同task class不同nuisance；whitened fivefold sequence-heldout linear probes；refit与frozen probes分开。跨全部位置/深度patch避免未patch副本重建，不能把单层patch失败简单当无因果作用。
6. **结果：** anchored保持可恢复但方差可下降，unanchored toy容易reroute/collapse，next-token-visible仍decodable；持续强WD主要删无保护invisible部分。当前LM受控GRPO反而amplify within-class logodds约10–20倍，anchor可回reference；toy和LM方向相反不是藏起来的失败。
7. **LM范围：** 三对同Qwen家族base/post-trained checkpoint；未见HMM streams而非自然知识。受控1.7/4B、2048context、6 single-token letters、LoRA32/lr1e-6/4prompts、1000步为主，一条小β续至10000；128 twin pairs/43582 decisions。另一家族base未收敛被预先排除；不能包装为所有LM/自然task的普适训练机制。
8. **阅读范围：** main1–7/limitations pp1–9全部；AppB/C/D开头pp12–13全部、E文本pp19–22全部；AppA只坐标/probe部分pp11–12，D其余表图及全部数学细节未核。图5 p8视觉核；未运行代码。
9. **对I06/I07/I08：** 三者都不能以QA变好/rank变化直接声称内部理解完好或被擦除。本文reward-null与我们的反向credit不是同问题；若前缀credit主动偏旧关系，是被错误奖惩而不只是reward忽略的方向。新叙事须给具体关系更新及选择后果，不能重复generic belief/action gap，也不因最新稿存在判死。
