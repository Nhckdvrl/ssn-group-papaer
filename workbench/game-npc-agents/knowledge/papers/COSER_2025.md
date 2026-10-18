# CoSER: Coordinating LLM-Based Persona Simulation of Established Roles

- 规范记录：`R11`；主题类型：`role_training_narrative`。
- 主源：[论文与出版信息](https://proceedings.mlr.press/v267/wang25dk.html)；实际所读文件：[PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/wang25dk/wang25dk.pdf)。
- 版本：ICML 2025, PMLR 267:64822–64858。
- 阅读范围（2026-10-18）：完整正文 pp.1–10、表1–6；未宣称37页附录全部读完。
- 证据身份：正文阅读；未进行代码复现、模型调用或玩家实验。发表／接收身份与实际所读版本分开记录。

## 1. 问题、原有做法与改变的前提（DOCUMENTED）

通用QA式角色数据与自然文学交互存在差距；本文用原著对话、经历、动机及情境建立训练和多人演绎评价。

## 2. 方法、任务与主要证据

从771本书抽取17966角色、29798段会话，平均13.2轮，建立剧情/经历/动机/内心思考等层次；Llama3.1 8B/70B多角色SFT并训练下一发言者/环境响应。Given-Circumstance Acting以各自隐藏动机和思想推进多人文本剧情，20轮上限；环境由GPT-4o模拟。原始台词来自书，思想/动作部分为模型推断，不能一概称真实原作标注。

200段测试（100来自见过书、100未见书），3次运行；原协议CoSER70B平均59.06、GPT-4o59.95。LifeChoice 93.47对75.96，是17.51个百分点/约23%相对增幅。人评60个场景7模型，3位标注员各评20场景，非每场景3独立评分。结构化经历/会话检索有效，原文片段检索弱；动机/内心思考总体有益，但8B去动机56.81略高于标准56.45，非每组都改善。

## 3. 与最近邻的距离

此表包含后来工作，用于当前领域定位，不把后来论文写成本文发表时的基线。

| 近邻 | 本文相对该工作的方法、对象或证据区别 |
|---|---|
| [character llm](../../../../library/themes/game-npc-social/papers/CHARACTER_LLM_2023.md) | 原始对话与合成思想混合，不是将整段经历都合成为训练文本。 |
| [rolellm](../../../../library/themes/game-npc-social/papers/ROLELLM_2024.md) | 从通用／角色专有QA扩展为给定情境的多人行为。 |
| [her](../../../../library/themes/game-npc-social/papers/HER_2026.md) | 后者新增隐藏系统推理、偏好奖励与RL，且更换CoSER评委。 |
| [characterbox](../../../../library/themes/game-npc-social/papers/CHARACTERBOX_2024.md) | 共享多人文本演绎目标，原始数据和评估参考的权威来源不同。 |

## 4. 证据边界与未排除解释

故事一致性以原著走向为参考，未验证玩家偏离原作的新分支应如何评估。人物fidelity、故事质量、原作一致性分开；模型评委随模型/参考/rubric/长度校正变化明显。NPC环境响应是文本模型而非游戏引擎，缺少玩家体验与因果执行证据。后续HER改变评委/格式后绝对分不可横比。

## 5. 对整个NPC领域可迁移的认识

连接人物学习、多人调度与故事质量的重要原始工作；支持阅读经历和动机的数据结构，不能升级为已解决实时可玩NPC。


## 6. 本次校正

正式ICML版的动机／思考消融在Table 6。旧卡将52.99→51.97、56.45→54.65写为去动机，实际是去内心思考；去动机分别为49.63与56.81。移除旧错误，不据其中一列声称所有模型都改善。正式页码是64822–64858。

## 官方资产与历史核查范围

[官方代码、模型与数据入口](https://github.com/Neph0s/CoSER)

作者README提供数据构建、GCA评价、样例及8B／70B模型入口。此前卡与本次阅读均未审完代码和数据抽取流水线；入口存在不代表已复现。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/COSER_2025.md)。
