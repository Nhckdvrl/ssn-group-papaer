# Game NPC Agents — 游戏中的自主非玩家角色

**状态：PROPOSED；用户选定本轮优先矿区 A：人物设定、真实利益与战略行为的关系。** 全局ACTIVE状态不变；安全、人格漂移、社会互动和游戏经济仍开放。允许结果显示Persona对真实行动很有效。

**执行：E74–E76全部完成；E77已通过完整profile与实体读回，全102图固定队列在四卡运行中。I04保持PROMISING，论文正文暂缓。** 最新[进度报告](PROGRESS_REPORT_2026-10-16.md)、[主张账本](CLAIMS.md)、[当日日志](logs/2026-10-16.md)。

中心问题：NPC面对自身目标、角色规范、社会关系、玩家请求与可见游戏状态，怎样形成选择并产生实际后果？新颖性按整体问题与证据链判断，不要求每个工具组件前所未有。

## 当前整体认识

**角色设定同时影响必要动作的推进和资源用途，物理前提决定它们怎样显露为最终任务表现。** E75非Give31图中，Agreeable相对Firm的首步Get增加Gemma/32B 15.05/29.03pp，请求交付增加12.90/27.96pp，自身任务却+5.38/−16.13pp。E76固定同一段对话后，Gemma人物×可及性任务交互仍为−21.51pp [−37.63,−6.45]，32B为0 [−11.83,11.83]。

这与既有C04任务/非冲突合作共存、C05执行规则的物理作用构成一条研究链。当前C06限定L2；推进差不直接等于潜在能力差，下一项应区分目标/等待价值和已选目标的实际实现。[整体定位与七篇新精读](knowledge/persona-behavior/BELIEF_CHOICE_POSITIONING_2026-10-16.md)。

## 最近完成的实验

| 实验 | 设置与结果 |
|---|---|
| [E74](experiments/E74-physical-consequence-prediction-and-choice.md) | 117原作者Give图、2808预测＋2808新增执行。自产后果表提高原任务17.4–33.3pp，替换原生真值未额外恢复；预测答案、行动链呈现和真实选择分开解释。 |
| [E75](experiments/E75-native-retrieval-task-transfer.md) | 102原作者自然Get前提图、四任务族、4896分支。原角色/目标/规则保留；ready是原生Get后的反事实。推进与用途共同变化，任务改善有不同来源。 |
| [E76](experiments/E76-fixed-dialogue-and-native-access.md) | 精确固定E75 retrieval对话，只变执行初态，1224分支。人物×物理前提作用在固定历史下成立于Gemma，32B的资源取舍更稳定；不增加新指令或表格。 |

三轮共29125实际本地调用、8928新增物理分支、2808预测上下文、208不同源图，3.83553观测GPUh/3.46147载入与推理GPUh，峰值4卡，0API/解析失败；本轮worker已退出。[合并成本与源图口径](results/E74_E76_round_accounting.json)。分支/调用不是独立世界，E76复用E75源图，E74与E75相交11图。

[结果清单](results/README.md) · [E74图](results/figures/E74_predictions_and_actual_actions.png) · [E75图](results/figures/E75_task_request_joint_outcomes.png) · [E76图](results/figures/E76_fixed_dialogue_access_effects.png)，均有PDF/SVG。

## 历史证据与明确冻结的执行线

- [E70–E76连续报告](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)：先保留E70–E73原报告（117源图、23868分支/125126调用），文末完整附加E74–E76续报；各期成本与样本口径分别保留。
- [E69同图任务报告](PROGRESS_REPORT_2026-10-15_MATCHED_TASKS.md)：112同图任务配对及三来源案例的后续执行；不把三个案例当总体机制。
- [E67/E68](PROGRESS_REPORT_2026-10-15_RULE_EXECUTION.md)：执行规则恢复在独立41装备图复现，60其他资产图保留角色合作差；三向统一分流未成立。
- [E65/E66](PROGRESS_REPORT_2026-10-15_CONSTRAINT_PROBES.md)、[E63/E64](PROGRESS_REPORT_2026-10-15_POST_REVIEW.md)、[E50–62](PROGRESS_REPORT_2026-10-15.md)：三模型200图确认、角色分量、实体任务/合作、动态伙伴及白盒正负结果。
- [10月14日报告](PROGRESS_REPORT_2026-10-14.md)：原生系统恢复与旧实验。PCSP/MeltingPot小模型RL及追加诊断、校园1200帧全图漫游、只改conversation的总体人格实验、无实体flag任务均按用户决定冻结；历史文件保留，不按旧下一步恢复。E00/E02–E05不自动恢复。

## 接手入口

[AGENTS](AGENTS.md) · [LOCAL_AGENT_START](LOCAL_AGENT_START.md) · [EXPLORATION_ENTRY](EXPLORATION_ENTRY.md) · [E06基线卡](experiments/E06-persona-strategy-baseline.md) · [领域地图](knowledge/DOMAIN_ATLAS.md) · [人格—行为知识](knowledge/persona-behavior/) · [强近邻](knowledge/persona-behavior/RELATED_WORK.md) · [源码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md) · [痛点](PAIN_LOG.md)。源代码事实、实测、解释分别记录。

## 资产与执行边界

完整轨迹、输入输出、模型与checkpoint在`/home/xiang/.cache/game-npc-research/`，不进Git；E74–76 raw位于`runs/e74_*`、`e75_*`、`e76_*`。源数据/driver/model pin、启动参数和成本在实验卡与manifest；统计重建脚本在`scripts/`。原生动作、错误与物理变化均记录，无脚本替模型完成任务。

环境优先现有Conda fgvd及deps overlay，模型复用HuggingFace缓存。用户授权节点资源按现场空闲使用，全时≤8卡、独立单卡/单节点优先，不干扰其他任务。NPC/伙伴/教师/判定核心链路全部本地；用户另授权Step5仅作数据并限定Token Plan，本轮0调用。人物表达、情境意图、真实执行分开；原子任务不是角色全部私人利益，不把抽象标签映射成唯一正确选择。
