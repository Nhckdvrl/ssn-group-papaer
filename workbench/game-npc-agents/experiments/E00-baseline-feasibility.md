# E00：自然 NPC 基线/评价可行性门槛（2026-10-13）

- **状态：** PLANNED。未运行，实际 GPUh = 0。
- **类型：** REPRO / environment and measurement gate（不是新颖性实验）。
- **对应：** D1–D4 驻留交付；RESEARCH_TERRITORIES A/B/C 的基线选择；尚无 C## 和 P##。
- **问题：** 哪个开放的游戏 NPC/近邻系统可以复算角色观察→合法动作→世界状态变化，且原论文的标准测量具有足够分辨力？
- **设置：** 核查 KNUDGE/CDT/NCP-Bench 的源码、license、自然游戏案例、数据/运行依赖、官方评价与模型 API；按证据与成本决定优先复现一项。GPU 运行前必须补全 upstream SHA、model revision、scene IDs、seed、n、配置和命令；**禁止先用十几条随手造样例替代官方数据**。
- **读数：** 环境 reset/step 成功；action validity；oracle 合法动作是否推进事件；world truth/agent belief/player input 审计的一致性；重复运行方差；judge 与确定性约束/盲标比较；每 episode tokens/p50/p95/wall/GPUh。
- **阳性对照：** 真实游戏中 scripted/walkthrough 的成功路线；触发确定已知无效动作/事实冲突确认 evaluator 真的能测到。观察不到必须先修测量。
- **噪声地板 + MIE：** 暂无数据；重复基准/固定种子后估计，同步确定何种行为效应值得科学投资，不能提前胡填阈值。
- **混杂审计：** 默认 prompt 差异、模型预训练故事知识、judge 变化、hidden state 访问、行动机会不等价、数据构造/人工标注误差、采样/过滤和等 token 调用。
- **决策表（跑之前写）：** 核心 NPC 环境可运行且可审计→保留并开展行为测量；仅 narrator 成立→NCP 只用作近邻，不冒充 NPC；judge 不可信→先独立人工/规则校准；开源权重无法完成最简单任务→修工具/选更合格单节点模型；成本过高→转另一公共底座，不新建大型游戏引擎兜底。
- **算力预算：** 由首个 CPU/单卡 dry run 得出后填；未估，**实际未使用 GPU**。

## 结果
未运行，没有 E00 结果文件。未来修改预注册部分需注明 POST-HOC 与时间；下一实验可因真实观察主动改变设计。
