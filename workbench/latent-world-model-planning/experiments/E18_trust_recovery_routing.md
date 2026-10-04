# E18｜Utility-Gated Recovery：更新、反馈、重规划还是保持不动？

- **状态：** RUNNING；两任务四response与扩六response均完成；接续恢复能力探索，不训练router。
- **对应：** I11 / R5。
- **来源：** S19–S20；这是第二波方法线。
- **阳性对照：** no-shift / in-distribution条件下HOLD应有竞争力；明显shift下至少一种干预应优于HOLD，否则recovery set本身无效。
- **噪声地板：** deployment start/state、shift instance、train seed、router split分开；同一fork使用common random numbers或尽量相同随机性。
- **决策表（跑之前写）：** utility router优于固定策略→扩task/shift；某固定策略统治→保留简化结论；fork labels噪声过大→增加重复或缩小intervention set；未来信息泄漏→作废该router。

## 核心问题

world model出现异常时，哪种intervention真的提高未来closed-loop utility，而不只是降低instant prediction error？

## Stage 0｜Fork ledger

在可重置环境选择预注册decision points。对同一个model checkpoint与environment state建立matched continuations：

- `HOLD`：不更新，按原planner继续；
- `FEEDBACK`：只更新latent feedback / observer state，不改参数；
- `SHORT-UPDATE`：用最近真实transition做1–K步轻量梯度更新；
- `EXTRA-REPLAN`：不改模型，只增加candidate/horizon/replanning compute；
- `FALLBACK`：若已有简单policy/short-horizon controller则加入。

每个fork记录未来H_eval steps / episode return / success / failure，并计算相对HOLD的 `ΔU`。

第一轮只需HOLD + 2种最容易实现干预，不要求全五类。

## Router features：只允许部署时可见

### 2026-10-02 无训练fork pilot（运行前）

动机：E13在两任务远goal上的self-consistency refinement没有收益；E16固定bank的regret也未支持“排序修正”解释。下一步改变**反馈/重规划设计**，不再局部调selector。

复用E13 A2锁定的75-step goal anchors，各task前32个预定episode，不按失败或结果筛选。使用同released Fast checkpoint、β=0、native macro rollout(3×25steps)与CEM N300/K30/30，先规划完整75动作，执行共同25步prefix。fork点在step25；若此前已成功，完整保留并标无需干预。

同fork比较HOLD（原剩余50动作）、FEEDBACK（真实当前pixel替换预测state，重新规划2×25剩余动作，N300）、EXTRA-REPLAN（同feedback，N900）；三者不改参数，剩余environment budget均50。这是feedback+replan组合，不把差值单独归因observer correction；首轮不训练router、不称新颖feedback方法。追加一种对照 PREDICTED-REPLAN（用预测step25 latent重新规划N300，不使用真实当前pixel），分开搜索更新与真实反馈。

跨两个conditions：no-shift action gain1.0与共同prefix第10步起gain0.7（fork前已有可见作用）；PushT使用relative action接口才允许action gain，否则拒绝此shift。所有干预面对相同gain/同prefix commands；selector/features不可输入真实gain或future utility。每task32×2conditions×4continuations，环境最多约25,600steps+prefix重放controls；模型不训练，单GPU。

公共prefix在fresh reset/public setter后执行；各continuation用同reset seed+完整prefix replay恢复fork的完整**本次生成**physics memory，state/pixel一致性需控制。不能声称恢复原dataset完整memory。部署features：step25 prediction/observation latent residual、可见goal progress、初始elite margin；future utility与特权state只用于离线标签。对已成功prefix与所有失败均保留。

主读数：native success、剩余50步的native task distance/return、对HOLD的配对help/harm与episode bootstrap CI；condition/task分开。另报重规划calls/candidates和fork replay开销，GPU非独占则降级timing。native-cached cost需H1/H2/H3一致性控制；动作长度必须75=3×25、remaining50=2×25。若fixed FEEDBACK普遍更好，先沿固定策略发展；若compute/feedback只在部分state值得，再扩ledger/shift或utility controller。不能因为firstpilot无utility异质性而关闭R5。

