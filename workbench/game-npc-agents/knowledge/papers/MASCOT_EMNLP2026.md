# MASCOT: Multi-Agent Socio-Collaborative Companion Systems

- 规范记录：`R15`；主题类型：`adjacent_multi_party_dialogue`。
- 主源：[论文与出版信息](https://arxiv.org/abs/2601.14230v3)；实际所读文件：[PDF](https://arxiv.org/pdf/2601.14230v3)。
- 版本：arXiv:2601.14230v3, 2026-09-14；作者项目/主页标注EMNLP2026 Main accepted，未以ACL正式论文集条目核验。
- 阅读范围（2026-10-18）：完整正文PDF pp.1–9（§1–5、limitations）；表1–3与人评图6；附录未完整阅读。
- 证据身份：正文阅读；未进行代码复现、模型调用或玩家实验。发表／接收身份与实际所读版本分开记录。

## 1. 问题、原有做法与改变的前提（DOCUMENTED）

多角色回复容易重复、互相附和；本文分别优化角色发言质量与整场交谈的发言调度，改变群体协调的训练目标。

## 2. 方法、任务与主要证据

把speaker角色对齐与director群体对话组织分开：GPT4o标注偏好→小奖励模型→GRPO角色训练；固定speaker和模拟用户后训练director选择谁说话与说话策略，以全轨迹相关、独特、互补贡献作为奖励。强调减少相互附和与重复，而非多agent自动总是更好。

Qwen3-8B为director/speaker/模拟用户；ED/ESConv情绪支持与QMSum会议上下文，非游戏。对照相同角色的提示、CoT、自一致、SFT、MultiAgentESC。40名标注者对200不同response-pairs每项2评；69%及68.5%是每基线200条评分层面的偏好。另20人100对话研究。

## 3. 与最近邻的距离

此表包含后来工作，用于当前领域定位，不把后来论文写成本文发表时的基线。

| 近邻 | 本文相对该工作的方法、对象或证据区别 |
|---|---|
| [coser](COSER_2025.md) | 多人调度相通，但服务情绪支持／会议，未评文学情境或游戏。 |
| [characterbox](../../../../library/themes/game-npc-social/papers/CHARACTERBOX_2024.md) | 由director选择发言者，而非以世界演绎作为主要构念。 |
| [her](../../../../library/themes/game-npc-social/papers/HER_2026.md) | 都使用场景化奖励；MASCOT另有整条群体轨迹目标。 |

## 4. 证据边界与未排除解释

没有玩家、执行动作、经济或叙事目标。显著性按评分层面计算，同样本/同标注者依赖需要保留；不能按400独立对话理解。SFT弱于zero-shot只证明所测训练配置，不能概括SFT普遍失败。当前安全/帮助评分不等于长期心理结果。

## 5. 对整个NPC领域可迁移的认识

为多角色交谈和群体对白提供双层协调思路，属于邻域方法而非原生游戏NPC系统；角色差异和群体贡献应同时评，群体多样性不能只靠降低文本重叠。

## 官方资产与历史核查范围

[作者仓库](https://github.com/hello-diana/MASCOT) · [作者发表页面](https://ahren09.github.io/publication/emnlp26_mascot/)

仓库README列生成、打分、训练与评价入口，并区分论文默认Director GRPO与可选DPO。此前只核README执行路径，本次未运行代码／训练。EMNLP 2026 Main身份来自作者页面与声明，和未核到的ACL正式条目分开。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/MASCOT_EMNLP2026.md)。
