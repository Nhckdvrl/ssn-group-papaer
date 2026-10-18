# Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased

规范记录：`yu_2023_hsp`；ICLR 2023。实际版本：arXiv:2302.01605v1, 2023-02-03; manuscript says published at ICLR 2023。

**实际阅读范围：** Complete main text sections 1-7, PDF pages 1-9; Appendix D.1-D.3, E.2, F.2-F.4 and Tables 5,6,19,24; pages 20,21,23,26-28,31; Not all proofs or event feature tables read

[原文](https://arxiv.org/pdf/2302.01605) · [发表／主源信息](https://arxiv.org/abs/2302.01605)

**来源与范围。** [原文](https://arxiv.org/abs/2302.01605)，ICLR 2023、arXiv v1（2023-02-03）；主文 §§1–7 完整阅读，附录 D.1–3、E.2、F.2–4、关键 Tables 5/6/19/24 已核；未逐行复核证明及全部奖励特征表。

**问题与机制。** 高分合作不代表尊重玩家玩法。HSP 随机采样手写事件特征的奖励权重，训练有不同隐含偏好的伙伴，按事件计数过滤重复策略；最终池一半这类伙伴、一半 MEP 策略，共 36 个，RNN 学习根据互动历史适应。目标 agent 仍最大化公共游戏奖励；“任何固定策略都能由某奖励表示”的存在性论证不表示恢复了真实人类动机。

**证据与边界。** 五地图含两个多配方新图，五种子、每策略 1 亿步，并认真重训 FCP/MEP/TrajDiv。原始旧 SOTA 在同一人类代理上的分数被强实现大幅超过，HSP 在三张旧图的额外优势有限；明显差距集中于有偏好伙伴。60 人分五组，先自由试探再每人 24 局争取高分。为给玩家贡献空间，每次 AI 动作前插入七个等待步。其番茄偏好测试中能接续玩家已开始的配方，避免混料毁掉订单。但附录明确 Coordination Ring 的人类偏好是 MEP 高于 HSP，不能复述摘要为所有地图一致最好。

**领域位置。** 它将“错误动作”和“合理但非最高分的偏好”分开，也把自由尝试纳入测试；这比单一收益评价更接近 NPC 队友。局限是奖励特征和配方语义由作者设计、伙伴主要固定，尚无语言谈判、长期共同适应或跨地图策略迁移证据。可继承的问题是如何在保证任务进度的同时容纳玩家不同玩法，而非把人类偏离最优一律当噪声。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Maximum Entropy Population-Based Training for Zero-Shot Human-AI Coordination](ZHAO_2023_MEP.md) | MEP 的熵差异不保证覆盖特定事件偏好；HSP 通过人工定义事件效用构造偏置伙伴。 |
| [Cross-environment Cooperation Enables Zero-shot Multi-agent Coordination](CEC_2025.md) | HSP 改变相同地图的伙伴偏好，CEC 改变布局与对象分布以减少环境特定约定。 |
| [CooT: Learning to Coordinate In-Context with Coordination Transformers](WANG_2026_COOT.md) | HSP 主要产出静态协调策略和训练伙伴；CooT 用连续交互上下文学习对伙伴的条件响应。 |
