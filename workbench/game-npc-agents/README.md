# Game NPC Agents｜游戏世界中的交互式角色智能体

**状态：PROPOSED（2026-10-13 用户明确批准创建）；不改变已有 ACTIVE 配额，不代表已开始 GPU 运行。**
**中心：** 研究可行动、受真实世界状态约束、有局部知识、关系和目标、需要与玩家及其他 NPC 互动的智能体。不是单纯 roleplay chatbot，也不是只控制玩家游玩游戏的 agent。
**算力：** 研究室十余张 A100 / 8 张 RTX PRO 6000；实习单位 16 张 H20。跨节点网络/I/O 差；独立单节点/单卡实验优先。

## 我们为什么在这里
> 一个 NPC 在长期互动中什么时候真正依据它所知和经历行动，并响应玩家，同时维持可信的角色行为与可执行世界后果？现有的语言、记忆、角色和叙事评估，在哪些情况下可以/不可以预测这件事？

这是开放的**研究领域问题**，不是论文的最终 claim，更不是固定方法。允许从强基线、意外失败和竞争解释中重新定义问题。

## 文档与执行入口
| 文件 | 用途 |
|---|---|
| [knowledge/README.md](knowledge/README.md) | **本工作台专属**知识库目录与阅读纪律 |
| [knowledge/LITERATURE_MAP.md](knowledge/LITERATURE_MAP.md) | 系统文献谱系、方向间区别、NeurIPS 2026 等前沿压力 |
| [knowledge/PAPER_LEDGER.md](knowledge/PAPER_LEDGER.md) | 原始论文、会议身份、代码、阅读深度记录 |
| [knowledge/CORE_NOTES.md](knowledge/CORE_NOTES.md) | 重点论文的 idea 起源重建、方法、对照、局限及近邻距离 |
| [RESEARCH_TERRITORIES.md](RESEARCH_TERRITORIES.md) | 候选科学问题、互斥假设与高价值实验逻辑 |
| [BASELINES.md](BASELINES.md) | 开源执行环境、代码真实性、算力与复现准入 |
| [knowledge/MEASUREMENT.md](knowledge/MEASUREMENT.md) | 数据与评价规约、轨迹记录、统计及数据构造质量 |
| [AGENTS.md](AGENTS.md) | 本地 Agent 自主研究指南，不机械执行 |
| [experiments/E00-baseline-feasibility.md](experiments/E00-baseline-feasibility.md) | **PLANNED**：强基线与可测性的前置检验 |
| [CLAIMS.md](CLAIMS.md)、[PAIN_LOG.md](PAIN_LOG.md) | 实证账本，目前均无本地观察 |
| [logs/2026-10-13.md](logs/2026-10-13.md) | 初始调研范围和实际未完成事项 |

## 范围与尺度
- **NPC** 应有引擎/游戏确定的 state、角色可见信息、合法 action 和执行后果。队友、对手、社会/剧情角色均可。
- **NCP-Bench** 主要是 narrator agent，**TALES** 主要是 player agent；均为重要可迁移研究，却不等价于 NPC。
- **起步不做**只有聊天形式的人格打分、新大型 UE/Unity 引擎、无评价定义的 NPC 产品 Demo、拼 RAG/记忆/ToM 模块。
- **允许做**机制/测量研究、有解释力的负结果、简洁方法、严谨 benchmark；是否成论文由真实认识增量决定，不以组合复杂度衡量。

## 当前论文形态卡
- 研究空间 A–F 均开放，尚未选定一个 paper story 或贡献数量。
- 本项目实测成功：**无**；有证据的 L1+ 主张：**0**；复现基线：**0**；GPU：**未使用**。
- 目标会议：ICML / ICLR / NeurIPS；如果更贴近 NLP+互动，可评估 ACL / EMNLP / NAACL 主会。截止日期待官方公布，**不倒排周计划**。
- 先决条件：读强相关正文和源码→验证自然数据与运行/评估环境→强 baseline→观察结果/痛点→决定研究动作，而不是为写论文找一个显得新颖的包装。

## 决策记录及资产
- **2026-10-13 / 人：** 明确批准新建 Game NPC Agent 独立 workbench；遵循大规模阅读、深入理解和自主实验探索。
- **本轮 / Agent：** 状态仅 PROPOSED；不恢复 2026-10-11 已从 HEAD 删除的两个旧 NPC workbench，不改其他线，不做实验结果声明。
- 外部模型、运行记录和大数据**尚未下载**；未来请在具体节点按 BASELINES 记录 git SHA、模型/数据版本、配置、授权、输出位置，不把私有实习资产上传至公共仓库。
- 全局规则：[根目录 AGENTS](../../AGENTS.md)、[EXECUTION](../EXECUTION.md)、[IDEA_EXPLORATION](../IDEA_EXPLORATION.md)。
