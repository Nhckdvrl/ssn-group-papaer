# Game NPC Agents｜游戏世界中的自主角色：能力、训练、安全与社会系统

**状态：PROPOSED。2026-10-14 按用户要求恢复真正开放的 NPC Agent 科研空间。** 不再固定“目标 vs 旧计划”或“只研究可训练的行为控制”为唯一主线；安全、人格漂移、游戏经济/多智能体攻击是同等正当的研究板块。未改变其他工作台、全局 ACTIVE 分配。

## 科学对象
研究**实际游戏中的 Non-Player Characters**：剧情/RPG 角色、生活模拟居民、玩家队友与敌对角色、虚拟世界中的商人/生产者/组织/群体。角色通过对话、感知、记忆、决策和实际行动影响玩家、其他 NPC 或游戏规则/经济。模型可以是 LLM/VLM、小策略网络、符号控制器或它们的组合。
- 不是单独训练 AI 通关游戏（player agent），也不是没有可玩机制的角色聊天 benchmark；相关论文**可以提供迁移方法**，但须解释回游戏内 NPC 的科学意义。
- 不规定每篇 NPC 研究都必须同时实现 3D、低级 motor action、符号世界或玩家实验。研究结论必须精确对应所检验的交互/世界/玩家后果。
- **剧情授权的谎言 ≠ 安全违规；经历带来的合理角色成长 ≠ 人格被劫持；规则内博弈 ≠ 利用世界系统漏洞。** 这三条直接决定实验真值。

## 领域全景：八片可独立演化的矿区
| 板块 | 自然、重要的问题 | 知识库 |
|---|---|---|
| A 角色决策和行为训练 | 如何学到可执行、多样、可编辑、创作者能控制的行动？ | [领域地图](knowledge/DOMAIN_ATLAS.md) / [训练前沿](knowledge/NATIVE_GAME_NPC_FRONTIER.md) |
| B 游戏世界与 Agent 系统 | 高层理解怎样与事实、合法游戏动作、快速策略、玩家互动形成闭环？ | [领域地图](knowledge/DOMAIN_ATLAS.md) |
| C NPC 交互与社会协作 | NPC 之间/与玩家怎样沟通、协作、背叛、改变关系和做出真实选择？ | [领域地图](knowledge/DOMAIN_ATLAS.md) |
| D 长期记忆、身份与人格漂移 | 角色什么时候该稳定、应该成长，什么时候发生无依据/受攻击的偏离？ | [人格与记忆](knowledge/PERSONA_DRIFT.md) |
| E **NPC 安全、攻击与防御** | 玩家/恶意 NPC 能否劫持角色、越过剧情权限、污染记忆、改变规则或滥用工具？ | [攻击面与证据](knowledge/NPC_SECURITY.md) |
| F **多 NPC 经济、系统性攻击** | 有贸易/货币/信誉/供求的游戏社会中如何出现诈骗、价格波动、协同行为、制度失效？ | [游戏经济与制度](knowledge/GAME_ECONOMY.md) |
| G 叙事、欺骗与玩家体验 | 可预期的故事承诺、合法侦查/谎言、玩家能动性、信任和有意义的后果如何共存？ | [领域地图](knowledge/DOMAIN_ATLAS.md) |
| H 具身/视频/语音、实时部署 | 视觉世界、语音实时互动、多 NPC 扩展与端到端成本怎样限定能力？ | [系统/资产](BASELINES.md) |

**八个方向不是八个预定实验，也不要求必须做全。** 不按旧“哪条方向最容易跑”的便利性强行选题；优先从顶会/游戏研究原问题、最新强近邻、可复现的自然游戏系统和信息量高的实验逐步收敛。安全与经济不会被强行归入训练分支。

