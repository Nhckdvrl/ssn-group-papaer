# Game NPC Agents — 游戏中的自主非玩家角色

**状态：PROPOSED；用户选定本轮优先矿区 A：人物设定、真实利益与战略行为的关系。** 全局ACTIVE状态不变；安全、人格漂移、社会互动和游戏经济仍开放。允许结果显示Persona对真实行动很有效。

**执行：E81双方原作者目的的126图合作任务，两模型全504逻辑episode已收齐并完成物理读回；E82原Minecraft多步制作CPU链已完成；E83进入有自身目的NPC的归还/奖励决策切片重建与完整episode检查。** 无人物提示词网格。[E81卡](experiments/E81-authored-cooperation-and-partner-response.md) · [E82原生见证](experiments/E82-minecraft-original-cooperation-baseline.md) · [E83角色任务](experiments/E83-npc-quest-receipt-and-reward-baseline.md) · [合作近邻与真实玩家日志](knowledge/persona-behavior/COOPERATION_REPAIR_POSITIONING_2026-10-16.md)。I04保持PROMISING，论文正文暂缓。

中心问题：NPC面对自身目标、角色规范、社会关系、玩家请求与可见游戏状态，怎样形成选择并产生实际后果？新颖性按整体问题与证据链判断，不要求每个工具组件前所未有。

## 当前证据与研究判断

**2026-10-16用户再纠偏后的判断：** E70–E80建立了人物、社会历史、物理前提与实际事件之间的诊断证据，但当前仍主要围绕同种物品索要及原子任务计分，继续细分不能自动成为重要贡献。应用审计已指出这一点，实验优先级却没有充分改变。下一新增证据应面对原始问题：有自身目的的NPC，能否应对玩家提出的不同合作办法、实际履约及条件变化，产生可理解、可执行且影响玩法的选择？已有执行器、回放与反事实是研究工具；不默认以它们自身的分解为研究终点，不机械续开E81，不改已有证据等级或人定状态。

**角色设定同时影响必要动作的推进和资源用途，物理前提决定它们怎样显露为最终任务表现。** E75非Give31图中，Agreeable相对Firm的首步Get增加Gemma/32B 15.05/29.03pp，请求交付增加12.90/27.96pp，自身任务却+5.38/−16.13pp。E76固定同一段对话后，Gemma人物×可及性任务交互仍为−21.51pp [−37.63,−6.45]，32B为0 [−11.83,11.83]。

E77进一步显示：非Give中固定当前trait换社会回应来源，Get增加16.13/10.75pp；固定C换当前trait，Get均值差2.15/0pp，请求交付仍+10.75/+6.45pp。明确原后果可恢复大量行为，但Gemma Give71仍只有38.50/41.78%履约。角色在互动中形成的立场、当前用途选择与路径实现共同起作用，不能读作普遍执行能力差或二模块定律。

这与C04任务/合作共存、C05执行规则构成整体研究链，C06仍限定L2。[整体解释与强近邻](knowledge/persona-behavior/PROGRESS_SELECTION_RESEARCH_2026-10-16.md)。下一新增数据先对照[真实玩法/强执行基线](knowledge/persona-behavior/PLAYABLE_NPC_APPLICATION_AUDIT_2026-10-16.md)及[玩家证据](knowledge/persona-behavior/PLAYER_VALUE_EVIDENCE_2026-10-16.md)，关注玩家回应/兑现/改变协商条件后NPC怎样更新并落实选择，不机械追加提示或机制网格。

## 最近完成的实验

| 实验 | 设置与结果 |
|---|---|
| [E74](experiments/E74-physical-consequence-prediction-and-choice.md) | 117原作者Give图、2808预测＋2808新增执行。自产后果表提高原任务17.4–33.3pp，替换原生真值未额外恢复；预测答案、行动链呈现和真实选择分开解释。 |
| [E75](experiments/E75-native-retrieval-task-transfer.md) | 102原作者自然Get前提图、四任务族、4896分支。原角色/目标/规则保留；ready是原生Get后的反事实。推进与用途共同变化，任务改善有不同来源。 |
| [E76](experiments/E76-fixed-dialogue-and-native-access.md) | 精确固定E75 retrieval对话，只变执行初态，1224分支。人物×物理前提作用在固定历史下成立于Gemma，32B的资源取舍更稳定；不增加新指令或表格。 |
| [E77](experiments/E77-dialogue-and-assigned-outcome-execution.md) | 逐字C来源×当前trait、共同C下对称终局指派，4896记录含1224旧对角。非Give明确原后果物理履约Gemma80.65/77.42%、32B96.77/93.55%；指派请求后32B人物差仍+12.90pp。全部任务族/失败/原事件与物理口径并报。 |
| [E80](experiments/E80-responsive-player-and-grounded-execution.md)（完成） | 响应玩家＋共同selector/两执行器，200图4800episode。A−F请求Give +10.50/+12.83pp；绑定goal −9.00/−12.50pp。首次共同两步前提实现3/12、38/124→12/12、124/124，全图原goal仅+.17/+.50pp；选择、实现、最终归属分列。 |

