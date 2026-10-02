# E11｜状态、历史与信息获取

- **状态：** PLANNED；未运行。
- **对应：** I07 / R4
- **来源：** S1历史动力学；既有记忆、belief和POMDP路线。
- **阳性对照：** 可见hidden变量/解除遮挡条件应减少信息负担；无关视觉扰动不应被解释为hidden-physics机制。
- **噪声地板：** 按场景/隐藏参数与独立训练种子分层；不可辨状态的oracle差距不是统计噪声或模型bug。
- **决策表（跑之前写）：** history已好→研究其效率/适用范围或换自然因素；belief/探测好→分析来源并扩任务；当前任务无信息需求→改此实验，不关闭R4。

## 问题
什么状态估计/信息获取设计改善自然部分观测下的控制？

## 首轮方案（可在运行前修订）
选遮挡、隐藏速度或接触/物理参数中一类真实任务因素。比较原生history、增量history/递归状态，以及一个简洁belief或探测策略；可先用同checkpoint评估。完整状态oracle为上界；同部署history不可区分的状态不能强求模型逐状态选中oracle动作。改变探测次数/成本时单独计账。

## 读数与资源
成功、风险/失败类型、恢复和探测成本；hidden-state probe辅助解释，不单独承载规划主张。

## 结果与修订
尚未运行。实际执行前补code/data/config、种子、授权资源与运行预算。探索性改动允许，必须留版本；发现数据/接口错误时修正该运行，不自动关闭母问题。


### R4部署状态估计pilot（2026-10-03，运行前）

推进P08/R4：current actual image encoder是否等于planner所需的动态state？借PlaNet filtering与经典fixedgain observer，不声称Kalman/belief保证/首次history。FIRM已有typedconfiguration+dynamicfiber，额外物理标签；本pilot只冻结Fast部署状态更新，不训新WM。与A5不同：固定EX5-SHIFT-WARM/CEM预算与反馈频率，只改planner initialstate。

两releasedFast/原source全量actionnorm/preparedg25各前16，SEED78000、budget50、H25/N300/K30/30。nominal/gain0.7/physics六cells，physics为导航wind+.15x、PushTmoment-only×2；全部16不筛，3methods共288episodes。共同首次native25plan、各method同first5真实issued prefix/replaystatepixel；此后OBS=E(actualimage)，PRIOR=frozenf5(previousselectedstate,issued5commands)，FILTER=prior+.5(observed−prior)。三个固定值不按结果调gain；OBS也计算prior仅作诊断，不喂future。每次规划init为prior/warm shift previousplan suffix，goal固定原E(goal)，不可读取hidden/applied gain/velocity。模型输入只能是issuedcommand，而不能拿已知simulation shift作oracle校正。

正控：prefix5/predictor/latentdimensions与nativecontrol，三个methods同初始physical/pixel，allobservedweights不变、nooptimizer/noextra训练数据，sharedstepseed如A5。保存所有frame/issuedcommands/previousstate/prior/observation/residual与solverplan，实际steps/调用/encode成本分开。为与A5复核，保留原native未clipcost；TwoRoom已知scoring-vsenvclip限制三个methods共同继承，不能据observergain归因velocity。PushT publicmemory恢复边界单列。

primary per-task/shift success/paired help-harm/physicaldistance对OBS、2000episode-bootstrapCI；prequential residual仅辅助、不据latentdistance直接说动态状态更准。决策表（跑之前写）：FILTER/PRIOR稳定utility且nominal无害→转history/残差结构或强backbone确认、区分offmanifold/cost/信息；OBS好→真实feedback是强baseline，历史训练/低维ID是另方法轴；仅MSE变好→不升机制/继续routegate。单checkpoint16episode条件CI非trainseed证据。raw `20261003-E11-latent-observer-RTX-s0`，代码≤180行独立、CPU预控/root审后授权空卡，尚未运行。