候选：
- recent prediction residual；
- ensemble / bootstrap disagreement；
- CEM elite margin；
- candidate rank instability；
- goal progress / stagnation counter；
- support/OOD proxy；
- previous intervention response；
- remaining compute / interaction budget。

禁止：
- fork未来return；
- privileged hidden state；
- “哪种干预后来最好”的真实标签直接在线输入。

## Baselines

1. ALWAYS-HOLD；
2. ALWAYS-FEEDBACK；
3. ALWAYS-UPDATE；
4. ERROR-THRESHOLD；
5. CHANGEPOINT detector（适用时）；
6. ORACLE-FORK（只作上界）；
7. learned / rule-based utility router。

## 训练方式

先把fork ledger当监督集：
- binary：best intervention vs hold；
- 或multi-class：HOLD/FEEDBACK/UPDATE/REPLAN；
- 或直接回归每种intervention的 `ΔU`。

第一版优先浅层模型，避免router本身成为主要算力/容量来源。

## 主读数

- closed-loop success / task cost；
- intervention count；
- extra model calls / gradient steps / wall-clock；
- real-environment extra transitions；
- utility gain per intervention；
- false-positive update cost：本来HOLD更好却触发干预；
- false-negative cost：需要干预却没触发。

## 确认范围

至少包含：
- no-shift ID；
- 一个dynamics shift（friction/action scale/layout等）；
- 一个model-error/stagnation自然失败子集。

如果router只在人工shift有效、自然失败不泛化，就明确限制，不包装成通用trust mechanism。

## 最近邻压力

- Feedback WM已经证明feedback-state correction有价值；
- WorldAgen / AdaJEPA类工作已做test-time update；
- CAWM做shift detection + replay forgetting；
- Counterfactual Utility Protocol已经证明“update本身可能伤return”，并提供update-vs-hold fork measurement。

因此E18的潜在新点是**从fork utility学习intervention selection**，而不是再证明某一种adaptation有用。

## 结果
首轮四response与扩六response均已运行，见下方记录；无科学主张升级。

2026-10-02首轮native cost正控因missing candidate axis在模型接口处停止，尚未执行fork/candidate银行；failure与源码留存。修复直接native scoring的显式candidate axis，保持全部seed/inputs/主读数，以s0-retry1重跑。该接口失败不是科学null，不覆盖原run。

### 2026-10-02 recovery set扩充（运行前）

首轮两task×32goals×2gains×4interventions已完成：no-shift TwoRoom HOLD12/32→FEEDBACK16/32，PushT4→7、EXTRA9；gain0.7时TwoRoom6→7，PushT1→0。全部40,696执行/重放steps，fork state/pixel error0。不能从这组方法推断“恢复不可能”；尤其面对未知动力学变化，单纯换成真实当前state没有改变错误transition。

接续同一64锁定goal/相同initial75-step plans/同step10 shift onset，不增加新goal、不按结果挑任务。扩 **SHORT-HEAD**（只更新action encoder）与 **SHORT-DYNAMICS**（action encoder+predictor，encoder/projectors冻结）；均使用fork前最后3段5-step真实pixel transitions与名义commands，frozen encoder target，16 AdamW updates/lr5e-5/WD1e-3/clip1、native prefix MSE，无privileged state/gain/reward输入，不读取fork未来。仅有3个新样本，可能过拟合，失败也全部保留；这是固定response的探索，不宣称新训练配方或普适update增益。

六方法同batch比较HOLD/PREDICTED-REPLAN/FEEDBACK/EXTRA/SHORT-HEAD/SHORT-DYNAMICS；每fork重新clone原权重、params更新不跨episode/condition污染。adapted dynamics在原latent坐标规划剩50steps，N300，与FEEDBACK额外search一致；单列16 gradient steps/更新参数数、所有policy总计算和physical steps。原基线HOLD/FEEDBACK同初始plan重算作控制。目标是比较**信息反馈 vs transition update vs search**三个设计，不先训练router，也不只研究一个gain值的阈值。后续确认需自然错误、别种dynamics shift、原任务保留与独立checkpoint。

