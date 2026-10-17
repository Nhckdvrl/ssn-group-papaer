# E29：原生生成式NPC物理目标闭环准入（2026-10-14）

- **状态：** DONE（单episode准入）
- **类型：** REPRO / 强基线恢复；非新idea。
- **对应：** C01 / P02；E07–E14后的更完整作者NPC系统。
- **问题（一句话）：** agent-sandbox的生成式NPC能否由本地模型决定动作，在原作者boil任务完成多步骤物理后果，并保留实际决策/脚本/执行归因？
- **设置：** agent-sandbox pin d7b872e…同仓godot-generative-agents Python backend，Godot只为viewer不需要GPU渲染。原world_data_boil.yaml与作者boil_from_memory设置（thirst_rate1/threshold2、seeded aversion/无memory、原recipe/stove/物理/goal不改）；hard作者场景只作CPU可行性和来源审计，不为结果自行搬场景。先原source CPU tests prove合法boil/drink/raw sickness、invalid拒绝和硬场景可解；author ScriptedPennBrain只作CPU管线不当LLM。随后Qwen3.5-27B本地原structured工具，原observe/decide→原parser→原世界/drink计数，先seed2901单完整episode/max80ticks/40modelcalls。真实LLM只接管decide，planner/reflector/embedding各调用来源显式记录，优先原none/mock默认，没有SDK云fallback；此阶段非完整GPT/Claude GA复现。若首gate有实际动作且成本可承受，才seed2902/2903与无memory原对照。异步deadline/late-answer源码另审，不自动施加延时制造现象。
- **读数：** 原author classify_outcome来自drank_unboiled/drank_safe计数，不靠台词；原逐root动作是否合法/material变化/来源(decider,schedule,engine)、NPC所见观测与目标、frames/events/memory、LLM token/latency/失败重试。首drink即停止：raw后再boil不算boil-before-drink，继承author协议。没有完成不预定为persona错误，先区分原schedule context/目标机会/工具能力/预算。
- **阳性对照：** 原source CPU自然recipe变化且stove在scope；非法动作不假称成功；hard原source正控制不冒称LLM探索成功；LLM不能被mock authored command/fallback代替。所有LLM请求在本机模型，reflection/embedding默认none不计未执行能力。
- **噪声地板 + MIE：** 原mock为deterministic源控制、真实1episode仅gate无总体CI；原3seed全保留。只语言/plan变化没有材料后果→不升级可行性；failed import/adapter先修不能叫NPC行为失败。进一步实验必须先出现竞争解释。
- **混杂审计：** 原上游已有aversive-memory/boil/hard及deadline测试，均已有source owner；CPU脚本demo命令不是科学阳性。live与offline actor/map/cognition路径不能混；旅行是真实BFS tile297ticks且行走不调用model，不能把tick预算缺口误判认知。生病/恢复属于世界规则，回报解释尊重source当前需求与经验。
- **决策表（跑之前写）：** CPU/强local闭环过→看成功/失败真实轨迹再起题；普通提示/target grounding恢复→承认旧解释；script/scheduler导致→只校正归因；有原生未解释的目标/人物/时间关系→新卡最小区分，不先强上RL。
- **算力预算：** CPU≤30分钟，现有fgvd/deps；首模型1GPU≤1小时，07:00后项目≤8GPU，0付费API。原raw/cache/model不入Git，不新建工作台。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
原source CPU tests16/16通过，5.61秒、0GPU/API（cache/runs/e29_cpu_gate.log）。包括hard场景源控制；mock不能探索不算模型失败。首seed2901/seeded原boil单episode Qwen27B启动；沿用原per-action tools、MockPlanner与none reflector/embedding。per-action-only client不暴露call_tool，因此原importance scorer未接入，明确配置限制，不偷称完整Haiku复现。

首episode完成：seed2901/seeded，原actor Nadia Okafor；6次本地model调用，原root parser 5/6合法，15 frames后首次饮用为安全水，raw drink为0、safe drink为1。6779输入/374输出token；总wall686.99秒（启动/I/O占主要部分），模型调用合计28.78秒，0云API。完整链路为 `perform boiling water` → `make boiled water`拒绝（缺持有水锅）→ `get pot of murky water` → `activate stove` → `make boiled water` → `drink pot of boiled water`。首个perform只设置activity，并未煮水；真正recipe物理变化在turn13，不能以台词或activity判任务完成。

校对：source parser的failure字段在成功后保留上次错误，本次按success和state delta读合法性，原raw不覆写。上游usage ledger未接入本地adapter，不能用其“0调用”展示成本；本地model_calls记录为准。MockPlanner决定已有日程与decide间隔，真实模型决定上述动作；没有importance/reflector/embedding的能力证据。

[汇总与配置](../results/E29_native_generative_npc_gate.json)，raw为cache/runs/e29_qwen35_gate。当前没有需靠另两个seed或无memory矩阵区分的未解释现象：作者原任务已经覆盖memory作用。先审完整角色目标/交互任务，再决定下一卡；不把重复准入当新科学实验。C01仍L1，新科学增量0。
