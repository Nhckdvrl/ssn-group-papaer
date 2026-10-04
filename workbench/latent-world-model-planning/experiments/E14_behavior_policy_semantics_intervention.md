# E14｜轨迹监督与规划性能

- **状态：** RUNNING；真正Bellman表示学习的JOINT/SEPARATE完整支点预控PASS、A100训练队列已启动，效用未出。
- **对应：** I09 / R1
- **来源：** S2数据研究与S4经验reachability；原路线诊断和sampler笔记见历史。
- **阳性对照：** 已观测可行路径检查正例预算语义；相同数据与seed的未改动基线；时间/动作接口一致。
- **噪声地板：** route/episode和train seed分别分层；不同latent空间raw MSE/L2不能直接当同一物理尺度。
- **决策表（跑之前写）：** 实际改善→分析数据与目标贡献并扩任务；coverage解释结果→发展采样/覆盖方法或收窄因果claim；保守经验关系更好→研究何时保留；无效→换设计，不强追残差。

## 问题
怎样利用轨迹关系改善规划，而不是只复现行为数据的时间统计？

## 首轮方案（可在运行前修订）
先用已有数据/目标比较LeWM-family与一个planning-aware目标，允许重采样、局部一致性或多路径聚合原型。数据可改变质量、路线混合或轨迹长度。多门TwoRoom可固定start/goal/layout比较近门、远门、混合，但只是诊断；路线变更可能同时影响occupancy与动作分布，不能预设任何变化都是缺陷。新增干预先确认实际加载的短clip/标签会变化。

## 读数与资源
闭环成功/代价优先，候选评分与真实回放辅助；记录样本量、coverage、局部动作变化、训练量。提出独立因果机制时再做所需matching/干预；协方差proxy不等于可识别性定理。

## 结果与修订
最新状态见下方Stage0及实际config/预控/进程记录；此前未运行段落是原设计历史，不覆盖当前训练。

## Stage0：真正Bellman表示学习的最小完整支点（2026-10-04，运行前）

对应I09/R1/R3/P05；旧frozen剩余时间head没有覆盖value propagation。按Value-Guided JEPA(arXiv2601.00844 §3.2)直接joint训练距离表示与原WM：V(s,g)=−||z_s−z_g||2，value target=−1[s!=g]+.99 stopgrad(V(s_next,g))，expectileτ.9，weight1，加原shifted预测+.09SIGReg；不使用observed time-to-go回归，不用物理state作value输入/标签。四frames0/5/10/15、三个真实5step macrotransition；负reward按macro单位记账。goal一半当前clip最后state、一半batch内打乱真实last-state，每batch另20% selfgoals明确identity终止，按原datasetrow相等判identity；target只SG，不EMA；联合encoder/predictor而非frozen附加MLP。使用同BASE100与相同初始化seed0、shuffle33000、freshAdamW/128batch/5650updates，native planner仍原latent terminalcost，距离平方单调不改变同候选顺序。独立九fullbaseline来自E01，与它们公平比较相同经历与部署；不把本pilot称完整GCIQL/HIQL/标准OGBench复现。

先做实际toy Bellman/identity/expectile/SG手算，真实index不跨episode、value梯度流到encoder、WM/原loss parity与CUDA native rollout控制，再启动单seed exploratory训练。零hidden evaluation outcomes参与训练；same100经历与目标重配单列额外监督/计算。主读数新48闭环success/steps+长goal分层/真实candidate regret，offline value fit仅诊断。阳控identity value为0以及原ABS同trainer；噪声trainseed方差已知，单seed不能确认方法。若joint目标有signal再扩全部三个独立seed、真实GCpolicy/层次与第二任务；null先查真实Bellman机制/优化与goal覆盖，不据此关闭value路线。GPU独立单A100，可与E01不同arm并行，node-local RAMcache；所有model在HF，raw不进git。此为已知完整目标的机制支点，不预称新方法。

原论文Table2与§5定向回读补充（运行前）：Sep/quasimetric强于若干joint/VCReg配置，不能让joint+SIGReg单null代表value方法。追加VGIQL-SEPARATE seed0：总5650updates不变，前2825仅encoder/projector Bellman表示（无SIGReg），后2825冻结encoder/projector并固定其BN，fresh optimizer训练predictor/action/pred_proj，仅factual预测；两个阶段checkpoint/optsteps分别保留。与JOINT的更新模块/曝光分配不同，显式报告而非孤立因果归因。新CPU读回发现selfgoal应吸收终止：target中bootstrap乘1[s!=g]；old预控只查identity值0而未查终止target，旧源码/limited-control artifact保留，不曾训练部署。新版在CPU/CUDA实际手算selfgoal target0和完整两阶段梯度/新optimizer隔离后运行。不是照搬Eq1的所有采样/训练设置；新的goals吸收语义按goal-reaching明示。若SEP null需先检查独立阶段训练充分性，不自动否定表示学习。两版本均wholeepisode新48、强baseline和总compute账本。

最终运行前语义校对：goal identity改为真实uint8 pixels的完整SHA256一致（而非row相等），同image不同source row不再被当未到达。state IDs只由训练观测生成，重复像素与selfgoal/absorbing target阳控实算；不使用物理坐标或evaluation outcome。CPU第一版/吸收终止retry1控制与源码均保留，最终版另CPU/CUDAretry2才作启动依据。修正preflight参数数量计数（eval requires_grad=False不能误报params0）与分阶段最终optimizer只统计active parameters；这些都是GPU训练前发现，无已训练方法读数被改写。

训练前原文App7.2再次核对：VF欧氏距离支点改用原文gamma=.98、tau=.80，覆盖早先.99/.9试写；paper明确过高两者可能不稳定。toy手算与CPU/CUDAretry3使用最终值。所有改动都在真实训练前，初稿preflight不当final训练契约。SIGReg/现代tinyViT/clip与planner仍是本地port的显式差异，不能把Sep效力或null说成原文numerical复现。

最终代码/actualCPU/CUDA与正式训练启动控制同E01：全部Bellman手算/duplicatepixel identity/terminal0/SG/finiteness/Sep两阶段freshoptimizer与encoder freeze/官方native parity通过。两arm JOINT/SEP seed0固定5650 A100独立queue，共用最终源码0400260f…，JOINT+SIGReg和SEP无SIGReg的差异是已知方法轴，不能当孤立loss因果；训练不读任何部署outcome。第一真实训练步待确认，尚无value efficacy结果。source0/1原plain已真实训练，value与source2继续按node-local独立jobs。