### 六response实测（2026-10-02）

[完整summary/config/hash](../results/E18_20261002_short_updates_seed0.json)，768 continuations、59,459执行/恢复steps，fork state/pixel差0。顺序HOLD/PRED/FEEDBACK/EXTRA/HEAD/DYNAMICS，每组32：TwoRoom nominal12/13/16/15/12/12，gain0.7为6/6/7/7/9/6；PushT nominal4/6/7/9/6/4，gain0.7为1/1/0/0/1/0。HEAD对FEEDBACK在nominal导航help0/harm4（−12.5pp CI[−25,−3.125]），shift导航help2/harm0（+6.25pp [0,15.625]）；不是跨seed稳定增益。

HEAD更新1,802,848参数，DYNAMICS更新10,826,272参数；均16steps/3 prefork transitions。导航shift的prefork fitting MSE中位0.06331→HEAD0.00504/DYNAMICS0.00474；这只拟合已有3样本，不是held-out预测证据，更不证明长期任务效用。当前短适配没有强恢复signal，不增加router复杂度。

RTX重算512条旧baseline的success全部相同，但4条重规划的完成步数及部分distance不同（max15.39）；HOLD步数全一致、距离差≤2.3e−13。prefork latent特征跨GPU也有差异，不能写成逐轨迹/特征完全数值复现，或混A100/RTX时间。新增方法的配对判断用本次同RTX baseline。保留全部原始输出、同initial plans与public-setter限制。


### 2026-10-02 P08/R5 连续适配pilot（运行前）

从AdaJEPA的recent-history/one-step-per-MPC/reset策略与adaptive MPC借方法，不称完整AdaJEPA复现。旧短更新只训练5-step前缀并一次fork；新比较预测模块/表示readout在持续真实反馈中的效用。不先造router，不先按短loss判update有益。

两released Fast，各锁g25前16；nominal、driver gain0.7、task-specific physics（TwoRoom每command加[.15,0]再native clip，无滤波记忆；PushT block moment×2、mass不变，reset恢复），shift onset0。模型看issued nominalcommand，不看shift/真实物理参数。3methods：FROZEN / DENSE25-PREDLAST / DENSE25-PREDLAST+PROJECTOR；PREDLAST为transition_stack最后层/norm/output_proj及pred_proj，PROJECTOR为MLP readout，不是ViT最后层。记录模块名/参数数。共288episodes，总budget≤50；common nominalH25/N300 plan首5步在条件下真执行并完整重放一致，absorbing首5成功保留。

此后每5steps同N300/K30/30/H25重新规划，执行首5。更新用最近≤25真实commands和每5步raw image，对所有合法source→已观测future directprefix等权MSE、target detach，无padding/future标签。t5/10/15/20/25共有1/3/6/10/15pair，**只有t≥25存在真实25step目标**。每决策1 fresh AdamW update/lr5e-5/WD1e-3/clip1，evalmode BN固定；每episode完整clone/reset参数+buffers，projector变后重encode全部buffer/current/goal，不缓存旧latent。t50无未来执行不更新。

主读数为每task/condition成功、vs frozen help/harm/paired episode CI；距离、pre-update fitting loss、updates、encoding/gradient/search时间分别报告，不能把训练误差降低当效用。各method每决策同env/CEM预算，adaptation额外compute不称equal-wallclock；native wrapperallclose、source不变、BN固定、prefixtarget count和5step重放为正控。只一releasedmodel/task，16episode CI条件于该model；普通条件可能成功ceiling/更新机会少，报告机会数。源25动作在各条件下factual replay只作诊断、特权状态仅恢复，不进部署feature。

