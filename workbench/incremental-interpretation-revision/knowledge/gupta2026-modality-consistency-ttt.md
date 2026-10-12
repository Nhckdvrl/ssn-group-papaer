# Test-Time Training for Modality Order Consistency in Vision-Language Models（arXiv2026 v1）

[作者原文](https://arxiv.org/abs/2607.20351v1)，Aditi Gupta（Chicago）/Yossi Gandelsman（Reve）。已读完整HTML主文§1–6，PDF同版本已缓存；附录未精读，主会接收/评审未核对。

1. **形态：** 可重复失败+自监督修复，因果定位支持方法。
2. **压力：** 同样image/question内容交换顺序，原生VLM得分相差6–26pp；语义无关变换暴露计算不一致。
3. **改变前提：** 两个视图不应平等蒸馏，经验更强的分支给弱分支提供定向监督。
4. **idea来源（RECONSTRUCTED）：** prompt sensitivity已有→找到稳定方向→TTT/蒸馏沿方向做更新→patch定位干预入口→更新小范围、每条reset。不需要全新TTT工具，关键是把变换失败变成可用监督。
5. **近邻距离：** TTT/熵最小化/augmentation consistency是工具；Deng/Hejabi已发现image-first优势；Chou对称一致性是直接方法对照；与CMU echo同期同现象，分别探索适配与纯prompt，可借研究动作而非用相似性判死。
6. **方法/实验：** InternVL2 8B、Qwen2.5VL7B/Qwen3VL8B（2族），MMStar1500/RealWorldQA765/AI2D3088。每条用两prompt候选分布，SGD momentum.9、3/4/5步在held-out calibration选定；teacher每一步stop-gradient、跨步随同一权重更新，完成后reset。主表QF+4.1至26.1pp，IF0至1.2；没有test label用于适配。
7. **机制与边界：** patch最后token的完整hidden，支持某处能够修复，而非证明所有失败只源于那一层。全样本patched accuracy与IF对/QF错fixable子集分开（487/250/700），未报告CI不能自己估。所有层window都可恢复>25pp，不能把“最佳中层”夸成只有中层能修。冻结teacher43.9 vs移动teacher61.5，支持共享权重反馈，但不是已完成因果bootstrapping证明。成本含逐条梯度与reset；主要MCQ，跨未询问用途未知。
8. **可迁移动作：** 从稳定方向的不一致找内生监督；优先测最便宜的跨用途迁移，能否使修复超出原目标，比继续细分层窗口更有信息量。
9. **对我们：** 若E65找出稳定的目标视图方向，可研究不同自然读取目标如何帮助共同关系状态，而不是只让某题分布模仿另一题。G2答案No约定与角色自由表达仍不同对象，不能直接互相蒸馏。当前没有验证方法，先看核心迁移矩阵。
