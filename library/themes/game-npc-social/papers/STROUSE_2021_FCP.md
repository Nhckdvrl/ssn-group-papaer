# Collaborating with Humans without Human Data

规范记录：`strouse_2021_fcp`；NeurIPS 2021。实际版本：official proceedings main-paper PDF。

**实际阅读范围：** Complete main text sections 1-6, discussion, impact and conclusion, PDF pages 1-10; Separate appendices referenced by paper not present in retrieved official main PDF; not read

[原文](https://papers.nips.cc/paper/2021/file/797134c3e42371bb4979a462eb2f042a-Paper.pdf) · [发表／主源信息](https://papers.nips.cc/paper/2021/hash/797134c3e42371bb4979a462eb2f042a-Abstract.html)

**来源与范围。** [NeurIPS 2021 正式论文](https://papers.nips.cc/paper/2021/hash/797134c3e42371bb4979a462eb2f042a-Abstract.html)，完整阅读主文 §§1–6、结语及影响讨论（PDF 1–10 页）；论文另引的附录没有包含在本次正式主文 PDF 中，未冒记为已读。

**问题与机制。** FCP 先训练 32 个不同随机种子的自博弈伙伴，保存初始、达到最终表现一半、训练结束三个检查点，再冻结这 96 个策略训练一个最佳回应。冻结伙伴很重要：目标 agent 必须学习迁就别人，不能让别人共同适应自己。五张 Overcooked 风格地图，RGB 观察、六动作、V-MPO 加 ResNet/LSTM；它不同于前作的 PPO 和状态接口，跨论文原始分数不能直接相减。

**证据与边界。** 与 SP、共同训练的 PP、人类行为克隆伙伴 BCP 比较；模拟五种子，真人研究 114 人、每人 20 个一分钟回合，收团队成绩和成对伙伴偏好。FCP 在总体得分和偏好均胜各对照。移除历史检查点后，人类代理合作交付量从 10.6 降为 4.7；增加网络结构多样性不再额外改善已有完整 FCP。这表明弱伙伴经验本身有用。另一个重要结果是 BCP 与 PP 得分无显著差别，玩家仍更偏好 BCP。

**领域位置。** 本文实证修正“必须采集人类数据才能合作”的强说法，支持以行为与能力覆盖提高队友可配合性；但它并未推翻人类建模的价值。作者限定固定共同奖励和单一任务，明确承认如果玩家有不同目的，FCP 可能失败。常见 NPC 需求如给玩家留出贡献机会、适应新手、不坚持唯一分工，可在这条非语言路线中研究；不能将其解释为学出了完整人格或真实心理理论。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [On the Utility of Learning about Humans for Human-AI Coordination](CARROLL_2019_HUMAN_AWARE.md) | FCP 的训练不需要人类轨迹，但其效果仍由真人验证；Carroll 直接以人类模型训练最佳响应。 |
| [Maximum Entropy Population-Based Training for Zero-Shot Human-AI Coordination](ZHAO_2023_MEP.md) | MEP 明确奖励平均策略熵来扩大池内行为差异，FCP 主要依赖种子及学习阶段产生差异。 |
| [Cross-environment Cooperation Enables Zero-shot Multi-agent Coordination](CEC_2025.md) | CEC 优先扩大训练环境分布；FCP 优先在固定环境内扩大冻结伙伴分布。 |