决策表：适配跨physics类改善且ID无显著伤害→独立head/episode确认与跨goal冻结复用、第二任务/新shift；局部fit改善但future弱→比较低维系统辨识/action-map、数据激励或cost/proposal，不连续调lr；readout有益但不能保留原任务→明确reuse问题。raw `20261002-E18-continuous-adaptation-RTX-s0`、单授权空RTX，完成自动复制durable。


连续pilot运行前物理干预校对：原PushT mass+moment同比例×2在锁定16 factual25轨迹的10D状态逐步差全0（15/16实际接触），构成无效transition干预；未用于任何GPU适配比较。CPU1200steps对比发现moment-only×2在15/16改变轨迹，故运行前修订为moment-only。这是按是否真实改变transition的干预正控，不是按适配效益选择shift；全部16保留。原实现/轨迹/诊断保存，[校对](../results/E18_20261002_physics_preflight.json)。E18等待queue仅在未运行时停止，修订完成后重启。


### 连续适配全288episodes（2026-10-03 JST）

[config/hash/summary/controls](../results/E18_20261002_continuous_adaptation.json)，14,313执行/诊断/重放steps，common prefix state/pixel误差0。FROZEN/PREDLAST/PREDLAST+PROJECTOR顺序、各16：TwoRoom nominal10/10/9、gain.7=8/8/9、wind=8/8/9；PushT nominal5/4/3、gain.7=3/4/3、moment×2=3/2/3。没有稳定成功增益，不能转成update普遍无效或完整AdaJEPA反驳。Pusht更新有distance退化；success与distance分开汇报，fitting loss不作utility。

此前E17 sameg25前16整25执行ZERO300为导航13/16、操作14/16，本次每5反馈FROZEN10/5，但两次plannerseed不同（68000/78000），**不能直接归因feedback**。新增共同初始plan、commit5/10/25和shift-warm控制已先写E13卡；若差由cold optimizerrestart解释，先加强MPC baseline，再研究update；如果仍有差，继续分辨预测对象、执行承诺、隐藏速度/反馈state替换，不预选narrative。


### F0：完整联合强支点的反馈频率（2026-10-05，运行前）

对应I11/P04/P05/P08/R5。INTACT全发布模型两task192已严格审计，Nav37/Push25（各48），证明冻结policy的弱结果不代表完整family。下一步跨控制接口，比较原EX25与EX5/EX1反馈；均用同完整publishedseed0、H1观测+causal原最后5primitive动作、同官方get_action horizon5的完整25primitive plan，仅执行prefix变。不是新的feedback方法，也不是EX1=新训练政策；固定模型、相同firstdecision prefix/同goal/同100step预算，不额外查询真实gain/futurestate。

新两task×EX5/EX1×原全部48=192，仅原native输出不clip；原EX25native96为HOLD参照，不能用clip等同混倍。先各实际CPU/CUDAget_action完整25output与原preflightsource/手算一致、前1/5执行prefix切片无越界、原全48warm状态/pixels exact、BN/weights unchanged；全部过再部署。记录每decision实际past5、完整proposal、执行prefix、replan次数及CUDA同步solver时间。原checkpoint/data/near/far/initial-success保留，时序介入改变采样分布属于所研究的控制设计，不称训练因果。

主读数：all/near/far成功、对EX25 paired48 help/harm/95CI、同起点首次plan逐项一致、envsteps、replan次数。噪声地板只anchor区间，一个trainseed；预先全部cell保留，不按近/远筛反馈或调阈值。昂贵fullH25实际算完再丢prefix，所以timing不能夸为最优implementation；若EX5有效，后续先测firstchunk H1短调用与fullH5第一chunk实际parity，成熟廉价固定feedback必须作为强基线。原RTX空GPU1/3各独立task，隔离INTACTvenv/source/环境不变，无router。