三轮共29125实际本地调用、8928新增物理分支、2808预测上下文、208不同源图，3.83553观测GPUh/3.46147载入与推理GPUh，峰值4卡，0API/解析失败；本轮worker已退出。[合并成本与源图口径](results/E74_E76_round_accounting.json)。分支/调用不是独立世界，E76复用E75源图，E74与E75相交11图。

[结果清单](results/README.md) · [E74图](results/figures/E74_predictions_and_actual_actions.png) · [E75图](results/figures/E75_task_request_joint_outcomes.png) · [E76图](results/figures/E76_fixed_dialogue_access_effects.png)，均有PDF/SVG。

## 历史证据与明确冻结的执行线

- [E70–E77连续报告](PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)：E70–E73原文、E74–E76完整续报及E77/应用审视按次追加；累计36468新增分支/171626实际调用/18.83551观测GPUh，仍208不同源图，各期样本口径分别保留。
- [E69同图任务报告](PROGRESS_REPORT_2026-10-15_MATCHED_TASKS.md)：112同图任务配对及三来源案例的后续执行；不把三个案例当总体机制。
- [E67/E68](PROGRESS_REPORT_2026-10-15_RULE_EXECUTION.md)：执行规则恢复在独立41装备图复现，60其他资产图保留角色合作差；三向统一分流未成立。
- [E65/E66](PROGRESS_REPORT_2026-10-15_CONSTRAINT_PROBES.md)、[E63/E64](PROGRESS_REPORT_2026-10-15_POST_REVIEW.md)、[E50–62](PROGRESS_REPORT_2026-10-15.md)：三模型200图确认、角色分量、实体任务/合作、动态伙伴及白盒正负结果。
- [10月14日报告](PROGRESS_REPORT_2026-10-14.md)：原生系统恢复与旧实验。PCSP/MeltingPot小模型RL及追加诊断、校园1200帧全图漫游、只改conversation的总体人格实验、无实体flag任务均按用户决定冻结；历史文件保留，不按旧下一步恢复。E00/E02–E05不自动恢复。

## 接手入口

[AGENTS](AGENTS.md) · [LOCAL_AGENT_START](LOCAL_AGENT_START.md) · [EXPLORATION_ENTRY](EXPLORATION_ENTRY.md) · [E06基线卡](experiments/E06-persona-strategy-baseline.md) · [领域地图](knowledge/DOMAIN_ATLAS.md) · [人格—行为知识](knowledge/persona-behavior/) · [强近邻](knowledge/persona-behavior/RELATED_WORK.md) · [源码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md) · [痛点](PAIN_LOG.md)。源代码事实、实测、解释分别记录。

## 资产与执行边界

完整轨迹、输入输出、模型与checkpoint在`/home/xiang/.cache/game-npc-research/`，不进Git；E74–77 raw位于`runs/e74_*`、`e75_*`、`e76_*`、`e77_*`。源数据/driver/model pin、启动参数和成本在实验卡与manifest；统计重建脚本在`scripts/`。原生动作、错误与物理变化均记录，无脚本替模型完成任务。

环境优先现有Conda fgvd及deps overlay，模型复用HuggingFace缓存。用户授权节点资源按现场空闲使用，全时≤8卡、独立单卡/单节点优先，不干扰其他任务。NPC/伙伴/教师/判定核心链路全部本地；用户另授权Step5仅作数据并限定Token Plan，本轮0调用。人物表达、情境意图、真实执行分开；原子任务不是角色全部私人利益，不把抽象标签映射成唯一正确选择。
