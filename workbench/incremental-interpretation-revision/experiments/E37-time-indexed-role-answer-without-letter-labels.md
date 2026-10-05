# E37：直接回答旧/当前/新事件的角色，无字母标签（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E34/E35旧事实NLI否定侧主导，追readout为什么失败，不从QA模板寻赢家。
- **问题（一句话）：** 自然who/whom回答能否分别取回被引用的初始角色、最终核实角色，并对新事件保留未知，而不经过NLI字母分类？
- **设置：** 原E34 other-actor passage192个历史（24×status2×prior2×final2）原字节，三个事前固定query：initial/current/new；current和new配base及E35同一句priority instruction，initial只base。独立Luna写24question fields后另两审全部完整passage/query672contexts；source-free96 baseline直接复用E29/E31已有role与new-event场景。共1056生成：current432/initial192/new432，GPU0/1/2独立。native no-thinking Qwen3-8B FP32 seed0 batch8，greedy max_new_tokens48，短语回答，不显示选择标签或示例。全输出留cache，另两Luna盲于gold逐条语义判答，保留cap/invalid/multiple/unknown，不能关键词匹配当gold。
- **读数：** 每family两source平均paired bootstrap10000/seed20261005/95CI；current/initial/new correct、回答方向source/ref/unknown/explicit-none/other/unclear，按status×conflict×finalrole×base/priority；old current与initial joint-correct（独立prompt，非同一次对话）和current/new joint；source-freecontrol。报告与原NLI的具体不同但不称pure label causal estimate；原NLI/current问题含义与输出格式同时变。
- **阳性对照：** source-free old role retrieval，source-free new U、history initial description内容检索；current两角色互补都报，不把平均50当丧失全部理解。
- **噪声地板 + MIE：** n12非1056独立n；审计不确定输出完整保留并单列，不筛选回答正确源。固定greedy无随机seed选择；E23曾出现审计不一致，此次先独立定问句语义，再分割输出语义标注，异常响应另加交叉审。
- **混杂审计：** initial提问只问描述内容，不声称hypothetical发生。current查询已明确final account，有retrieval cue，所以成功不证明raw未提问隐藏状态；new问题who-if-any不强假设已知患者。direct output取回事实与预测反向可共存但不是统一双系统机制。无representation/probe/训练/模型下载。
- **决策表（跑之前写）：** current/initial皆高、new以未知答 → NLI低分不能当不可修订，关系预测应独立解释；复核真实history的行为来源而非卖generic knows/use gap。current仍追initial或explicit-none → polarity/priority是真实role-retrieval干扰，继续分正负role correction，不能称修订成功。source-free失败 → 先审问题/短语回答材料why。R8只改善特定方向 → 完整报告不挑赢家。上述均继续同一I01，核心候选的event/action边界由E31/E33/E36支持，不进入论文。
- **算力预算：** 三单卡已有venv，≤.30 GPU·h；**实际：** 待填。
- **命令：** `time_indexed_role.py build/adopt/run`；后续独立response审计与paired分析。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

## 跑前材料审计

24source问句由独立Luna构造；另两独立审查全部672contexts（1056mode tasks），passage/question全部hash匹配，clear/eligible1056，外部语义标签与proposed1056一致。审计共source216/reference216/unspecified240contexts，语法acceptable504/marginal168，未选删源。base与priority同context共享语义gold；初始问题只问引文内容、new问题不把未说当无人。详见[D0](../results/D0-E37-query-audit.json)。未开始生成。
