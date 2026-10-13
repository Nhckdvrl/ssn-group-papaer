# 核心论文拆解与实验设计逆向训练｜2026-10-13

阅读声明：本轮实际查看了 TALES arXiv HTML 主要章节及官方 README，其他论文主要是**正式摘要 + 原作者代码 README/结构**（或既有 library 研究卡）；没有新建假的 P3 全文精读。下面的“RECONSTRUCTED”是研究动作的合理重建，不是作者写作/思考发生顺序。数值来自原论文或官方 README，不是本地重复验证。

## 1. NCP-Bench：叙事承诺能否在玩家介入下存活？
来源：[ICML 2026 正式页面](https://proceedings.mlr.press/v306/ma26ap.html)、[官方仓库](https://github.com/NLP2CT/NCP-Bench)；级别 P1 paper + P2 repo。
- **旧问题**：把互动叙事评成“语言自然、剧情好看”并不能检查已成立的世界事实与剧情约束能否随着玩家不断改变计划而保持。
- **DOCUMENTED idea**：Narrative Commitment Preservation；从 100 个电影概要构造 initial facts、must/must-not 的 commitments、trajectory，逐回合审计 fact/commitment/player-input conflict。官方数据共 1,660 facts、1,222 commitments、1,511 nodes。
- **公开结果**：最优 GPT-5.2 在 20 turns 后无冲突 survival 42%；HiAgent 相比某 GPT-4o-mini baseline，在官方 README 中减少 commitment conflict，同时 player-input conflict 上升。**README 中 HiAgent 与单模型表的裁判模型不完全一致，复比需固定 judge**。
- **RECONSTRUCTED 转折**：把“叙事可信”由纯粹主观印象转化为可枚举、会被每一步玩家输入实际打破的不可违反状态约束。不是发明复杂的 narrator 框架，而是改变**评价单位**。
- **可疑推断**：电影既定剧情路径≠所有合法玩家游戏路径；预设承诺的数量和密度可能决定违约概率，长交互失败也可能是机会次数变多；单个 judge 对角色、玩家行动的偏好会改变命中。应分开 hazard per turn 与累计 survival、合法分支、不同冲突子类。
- **邻接与非重复**：NCP 已占“长程承诺受扰动 + 100 环境验证”这座地；简单加 memory 降冲突或重复 trade-off 不是新 paper。与 NPC 真正的区别是 narrator 负责书写世界，并未必作为有局部信息的世界内 NPC 执行动作。
- **下一阅读债**：正文 appendix 的审计准则、代码中状态更新与合法玩家分支；judge/模板同一性。仅看 README 不能证明一个新的解释。

## 2. CDT：角色“懂”自己应做什么，怎样才可执行？
来源：[ACL 2026](https://aclanthology.org/2026.acl-long.568/)、[代码](https://github.com/KomeijiForce/Codified_Decision_Tree)；P1 paper + P2 repo。
- **旧问题**：角色 profiles 通常是非结构文字，模型能“说起来像”角色，却不必稳定选择合场景的行动。
- **DOCUMENTED 方法**：从故事场景—行动对中归纳经数据校验的条件规则和递归细化树，运行时查 context-appropriate leaf；对应脚本 build_cdt.sh / codified_decision_tree.py。
- **RECONSTRUCTED idea 起源**：从“长 persona 更多文本”退回角色选择实际上是一组可检查的**条件决策**；将过往故事作为监督实例；让可解释性来自设计的执行结构。
- **需要警惕**：从故事中抽的行动可能被传统 story genre、角色称呼、作者剧情安排所决定，不代表陌生世界/玩家新动作下的自治 NPC；构树过程使用外部 GPT-4.1，不等于低成本纯本地基线。要分开规则记忆能力与情境迁移能力。
- **最强近邻距离**：人格→行为条件树已有人做；单纯“角色规则表/RAG + 规划”易被吸收。我们可以研究哪些角色状态/观察条件真正进入行动，而不是提出又一种规则化容器。

## 3. PCSP：内部角色可辨识指标等于外部行为吗？
来源：[论文预印本](https://arxiv.org/abs/2605.23652)、[开源 README](https://github.com/yoosunghong/pcsp)；P1 paper + P2 repo。
- **旧问题**：大量 life-sim NPC 既要共享高效政策、又要表现出不同人物个性，LLM 每步推理太慢。
- **DOCUMENTED 方法**：frozen language persona embedding + shared PPO policy + InfoNCE trajectory/persona alignment + diversity regularization；引擎动作分层。
- **关键公开审计**：repo README 报内部 InfoNCE 消融明显影响 trajectory-to-persona retrieval；同时独立 action-only Big Five probe **full 0.482 vs no-consistency 0.511**，action+state probe **0.556 vs 0.558**。这是**方法内部成功不等于独立行为意义已证明**的现实范例。
- **RECONSTRUCTED**：把“一万个 NPC 需要一万个定制策略”的成本瓶颈转成 shared policy 的条件控制；通过内部可追踪目标约束 persona 信号不被任务 reward 遮盖，再审计它是否真的可见于行为。
- **可疑推断**：独立 probe 未必对所有角色属性灵敏，Big Five 不等于游戏动作；但不能用训练时 InfoNCE 指标单独宣称玩家可见的角色一致性。对这座评估桥梁做更有解释力的实证，必须超出作者现有独立行为审计。
- **代码债**：独立 evaluator 的数据形成/标签和 actor 梯度连接、负样本采样、UE 状态记录，必须逐项实读；优先这些脚本而不是一开始大规模复训 Unreal。

## 4. TALES：简单的先决能力为何值得在复杂游戏之前测？
来源：[NeurIPS2026 对应文章 HTML](https://arxiv.org/html/2504.14128)、[Microsoft repo](https://github.com/microsoft/tale-suite)；P2 paper+repo。
- **旧问题**：各 benchmark 框架相互割裂，强提示/专家知识掩盖 agent 本身的困难。
- **DOCUMENTED 方法**：最小 scaffolding，集成 TextWorld 10、TextWorldExpress 16、ALFWorld 12、ScienceWorld 30、Jericho 54，总计 122 个游戏；34 模型。任务需 spatial/deductive/inductive/grounded reasoning。
- **核心设计**：另做 Simon Says with memory，这不是复杂任务，也不是贡献目标本身，而是**廉价先决能力阳性筛检**；其与游戏表现相关性作者报 Pearson r=0.83。作者以轨迹定性比较分析为何长期游戏难以进展。
- **RECONSTRUCTED idea**：先在无复杂语义的游戏中暴露模型执行/规则跟踪基本能力，避免无穷讨论具体世界难点。再在自然、人写游戏里验证其解释范围与失败传导。
- **限制**：相关不等于 Simon Says 是通用的因果瓶颈；游戏耗 token、命令 parser 和先验训练知识不同。Jericho 被设计来让人探索，score 不是 NPC 可信行为；不能拿这 122 个游戏直接宣称 NPC 研究完成。
- **可迁移方法**：给 NPC 加 action-parser、world-grounding 的低成本 gate；不过真正科学结论仍要在自然 NPC 后果上成立。

## 5. Collab-Overcooked：先让合作成为不可绕开的依赖
来源：[EMNLP 2025](https://aclanthology.org/2025.emnlp-main.249/)、[作者代码](https://github.com/YusaeMeow/Collab-Overcooked) 与已有 [研究卡](../../../library/themes/game-npc-social/GAME_NPC_LANDSCAPE.md)；P1 本轮论文+P2 代码；既有库中有更深入的历史摘录。
- **旧问题**：单人可以独自完成的任务，最终成功率不能说明是否发生了真正的合作。
- **DOCUMENTED 方法**：基于 Overcooked 的资源限制、不同任务知识，设置协作必要性；TES/ITES、initiate/respond 等过程读数、完整游戏动作轨迹；README 提供评估脚本和本地 vLLM 支持。
- **RECONSTRUCTED 研究动作**：先修改游戏以确立相互依赖，再从参考动作序列中测请求/响应/冗余，而非先打造一个 multi-agent brain。测量与失败机制因任务结构而变得可识别。
- **限制**：TES 对“合理但不同于参考轨迹”是否惩罚？负载/任务长度/沟通机会常同时变化；料理伙伴 agent 未必有故事角色 persona。
- **迁移**：NPC 与玩家协作研究需**先证明 NPC 的行动实际影响了玩家**，而不是好像很体贴。

## 6. KNUDGE：真实 RPG 的 quest 限制比合成 persona 问答更难
来源：[EMNLP 2024](https://aclanthology.org/2024.emnlp-main.520/)、[作者仓库](https://github.com/nweir127/KNUDGE)；P1 paper + P2 repo。
- **旧问题**：生成 NPC 台词时遗忘作者写过的游戏世界任务状态，玩家得到貌似自然但世界不一致的回应。
- **DOCUMENTED**：现成专业叙事游戏的 quest objectives、角色/对话 graph、知识支持片段与 dialogue node，形成具有任务事实基础的自然数据，而不是全部从模型合成。
- **RECONSTRUCTED**：从“生成一段话是否像角色”转成“这句话处于何种真实任务阶段，有何角色参与者、先决条件和已完成目标”；真实任务结构带来有意义的正反例。
- **方法边界**：可忠实生成对话，但不保证 NPC 自动拥有自由行动、误信的更新或独立于作者脚本的政策；用它研究 action-level belief 需要合法的真实后果接口，不能自己凭空宣布已经存在。
- **要查**：数据 license、quest graph 的边定义、观测可见性、自然数据是训练还是评测、可执行动作有多少。读代码前不把它当完整游戏引擎。

## 对这些论文的共同反思
有时论文创新在于改变**可以被证伪的评价单位**（NCP、Collab）；有时在于寻找**可执行决策结构**（CDT）；有时关键价值来自真实代码里发现**内部指标↔外部行为的推断断裂**（PCSP）。我们要学习的是如何提出能区分解释的实验，而不是复刻这些名字或虚构一个“无人涉足的中间空白”。
