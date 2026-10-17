# 痛点与解释边界

本页按稳定ID记录实际问题、竞争解释和证据，不作逐轮进度日志。**当前保持暂停，不由历史问题启动实验或改变状态。** 整体脉络见[项目报告](PROJECT_PROGRESS_REPORT_2026-10-16.md)，过程见[实验卡](experiments/README.md)与[日期日志](https://github.com/Nhckdvrl/ssn-group-papaer/blob/caedd5c8/workbench/game-npc-agents/logs/2026-10-16.md)。原有11个痛点ID保持不重排。

## 稳定痛点表

| ID | 痛点与独有来源 | 当前认识／竞争解释 | 原证据与边界 |
|---|---|---|---|
| <a id="p01"></a>**P01** | 依赖／运行失败与人物行为混淆。Action Castle缺prompty／aiofiles，PCSP旧PettingZoo AgentSelector失败；Qwen权重能加载但flashinfer warmup缺PATH中的ninja | 工程恢复、CPU正控与真正推理分开，导入／warmup不是persona失败 | [E07](experiments/E07-native-actioncastle-closure.md)／[E08](experiments/E08-pcsp-gradient-and-protocol-audit.md)保留版本和失败；本地资产见BASELINES，不再开环境QA线 |
| <a id="p02"></a>**P02** | E07 seed101的20次决定中11次合法；troll已在岗位却说返回并离开，ghost离开后因黑暗返回失败 | 观测／语法／后果信息、地名与位置整合、运行模式／预算、全局narration与不在场历史均可解释；非总体persona失效 | E07／[E09](experiments/E09-viewpoint-grounding-control.md)；单seed只定位，自动吃鱼另作引擎归因 |
| <a id="p03"></a>**P03** | 位置probe不等于动作contract。E09 Gemma位置9/9而合法动作3/9；换说明后位置可对、动作却0/9且含不在场target | 前缀literal、probe格式、对象scope和动作语义需分开，知道地点不等于能执行 | E09／[E10](experiments/E10-strong-native-action-interface.md)；原per-action说明和可靠格式是普通基线 |
| <a id="p04"></a>**P04** | E14原目标能执行，但独立intent／action常不同，含多种emote／speech替代 | 两次随机draw、问法／同会话priming、粒度／载荷可解释；E15的I/A相对A/A未超抽样地板，差异本身非gap | [E14](experiments/E14-light-author-goal-npc-episodes.md)通信初版错误与全量修正、[E15](experiments/E15-intention-action-sampling-floor.md)噪声与fork对照均保留 |
| <a id="p06"></a>**P06** | PCSP训练混合读出η与投影φ，no_consist移除不止一条路径 | φ塑形、政策原有信号而η未读出、state／needs信号都需区分；冻结政策只训练读出可改善retrieval，不能直接归因政策形成 | [E17](experiments/E17-pcsp-frozen-policy-readout-control.md)／[E25](experiments/E25-corrected-baseline-gradient-route-pilot.md)／[I02](ideas/I02-causal-separation-of-role-control-and-readout.md)；作者已有梯度及外部trait负结果，旧执行冻结 |
| <a id="p07"></a>**P07** | E20的36局／70合法动作无speech，说话与物理行动争用机会 | 共享资源／饥饿、单动作交替的先手、对话规范与动机未正交；无speech非无社会能力 | [E20](experiments/E20-native-two-character-resource-episodes.md)／[E21](experiments/E21-native-dialogue-action-protocol-control.md)；Dragon已有speech/action分解，scheduler不冒充人物新机制 |
| <a id="p08"></a>**P08** | bird把worm称幼鸟食物并放开放nests，fox合法取走；短期eat worm、中期feed young with nut | 合理长目标／威胁应对、规范归属误作权限、自己的台词priming／对象绑定、抽样或接口均可解释。E22未支持权限投射，目标提醒9/32→1/32，事实提醒未恢复动作 | [I01](ideas/I01-normative-ownership-and-mechanical-access.md)／[E22](experiments/E22-native-storage-access-belief-control.md)：负向字段连neutral正控失败，联合forecast降级；Can与Will分开 |
| <a id="p09"></a>**P09** | 原500行编码有480行末列pool取padding query，同文随batch伙伴长度改变 | padding信号、旧政策对训练编码敏感、多角色变码互动均影响解释；正确last-nonpad是已有算法，Full／No无统一收益稳健性排序 | [E23](experiments/E23-persona-encoding-context-invariance.md)／[E24](experiments/E24-native-policy-utility-under-encoding-context.md)／E25；修pool非创新，旧资产／负结果保留，执行冻结 |
| <a id="p10"></a>**P10** | train400为20种BF配置×20身份，held非C背景另5类，无精确单C配对；设计满秩非非线性组合能力 | 训练／投影路径、属性覆盖不足、目标与身体／状态机会相关均可解释；Full局部C更强与整体return更低并存，增强／绑定无统一排序 | [E34](experiments/E34-full-budget-corrected-baseline.md)、[E37](experiments/E37-matched-role-edit-functional-geometry.md)、[E39](experiments/E39-cross-role-direction-transport.md)、[E40](experiments/E40-preference-control-and-need-dynamics.md)、[E41](experiments/E41-interventional-persona-coverage.md)／[I03](ideas/I03-interventional-coverage-for-functional-persona-control.md)；surface v1作废与有效全预算均保留，不恢复RL |
| <a id="p11"></a>**P11** | E35 seed3502 turn787/call77输入有warm／precise、Irvine与6条记忆，却无时钟／10:00讲座；frame967离开 | 时钟不可见、责任检索／显著性、合理教学重排或执行gate均可解释；3503错地点计划后恢复共同Irvine活动的正例保留 | [E35](experiments/E35-original-three-npc-goal-loop.md)／[E44](experiments/E44-natural-duty-context-restoration.md)：旧v1未覆盖fallback，不作统一事实证据；校园漫游冻结 |
| <a id="p12"></a>**P12** | 用户审计指出把源码管道／QA当机制、独立场景不足、局部persona不一致；后期又过度细分物品索要 | 当前困难是角色能否围绕自身目的理解玩家真正做过的事、形成／修订可行方案并执行；目的取舍、近期语言／对象、路径采用与双方实现未完全分开 | [I04](ideas/I04-commitment-conflict-stage-arbitration.md)、[E84](experiments/E84-independent-goals-and-alternative-cooperation.md)／[E85](experiments/E85-partner-performance-and-revision.md)；扩大N／提示格／统一失败名不能替代研究判断 |

## P12当前未解关系

普通系统已有实际交换、借用、帮助、拒绝和响应新请求。关键未解的是：**同一目的下，玩家用合法替代满足前提，或原办法失效而另有路径时，NPC能否理解贡献、保持目的并落实调整？** 它面向玩家未预编写的解决办法，同时允许NPC有自己的立场；当前只保存问题，不生成队列。

目的相容的取舍，与近期话语／局部物品／双方衔接主导可能并存。原子goal、Give、曾取得、终态和完整利益不合成一个正确合作分；前期人物干预与E81–E85自然互动分开，后者不补成新persona因果证据。

## P12负结果与撤销解释入口

| 需要保留的边界 | 证据入口 |
|---|---|
| 局部人物／渠道和小样本被过度解释 | [E45](experiments/E45-natural-persona-and-goal-adoption.md)／[E49](experiments/E49-cross-role-commitment-causality.md)不作完整persona；[E48](experiments/E48-conversation-plan-update-ablation.md)只阻agenda未清记忆，非承诺总效应；[E50](experiments/E50-commitment-decision-snapshots.md)重构一致干预 |
| 普通指令／弱责任句形成虚假遗忘或自毁故事 | [E56](experiments/E56-native-state-belief-and-action.md)阶段结束恢复；[E58](experiments/E58-disposition-and-priority-components.md)弱责任句不等于优先规则，[E63](experiments/E63-native-dependency-and-explicit-priority.md)明确规则有效 |
| 小样本持有／交付被当完整利益 | [E57](experiments/E57-native-private-goal-interaction.md)／[E64](experiments/E64-native-reciprocal-goal-negotiation.md)消费、付酬、敌对伤害／死亡与通信控制保留；E64仅9图，双Give非总体互利 |
| 否定过载／熵增／防卫分流及纯接口解释未成立 | [E65](experiments/E65-constraint-scope-and-permission.md)／[E66](experiments/E66-native-action-logit-competition.md)、[E67](experiments/E67-stage-rule-physical-cross-swap.md)／[E68](experiments/E68-clean-reserve-rule-predictions.md)保留许可异质、反馈未恢复及反向结果；[逐项预测](results/E68_prediction_readout.md)不删阴性 |
| 知识、选择与作者后续目的不相同 | [E69](experiments/E69-matched-task-and-motivation-window.md)共同窗口仍缺失、知识只部分恢复，绑定敏感性另报；[E70](experiments/E70-native-goal-request-and-execution-preconditions.md)／[E71](experiments/E71-unsolicited-authored-goal-baseline.md)／[E72](experiments/E72-native-candidate-feedback-and-goal-execution.md)／[E73](experiments/E73-equal-initial-native-feedback.md)保留前提、请求方向与反馈控制 |
| 测验／推进／终局指派未给统一潜在能力或二模块机制 | [E74](experiments/E74-physical-consequence-prediction-and-choice.md)真值未额外恢复；[E75](experiments/E75-native-retrieval-task-transfer.md)／[E76](experiments/E76-fixed-dialogue-and-native-access.md)状态作用依模型；[E77](experiments/E77-dialogue-and-assigned-outcome-execution.md)Give反例、879未履约构成及未Get无源Get拒绝保留 |
| 实现支持或终局交换不自动是目的延续 | [E80](experiments/E80-responsive-player-and-grounded-execution.md)技能支持当前用途；[E81](experiments/E81-authored-cooperation-and-partner-response.md)／E84有合法替代与拒绝；[E82](experiments/E82-minecraft-original-cooperation-baseline.md)只为CPU见证；[E83](experiments/E83-npc-quest-receipt-and-reward-baseline.md)提前／重复奖励与拒借并存 |
| 收到／声称／改约非普遍合理回报或内部信念 | E85真实转移未统一提高GiveY，终局含后补交、自取／偷取、释放／接取；216问答两字段不稳定，改变的是新请求而非世界失效；[独立统计](results/E85_statistical_independent_review.json)及两模型完整原生审计／结果保留 |

工程兼容、协议错误、降级／作废、同名替代物、消费同义事件、失败和成本继续保存在原卡／最终JSON／[CLAIMS作废记录](CLAIMS.md#作废降级记录)。I04另保留E52／E62白盒阴性索引。不删除证据，不据阴性关题；旧RL、漫游、细标签或无回路patch不自动恢复。本页不再逐轮写“最新运行中／已完成”。