## 最有分量的新阅读（原始出处）
- [ProvSec 2025 NPC secret extraction](https://arxiv.org/abs/2508.19288)：游戏 NPC 遭受玩家对抗输入，正文仅单个角色/30 条单轮测试，值得延伸但**不能冒领发现“首次可泄密”**。
- [KDD 2025 MMO economic simulation](https://arxiv.org/html/2506.04699v1)：网易伏羲/USTC 等在 MMO 经济里做生产、拍卖与 P2P 交易；正文含结构动作、30 agents×200 steps、代码归档入口。
- [COLING 2025 RoleBreak](https://aclanthology.org/2025.coling-main.494/) 与 [ACL 2026 Dynamic Persona Coherence](https://aclanthology.org/2026.acl-long.1336/)：角色受攻击的失真、身份稳定与正常心理变化均有直接先验。
- [CHI 2024 游戏里的欺骗与玩家信任](https://www.robertxiao.ca/research/lies-deceit-and-hallucinations/)：作者观察到有意谎言与无意幻觉在玩家意义中不同。
- [NeurIPS 2024 AgentDojo](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html)、[ICLR 2025 ASB](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5750f91d8fb9d5c02bd8ad2c3b44456b-Abstract-Conference.html)：通用 agent 攻防基线，**并非已验证的游戏 NPC 攻击实验**。

## 现在的研究入口
| 文件 | 为什么先读 |
|---|---|
| [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) | 不预设 paper story 的多方向研究入口及高信息量测量 |
| [knowledge/DOMAIN_ATLAS.md](knowledge/DOMAIN_ATLAS.md) | NPC 类型×科研构念×相关领域方法的整体地图 |
| [knowledge/NPC_SECURITY.md](knowledge/NPC_SECURITY.md) | NPC 对抗交互、权限/秘密/记忆污染、攻击与剧情玩法的边界 |
| [knowledge/GAME_ECONOMY.md](knowledge/GAME_ECONOMY.md) | **直接游戏经济**KDD2025 / AIIDE2008 vs 2026 agent 市场攻击的证据距离 |
| [knowledge/PERSONA_DRIFT.md](knowledge/PERSONA_DRIFT.md) | 角色一致性、动态成长、操纵和受攻击漂移 |
| [knowledge/SOURCES_AND_STATUS_2026-10-14.md](knowledge/SOURCES_AND_STATUS_2026-10-14.md) | 会议身份、读到原文哪部分、哪些只看摘要 |
| [BASELINES.md](BASELINES.md) / [LOCAL_FIRST.md](LOCAL_FIRST.md) | 各板块的真实本地资源/零付费 API 闭环 |
| [AGENTS.md](AGENTS.md) / [knowledge/README.md](knowledge/README.md) | 本地科研 agent 自主探索/更新与防止局部锁定 |
| [experiments/README.md](experiments/README.md) | 旧未运行窄切口已撤执行优先级，**当前没有强行指定下一个实验** |

## 本轮决策与证据边界
- **2026-10-14 / 用户：** 显式否决上两轮的狭小框架，要求 NPC 领域保持开放，并正面纳入安全、人格漂移、游戏多 Agent 经济攻击。
- **2026-10-14 / agent：** 整理开放研究领域；旧 E03/E04/E05 保留为未运行、被替换的实验卡；新知识库全部在本 workbench 内，不复制到外部 library；**不自动关闭或暂停此 workbench**。
- **实证状态：** 没有新本地 NPC rollout/训练、没有实际攻防/经济试验或自己的 L1+ 科学发现。E01 仅旧 CPU 源码合约测试，非 NPC 科学结果。
- 资源：研究室十余张 A100/8 张 RTX PRO 6000、实习单位 16 张 H20；跨节点通信/I/O 很差。研究默认 **全部本地、0 付费推理 API**，多卡用于独立实验而非强行大规模 DDP。来源、数据与实习资产授权彼此独立。研究纪律继承 [根 AGENTS](../../AGENTS.md)、[EXECUTION](../EXECUTION.md)。
