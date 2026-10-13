# 2026-10-13 更新：从窄“目标 vs 旧计划”回到原生游戏 NPC 训练

用户否决旧切口的主优先级；它未被实验反驳，作为潜在具体失败仍可参考 [GOAL_CONTROL_REVIEW](GOAL_CONTROL_REVIEW.md)。本页按**游戏内 NPC**划定最近邻 ownership。反常必须相对这些强工作而不是相对我们对领域的误解。

| 已有方法/源（身份） | 它已证明/直接研究 | 不属于我们新颖性的说法 |
|---|---|---|
| EA *Augmenting Game AI with DRL*（2026游戏研究） | FC25/BF6 游戏引擎中的行为学习、7项开发要求、快速训练与局部修复 | “第一次关注可信NPC/设计师反馈/游戏端实时约束” |
| EA *MultiGAIL*（CoG2023） | 多专家行为示范→一个条件化策略混合角色/游戏玩法 | “首个一套策略生成多种 NPC 风格” |
| *Direct Behavior Specification*（ICML2022） | 行为约束监督策略而非手工调 reward | “角色不应只最大化胜率”“添加设计师约束” |
| modl.ai/Riot *Human-Like Bots*（IEEE ToG2025） | 真实行为示范、低成本观测与玩家评价 | “首次人类模仿战术NPC/廉价传感” |
| PCSP（arXiv2026,游戏NPC） | 冻结文本 persona embedding+共享 PPO+内部对齐/UE动作验证 | “首次自然语言条件共享策略/LoRA/InfoNCE用于NPC” |
| UBCL（IEEE ToG2026） | 连续可解释风格向量训练共享游戏 bot 策略 | “首次连续风格可控/条件策略不需每风格重训练” |
| NeurIPS2026 Events as Triggers（非游戏发布NPC） | 事件触发共享策略角色改变, hypernetwork/LoRA | “首次事件条件行为切换” |
| KRAFTON PUBG Ally（2026生产实现） | 小模型高层角色交互、BT实时控制、蒸馏域知识/用户反馈 | “第一次LLM+行为树/第一次零云API游戏伙伴” |
| ReactiveGWM / WorldMind（2026世界模型预印本） | 视频世界模型中多角色控制/反应 | “首次世界模型里的可控NPC角色” |

**可能的科学增量：** 不同设计师行为反馈对可执行 NPC 政策形成怎样的真实因果约束；学习到的角色行为在真实玩家变化/新增机制/局部编辑中可否保持和修复；低成本训练信号能否替代昂贵的每角色 reward engineering。都需要先跑实际强基线、取得新现象或成功边界，再谈 novel method/benchmark/analysis。

注意证据分层：EA/CoG2026 vision 是真实行业问题权威但不等于已公开可复现实验；PCSP 是开源预印本不是ICML/NeurIPS认可；ICML角色对话论文不自动拥有游戏动作 claim；“agent 玩游戏”也不是“NPC在游戏中陪玩家”的同一个社会/设计目标。
