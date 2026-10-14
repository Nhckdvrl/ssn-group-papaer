# E51：承诺记忆的完成状态是否改变原生任务裁决（2026-10-15）

- **状态：** RUNNING；以下设置登记于模型运行之前。
- **类型：** PILOT，来自 E50 的具体异常，不是又一轮仓库排错。
- **对应：** I04、P12；不预设人设无效或记忆一定有害。
- **问题：** 同一承诺、原计划及游戏状态下，把未执行的承诺写成已完成，是否使执行器错误地认为承诺已履行并转回原任务？
- **线索：** E50 32B agenda-only→both 中 10/120 个 agreeable 分支失去请求终点，其中 8 个转为原任务。bag 与 flower 两例在实体尚未转移时生成了“I gave …”记忆。全体 40 图进入本实验，不按异常筛图。
- **竞争解释：** H_status 是完成状态误记；H_goal 是记忆重复原任务提升其显著性；H_choice 是原任务与社会承诺的正常取舍；H_ability 是执行能力。外在效应与内部机制分开验证。
- **设置：** 原 E50 固定 40 pilot 图；Qwen3.5-27B、Qwen3-32B，Gemma3-12B 独立家族参考；BF16、本地 nonthinking、temperature .7、512 tokens、seed 5101/5102/5103。原人物＋同一 firm/agreeable，所有涉及人物的提示保持一致。原生世界、原任务、请求与合法菜单不改。
- **干预：** 固定已接受的即时请求及下一计划为 request_command，这是受控承诺 fixture，不称自然接受率或总体 persona 效应。记忆条件为 none、pending、completed、pending+own-goal、completed+own-goal、pending+own-goal+state、completed+own-goal+state；另加一句直接执行 requested transfer 的强控制。主对比逐字固定为“I committed to {request_command}; this commitment is pending/completed.”，只改变状态词；own-goal 后缀逐字相同；state 两格加同一引擎事实：物品仍由自己持有且没有发生转移。保留两文本长度及 tokenizer 计数，后续自然时态释义复核而非只靠一个词对。
- **执行：** 原生 LIGHT 最多 6 个焦点行动，首次分配/消耗/装备结束；状态记忆 cue 仅在首次决策显示，随后以真实当前观测和行动历史为准。不给伪造完成 flag，不强迫人格对应唯一正确动作。
- **读数：** 每条件 request/own-task/other-allocation/unresolved 的实体 flag、首动作、至裁决步数；completed−pending 的配对图级差、goal 后缀交互、state cue 对 status 差的交互、两 persona 的效应差。三 seed 先在图内平均，图簇 bootstrap 95% CI；接受率由 E50 自然链路报告。
- **阳性对照：** 每图 CPU native 两条合法路径及互斥读数；具体请求指令测试执行能力；no-memory 揭示 fixture 下基线分配。解析失败和未裁决保留为独立结果，不算成功或自动排除。
- **噪声地板 + MIE：** 三 seed、配对采样种子，报告每种子与图簇区间；不设淘汰 bar。完成状态影响、目标提醒影响、状态纠错影响均会改变后续机制判断。
- **混杂审计：** 原 source graph/目标/观察/人物/seed/菜单固定；拟制记忆明确标 counterfactual。物品 give 可后续再转移、wear/wield 可撤销，因此读数是第一资源裁决而不是长程不可兼容。自然发生频率由独立 E50 轨迹测量，本实验仅识别状态表述的因果效应。
- **决策表（跑之前写）：** completed−pending 改变且 state cue 修复→完成状态/现实校验；仅 own-goal 后缀改变→目标显著性；两者均有→联合机制；具体指令也不执行→能力/协议；均无→保留负结果，回到自然渠道交互及社会承诺阶段，不人为制造 Gap。白盒后续需能预测这些实体读数，角度不作为机制结论。
- **算力预算：** 每模型约 0.5–1.5 GPU·时，独立单卡；总占用最多 8 卡。**实际：** 待运行。

## 结果

尚未运行。原 E50 的 POST-HOC 异常定位见 `results/E50_32b_memory_interaction_inspection.json`；它是本实验来源，不是本实验验证。
