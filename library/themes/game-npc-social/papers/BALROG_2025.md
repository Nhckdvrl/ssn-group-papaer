# BALROG: Benchmarking Agentic LLM and VLM Reasoning On Games

- 规范记录：`R17`；主题类型：`game_playing_benchmark`。
- 主源：[论文与出版信息](https://proceedings.iclr.cc/paper_files/paper/2025/hash/f0b1515be276f6ba82b4f2b25e50bef0-Abstract-Conference.html)；实际所读文件：[PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/f0b1515be276f6ba82b4f2b25e50bef0-Paper-Conference.pdf)。
- 版本：ICLR 2025 正式会议论文。
- 阅读范围（2026-10-18）：完整正文 pp.1–10，表1–3、能力分析与开放问题；37页中的任务附录未完整读。
- 证据身份：正文阅读；未进行代码复现、模型调用或玩家实验。发表／接收身份与实际所读版本分开记录。

## 1. 问题、原有做法与改变的前提（DOCUMENTED）

模型知识考试不能充分检验连续游戏行动；本文统一六个经典环境并按进度观察行动、探索和推理差距。

## 2. 方法、任务与主要证据

统一BabyAI/TextWorld/Crafter/Baba Is AI/MiniHack/NetHack六个环境，区分模型与推理时agent策略。语言与语言+当前画面双接口；按成功或进度里程碑评分，记录探索、空间推理、长程计划与知识—行动失配。

正式主实验是零样本直接下一动作、历史16观察、无显式检索/反思/强规划；2024版模型。语言平均Claude3.5Sonnet32.64%、GPT4o32.34%；o1-preview仅NetHack因预算受测、进度约1.57%。视觉附加对部分模型降分、Sonnet则提升；视觉全榜与文字全榜游戏集合不同，不能直接作总均分因果比较。

## 3. 与最近邻的距离

此表包含后来工作，用于当前领域定位，不把后来论文写成本文发表时的基线。

| 近邻 | 本文相对该工作的方法、对象或证据区别 |
|---|---|
| [videogamebench](VIDEOGAMEBENCH_2026.md) | 文本／简化环境与旧商业游戏原始画面不同。 |
| [rpgbench](RPGBENCH_2025.md) | 现有规则游戏中的玩家agent，而非生成和模拟RPG的引擎模型。 |
| [agwm](../../../../workbench/game-npc-agents/knowledge/papers/AGWM_2026.md) | 完整交互任务评价与局部世界预测评价不同。 |

## 4. 证据边界与未排除解释

不能将零样本下的局限写成充分工具/记忆/重规划商业系统上限；不能将进度百分比当游戏通关率。程序生成减轻实例重复但不保证规则/知识从未见。长期任务只保留16观察可能混杂记忆机制；失效机制主要定性轨迹，不是已被因果定位的神经机制。没有NPC人格、作者工具或真人队友。

## 5. 对整个NPC领域可迁移的认识

通用游戏行动与领域专用NPC的邻接入口；为接口控制、长程技能/记忆与评估预算提供清晰比较框架。

