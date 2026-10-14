# E48：新增承诺的显式计划修订是否传递人物效应

- **状态：** RUNNING；真实 outcome 路径 CPU 资格已通过，两角色完整后缀启动。
- **类型：** 原生机制辨识，不预定新方法。
- **对应：** P11，E45–47；中心仍为人物如何影响真实目标选择／行动。
- **触发：** 原对话角色的一处描述改变新承诺与之后真实行程，executor/planner的人设始终原样；真实计划进度和512预算后仍有两个角色的任务选择差异。需要区分显式计划渠道与对话记忆／伙伴反馈。
- **竞争解释：** H1差异主要经conversation-triggered plan revision；H2保留下来的实际对话、意图记忆及伙伴行为已足够改变动作；H3其他clock/failure触发再次修订计划。读出／分数本身不回答这些。
- **设置：** 继承E47 source3502/787完整prefix、原27B、真实进度／两角色指令／教授两路512budget。仅787后教授CONVERSATION原因的maybe_revise_plan返回原PlanRevisionResult()，不调用其planner。其他trigger、其他NPC原样。真实speech、outcome原输出、relationship note、源高importance INTENTION/PLAN memory均保留。world／parser／clock／目标评价不改。两个新完整1200frame后缀，与E47两个原机制格配对读。
- **范围：** 只消融显式conversation计划修订，不称所有目标／内在欲望被移除。聊天和意图记忆仍能影响decider或后来的其他trigger；这些正是竞争渠道。源#778/#829已实现该机制，发现这段代码不是我们的创新。
- **读数：** 每次被阻止修订的actor/step/原因/原承诺、原计划hash／指针、memory写入、其后来自其他原因的计划、真实角色对话／承诺／合法动作／世界行程。所有格／失败／无触发都保留，不规定正确目标。
- **阳性对照：** 同787frame/source77请求；上游真实apply_conversation_outcome使用CPU固定outcome，确认PLAN intention仍写入而agenda不改；限定条件外调用原函数；完整cassette独立1200重放。数值／实现资格不当科学bar。
- **噪声地板 + MIE：** 单发现性case、局部角色指令，原采样seed续起、调用数量后续可不同。不估人口CI，不设科学阈值；需要后才跨角色／场景。无效果也能改变渠道判断。
- **混杂审计：** 省去planner调用会影响后续call-index种子和计算成本，明确不是全后缀同随机数；真实口头承诺与内部agenda可能不一致，是agent机制干预而非基线失败。伙伴与意图记忆保留，不能声称纯personality/value或全部goal mediation。
- **决策表（跑之前写）：** 行程差异大变→显式agenda渠道贡献；差异保留→读memory/伙伴/其他trigger；无被阻止事件→本case未测试H1，保留事实。结果只改变机制理解，不因旧机制owned关闭研究，也不把普通ablation当新方法。
- **算力预算：** CPU前缀和真实outcome路径资格后，两已空闲单卡各完整后缀，现有fgvd/deps/cache，0API，总≤8。不为整齐扩大矩阵；raw cache/runs/e48_*。

## 结果
CPU 原生前缀 787 帧、77 条模型响应逐字复现；第一条后缀请求与原记录一致。真实 `apply_conversation_outcome` 路径用固定 outcome 验证：关系记录与 PLAN 意图记忆均写入，显式 agenda 保持原样，仅一次目标 conversation 修订被阻止。资格文件位于 `runs/e48_cpu_source_outcome_control/cpu_prefix/actual_outcome_control.json`。这是实现资格，不是科学效果。
