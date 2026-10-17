# I04：人物、自身目的与真实NPC选择

- **状态：PROMISING。** 用户2026-10-15认可研究张力；工作台PROPOSED、C01–C06等级保持，论文正文暂缓。2026-10-16用户要求本轮结束后暂停，E85已完成，无待运行队列；恢复须用户明确指令。
- **对应：** P12；C02／C04／C05／C06限定L2，C03发现性L1，以[CLAIMS](../CLAIMS.md)为准，不由本卡升级。
- **问题：** 有自身身份、目的和社会关系的NPC，面对玩家请求、真实行动和新方案，怎样选择、修订或拒绝，并经合法动作产生后果？
- **候选认识：** 人物立场、互动中形成的回应、行动前提和资源用途共同形成真实行为；任务分数不能直接反推人物有用／无用、潜在能力或私人目标权重。这有实证支撑，尚非统一内部机制或已验证新方法。

## 来源与整体增量

- **来源：** P12；E14／E22的LIGHT目标与台词、E42焦点强LLM参考、E45–E49校园后续的成功与矛盾。用户审计推动一致人物与实体后果测量，并纠正将双信道、TCE／SFR或“迎合自毁”钦定为故事。E42不是双角色对话博弈；校园局部改写不作总体persona效应。源事实与纠偏见[整体报告](../PROJECT_PROGRESS_REPORT_2026-10-16.md)、[E22](../experiments/E22-native-storage-access-belief-control.md)、[E42](../experiments/E42-native-llm-persona-utility-reference.md)、[E45](../experiments/E45-natural-persona-and-goal-adoption.md)及[E49](../experiments/E49-cross-role-commitment-causality.md)。

整体增量应来自对**角色目的、社交互动与真实实现怎样共同组织选择**的新理解或改进。不是首次发现言行差异、长程互动、失信或steering，也不要求每个组件首创。分析／测量、机制或方法的形态由证据决定，不预选训练／架构／损失，不用自设bar或某个区间自动去留。

## 证据与解释范围

| 当前认识 | 证据入口 | 范围 |
|---|---|---|
| 一致角色立场改变真实行动 | [E55](../experiments/E55-independent-native-role-confirmation.md)：200独立图／三seed，请求交付差6.7–13.7pp；E58只性格句仍有效 | 非纯Big Five；友善多给物只是可靠起点 |
| 当前任务与角色合作差可共存 | [E63](../experiments/E63-native-dependency-and-explicit-priority.md)／[E68](../experiments/E68-clean-reserve-rule-predictions.md)：独立其他物品图保留人物差，任务Gemma约81%–82%、Qwen约99% | 非数学独立／零代价，其他物品非完整人物的无价值资产 |
| 执行规则仍改变相同上游后的实体后果 | [E66](../experiments/E66-native-action-logit-competition.md)→[E67](../experiments/E67-stage-rule-physical-cross-swap.md)／E68独立图确认，C05限定L2 | 采用原计划和重新找回目标并存，未识别神经病因 |
| 推进与用途共同影响任务分数 | [E70](../experiments/E70-native-goal-request-and-execution-preconditions.md)–[E77](../experiments/E77-dialogue-and-assigned-outcome-execution.md)：前提、固定回应、当前trait及明确后果对照，C06限定L2 | 非严格二阶段分工／全中介／行为守恒；Get多非更重视自己 |
| 可靠执行落实当前选择，但不替代目的判断 | [E80](../experiments/E80-responsive-player-and-grounded-execution.md)：共同两步后果的前提实现恢复到100%，全图goal增量约0.17／0.50pp | 下层可重新取舍；原子失败可伴随支付、腾手和取得宝物 |
| 普通系统已有实际合作与响应新请求的能力 | [E81](../experiments/E81-authored-cooperation-and-partner-response.md)／[E84](../experiments/E84-independent-goals-and-alternative-cooperation.md)有帮助、借用、拒绝和替代；[E85](../experiments/E85-partner-performance-and-revision.md)Qwen新返还+30.56pp | 交付／取得／终态不等于完整目的；E85未干预persona或证明原方案失效 |

E57／E64的消费、付酬与敌对伤害／死亡均保留；E82只为CPU物理见证，E83为同一论文角色两路径的明确重建，不补成跨游戏总体确认。全部数字、成本、曝光及原始来源按原卡／最终JSON核对，不在本卡复制流水账。

## 竞争解释与当前未解问题

