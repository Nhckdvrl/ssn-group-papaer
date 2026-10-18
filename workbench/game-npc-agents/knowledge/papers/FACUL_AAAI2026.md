# F.A.C.U.L.: Language-Based Interaction with AI Companions in Gaming

- 规范记录：`R14`；主题类型：`commercial_game_companion_system`。
- 主源：[论文与出版信息](https://ojs.aaai.org/index.php/AAAI/article/view/38842)；实际所读文件：[PDF](https://arxiv.org/pdf/2511.13112v2)。
- 版本：arXiv:2511.13112v2, 2025-11-27；AAAI2026正式条目已核验。
- 阅读范围（2026-10-18）：完整主文PDF pp.1–8：引言、相关工作、全部方法、实验、用户研究、结论；补充材料尚未逐项读。
- 证据身份：正文阅读；未进行代码复现、模型调用或玩家实验。发表／接收身份与实际所读版本分开记录。

## 1. 问题、原有做法与改变的前提（DOCUMENTED）

真实FPS伙伴须把短语、指代、方位和战术命令落到资产及动作，同时满足延迟和并发要求；本文组合快速意图解析、模型规划和引擎执行。

## 2. 方法、任务与主要证据

Arena Breakout: Infinite中的语音战术伙伴：BERT-FID解析高置信简单命令，低置信送领域微调Qwen2-1.5B规划为Python原子函数；文字/CLIP检索结合引擎实体坐标、方向、掩体点定位目标；行为树执行并语音反馈。贡献是开放措辞和战术指代落到已有游戏能力的整合与吞吐权衡。

100场游戏2550条命令，玩家失败反馈由至少两名熟悉FPS标注者修正；全系统87.2%accuracy、613ms、916QPS，LLM+CLIP版本89.2%、614ms、210QPS，快速版73.9%。24名有FACUL使用经历的经常玩家比较四模式，体现初步偏好，而非随机大规模留存实验。

## 3. 与最近邻的距离

此表包含后来工作，用于当前领域定位，不把后来论文写成本文发表时的基线。

| 近邻 | 本文相对该工作的方法、对象或证据区别 |
|---|---|
| [larp](../../../../library/themes/game-npc-social/papers/LARP_2023.md) | 给出真实游戏命令数据和系统测量，LARP主要提出架构。 |
| [videogamebench](../../../../library/themes/game-npc-social/papers/VIDEOGAMEBENCH_2026.md) | 拥有引擎状态、实体语义和技能，与只准像素按键的任务接口不同。 |
| [balrog](../../../../library/themes/game-npc-social/papers/BALROG_2025.md) | 测玩家发出的具体伙伴命令，而非通用agent独立通关。 |

## 4. 证据边界与未排除解释

87.2%是命令/实体识别正确，不是任务胜率或全部玩家行为可实现。已知资产结构、25intent类别和行为树承担关键可靠性；没有强商业LLM加同引擎信息的对照。只在一款FPS，推广RPG/MOBA是未来设想；人物性格尚属未来工作，不能以此支持角色自主性结论。

## 5. 对整个NPC领域可迁移的认识

游戏NPC中的成熟集成方向：语言交互、状态接地、可靠技能、实时反馈的分层。对作者而言资产语义和工具接口本身是研究/制作成本，不能把小模型接口研究缩成更会聊天。

## 官方资产与历史核查范围

[作者演示与资产页](https://sites.google.com/view/FACUL-demo) · [项目页链接的代码仓库](https://github.com/tencent-facul/code)

项目页的Code and Datasets按钮指向该仓库。旧卡记录2026-10-16仓库为空，这是带日期的历史观察；本次确认项目入口，不据此断言当前仍为空，也不把按钮存在当完整代码／数据已可复现。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/FACUL_AAAI2026.md)。
