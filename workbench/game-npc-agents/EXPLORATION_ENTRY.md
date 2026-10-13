# 开放探索入口：Trainable, Designer-Controllable Game NPCs

2026-10-13 用户要求重设切口，因为旧“目标坚持/旧计划”仅是 NPC 决策子问题。**当前是较宽但可驻留的训练/方法研究 territory，并非已有新方法/实证 claim。** 不再用 LIGHT/旧 E03 的数据去“证明”那个小问题重要。

## 一、科学对象与实际制作压力
从游戏设计者角度，需一种能部署和持续修改的 NPC：具有被作者指定的行为风格、任务要求、游戏边界，在玩家扰动时做可执行动作；合理的挑战性不等于最大胜率，符合角色行为也不等于自我介绍正确。需求来自 EA 2026（实际 FC25/BF6）、modl.ai/Riot 2025（可部署的模仿学习 bots）、KRAFTON 2026（高层语言决策+反射级控制）以及游戏 NPC 论文。
**优先科学轴：怎样用有限行为反馈训练出可编辑、可泛化、实际有后果的 NPC 政策？** 既可以从预训练表征+微调入手，也可从 PPO/模仿学习/偏好学习/条件化策略入手；先观察 strong baseline 才决定。

## 二、已由最近邻占有的主张
- PCSP (2026 arXiv) 已提出 frozen persona embedding + shared PPO policy、InfoNCE/多样性项、Mini-Inzoi/Melting Pot/UE 验证；不能称“首次自然语言条件的共享 NPC policy”。作者独立行为 probe 与内部检索分数并不一致。
- EA MultiGAIL (CoG2023) 已从多种人类行为示范学习可混合人格政策；UBCL (IEEE T-Games2026) 已用连续行为控制向量训练共享政策。**“训练多种风格的 NPC”本身不新。**
- EA (CoG2026 vision) 已明确 designer-in-loop、行为修复、模块化、实时成本难题；仅重述其未来方向不构成贡献。
- NeurIPS2026 *Events as Triggers for Behavioral Diversity in MARL* 已利用事件条件的 hypernetwork/LoRA 切换共享策略角色；虽然非直接游戏 NPC，照搬此方法到生命模拟也需谨慎。
- Roleplay 的 CRPO / Persona-Pruner 即便 ICML2026，也主要评价对话，**不能当直接游戏行动的能力证据**。
- 游戏玩家通关 agent 与生产 NPC 优化目标不同。基于 agent 通关率提点，不经真实 NPC 转译不能写成 NPC 论文。

## 三、可以带进基线的观察轴（不是必须出现的失败）
- **角色可控性：** 同一环境/奖励，设计者改变可解释行为要求（例如照顾伙伴、偏保守的行动选择），输出真实合法动作分布有多大条件性变化？它对独立任务结果造成什么影响？不把人格刻板印象直接当唯一真值。
- **训练信号：** 真实示范、少量偏好比较、人工规则奖励、简单条件向量在匹配人类设计成本/运行成本下，分别学到什么、不能学到什么？先运行现成已发表策略，不能先造教师自己给自己标签。
- **策略可编辑性：** 对已训练 NPC 的一个具体行为进行少量新反馈修正后，未针对该行为的其它场景是否保持？这是自然产品问题，但需要与现有 fine-tuning/behavior editing 强近邻比较。
- **规模与复用：** 多个 NPC 共享政策与独立政策/规则 BT，在相同总训练样本/总人工设计量下的样式覆盖、任务可靠性、延迟及资源占用。不能不计 actor/embedding/teacher 的实际成本。
- **社会互动：** 风格只看无伙伴的行动是否“成立”？同一角色换玩家/同伴或互动局势时，哪些训练信号仍有效？不要用模型自称“我是善良的”判分。

## 四、目前最务实的驻留底座
1. **PCSP research/Mini-Inzoi v3：** 正式源码含 PettingZoo、行为动作语义、共享 PPO、多个 baseline、训练/测试 persona split 和独立行为评价，是第一个应审计能否在单节点复现的真实 **NPC 训练** 环境；但原论文是 arXiv，未核实顶会接收，且用户生产场景远比其简化模拟复杂。
2. **ccb/agent-sandbox：** UPenn/Chris Callison-Burch 2026 开源，确实为游戏 NPC 提供合法世界 action precondition/effect、回合、NPC ReAct/Reflect 与本地兼容 API（LLM_BASE_URL）。可用于 LLM 高层行动 cross-check；它是持续开发的研究底座而非已验证顶会 baseline，README 不同段落存在阶段描述差异，须读当前代码。
3. **LIGHT/Dragon：** 有真实角色动机和任务的数据/机制，但环境归档与现代执行对齐需要核查；作为 RPG 角色的第二真实对象，不再独占主方向。
4. **ReactiveGWM v2：** 有 2026-09-29 公布的完整代码/视频数据/模型，方向是视觉世界模型中的 NPC 控制，非多数 NPC 游戏引擎策略的同构基线；训练预设 8 卡、20k updates+视频 IO，目前不适合作为弱互联/弱IO主线。
5. **EA 游戏资产、PUBG 内部训练链、modl.ai/Riot 人类轨迹不可直接认为开放**；它们用来建立问题与强方法评估标准，不能伪造可复现 benchmark。

## 五、E05 真正的下一步
先复现开放训练底座上的强共同政策 vs 规则/独立政策/同成本基本方法，报告 task reward + 明确定义的行为度量 + independent action-conditioned measurement + 不同角色/局势的交换评估。先检验指标是否真实辨别“玩家可观察到的行为”，不只内部轨迹检索。
**不同方向对应不同需求：** 若原样本本身少、行为机会不充分，先换合格场景/度量而不是凭人造奖励制造训练问题；若强 baseline 可靠且有新行为测试变化，再决定该研究新训练方法、机制认识或行为可编辑性。观测可以改变问题，不机械执行一个预定研究剧本。

## 六、执行约束
外部 LLM API 默认 0 调用；模型 teacher/任务模拟/裁判/额外 replan 都计完整成本。本地 Qwen 等 LLM 可以批量产生**候选**行动数据，但不能直接把自己的 judge 分数当真值；环境事件/行为证据优先。先单节点小量级真实 rollout 统计 CPU steps/s、token、GPUh，再并行不同 seed/model/condition。实习权重/数据不跨机构拷贝。
**本轮没有任何行为研究实测结果，不声称形成了论文级 novelty。**