原H1–H5保留为解释类别，不是已经找到的五个模块：

| 类别 | 可解释什么 | 已有约束 |
|---|---|---|
| H1：角色／目标信息未有效保留 | 未行动或偏离原目的 | E56普通阶段说明解决了部分问题；事实问答不直接证明行动中遗忘 |
| H2：信息可用但目标优先级／合作价值不同 | 保留、转移、拒绝、取得前提后转向自用 | E63明确优先有效；低Give不自动错误，原子goal不是全部利益 |
| H3：抽象立场与具体动作／对象／接收者绑定不同 | 粗动作与参数、任务族作用不同 | E58弱责任句非明确规则；E62／E69未给统一词位／动词机制 |
| H4：路径采用、执行前提与互动机会 | 有可行计划未采用、已释放资源却未接取 | E70–E74普通支持、E80可靠技能解释部分损失；未尝试非原生执行失败 |
| H5：近期台词／请求改变状态与目标绑定 | 历史来源、承诺与当前立场参与后续 | E51／E59状态、E60／E61同历史及E77固定C有边界，未识别纯模块中介 |

当前关键关系是：**同一目的下，玩家按原办法实现前提、用合法替代实现同一前提、原办法失效但另有路径时，NPC能否保持目的并实际调整方案？** 目的相容的取舍，与近期话语／局部物品／双方实现过程主导，对此可作不同预测，也可能共同作用。E85只改变转移、说法和新请求，尚未裁决；这不是已注册队列。

## 领域尺度判断与下一轮建议（2026-10-17，只设计，未运行）

**现有结果最有价值的整体认识：人物控制的行为效果取决于“角色目的—他人请求—共同动作前提”的关系。** E55给出真实行动效应；E63／E68说明保护当前任务可以保留其他合作差；E75同一立场同时提高Get与请求交付而任务方向不同；E80可靠实现不替代用途判断；E84／E85已有实际合作和修订。整体可形成对人物控制／任务评价的实证认识：人物并非只改台词，其效果也不能从一个终局分数读出。不同任务下的异质性有可检验的结构来源，不是统一神经机制已被识别。

**最值得继续的是：玩家改变合作的实际作用后，NPC该坚持什么、该改变什么？** 同一角色既要保留自身目的与职责，也可能负有已接受承诺；具体物品、提供者、分工和实现路径则可能变化。这直接关系玩家能否用非预编写办法解决问题、是否被要求重复无用劳动，以及NPC能否拒绝越界却提供可行支持。物理上达到同一结果不自动产生同一社会义务；已经接受的回报也不会因为NPC目的已达而自动消失。当前数据仍未把这些关系区分。

