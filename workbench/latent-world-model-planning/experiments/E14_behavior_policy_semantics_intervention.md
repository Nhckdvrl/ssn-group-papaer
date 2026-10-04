# E14｜轨迹监督与规划性能

- **状态：** RUNNING；JOINT/SEPARATE三训练source与完整闭环重复已完成；已知机制far收益重复，下一增量未确认。
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

### 2026-10-05完整两阶段支点结果与独立seed重复（运行前）

原single-source两value与九matched模型全22groups/1056episodes独立trace/hash/初始state/native成功复算PASS，见E01_E14_20261005_matched_control_results.json。same-seed0 ABS physical近17/远7，native21/9；JOINT physical8/9、native10/7；SEPARATE physical16/17、native19/13（各tier24）。SEP对ABS总体physical+.1875 CI[.0208,.3542]、native+.0417[−.0833,.1667]；SEP对JOINT两个接口+.3333/.3125且单seedpaired-episodeCI均正。重点是far改善/near损失、接口依赖与seed不确定性，不能包装为新方法；Value-Guided JEPA本已比较分阶段与联合，当前是baseline机制支点、非原paper数值复现、非novelty。FULL-AD同data三sources总体不稳定胜ABS，不能以相对较弱RES的gain替代强base。

按第一exploratory hint扩到原独立trainseed1/2，每seed仍全部JOINT→SEPARATE各5650，原source saved初始化、sameBASE100/norm/encoder/predictor结构/γ.98/τ.8、goal_future50%/inbatch-random50%/self20%、pixelidentity、原3teacherfuture/目标SG/JOINT SIGReg.09与SEP2825value→2825dynamics均不改。原m训练代码0400260f…freeze，原seed0完整保留；seed1/2 ABS强参照已固定训练/闭环，不筛任何source。当前goal_spec只含local15step未来或batch末帧，跨context随机goal可能不可达；这个范围必须记录，不能把它当完整GC-IQL或一般long-goal算法。此次重复用于先分辨seed与目标/优化设计，暂不换采样器救数值。

四新trainruns/两个独立A100slots，node-local原1.4GB cache、同stage源码/hash既有完整CPU/CUDA控/全部savedinit三source已验证；wrapper只取实际free。新HF/raw沿冻结m命名20261004-E14-{JOINT/SEPARATE}-A100-s{1,2}（实际启动2026-10-05；参数名VGIQL-JOINT/VGIQL-SEPARATE），不覆盖s0。完整终点后原RTXsame48两接口各source2arms/384episodes，samebudget/seed/精确warm守卫/全部目标分母，value_model_loader明确ABS303/schema。主读数分层success、每seed原数/paired source+anchorCI、新envsteps；single-src先前CI不升级独立seed证据。决策：far收益三源稳定且面对strongnative→完善真实goal机制/跨task/GCpolicy近邻以找增量；仅弱physical成立或seed不重复→保留counterexample，回看预测对象/goal语义/数据覆盖，不调τ/λ网格。R1–R5与主旨/PROPOSED保持，科学主张0。

两个新source各JOINT/SEP全部固定5650已自然完成（四runs），合计三个source六value终点连原九baseline独立初始化/hash/data/firstbatch/finalsampler/finite全weights与moments/297×5650或204×2825→93×2825审计PASS；SEP保存value phase与final encoder/projector全部参数/buffers bit-exact相同。结果E14_20261005_three_seed_endpoint_audit.json。两原A100队列3621335/3621386已自然退出，禁止重复。新RTX384eval first launcher3573734因CUDA_VISIBLE_DEVICES=1却指定local --gpus1在mapping处失败、未初始化CUDA/没有controller输出；原log保留。修正仅launcher local索引0，新PID3574468/log/tmp/latent-E14-three-seed-control-RTX-queue-retry1.log，已确认实际GPU1 context，value_seed_control_queue.py显式同namespace/303/schema，训练/任务/预算未改。完整matrix未齐，不报partial效用。

### 三独立训练源的完整闭环重复（2026-10-05）

全部三source ABS/JOINT/SEP、两接口、18groups864实际轨迹独立审计PASS：[完整结果](../results/E14_20261005_three_seed_control_results.json)。native ABS30/23/24、JOINT17/2/7、SEP32/34/39（每source48）；physical24/18/24、17/4/15、33/33/40。native远24目标分别ABS9/6/5、SEP13/17/18；physical远ABS7/4/6、SEP17/16/20。SEP对ABS整体native+19.44pp、paired source+anchor95%CI[2.08,36.81]，physical+27.78pp[12.50,42.36]；far分别+38.89pp[12.50,62.50]与+50pp[33.33,66.67]，近native0pp。所有三个训练源保留，包括JOINT2/48，无幸存seed筛选；共享48开发任务不等于144独立新任务，只有三个训练种子的CI仍须谨慎。

完整初始化、297/204→93 optimizer步数/finite moment、encoder/projector所有参数与BN冻结、firstbatch/finalsampler、所有episode初始state/native success/trace/checkpoint/load来源通过独立reader。原value repeat384队列3574468已自然退出，禁止再启动同unique run。raw/durable全审计20261005-E14-three-seed-control-audit；git仅summary，完整rows留artifact。

这是可靠的已有baseline机制支点，Value-Guided JEPA已拥有Sep/Joint与距离价值设计，不能叫新idea或原paper复现。下一增量应利用它理解有限经验、动作后果、可复用目标空间与不同模型使用方式；不围绕τ/λ网格优化已知方法，不因已有近邻关闭R1–R5，当前科学主张0。