决策表：fixedfeedback统一主导→以该固定策略为支点，不硬造gate；help/harm随实际state异质→下一步同state replay fork ledger，futureutility只离线label，部署feature仅observable残差/goal progress/actor uncertainty；feedback无收益→转向data/representation/可复用cost设计，不关闭R5。只是跨轴exploratory test，无科学主张/narrative/state升级。


### F1：强联合模型的同状态恢复效用与干预类型（2026-10-05，运行前）

对应I11/P04/P05/P08，母问题R5兼R4：真实观测误差何时值得改变已有计划？F0仅wholepolicy频率，不能拿不同controller走出的不同state作同state utility label。F1固定完整INTACT两task/original48/100step/首25plan；每起点先执行同一plan前10primitive，然后same reset+完整prefix replay恢复完整本次物理state/pixels，在t10 fork比较三种15step response：HOLD=旧plan剩余15；REFRESH15=真实当前像素/causal最后5已发command，官方full25plan首15；REFRESH5=相同freshplan首5、每5再次观测，执行共15。t25以后三者均按相同EX25 basepolicy继续至100；不是比较三种整个episode频率，也不把feedback+新action plan称纯observer因果。REFRESH15与HOLD相同新动作window、REFRESH5更多调用；额外compute完整报告，不称等墙钟。

两task各全部48×nominal/gain0.7/physics×3=432，总864continuations；hidden shift从新执行第6步起：gain对发出的command乘.7；Nav physics为command+[.15,0]，Push为block moment×2且mass不改。模拟器仅用于实施shift和恢复，controller/feature不读shift/physics参数；真实past是agent已发command，而不是不可见scaled执行量。原warm10不shift。所有absorbing prefix成功保留；不是按失败筛state。原发布预训练未知、一个trainseed/48开发goal，不当确认或novel方法。

阳控：原两taskCPU/CUDA/48warm与完整actor grammar守卫先过；所有初始plan CUDA bitexact F0/EX25；官方get_action(prefix_actions=首2macro,horizon3)必须bitexact原tail15，手算rollout_one_step首5/10与同原actor递推一致。nominal prefix必须bitexact原EX25trace前10或吸收点；每condition prefix独立replay全部state/pixel bitexact，shift在t5以前与nominal exact。事前报告每condition真正改变轨迹的比例、Push接触与moment变化，零效果起点仍保留，不依恢复收益择shift。全部source/frozen BN/weights unchanged；执行budget、angle+position native成功、pre-success停止守卫沿用，不允许放松。

部署feature在fork未来执行前存：5/10步模型预测与真实编码residual、latent goal progress、actor clamped Gaussian variance、旧tail与新plan首15分歧；只用真实已观测images/已发commands/原model预测/current goal。future success和state仅离线标签，feature生成函数不接收condition、特权state或未来数组。不训练gate，不用这批拟合阈值后重报同批效用。

主读数：各task/condition全48 success、vsHOLD help/harm/paired anchor bootstrap95CI、near/far全分母、envsteps/replaysteps/modelcalls；fork前成功单列，不丢失。独立reader重生原full25D或2D native成功、所有command因果历史、所有prefix与trace/sourceSHA、首次REFRESH15/5 proposal exact、t25后EX25协议。48anchor CI条件于一个model，condition间以sameanchor clustered，不把864当独立训练。噪声以paired episode区间，不按partial挑方法。

决策：固定response在全部主要条件主导→保留强简单baseline，不造router；显著help/harm共存且可见features可区分→新增独立episode same-state数据，再比较固定/阈值/近邻的utility选择；只有人工shift收益→明确适用边界，追加自然失败/真实数据而非缩成moment特例；全部null→用结果转向CF监督/表示和task reuse，不关闭R5。最新cross-domain SA/DEHP/attention chunking已有sensitivity/uncertainty/adaptive length，后续不能claim首次adaptive chunking。两个授权空原RTX0/2，各独立task，无新ACTIVE资源；raw unique20261005-E18-intact-forks-{task}。


