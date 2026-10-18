# ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination

规范记录：`wang_2024_zsc_eval`；NeurIPS 2024, Datasets and Benchmarks Track; official proceedings PDF。实际版本：Official NeurIPS 2024 proceedings PDF, 34 pages。

**实际阅读范围：** Complete main text §§1–6, PDF pp.1–10 (conclusion continues on p.10); Algorithm 1, Tables 1–3, Figures 1–6; Appendix C pp.19–22: evaluation count, modified baseline implementations, human study N=145; Appendix D pp.25–26 and human outcome figures p.34; dense unlabelled visual plots pp.27–33 not all independently rendered/read

[原文](https://proceedings.neurips.cc/paper_files/paper/2024/file/54a7139c548c88e288aa0fcd2bcbeceb-Paper-Datasets_and_Benchmarks_Track.pdf) · [发表／主源信息](https://proceedings.neurips.cc/paper_files/paper/2024/hash/54a7139c548c88e288aa0fcd2bcbeceb-Abstract-Datasets_and_Benchmarks_Track.html)

**稳定 ID：** `wang_2024_zsc_eval`。NeurIPS 2024 Datasets and Benchmarks正式34页PDF。**实际阅读：** 完整主文§§1–6（1–10，结论延至10页），附录C（19–22）、D文字/主要表（25–26）与人类排名图34；27–33密集图未逐图独立核值。

ZSC-Eval针对“排行榜被训练搭档分布和伙伴能力左右”设计评价工具。事件偏好奖励生成伙伴和近似最佳响应，原任务奖励保留以减少故意破坏；用最佳响应行为的多样性 **BR-Div** 而非伙伴自身动作差异选评估池，再加入中期检查点。直觉是两个表面不同的伙伴可能需要同一种应对，评估应要求真正不同的互补策略。结果除原始回报外报告相对于该伙伴近似最佳响应的比例 **BR-Prox**，使用四分位均值、95%置信区间和分布；这补足平均分被容易/高手伙伴支配的问题，但近似BR不是精确最优上界。

九个Overcooked布局（含资源共享/多配方新变体）、7算法、3池大小（co-play12/24/36、COLE25/50/75），5随机种子，每种子20或30伙伴各50轮；GRF三人攻防用6伙伴的168种组合、3种子。某些经典分隔布局连SP都能做得好，对合作泛化区分弱；共享资源和多配方使不同策略/池大小差距明显。高手伙伴配对原始分高不代表适应充分，相对其最佳响应的差距反更大。增加人数只有增加有效行为多样性时才有用。必须留意实现改变：E3T去掉伙伴建模，COLE用回报排序替代Shapley，TrajeDi采样估散度，不能说原论文全部原版被公平击败。

人类N=152招募、145有效（70有游戏经验），每人7算法×2地图14轮，400步/轮，随机算法/地图顺序。基准排名与人类在Coord Ring的Spearman 0.90，Counter 1.00；前者BC代理同样0.90，后者代理0.60。只在两地图、主文5算法排名计算的有限一致性，不能当合成人类已被普遍替代。偏好事件由领域专家手工定义，采样/筛选排除完全不合作者，仍无法覆盖真实人的沟通、共适应、目标变化。

这是知识库的评价方法主轴：必须显式记录部署伙伴分布、有效互补响应类型、伙伴自身可达能力和ego跨伙伴分布，而非堆回合数；BR-div指标的高低只有同特征/同池大小下才可比。其价值是让实验揭示不同困难，不能把“算法更易区分”本身当真实玩家价值证明。

**主源：** https://proceedings.neurips.cc/paper_files/paper/2024/hash/54a7139c548c88e288aa0fcd2bcbeceb-Abstract-Datasets_and_Benchmarks_Track.html ； https://github.com/sjtu-marl/ZSC-Eval

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased](YU_2023_HSP.md) | ZSC-Eval 借事件偏好构造候选伙伴，但以最佳响应多样性筛测试池；HSP 将偏好伙伴主要用于训练。 |
| [CooT: Learning to Coordinate In-Context with Coordination Transformers](WANG_2026_COOT.md) | CooT 的在线适应还需前后回合与伙伴切换证据；ZSC-Eval 的 BR-Prox 衡量相对可达合作能力，二者互补。 |
| [Scalable Evaluation of Multi-Agent Reinforcement Learning with Melting Pot](LEIBO_2021_MELTINGPOT.md) | ZSC-Eval 聚焦共享任务合作和互补响应；Melting Pot 还包括竞争、社会困境和对背景群体的外部影响。 |
