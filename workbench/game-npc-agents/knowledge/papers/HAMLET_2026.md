# HAMLET: A Hierarchical and Adaptive Multi-Agent Framework for Live Embodied Theatrics

规范记录：`hamlet_2026`；ICLR 2026（OpenReview会议PDF及官方proceedings索引确认）。实际版本：arXiv:2507.15518v5，2026-05-11，32页；与正式版作者列表有差异，读此明确版本。

**实际阅读范围：** 完整正文第1–11页；附录A–B第14页、C–J第16–31页完整机制、标注、训练、延迟与提示；第15页文学清单未逐条核、第32页贡献说明未细读

[原文](https://arxiv.org/pdf/2507.15518v5) · [发表／主源信息](https://openreview.net/pdf/ff2021fc57224626dd60a1f3845f30a41ca8a245.pdf)

**来源与范围：** 2026；ICLR 2026（OpenReview会议PDF及官方proceedings索引确认）；arXiv:2507.15518v5，2026-05-11，32页；与正式版作者列表有差异，读此明确版本。完整正文第1–11页；附录A–B第14页、C–J第16–31页完整机制、标注、训练、延迟与提示；第15页文学清单未逐条核、第32页贡献说明未细读。[HAMLET: A Hierarchical and Adaptive Multi-Agent Framework for Live Embodied Theatrics](https://arxiv.org/pdf/2507.15518v5)。阅读标记：first_full_body_after_existing_partial_card。

**问题与机制。** 把简短主题/文学作品变成可即兴演出的戏剧：离线角色、剧情、审核及导演生成带终点的分层蓝图；在线私人角色目标与公开剧情旗标共同引导行为。Planner 给多条中间路径，Transfer 判断旗标，Advancer 在停滞时直接要求角色推进；PAD 选择快、慢、沉默及动作。道具行动由 LLM Narrator 裁定成败和更新场景，不能等同于经形式验证的物理执行器。它将强故事控制与角色自主性做成可运行协调架构，但“角色不愿冒险”被改判为剧情停滞，是明确的设计取舍。

**证据与单位。** 100个内容案例＝50文学作品＋50定制主题；中英各75项含共享定制主题，不是150独立世界。PAD消融用随机30主题、贪心 GPT-4o，比 raw-prompted 单模型及无 PAD；未给同信息、同预算普通规划的强对照。模型排行榜也包含强商业与推理模型，不能把全领域不足归于小模型。Advancer 完成率100%对68.1%（表13），附录文字却68.7%，且未交代该子集分母；它证明对预定剧情终点的推进，不证明玩家自由或角色目标得到保存。PAD动作参数因多解未进入定量评价。

**评价与局限。** 5位有一年相关经验的标注者；HAMLETJudge 9,450比较标签来自7模型、21模型对、150语言项目、3维，按维度分层随机留出4.7%，并非说明按故事/模型隔离；人类相关平均 .791 因此限于这一分布。Interaction Experience 的完整标注实际要求阅读剧本评流畅/沉浸感，不能写成真实玩家体验实验。PAD保留≥4/5一致标注，14,412项，随机5%测试；表10单工具总数仍用含多工具的14,412，口径有歧义。延迟罚函数人为设阈，八H200测的0.36秒不保证端到端实时。

**领域位置。** 有价值的整体能力是作者给剧情骨架、角色在骨架中实时选择路径和非言语行为。必须同时评价终点完成、可接受的意外、对玩家偏离的响应及强制介入代价；仅把所有旗标完成当成功会奖励过度导演控制。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Declarative Optimization-Based Drama Management in Interactive Fiction](../../../../library/themes/game-npc-social/papers/DODM_2006.md) | 继承作者目标和角色即兴的管理问题，采用LLM蓝图与停滞指导而非预定义奖励搜索。 |
| [Can LLM Agents Stick to the Script? A Benchmark for Long-Horizon Consistency in Interactive Narratives](NCP_2026.md) | NCP将状态/剧情/输入约束变成外部审计；HAMLET主要评价完整表演品质和旗标完成。 |
| [Deriving Character Logic from Storyline as Codified Decision Trees](CDT_2026.md) | CDT诱导单角色条件行为知识，HAMLET主要编排多角色与场景推进。 |

## 官方资产与历史核查范围

[作者仓库](https://github.com/Tsumugii24/HAMLET)

此前固定commit bb2c09e9fdbc2dfc3032da8f11ac75cf97ca87cf只核查到README与poster PNG，未见可读PAD／narrator／runner实现。该观察只约束当时版本；本次未重新审当前仓库或运行系统，不宣称完整框架已开源。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/HAMLET_2026.md)。