F0完整192新episode+96原EX25 native参照全部独立source/causal过去5/首proposal bitexact/native真实成功/全trace审计PASS：[结果](../results/E18_20261005_intact_feedback_frequency_results.json)。Nav EX25/5/1=37/28/30，near22/18/19、far15/10/11；EX5−25=−18.75pp95CI[−35.42,−2.08]，help4/harm13。Push25/29/27，near22/23/21、far3/6/6；EX5−25=+8.33pp[2.08,16.67]，help4/harm0；EX1−25两task CI含0。EX5 calls Nav567/Push573，EX1为2707/2881（EX25原87/129）；新solver平均约.18sec，旧EX25无timing，不claim加速/最优实现。所有48/initial1保留、single trainseed、开发任务区间，不升级科学主张。wholepolicy反馈异质给F1动机，不等价同state utility gate证据。

F1首launcher的源码多一个右括号，py_compile失败但串行shell继续launch；两个wrapper在import/model/预控前退出，效用0。原source/SHA/两logs保存raw20261005-E18-intact-fork-launch-syntax-failure。修正后使用subprocess check=True强制编译成功才launch，不改方法/目标/guard；新日志/tmp/latent-E18-intact-forks-{task}-RTX-retry1.log，原RTX0/2 wrapper3652205/3652206，实际CUDA context建立。完整864未齐，不把PID/部分guard当效用；后续reader整批审计。


F1 API校对：首feature生成把原Gaussian tuple函数inverse_action_distribution当dictionary用；guard在anchor0/preflight内拒绝，两个task均正式continuation rows0。实际源码+failure+launcher完整保留raw20261005-E18-intact-forks-{task}。已读原jepa/module确认为inverse_action_parameters的规范dictionary（同原actor/clamped std）；v2只改这个API和新unique路径，不改任务/计划/feature定义/容差。v2两task全部144prefix组的exact replay、shift t5前一致、原nominaltrace、firstproposal/predictedtail/native/模型不可变全部PASS；实际432/task正在跑。原RTX0/2 wrapper3652843/4，logs/tmp/latent-E18-intact-forks-v2-{task}-RTX.log；独立intact_recovery_forks_audit.py准备好，整批complete齐才读效用。


### F2：反馈改变什么——保留世界预测参考与重新追goal（2026-10-05，运行前）

对应I11/R5，兼R2/R3的预测对象复用；承接INTACT的共享local/goal action law及RWM的reference tracking，**不claim首次用世界预测作控制target/新RWM**。F0导航更密反馈有损，不够说明反馈本身坏；换最终goal action plan可能改变原行为/承诺。F2复用F1相同原48×3condition/common10prefix/response至25/EX25suffix，加入两个训练free arm：WAYPOINT-FEEDBACK每5步用真实当前image编码、原first25plan预测的下一5step latent reference、真实已发last5commands查询原inverse_action_parameters mean；WAYPOINT-OPEN以同原预测当前latent代替真实当前pixel，其余target/history/预算相同。reference由原goal actor full25计划的官方world recursion产生，全部是model prediction，不能读真实future、data-state或shift参数。

每task48×3×2=288，总576；与F1 HOLD/REFRESH15/REFRESH5同state ledger全矩阵比较。三次response决策均用actor output5primitive，不把goal5回路的25step生成冗余计算当公平速度优势；分别记encode/head/worldcall/model seconds，任何速度主张需优化后的REFRESH5强对照。OPEN有actual past commands，但不看新image，不误称无信息openloop。只是local-vs-global目标/实际反馈的exploratory factorial，不要靠融合系数、τ或挑subset救方法。

阳控：source与原F1/preflight严格same、48warm/prefix全state/pixels exact；新actor接口actual CPU/CUDA goal/physical-next query手算five-slot graph/mean与clamped std一致；global-goal query mean bitexact原get_action首macro。CUDA原firstplan与F1 reference逐项exact，完整5×rollout_one_step reference首0/5/10必须bitexactF1 feature expected_embeddings，全部predictor/encoder/BN immutable。保存全部6 latent states、实际response current/target/previous action embedding/returned mean/logstd供独立reader重算typed graph。同model的forward→inverse cycle误差只记录，不假定为0或拿失败消融掉。

