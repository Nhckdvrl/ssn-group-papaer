# E12：恢复作者逐动作工具与原生重试（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（P03，强基线资格；非新方法）
- **对应：** C01 / P02 / P03；E10 single choose_action 不能代表源码首选的 call_tools 路径。
- **问题（一句话）：** 原生逐动作描述、可见参数枚举与原生同会话错误重试，能否解释当前不可执行选择及角色离岗？
- **设置：** agent-sandbox d7b872e…；原 Action Castle、作者 build_llm_game、工具 tools_for 与 run_tool_loop 均不改。Qwen3.5-27B fc05daec…，fgvd，128token/.7/nonthinking，intruder/feed，各 seed101/102/103。无 cognition/脚本fallback/云客户端。本地适配器将作者工具转成 name+arguments 联合 JSON schema，原生工具消息保留并转换为 tokenizer 支持的消息；约束格式，不替角色选择工具。普通一句指令对照：只操作当前可见目标，守护职责持续存在，但无人侵犯时可以等待；不规定唯一动作。两条件共12 episodes；先各一对测成本。
- **读数：** 原始工具call、首次/retry命令及合法性、错误内容、材料状态delta、原生玩家能否过桥/昏迷、角色位置与因果理由。表达/场景意图不混入执行线程；仍不把离岗直接定义人格失败。
- **阳性对照：** CPU工具loop对合法wait及非法目标→合法wait重试核验；保留作者工具描述/schema及 parser gate；工具失败必须回到同一会话且最多2轮。
- **噪声地板 + MIE：** 3seed全保留，episode为单位，描述范围，不以逐动作iid CI放大样本。只要普通强接口/单句能恢复，就降低先前缺陷的科学价值并转真实自然利益测量；样本不足时不升级新机制。
- **混杂审计：** tool adapter仍不是作者云SDK精确复现，native tool约束与额外文本封装记录；工具更长/token不同；原生prompt/世界/目标不改。额外句子不是数据中的规则，单列诊断条件，不能当独立NPC自然行为。合法性与策略/人物一致性分开。
- **决策表（跑之前写）：** 大幅恢复→P03是接口/说明解释；仍非法且常用参数正确→先审parser描述是否真覆盖合法条件、输入/思考预算；合法但策略异常→逐例提竞争解释，不自动判persona gap；角色控制只见engine自动动作→不得归因LLM。
- **算力预算：** 本地1GPU ≤1小时，既有模型cache/Conda；07:00东京起全项目≤8GPU。CPU控制≤1分钟。实际待填。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚已完成，以下为结果。

完成12episodes；总wall时间947.43秒（含启动；单GPU wall上界，不等于纯推理时间）。原摘要见results/E12_native_episode_summaries.json。

POST-HOC归因校对：parser对逗号命令有递归子调用，raw records数量不是LLM决策数量；用作者decision/tool parser重建并匹配所有root，零missing，raw不覆写。不能将子命令的successful和parent同计为两个LLM选择。以下只修readout归因，不改变世界规则或评分目标。

- native_tools: LLM root合法71/218，首次合法48/133，root material变化28；3seed与两原script全保留。
- native_tools_sentence: LLM root合法108/178，首次合法92/135，root material变化19；3seed与两原script全保留。

原生逐工具多数为generic arguments，实际本任务未声明typed scope schema，不能宣称已经获得闭集合法参数。普通一句“可见目标/无人侵犯可等待”显著提高首次合法（48/133→92/135），六episode合法率范围21.6–43.5%→50.0–73.0%。这说明先前能力/Persona失败故事被强提示部分吸收；没有训练方法贡献。状态材料变化较少不代表策略更差（守护职责可由等待維持）；玩家过桥又可由引擎饥饿规则决定。未升级科学claim。
