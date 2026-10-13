# Game NPC & Interactive Agents：领域谱系与认识边界（2026-10-13）

## 第一层：游戏引擎与真实状态，早于 LLM NPC
经典行为树/规划/状态机负责**可复算的 world state transition**；TextWorld/Jericho/Overcooked 等提供可执行游戏与实体动作。核心教训：**NPC 的想法不是世界事实；语言行动不是已经执行的行动；旁白不是玩家能够自主控制的 NPC**。比起纯角色对话，我们需要一个可信的状态权威。

## 第二层：语言角色→记忆、剧情与长期社会模拟
- [Generative Agents, UIST 2023](https://arxiv.org/abs/2304.03442)：记忆→反思→规划框架，后续“加长期记忆”不能声称新颖。
- [KNUDGE, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.520/)：利用现成专业 RPG quest/ontology/对话结构约束 NPC 话语，世界绑定并非无人做。
- [SOTOPIA, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/b3075b88e583a0e98d8b24338a613060-Abstract-Conference.html)：角色目标与社会互动的 benchmark；[SOTOPIA-π ACL2024](https://aclanthology.org/2024.acl-long.698/) 用该环境后训练 social agents，说明“社会互动”早有框架和方法。
- [RoleKE, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1689/)：角色知识与错误识别；不能等同真正游戏内的信念转移。

## 第三层：从角色台词转向行动、角色逻辑与伙伴
- [Collab-Overcooked, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.249/) 明确构建**必须合作**的任务和过程性诊断，不能把终局成功率直接等同协作。
- [Deriving Character Logic / CDT, ACL 2026](https://aclanthology.org/2026.acl-long.568/) 将故事场景→行动规则学习为**可执行决策树**，泛化角色行动控制属于已被关心的领域。
- [FAIRGAMER, ACL 2026](https://aclanthology.org/2026.acl-long.2015/) 直接研究 NPC 交易/协作/竞争中的实际决策偏差；外部差异不是只有“persona embedding”的问题。
- [PCSP, arXiv 2026](https://arxiv.org/abs/2605.23652/) 用 persona-conditioned shared RL policy 控制实际 NPC 动作，源码附独立行为 probe 与 representation probe，二者不等价。**不能把这条证据当我们的 discovery。**
- [CollabBench, ICML 2026](https://proceedings.mlr.press/v306/qian26c.html)、[Decrypto, ICML 2026](https://proceedings.mlr.press/v306/lupu26a.html) 继续推进有实际行动的协作、伙伴适配和信息不对称；简单的 multiagent + partner model 已偏拥挤。

## 第四层：长程事实、剧情承诺与玩家自由
[ICML 2026 NCP-Bench](https://proceedings.mlr.press/v306/ma26ap.html) 把电影叙事变为 100 个可核对事实/剧情/轨迹环境；强模型在 20 turns 无冲突 survival 仍有显著困难。官方 [代码与数据](https://github.com/NLP2CT/NCP-Bench)。**它是 narrator–player 互动，不能直接代表独立 NPC。** 如果玩家用另一种合法方法解决任务，电影剧情承诺本身可能偏好旧路线；这是一个尚待验证的评测风险，而非已证明的错误。
[ACL 2025 interactive drama](https://aclanthology.org/2025.acl-long.546/) 已经研究玩家的沉浸感与能动性；不能声称 agency 没人研究。

## 第五层：NeurIPS 2026 与最新的压力
从 [NeurIPS 2026 官方题目列表](https://neurips.cc/Downloads/2026) 出发逐篇核查（接受标题不代表我们已经精读）：
- **[TALES: Text Adventure Learning Environment Suite](https://arxiv.org/abs/2504.14128)**：122 个不同真实/合成文本游戏；游戏行动推理很难。**玩家式 agent**；可迁移可执行测量，不是 NPC 直接强基线。
- **[Population-Aligned Persona Generation for LLM-based Social Simulation](https://arxiv.org/abs/2509.10127)**：批量人物设定需要符合真实人口层面分布；提醒不要拿几十个人工拼的 persona 宣称真实社会模拟，也不能直接推广到具体 NPC。
- **[How to Interpret Agent Behavior](https://arxiv.org/abs/2605.13625)**：对轨迹归纳行为层级的可解释分析可迁移，但非专门 NPC。
- **[Personalize-then-Store](https://arxiv.org/abs/2605.25535)**：可个性化长程记忆；加 memory 不是自己的 originality。
- 另需核查 [Perception, Not Reasoning, Limits Visual Theory of Mind](https://neurips.cc/Downloads/2026)、[Task Success Is Not Enough: Side-effect-Aware Evaluation of Tool-Using Language Model Agents](https://neurips.cc/Downloads/2026) 等新题目如何影响我们对“理解/成功”的解释；未做全文查证，**不归纳其发现**。
- **不把官方题目列表视为唯一主会身份来源**。含 Workshop/D&B/Position 的项目必须查 track。网上流传的 MafiaPersona dataset 页面自称 under review，不在此写成 NeurIPS main 已接收。

## 对我们的具体意义
自然问题不是“让角色更真实”，而是**在玩家真实施加变化时，怎样从 observation、belief、action、state transition 的可分离测量中理解 NPC 能力和评价偏差**。与相关会议最强近邻相比，纯 LLM persona QA、叙事 self-consistency、单一 memory 问答、简单 ToM prompt 都不够；这并不意味着不能做它们的真正机制性研究。

领域地图不是优胜者名单。正式读完最强论文的附录和代码后再调整各子领域热度与值得做的尺度，不先凭直觉“判死”。
