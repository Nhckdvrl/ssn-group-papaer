# From Triggers to Emotions: A CPM-Grounded Appraisal Multi-Agent for Dynamic Emotional Evolution in Persona-Based Dialogue（2026 预印本）`[证据级别：全文]`

规范记录：`cpm_multiagent_2026`。作者 Jingyao Cai 等；[arXiv:2607.07824v1](https://arxiv.org/abs/2607.07824v1)，2026-07-08。**实读：23页完整正文、局限、伦理、附录A–H及全部提示/结果表；未运行代码。** 未核得正式会议接收，不把ACL版式当发表身份。[PDF](https://arxiv.org/pdf/2607.07824v1)

## 1. 论文形态与背景

角色自身情绪演变的多代理系统。问题是新事件如何经角色的目标、处境、应对资源和规范被解释，再改变角色的情绪；这不同于让助手安慰用户，也不同于固定“愤怒”标签控制文风。

## 2. 改变的前提与 idea 来源

**DOCUMENTED（§1–3）**：借 Component Process Model（CPM）把情绪视为事件评价的结果，拆出触发分析、relevance、implication、coping potential、normative significance、交叉复核、整合和critic。旧状态与本轮增量结合；附录整合器实际上为每个情绪选择 −1/0/+1，再截断到1–5。它以解释和数值状态作为响应生成前的中间表示；正文实验主要评价该中间表示，不能据架构图声称已经验证了整场游戏表演。

## 3. 方法、数据与强基线

24个合成persona dialogue trials，分医疗训练、学校沟通、客服三个领域；不是24款游戏。主干及自动评判均为GPT-5.4，另测mini、nano和Qwen3.6-35B-A3B。基线包括zero/few-shot、CoT、self-consistency、Self-Refine、适配后的EQ-Negotiator；作者声明尽可能配平角色、场景、历史、当前发言和前情绪状态。Table 4/10另有单体CPM提示，因而不能将比较描述成只打无状态弱提示。

主表Overall（1–5评判分）为zero-shot **4.283**、EQ-Negotiator **4.311**、完整法 **4.322**；单体CPM **4.295**。完整法相对zero-shot和单体CPM分别只有 **0.039、0.027分**，未给置信区间或显著性检验。nano对应4.083→4.211→4.277，显示收益依赖主干和所补结构，不能从一个平均分推出模型普遍不会情绪演变。

## 4. 人评究竟验证了什么

103名无偿志愿标注者，未采人口信息，盲看状态与理由的配对输出。对zero-shot，情绪更新为48赢/23输/32平，评价理由为84/12/7；对EQ-Negotiator为41/26/36和67/24/12。**较强结果是人们更认可结构化理由；不是103名玩家长期与角色相处。** 每个基线比较总票103，不能相加为721个独立玩家。

附录D声称给出方法、基线和评判提示，实际展示CPM模块与评判器，单体/普通基线完整指令未列；24 trials如何展开成主表所有评分单位未充分交代。评判提示输出schema不含主表ARQ，需进一步澄清其取得方式。方法中的顺序依赖与并行延迟实现也需要代码核查。Table 5文本并行为GPT-5.4 **11,004 ms**、mini **6,487 ms**；不是完整实时游戏性能保证。

## 5. 与最近邻的距离

| 近邻 | 区别及本篇仍需证明的增量 |
|---|---|
| [EMA](EMA_2009.md) | EMA已有事件评价、重新评价与应对改变认知/行动；本篇新增LLM分工实现，不是首次动态情绪。 |
| [FAtiMA Modular](FATIMA_MODULAR_2014.md) | 已有模块化评价与情绪推导；本篇使用自然语言情境和多次模型审议，尚无同条件作者/玩家比较。 |
| [Chain-of-Emotion](CHAIN_EMOTION_2024.md) | 更简单的自然语言情绪历史已进入真人角色扮演；本篇主要评价更细的内部状态更新。 |
| [Dynamic Persona Coherence](../../../../workbench/game-npc-agents/knowledge/papers/DYNAMIC_PERSONA_COHERENCE_2026.md) | DPC身份/状态分评并修复；本篇基线更明确保留历史与前状态，但真人仍只评输出。 |

## 6. 证据强度、可迁移动作与对我们

可以借鉴分离**状态合理性、理由可读性、最终角色体验**，以及同模型单体CPM比较。不能把理论命名、漂亮状态轨迹或理由偏好当作真实心理机制。对新矿区的实质压力是：在相同历史、角色知识和预算下，哪些状态表示确实使角色在新处境中表现出可解释的延续、恢复或关系改变，并为玩家提供有意义的角色体验？单纯再加appraisal agents并追求类似分数，距离已有工作太近。
