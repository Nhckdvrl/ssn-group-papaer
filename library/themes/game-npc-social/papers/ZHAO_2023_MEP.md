# Maximum Entropy Population-Based Training for Zero-Shot Human-AI Coordination

规范记录：`zhao_2023_mep`；AAAI 2023, 37(5):6145-6153。实际版本：official AAAI PDF main text; arXiv:2112.11701v3 (2022-06-27) for appendices。

**实际阅读范围：** Complete official main text PDF pages 1-7; arXiv Appendix C end and D, pages 16-17

[原文](https://ojs.aaai.org/index.php/AAAI/article/view/25758/25530) · [发表／主源信息](https://ojs.aaai.org/index.php/AAAI/article/view/25758)

**来源与范围。** [AAAI 2023 正式页](https://ojs.aaai.org/index.php/AAAI/article/view/25758)，37(5):6145–6153；正式 PDF 全部主文（1–7 页）及 arXiv v3（2022-06-27）附录 C 末、D 训练设置（16–17 页）。正式版散列另列于来源表。

**问题与机制。** 随机种子不一定带来足够不同的伙伴。MEP 从个体动作熵与两两策略 KL 出发，构造平均策略熵这个有界、线性复杂度代理目标，训练行为池；第二阶段提高难配合伙伴的抽样概率，避免只在好队友身上刷分。这里的多样性是状态条件下的动作分布，不等于人物动机、长期风格或人类偏好覆盖。

**证据与边界。** 矩阵游戏及五张 Overcooked 图上，与 SP、PBT、TrajeDi、FCP、直接优化总体差异比较；五种子。MEP 基础池五个策略再取三个检查点，FCP 比较用十个基础策略，不能把“五个/十个”写成最终伙伴总数。移除熵奖励或优先采样降低当时实现的成绩。真人对照中 SP/PBT 数据沿用 Carroll2019 的旧研究，而 MEP/FCP/TrajeDi 新采集；已读正文和实验附录未交代新招募人数，也没有伙伴喜爱程度。理论保证依赖测试人的策略足够接近训练池，并不是自动证明真实人类已被覆盖。

**领域位置。** 它把伙伴多样性从“多训一些种子”转成显式优化，但最可维护的认识是机制与条件，不是永久排行榜。HSP 后续对同类基线增加记忆、改进批次与训练预算后大幅提高成绩，还发现优先采样未必有益。需要把行为多样性、训练充分性、真实偏好和评估分布各自记录，防止把实现差距误认成新社会能力。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Collaborating with Humans without Human Data](STROUSE_2021_FCP.md) | MEP 在 FCP 式两阶段伙伴训练之外加入显式种群熵和难伙伴采样；不能把基础策略数当最终检查点池大小。 |
| [Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased](YU_2023_HSP.md) | HSP 的事件偏好偏向语义上的策略差异，并指出更强训练实现会大幅改变 MEP 等早期基线水平。 |
| [ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination](WANG_2024_ZSC_EVAL.md) | MEP 优化伙伴本身动作分布多样性；ZSC-Eval 主张还应看它们是否要求真正不同的互补响应。 |