主读数为全48 per task/condition成功、vsF1 HOLD及REFRESH5 help/harm和paired95CI、WAYPOINT-FEEDBACK vsOPEN、native位置/角度criterion、原全部initial/prefix-success和source/hash；同state吸收prefix全保留。预训练未知、一个modelseed/开发48不能作论文确认。若feedback tracking真有跨条件收益→与RWM/成熟trajectory tracking完整方法及强固定feedback比较，新的同budgetepisode、多个published/trainseeds、第二family确认；若OPEN一样有效→localtarget而非feedback解释；若两者弱→inverse读取想象局部target仍不可用，转向训练/CF监督/task复用，不连续调trace长度，不关闭R2/R5。原RTX1/3授权空卡，各独立task；raw unique20261005-E18-intact-waypoints-{task}。


F1全部864 DONE，v2独立reader完整native真实成功/因果commands/隐藏applied/全部prefix与feature/source/首重算proposal/hash/control协议审计PASS：[结果](../results/E18_20261005_intact_recovery_fork_results.json)。HOLD/REFRESH15/REFRESH5各48：Nav nominal37/37/37、gain32/33/33、wind34/36/33；Push nominal25/26/28、gain16/19/21、moment20/22/19。Push gain REFRESH5−HOLD+10.42pp95CI[2.08,18.75]，help5/harm0；其他主要整体差CI含0。先知union比bestfixed：Nav三condition均0，Push分别+1/+1/+3条，**不足支持复杂gate**；未来标签oracle不是可部署能力。

真实shift从t5改变prefix轨迹的比例：Nav gain44/48、wind43；Push gain47、moment24；零变化和prefix吸收仍保留。Nav nominal commonprefix吸收9/48、Push2/48（两taskinitial1）；数据不是864独立trainseed。F1 nominal没有Nav success harm，但F0与F1的反馈起始点/介入时长都不同，不能说harm只在t25后。下一F2比较不同target使用，而不是局部调频率/router。

F1首独立reader按NumPy均值重算小goal_progress时，两个较大CUDA float32 MSE相减的reduction误差3.58e−7超reader容差；原source/失败留20261005-E18-intact-fork-audit-reduction-failure，未写正式result。v2先按原容差独立校对两个component MSE，再重生这两个已验证scalar的float32减法，不放宽任何执行/状态/模型guard，训练/轨迹/原feature不改。已完整PASS；科学主张0保持。

F2已在原RTX1/3实际启动wrapper3654985/6，logs/tmp/latent-E18-intact-waypoints-{task}-RTX.log；actualCPU/CUDA typed-graph/goal-native mean/std、整144prefix/48reference全部预控PASS。两task完整576待齐，用intact_waypoint_recovery_audit.py读全matrix并CPU独立重算全部保存的local query；不能拿Nav先完成当赢家。


F2全576 DONE/独立native/因果commands/hidden shift/typedgraph/所有local query CPU重算/source/trace audit PASS：[结果](../results/E18_20261005_intact_waypoint_recovery_results.json)。WAYPOINT-FEEDBACK/OPEN各48：Nav nominal37/37、gain35/33、wind37/35；Push28/26、gain23/15、moment20/19。Push gain feedback−HOLD+14.58pp95CI[4.17,27.08]、vsREFRESH5+4.17[−4.17,12.5]，feedback−OPEN+16.67[6.25,27.08]；Nav wind vsREFRESH5+8.33[2.08,16.67]，但最强REFRESH15为36/48，尚无稳定强fixedbaseline胜利。正常Push vsREFRESH5=0且help2/harm2，不拿平均掩盖具体伤害。所有query再做CPU读出只验证保存input的actor graph，未每步独立重编码image，明确审计范围。原1/3 wrapper3654985/6已退出，禁止重启unique。

