# E67：上游规则×执行规则的原生闭环与阻挡状态反馈

- **状态：** RUNNING
- **类型：** CLAIM / 解释性实验
- **对应：** C05 / I04 / P12；用户2026-10-15最新审计授权，暂缓论文。
- **问题（一句话）：** 保持原生世界、人设和具体上游输出固定，执行规则能否改变8步内实体结局；重复block是否由缺少显式状态反馈扩大？
- **设置：** 原79 wear/wield图全部，Gemma-3-12B与Qwen3-32B，原固定6301/6302/6303，两traits全链不变。直接复用各模型E63同case/persona/seed的conversation/update；上游rule=asset/generic × exec rule=asset/generic四格，每格legacy和block_status两反馈，共79×2×3×4×2=3792新执行episode/模型。上下游规则交叉是明确标注的实验，不是人格改半截。所有上游输出均保留，不以计划正确与否筛样。
- **反馈对照：** legacy保持原exec输入；block_status仅在已有动作后，若原生actor.get_blocking()非空，追加“Status: You are already blocking <native name>.”；若上一步是引擎ErrorEvent，同时给其原文。没有状态时不加句子，首步输入相同。不改菜单、不禁止block、不加原目标提醒或策略建议。状态与错误全文是一个普通反馈包，不拆成更多网格；可排除缺反馈总解释，不能单独识别包内哪个字段。
- **B/C补充：** Gemma另复用E65的negative_only与retention_only上游，每个两反馈×全部79图×两P×三seed=1896新执行；比较完成首次防卫后继续任务，保留同批legacy。两模型合计9480条上限8步；C/U输出直接重用，不重采样。
- **读数：** 真实goal/request/both/neither；首步合法block、任何首次合法block、block后随后goal；重复already-blocking拒绝数、非法动作数、原生非物理变化动作比例；第一次goal/defense/transfer的顺序与步数。以全体世界为分母的block_then_goal为主；条件于block的率仅描述，避免事后选择偏差。计划按原生命令回放可行性只作解释分层，不预设正确。
- **预登记对比：** 每反馈、每上游下Exec generic−asset；每Exec下Upstream generic−asset；2×2交互（差中差，不假设贡献可加）；每四格status−legacy；Gemma B−C及反馈×(B−C)。先每图三seed平均，再图簇95%CI，所有P和任务种类完整报告；首步block效应与后续拒绝分开。
- **阳性对照：** 原79目标和Give原生见证；CPU原源动作回放与输入字段核对；首步legacy/status输入完全相同；block状态句来自实际图，非模型自述。原E63/E65对角结局作为历史参照，新同批对角作为主对比。
- **噪声地板 + MIE：** 同原三seed、固定采样公式与8步窗口，报告世界簇CI与同批对角对历史差；不设通过bar或筛种子，方向不同亦入主表。
- **混杂审计：** 上游因素联合改变conversation与plan/memory，不叫纯plan干预；固定个体上游可测执行效应，但不假定自然中介可正交相加。反馈控制的总效应与规则效应分开。保有资产、原子goal与完整角色福利分开；合法block不预定义为错误或合理。
- **决策表（跑之前写）：** Exec替换改变原生goal→推进C05物理证据；只概率变而实体不变→保留概率主张、分析被后续动作恢复的路径。status显著消除重复且恢复goal→反馈解释承担相应现象；首次block仍更多→保留独立行为转向。status消除重复但goal未恢复→任务选择仍需解释。上游×执行交互则报告条件效应，不算唯一贡献率。无论结果怎样，不追加词句搜索或patch层扫描。
- **算力预算：** 预计3–6 GPUh，现有Conda/HF缓存，优先本地4卡按模型/世界独立分片；全时≤8空闲授权卡。0API/训练/激活干预。

## 结果
运行前登记；待固定队列完成填写。

### 推理前协议落实
历史look/inventory的物品枚举受Python进程hash次序影响，无法把新过程称为全部字节复刻；源system/schema/原任务/计划/记忆与动作历史逐项相同，CPU重放核物理状态。E67/E68统一PYTHONHASHSEED=0，全部主对角与交叉在同批新运行；原E63/E65仅历史参照。不同feedback首步输入同字节，完整messages/schema/采样seed相同的调用只执行一次并记录复用，之后仅在输入真正改变时新推理。没有跨不同prompt复用。
