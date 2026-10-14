# I02：人物一致性训练的控制路径与读出路径（2026-10-14）

- **状态：** SEED；尚非新科学贡献。
- **来源：** P06；E17冻结控制器只拟合η已部分恢复检索，E19白盒动作信息明显超过η；E23–E24排出人物编码batch/pooling混杂且确认原生utility影响。不是从“人格≠行为”概念二分起题。
- **研究动作：** 重新归因、设计空间分解、梯度路径因果干预。
- **如果为真，主张是：** 某些persona一致性收益来自评价读出的学习，另一些来自用于行为/价值的共享projection塑形；两者对实际utility与语义扰动稳健性的作用可能不同。只有在正确编码、匹配初始化/数据/预算、真实原生任务和独立控制之后才谈新的形成机制。
- **不同结果的信息增益：** readout-only达到Full且控制器与NoCons逐byte相同→InfoNCE不能仅凭检索归功政策形成；Full独有实际utility/语义稳健性增益→保留其真实控制机制；Full读出高但utility/语义稳健性下降→再查共享actor/critic projection漂移；都差→检查环境机会/目标构念，不强造新损失。
- **最近近邻与增量：**
  | 近邻 | 已有ownership | 必须补证的增量 |
  |---|---|---|
  | PCSP gradient-path / independent-behavior / MeltingPot PHASE5 | 梯度拓扑、internal/external差异、读出可能读不出policy signal | 匹配实际训练的梯度路由干预，原生utility与语义稳定性，不冒领这些已有结果 |
  | The Geometry of Projection Heads (2605.17180) | 头的条件数/不变性/信息损失，SSL通常丢弃head | NPC actor/critic实际依赖同一head、不能直接discard；不冒领一般投影几何理论 |
  | Rethinking Psychometric Evaluation | 构念尺度/上下文/意图与行为评价 | 真正policy训练路径；不把新统计口径当独立人格效度 |
  | Persona Vectors in Games | steering可改变策略/他人预期 | 现有共享NPC政策形成机制，不是首次改变策略 |
- **最便宜pilot：** [E25](../experiments/E25-corrected-baseline-gradient-route-pilot.md)，正确last-nonpad编码+原NPC游戏，三路Full/NoCons/仅η，先完整iteration成本及精确policy同一性control，seed42最多30iterations。只有改变判断才原预算继续/其他seed确认。
- **阳性对照：** 仅η的consistency梯度对policy/φ=0、对η>0；源码NoCons与仅η在匹配随机性下policy逐byte同一，native行为/utility亦相同；Full确有φ梯度。初始模型/角色sampler/物理/reward/hash固定。
- **噪声地板/MIE：** byte replay与同初始seed控制，独立held100/3worldseed；短训练只有pilot不冒称300iteration原数复现。若role控制尚未学会，不判机制。只看检索升不算能力证据。
- **预期论文形态：** 有深证据时机制+控制方法；当前只做因果形成机制pilot，不预定新loss/SFT/GRPO。
- **排序打分：** 证据2 · 增量清楚度1 · 形态匹配2 · 成本2 · 可完成性2 · 信息增益3。
- **compression risk：** 高；可能只是已知decoder共训练/普通stop-gradient工程。必须补独立语义扰动与真实utility的预测机制，不能把padding bug或读出恢复当完整贡献。

2026-10-14定位校对：进一步读PCSP PHASE5 §9–12，作者已有contrast-pool、persona-balanced sampling、各substrate8seed确认、projection几何及ID/OOD tradeoff。单纯检索恢复或投影几何敏感性不归我们。venue nearest与最新arXiv查询已执行，ECLIPTICA/CITA的instruction条件偏好/因果识别也是强邻居（尚未全文/代码核验）。E25只作原生形成路径诊断；是否存在独立utility/语义稳健性新知识仍不确定。

E25–28后：η-only own200检索5%/Full8.667%，policy和utility与NoCons逐byte同一；Full utility差CI跨零。E26两政策都有顺序敏感，E27输入code确有行为作用且C的state信息有环境通道。E28真实co-step坐标补偿utility只有约.1且CI跨零、NoCons同样存在，坐标机制分支降级，不继续大训练。PPG、Holonomy、Multi-Way Alignment、LIBERO-Para/GSR/DAIL均强化已有ownership。I02仍SEED、无新claim；上述普通读出/语义资格/原生归因结果不足以称好的新增量。