目前是有用的候选设计线索，不是成立novel method或可投signal；继承INTACT已有共享local/goal action law、RWM/reference-control，不claim首次。下一步离开t10–25小window，新的episode与三独立发布trainseed0/42/3072确认完整部署vs强固定策略，保留人审优先I14/E20、R1–R5/状态，不预选paper narrative。


### F3：新episode、三发布seed与完整部署（2026-10-05，运行前）

对应I11/R5，兼R2/R3；F2只有条件线索，最强fixed已接近，不能继续在t10–25窗口弯绕。新两task各48episode（near/far24/24）×三独立publishedtrainseed0/42/3072×nominal/gain0.7/physics×四完整policy=3456episodes。固定goal100step预算，不从F0–F2成功/失败挑起点；新bank排除旧所有已用source episode及本地已知train/cache，公开预训练未见性未知。依原真factual continuation生成goal image/state，不使用dataset setter当原完整memory；全部warm10/state/pixels/actualgoal/factual replay exact，所有initialsuccess保留。newselectionseed121000/nav、122000/Push；startseed+1/resetseed+100+j，episode/clip ledger在任何model outcome前锁定。

四策略BASE25=完整25plan执行25；GOAL15=完整25plan执行首15；GOAL5=官方horizon1执行5（与fullhorizon5首macro bitexact才用）；REFERENCE5=每25步以原goal actor生成完整25plan/reference6latent，先执行同原首5，随后每5以真实current+预测下一reference+causal过去5发出commands查询原local inverse mean，到25或预算端重建plan。真实feedback不改变已有reference，不用actualfuturetarget/physicsstate或condition作为input。此处第一macro保持originalpolicy，非F2先执行10；全部episode的策略变化确实是新deployment对照，不与F2window直接作因果差。NO新loss、NOgate、NO阈值或融合系数。

shift从第6新步起，gain.7/Navwind+.15/Pushmoment×2与F1完全同定义；startwarm仍nominal，所有task/seed/condition/policy使用同bank。每个seed独立weights，不能把seed0三次repeat当trainseed；HF immutable0430df6…两额外archives按官方manifest SHA/bytes/sharedencoder/meta/epoch5/seed严格验，不改变既有seed0 helper、旧env/vendor或任一权重。模型放标准HF缓存。

主读数为全48task×condition×trainseed的native成功/nearfar/help-harm、REFERENCE5对全部三个fixed的paired来源+anchor cluster95CI，以及每source真实方向；不按同批选bestseed/方法或删zeroeffect shift。envsteps/encoder/head/worldcalls/实际同节点timing分别记录，不混硬件/训练量，也不拿已优化GOAL5之外的冗余fullplan当速度solebaseline。单task特定shift正而nominal/另一task不稳不能称可投；若最强fixed吸收先保留，转向data/representation/update设计，R2/R5不关。

阳控：六模型strictcfg/SHA/sharedencoder与全部sourceimmutability/BN；各实际CPU/CUDAgoalquery/localquery/manualtyped graph/clampedstd；GOAL5首macro对fullH5 bitexact；新48factual/warm/replay；初始BASE25/GOAL15/GOAL5/REFERENCE5首5同模型exact；reference首6完全按officialrollout_one_step复算。conditionalfeature只actualobservedpixels/goal/已发commands/imaginedrefs，truth仅成功与恢复；任何guard失败整组不作效用解释，留unique失败后再全重跑。

决策：三来源/newepisode跨任务/正常不伤害且shift对strongestfixed稳定增益→与RWM/轨迹tracking/其他WAM近邻完整定位和强baseline后申请人审，不能因similarabstract关闭；只比BASE25好→known反馈reference支点，不是newnovelty；某task全null→用source/task结果设计模块更新/经验监督，不继续调macro参数。单卡独立task×trainseedjob，原RTX空槽或其他已授权空卡，localdataset cache/同node timings；新资产盘点不算实验效用。