近邻要求我们继承动态grounding、条件履约、可靠路径和及时重规划，见[合作定位](../knowledge/COOPERATION_AND_GOAL_POSITIONING.md)及[目标谱系补核](../knowledge/COOPERATION_AND_GOAL_POSITIONING.md#field-review-2026-10-17)。核心增量不能只是“换目标会失败”“提醒后恢复”或“调用重规划”。有价值的整体目标是解释角色何时应保持目的／承诺、何时能接受替代／改约，并检验这种解释能否跨任务结构预测实际后果。

具体任务、路径、竞争解释、主对照、读数与结果决策见[合作路径设计](../experiments/COOPERATION_PATH_DESIGN.md)，全量来源／SHA见[只读索引](../results/COOPERATION_PATH_SOURCE_REVIEW_2026-10-17.json)。不再以百级数量为目标：源核查得到LIGHT三方转交51份NPC任务／43图、装配5任务／5图（合计47图）；另有12个Minecraft原制作配置作能力参照。142个原转交配对共享这些世界；旧串行路径有原生见证，新代送／装配路径只读源码支持，尚未执行。合格来源和曝光范围须在恢复后冻结，不造场景、改世界或拿分支充独立N。

本次设计特别区分原作者“由本人做某动作”的G、实际收件／包含的P与有效社会义务。代办导致G不计分是已知定义，不是模型机制；P已达也不自动取消赠礼署名／回报。主设计保留完整原人物和目的，不把相同物理结果强行定义成全部利益相同；普通事实重审、及时重新决策及可靠实现均为强参照。设计文档保留所有结果怎样改变解释，不预定训练、内在病因、通过bar或新方法。

当前只有静态来源核对与设计，没有E86／新队列，没有导入或运行CPU引擎、生成模型数据、推理API或GPU实验；暂停继续有效。

## 负结果与撤销解释的索引

| 不再成立的强解释／测量 | 保留证据 |
|---|---|
| 局部conversation改写等于完整人格，阻止agenda便得到承诺总效应 | E45／E49不一致、[E48](../experiments/E48-conversation-plan-update-ablation.md)仍有记忆入口，不作总体persona／总中介主张 |
| 不行动等于人格遗忘；完成时态等于物理完成 | [E56](../experiments/E56-native-state-belief-and-action.md)阶段结束恢复；[E59](../experiments/E59-fixed-history-state-invariance.md)状态标签非真值 |
| 性格普遍压倒明确规则，必然自毁 | [E58](../experiments/E58-disposition-and-priority-components.md)第二句只是责任态度；E63明确规则有效，27B资产包也可有效 |
| 已定位统一内部人物方向 | [E52](../experiments/E52-dialogue-goal-binding-causal-probe.md)独立N=1；[E62](../experiments/E62-native-recipient-causal-diagnostic.md)单层donor无稳定跨模型定向效应，随机／sham与阴性保留 |
| 统一否定安全瘫痪／熵增／三向分流；重复block解释全部损失 | [E65](../experiments/E65-constraint-scope-and-permission.md)许可异质、E66无统一熵增、E67反馈未恢复主要损失、E68部分预测反向；[逐项读数](../results/E68_prediction_readout.md)保留 |
| 后续缺失全是动机压制，普通知识无用 | [E69](../experiments/E69-matched-task-and-motivation-window.md)共同窗口仍缺失、知识仅部分恢复；已知图／同名物敏感性与原主表并报 |
| 问答错误直接说明行动信念；推进全由对话中介 | [E74](../experiments/E74-physical-consequence-prediction-and-choice.md)真值未额外恢复；[E75](../experiments/E75-native-retrieval-task-transfer.md)／[E76](../experiments/E76-fixed-dialogue-and-native-access.md)状态作用依模型；E77 Give反例和指派失败保留 |
| 最终交换便是按约继续；初始假声称组给物便是一直受骗 | [E64](../experiments/E64-native-reciprocal-goal-negotiation.md)N=9不推总体；[E83](../experiments/E83-npc-quest-receipt-and-reward-baseline.md)提前／重复奖励与拒借并存；E85补交／自取／偷取／释放接取与216份不稳定问答保留，不作内部信念／persona新因果 |

## 近邻与接手边界

自述效度、粒度／同会话、叙事／动作锚点、策略steering已有Personality Illusion、Rethinking、Story Shapes、Persona Vectors；未来意图／记忆干预已有PM-Bench、PASB等邻域。Dragon／CDT／KNUDGE已有动机—对话—行动谱系。When Identity Overrides Incentives已研究人物×收益与收益优先提示；Dialogue is the Plan关注grounding／repair，Persona Circuits是内部干预近邻。CT-Bench、TradeCraft、ContractSim已有私有目标、承诺／拒付与强状态支持；GenCoord、FACUL／PUBG已有可靠技能，GAIA有冲突目标协商，CoopEval有序贯合作。整体问题是角色身份／目的怎样与开放玩家行动、可变实现和持续后果相联系，不靠RPG外壳／一般失约改名，也不逐组件压缩增量。

阅读／源码与应用范围集中在[合作定位](../knowledge/COOPERATION_AND_GOAL_POSITIONING.md)、[应用审计](../knowledge/PLAYABLE_NPC_APPLICATION_AUDIT_2026-10-16.md)、[玩家证据](../knowledge/PLAYER_VALUE_EVIDENCE_2026-10-16.md)。成功、合理拒绝、普通控制与负结果都是证据，不预定steering／SFT／LoRA／GRPO／新协议。历史过程与人审见[整体报告](../PROJECT_PROGRESS_REPORT_2026-10-16.md)、[实验卡](../experiments/README.md)及[14日](https://github.com/Nhckdvrl/ssn-group-papaer/blob/caedd5c8/workbench/game-npc-agents/logs/2026-10-14.md)／[15日](https://github.com/Nhckdvrl/ssn-group-papaer/blob/caedd5c8/workbench/game-npc-agents/logs/2026-10-15.md)／[16日](https://github.com/Nhckdvrl/ssn-group-papaer/blob/caedd5c8/workbench/game-npc-agents/logs/2026-10-16.md)日记；当前保持暂停。
