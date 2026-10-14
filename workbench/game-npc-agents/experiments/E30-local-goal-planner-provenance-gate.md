# E30：本地目标计划到原生行动的来源准入（2026-10-14）

- **状态：** DONE
- **类型：** REPRO；补E29的来源缺口，非新机制实验。
- **对应：** C01 / P02；不新增方法idea。
- **问题（一句话）：** 原LLMPlanner生成、验证、fallback及revision是否真实进入本地NPC的物理行动，还是我们只观察到脚本日程下的decide？
- **设置：** 同pin agent-sandbox d7b872e…/同原world_data_boil.yaml、Nadia原persona/目标/recipe和author seeded memory；Qwen3.5-27B pin fc05daec…。首seed3001、单完整episode/80ticks/80总modelcalls。保留原simulate/LLMPlanner/importance scorer/LLMReflector/阈值/工具，planner和reflector由独立client context共享同本地模型；embedding仍原None lexical检索，_RETRIEVAL继承作者。源码不修改，formatter只实现原call_tool/工具协议，不把choose_action的提示套给planner或scorer。先CPU原planner/反射相关tests确认既有依赖，再单GPU成本gate；不扩到多角色/新场景/多seed矩阵。
- **读数：** 全组件call按actor/role/tool记录原消息/schema、成功/截断/成本；原out_planner_sources区分llm/static/mock，生成plan及原验证/日程commit/revision；原root parser成功和material delta；首次drink safe/raw计数、thirst变化。perform描述不能替recipe成功。失败token/尝试不删除，参数来源与实际source gate分开。
- **阳性对照：** 原作者tests确认plan未知place拒绝/empty→static显式回退/执行prefix保护及reflection证据；原boil CPU recipe有效且非法缺锅拒绝；typed工具模型输出进入原parser，非schedule commands强制。整个客户端只持有本地vLLM，没有provider SDK对象/云fallback。原role已存在或返回source stamp，未执行reflection只记0，不声称已恢复效果。
- **噪声地板 + MIE：** 单episode只判来源与可行性，无总体CI/性能提升MIE。E29与E30组件/seed均不同，不作为因果比较。0parser实际动作、static fallback、预算耗尽分别记gate不足，不能成为persona无效证据；完整来源可追踪且真实物理链可执行才补基线准入。
- **混杂审计：** 多组件恢复会同时改记忆评分/检索及计划，明确只作完整链准入；不据结果分摊机制。原目标并未新设，world/task/eval都不变；原importance threshold和检索不根据结果调。观察异常若可由普通目标/合法工具指令恢复，单独写后续卡，不当新科学贡献。上游已有memory/commitment修复与wish实验是owner。
- **决策表（跑之前写）：** 真实llm plan+legal material闭环→归档来源与未恢复范围，再选科学问题；static/parse/import问题→先修适配、不讲人格；合法perform但无材料结果→保留三层读数，先grounding解释；有跨目标/承诺的未解释现象→先两解释+最小控制卡，禁止直接训练。
- **算力预算：** 原CPU≤10分钟；1GPU首gate≤1小时，07:00后项目≤8GPU、现有fgvd/deps、0API，原raw不入git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
原source planner grounding及importance tests25/25通过，CPU2.01秒、0模型/API。首次本地生成式planner gate启动；所有组件原消息/工具及fallback保持。

单episode：seed3001/seeded，plan_source=llm，18calls（day1/hour1/minute2/score5/salient_questions1/record_insight3/decide5），原root4/5合法、5frames后首次safe drink1/raw0；11864输入/2148输出token，总wall220.80秒、0API。初始minute生成含未知Student Union，原已知位置验证删去这些stops、保留Houston Hall，未回退static；第一次make缺锅失败触发原revision，执行prefix保护保留current stop。真实get/activate/make/drink成功；reflection实际执行，不把“接入”当“有效果”。

[组件、plan及结果](../results/E30_local_goal_planner_gate.json)，raw cache/runs/e30_local_cognition_gate。反思把过去illness解释为当前计划变化的原因，该措辞也可能只是引用t0经验/原日程；不草率判事实幻觉，更未证明影响行为。单episode无总体CI，不与E29作性能比较，C01仍L1；下一步回到原自然玩家/NPC利益任务而非在此局部调planner。
