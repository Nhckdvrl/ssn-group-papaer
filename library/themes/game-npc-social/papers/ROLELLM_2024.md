# RoleLLM: Benchmarking, Eliciting, and Enhancing Role-Playing Abilities of Large Language Models

- 规范记录：`R04`；主题类型：`training_and_benchmark`。
- 主源：[论文与出版信息](https://aclanthology.org/2024.findings-acl.878/)；实际所读文件：[PDF](https://aclanthology.org/2024.findings-acl.878.pdf)。
- 版本：ACL 2024 Findings, pp.14743–14777。
- 阅读范围（2026-10-18）：完整正文 PDF pp.1–9（§1–6、limitations）；附录C数据清洗与E部分超参。其余附录未宣称完整读。
- 证据身份：正文阅读；未进行代码复现、模型调用或玩家实验。发表／接收身份与实际所读版本分开记录。

## 1. 问题、原有做法与改变的前提（DOCUMENTED）

单靠名字或人物简介不能稳定产生角色知识和表达；本文把角色专属知识与通用问题上的角色风格分别合成，再联合训练。

## 2. 方法、任务与主要证据

RoleBench与RoleLLM是一项工作：从脚本提取100角色的背景与话语，用Context-Instruct合成角色知识问答，以RoleGPT合成有角色语气的通用问答，再通过角色条件SFT训练RoleLLaMA/RoleGLM。核心是把角色知识与说话方式分别制作训练材料；提示基线含人物说明、口头禅和BM25检索5条对话。

95英文+5中文角色；168093样本对应23463不同指令，不能按样本数当独立情境。评估分指令泛化、10个未见英文角色泛化，用ROUGE-L的RAW/CUS/SPE、GPT4与3位NLP研究生500指令子集判断。RoleLLaMA对RoleGPT的英文人评胜率52.0%，未见角色56.1%；未见角色的角色专有知识没有明显提升。

## 3. 与最近邻的距离

此表包含后来工作，用于当前领域定位，不把后来论文写成本文发表时的基线。

| 近邻 | 本文相对该工作的方法、对象或证据区别 |
|---|---|
| [character llm](CHARACTER_LLM_2023.md) | 从每个角色单独训练扩展为多角色条件训练和未见角色测试。 |
| [ditto](DITTO_2024.md) | RoleGPT使用外部教师；Ditto重点是同基座自对齐与规模交叉监督。 |
| [coser](../../../../workbench/game-npc-agents/knowledge/papers/COSER_2025.md) | 单轮问答材料与文学多人场景、经历及调度数据不同。 |

## 4. 证据边界与未排除解释

作者明确只针对单轮问答。ROUGE与合成教师参考易奖励表面风格/措辞；数据清洗排除了拒绝回答或提供信息的样本；角色内出于目标、关系或知识权限而合理拒绝的能力未被单独评估。基于稀疏噪声脚本的检索结果不如SFT，不能泛化为RAG无效。没有引擎行动或玩家体验。

## 5. 对整个NPC领域可迁移的认识

角色数据训练与提示强基线的早期方法参照。角色数量、独立指令数、模型生成样本数分别记；用可保持任务功能的角色表达问题定位，避免把风格问答胜出说成游戏行动自主性。

