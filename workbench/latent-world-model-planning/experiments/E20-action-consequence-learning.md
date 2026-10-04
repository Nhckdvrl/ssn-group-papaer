# E20：有限数据下真实动作后果学习（2026-10-04）

- **状态：** RUNNING；Nav15/15与Push五arm训练/离线校对DONE；新48 physical与强native闭环全方法matrix进行中。
- **类型：** PILOT
- **对应：** I14、P04/P10，R1/R2/R4。
- **问题（一句话）：** 同样有限真实分支数据下，后果相关训练/表示机制是否超越充分训练的普通预测与inverse，并改善新动作/新目标控制？
- **设置：** 原生SWM0.0.6 TwoRoom/PushT，既有venv；Stage0每task从既有100训练episodes随机固定6个，seed104200，合法physical action Box[-1,1]^2。每anchor从数据public state的t−10 freshreset/setter开始、统一10步实际合法warm prefix，实际history帧−10/−5/0与过去actions保存；不是精确原dataset hiddenstate。source selection无reward/goal/success/features。12个25-step branches全执行：zero/重复zero/factual clipped/±x/±y/smooth/negative smooth/random constant/IID/reverse IID；重复zero是恢复阳控，训练时须排除重复控制。再单独重复首branch验证。preflight只每task1anchor，完整batch每task6，预控失败不看方法效用修改。
- **读数：** 所有primitive pixels/public state与Push agent/block velocity/angularvelocity/force/torque诊断、history/action/5:5:25 future、action bounds；重复轨迹的exact error、不同合法commands的完整state/未来分歧。不以末帧或position相同宣布full equivalence，不把branchpairs当独立samples。Stage0不比较方法success，不claimnovelty；完整小bank后模型只能读history/actions预测全部branch，再由真实后果评价选择误差，另做native闭环。
- **阳性对照：** identical action/freshreset/warm prefix重复必须全部pixel/state/flags一致，跨branch history一致；different-action真实state差作为measurement阳控，若没有差异报告，不筛anchor。标准环境步进即使done仍固定记录25步（训练transitionbank非episode success评测），flags原样保存，无reward选择。
- **噪声地板 + MIE：** deterministic重复maxabs=0且pixelexact；非0则暂停当前数据bank查restore/integrator，母问题不关闭。Stage1至少3固定data trainseeds和新的锁定评估集合，数值阈值依据真实noise另锁，不能用数千pairs提高虚假n。
- **混杂审计：** 采样/实际动作都是physical合法域，模型入口才normalize；训练state标签权限全部一致，物理量仅诊断；source warm重新生成不声称原始轨迹复制。12branch全执行与fixedselection ledger先写，不读hidden outcome挑数据。原16/32/48均开发集，后续确认另锁；此144branches仅Stage0数据/接口试跑，不是完整方法证据。
- **决策表（跑之前写）：** 重复失败→查数据/接口后新unique retry、原failure保留；存在legal差异→同数据plain/effect/deterministic-probabilistic inverse连续训练；只有pixel相似但dynamic不同→保留history/多步标签，禁止合并后果；普通预测或概率inverse已解决→接受强baseline，不包装loss；effect改善error但不改善nativecontrol→调整任务/预测/接口，不只lambda sweep。
- **算力预算：** Stage0 CPU，无GPU训练，full 12anchors×(12+1)branches×(10warm+25)=5460env steps；preflight2×13×35=910steps；uint8 nodecache，大raw不入git。

## 后续训练设计（尚未运行，执行前继续锁定实际config）

同一legal branch bank/充分训练base、samewarm history、equal branch exposure与optimizer isolation；联合训练encoder/predictor而非永久冻结。首个机制为sameanchor-centered预测与stop-gradient真实后果匹配；这只是残差方差重权，不是novel贡献。普通prediction、等weight全局MSE、匹配target-detach、deterministic/probabilistic inverse及最近AD-WM结构是强对照。继续开发history/action-dependent effect code必须由首轮结果驱动；state-only线性降秩可能误伤离开障碍的作用，不预设正确。

## 结果

见下方按阶段追加。raw完整bank、code/hash/seed/训练权限与失败写回；不升级science claim。

Stage0首次CPU预控仅在数据入口失败：PushT路径被错误写成pusht.h5；没有simulator/outcome读数。原failure、log和失败源码保留于20261004-E20-legal-effect-preflight；重试改为读取已有native config的实际dataset路径pusht_expert_train.h5，记录config SHA，不重新采样/改seed/挑anchor。source/config/fileexists在生成ledger前核对；retry1为unique raw，不算方法负结果。

Stage0 retry1真实CPU预控PASS：两task共24branches/910env steps，每branchhistory相同、duplicatezero和最后fresh重复全primitive pixels/诊断state/flags/reward完全一致；源码7d721c4869cc8412f477b77d4851310cce472f40015ef06a4ed10ec8c3ad1564。实际结果只证明collector/合法动作重复契约，不证明fullstate等效或方法作用；保留firstfailure。完整6×2anchor/144branch全bank沿相同seed/协议开始，new raw/durable `20261004-E20-legal-effect-bank`，不再挑anchor。

Stage1数据协议（生成前）：Stage0完整12anchors/144branches/5460steps、全重复exact已落盘；不是方法证据。扩大每task固定44个原100训练episode，由同seed无replacement选择，first32为新增branch训练、last12为held-out branch query development；所有WM baseline可能已见这些sourceepisodes，不能称unseen states。每个anchor保留12候选全真实outcomes和fresh重复，共2×44×13×35=40040env steps，全成本计入。训练排除branch1重复控制，所有方法相同rawbank、相同train/eval split，val outcomes只label不参与sample selection；CPU不加新GPU。新collector仅可配置anchors6/44，其余契约不变，原Stage0源码/hash保留。raw/durable `20261004-E20-legal-effect-bank44`。

Stage1a训练matrix（执行前锁定，尚未训练）：Nav先用固定BASE100充分训练u5650的三个独立source seed，不永久冻结encoder/predictor；新branchbank每task44里first32训练/last12新branch query开发；每anchor11有效branches，zero重复branch1不用于训练。每job fresh AdamW/LR5e-5/WD1e-3/clip1/bf16，2000updates、8anchors×4branches，5个sliding three-frame teacher-forced futuretargets+.09 SIGReg、same sample RNG104800+seed/labels/actions。五arms PLAIN / GLOBAL-SG(额外整体现实target-detach MSE) / CENTER(同anchor中心化额外target-detach MSE，λ1) / DET-INVERSE / PROB-INVERSE(raw10维动作embedding组件，λ.1；后者heteroscedastic Gaussian NLL)。GLOBAL-SG对齐额外loss和SG，不把loss放大当机制。两inverse只是显式组件强对照，不是完整SMWM/AD-WM复现，不能用它们被击败宣布战胜近邻。

固定u0/600/2000：每个held12anchor预测全部12实际候选；goal候选ID=2+anchor%10只提供目标图，不向model读物理future；actual候选轨迹对应同共同warm状态，position成功阈值16与GTdistance作为offline读取，不把latentL2当truth。12anchor为独立分析单位，不把12×12pairs扩n；不是native闭环或confirmation，尚无方法science claim。随后必须physical-bounded CEM采样/评分/eliteupdate/执行全部一致的新native闭环（含原nativecontrol参考）和新锁定goalset；未经这步不称方法成立。CPU实际joint gradients/loss hand-recompute/中心误差分解/原生H3→5future索引控全部通过后再GPU。source SHA e8b2dee8f8aaa660022c9492c5e03f99c3ff9cca65f6f0c370e2466da550b26e，源码/数据ledger执行后冻结。首seed0五arms并行，seed1/2对应各独立充分训练source继续，不筛seed。

Stage1a root全文审/actual CPU和CUDA/bf16预控全部通过：五方法jointgradient/freshoptimizer firststep、source不可变、center与global SG误差手算/decomposition、H3历史+future5和原生rollout一致、全部held12完整bank queryeval且eval权重/buffers不变。source e8b2dee8f8aaa660022c9492c5e03f99c3ff9cca65f6f0c370e2466da550b26e。全controls/脚本/log已durable，portable E20_20261004_joint_training_preflight.json。将五arms各接source0/1/2（base devsuccess38/19/36全部保留）；source1弱不筛，方法对其增益必须面对PLAIN同data/update。五独立A100任务槽，各顺序3独立source seed，stage同nodecache/archiveSHA cb27e11df5653052d3fe6967f6c325258cf3824e1182ff80851c079ad07eb5f0，模型HF不同目录；A100 timing不混RTX。首GPU真实step确认后再扩大其余任务，不占已在用卡，source/selector/config固定。

A100实际运行扩展：PLAIN首source0已到850updates并保存固定600快照，无failure；首job完成真实I/O/训练/完整candidate query控制后，第二GLOBAL-SG slot启动，待其首步确认再扩至其余三arms。source0的单partial读数不用于筛方法；三个source和所有五方法既定均保留。

扩容前核对（2026-10-04）：PLAIN source0/1已过2000、source2到1050；GLOBAL-SG source0已过2000、source1到950。两并发真实训练约8GB/slot，没有failure；其余三目标CENTER/DET-INVERSE/PROB-INVERSE按既定2000updates×三source启动。扩至四个同node A100槽与第五个另一node同型号A100槽，所有输入已node-local stage/hash复核；不合并不同节点timing为无噪声性能结论。不依据任何partial效用筛选方法或seed。

## Stage1b：独立source episode的闭环检验（运行前锁定）

目的：Stage1a全bank离线选择能否转化为新episode/newgoal控制，同时区分继续训练收益与loss机制。固定新48个TwoRoom episodes（与BASE100、曝光1000、旧48和既有native/development来源episode取并集排除），seed105200/105201，不看WM输出；24个25-step future goals、24个75-step future goals，不把goal span叫预测horizon。两类均部署H25、execute25、最多100新envsteps，past3frames/10真实actions来自同fresh reset+合法10warm prefix；goal image/state来自原dataset，只用于目标/环境评估，未来actions不交planner。原始goal可能易/难全部保留，初始已成功单列。新set目前是方法开发验证，非事后独立confirmation。

先CPU生成sealed selection ledger与actual warm history，全部48合法factual suffix阳控、精确freshwarm重复控通过再启动模型。新CEM仅复现现有300candidates/30elites/30iterations的算法，候选在physical域生成并clamp[-1,1]，cost入口按各model同source mean/std转换，elite mean/std来自同批实际评分的physical候选，执行同返回physical mean；不只clamp cost。禁止修改原native solver；保留同budget原normalized native控制。CPU手算采样/topk/mean/std及CUDA原生rollout parity通过后再跑。raw保留每decision动作/候选摘要/hash/成本/真实执行轨迹，权重和buffers hash前后相同。

全部既定5arms×3source的固定u2000、3个BASE100 source以及released LeWM同physical接口，48×19=912episodes；released与3source另保留原native接口48×4=192episodes。每个seed方法gain相对同seedPLAIN及未继续source分别报，不筛选弱seed；所有失败记入分母、无survivor替换。主读数native success/100step、goal span分层和新steps；paired episode差值及95%CI、各独立trainseed原数，候选/goal pairs不是独立训练重复。不是完整AD-WM/SMWM复现，不把单导航验证当论文成立。失败预控只修工程并保留failure/newunique retry，不依效用改任务/预算；若离线好而闭环差，先解读候选覆盖/域迁移/代价而非lambda sweep。参考模型的预训练dataset split未核对，不能称它unseen episodes。新增cross-task、同数据replay充分训练、完整近邻和后续独立data/confirmation仍待执行。

Stage1b实控通过：新48sourceepisodes sealed/factual48全部success、terminal position误差<1e−4、goal pixels exact、freshwarm重复exact，实际preparation3360steps；其中1个初始已成功保留并单列。CPU/CUDA bounded CEM逐iteration候选、cost、elite set、mean/std与独立reference完全一致；实际训练模型normalization→原生H3+future5 cost maxabs0，权重未变。预控数学/主controller源码f02bc50a…；追加released checkpoint使用既有全dataset norm与303keys验证后的运行源码2271de3de2ecd483ec51fa9dbfd5cc8d242f0ab81ff6d1afa883fc4520b63e6a。该新增loader路径需首released完整episode运行验证；solver/cost本体未变。全部preflight/raw已durable，portable E20_20261004_bounded_control_preflight.json。首组released与3个原source的physical/native校准先运行，不根据效用改变其后五方法matrix。两独立RTX任务槽，timing不与A100 train混合。

全部Stage1a15trainruns已有complete，开始一次性CPU checkpoint/query/optimizer/RNG复核，再汇总整批；不拿单600快照筛选。Stage1b扩展主matrix到空闲A100（同family）按source0/1/2独立队列：每source先BASE再五个u2000，source0另released，共19×48。这是同hardware主比较；目前RTX的released/三BASE physical+native八组保留为接口/硬件参考，不与A100混timing或把跨hardware的single结果当methodgain。所有方法/种子/任务预算不变，仅减少等待GPU；A100每条queue必须真实free wrapper、先stage小eval cache+archive SHA验证，不抢占其他进程。

Stage1a整批结果（15/15 complete/no-failure；预定u2000）：12个真实bank查询每source，PLAIN8/11/9、GLOBAL-SG8/10/6、CENTER12/11/8、DET-INVERSE7/11/9、PROB-INVERSE10/11/11。CENTER相对PLAIN平均success差+.0833，双向source+anchor paired开发bootstrap95%CI[−.1667,+.3611]；PROB-INVERSE+.1111，CI[−.0278,+.3333]。CENTER物理选择distance差−11.04，CI[−40.07,+10.46]；PROB−8.26，CI[−26.69,+8.75]。全部区间仅描述开发不确定性，3sources/同12anchor，不把36条当独立episode/trainseed；没有novel/control成立证据。概率inverse是已有组件强对照，其较稳定开发线索优于只救CENTER。闭环既定matrix不变；下一步关注完整近邻/跨任务/同数据replay与后果机制，不做CENTER阈值堆叠。

一次性全checkpoint/query校对PASS：同source所有方法u0全部12候选scores/selection bit-exact相同；three source initial/checkpoint hash不同，同seed source/hash/数据相同；15组完整12候选真实distance/argmin/native Nav阈值/计数复算；u2000 HF SHA与snapshot一致，fresh AdamW297或301states全step2000，末batch RNG跨方法完全一致。raw audit与完整输出durable20261004-E20-joint-result-audit，portable E20_20261004_joint_candidate_results.json。未升级science claim，真实native闭环仍在执行。

## Stage2a：操作任务的同机制检验（运行前）

不根据Stage1a排名挑方法：五arms全部同配方拓展PushT，first32/last12固定bank44，batch8×4/2000updates/五teacher future+.09SIGReg/同loss系数，encoder/predictor共同训练。初始为官方充分训练LeWM PushT同一个发布checkpoint，首exploratory seed0；pretraining split未知，不能称固定100-data从零训练或三个independent sources。native full HDF norm沿原资产，HF source SHA0c095fc4a26856678f67bf299f261506b45f1a25fbdb4cbb8828b4a8281dc048；每arm重新strictload原303weights、fresh AdamW，不带其他arm optimizer/weights/RNG。sample RNG105800，所有armmatched；参数/aux结构与Nav组件完全一致，不追加物理GT训练标签。

主读数是全部12真实branches的选择native Push成功（position前4维距离<20且wrap角差<π/9）；7D state_dist只次读数，完整body/velocity/force诊断不得替代原native success。goal为2+anchor%10实际branch图像，目标和GT只eval时用，deployment model只warm pixels/actions/goalimage。同shape256images batch不能静默丢掉warm history/未来索引；CPU loss手算/原生index parity与CUDA实际joint step/全部12held queries通过后才train。三份u0/600/2000同样保留；12anchors不可当144独立trial。额外模型pretraining/复用条件与Nav不同，跨task只比较各自同source方法gain、不合并绝对分数/timing。freshactual bank完整cost已在Stage1记账，不重买branch预算。单RTX sequential五arm可摊薄NFSimport、不占新ACTIVE资源；失败保留且停止queue，不筛幸存arm。闭环和≥3本地train seeds/data resampling与完整AD-WM仍后续必须，不把单tasktransferbank影子登记novel。

Stage2a五arms真实CUDA/bf16预控全部PASS：source strict303/同initial、实际joint gradients/freshoptimizer1step、所有12held queries且eval不改模型；原生H3+future5 cost差0；144个Push候选的native position+wrapangle成功契约逐项一致。源码42285bb9e33d0cf96dbfc33d5d8bf17b1080038646d3d7bb1de6fed8d1a0e2f4，引用loss helper e8b2dee8…。完整controls/raw已durable20261004-E20-transfer-preflight，portable E20_20261004_transfer_preflight.json。现在五方法sequential RTX单slot开始训练，禁止重复启动或根据600snapshot筛arm。

Stage1b接口范围补记：physical CEM目前以physical零均值/unit std初始化，native以normalized零均值/unit std初始化；转换后initial search scales不同。因此二者差异包含bounds与sampling-coordinate/scale，不能称“仅clipping修复”的因果效应，亦不能据其较低读数判WM方法上限。新method主matrix严格同physical协议，并保留native强reference；后续若要归因bounds，需额外matched-affine initialization校准，当前不根据partial method结果改正在运行主matrix。

RTX接口校准整批8组/384episodes complete且trace SHA/shape/真实success/physical全bounds/48保留复算PASS：发布near/far physical20/6、native21/10；BASEsource0=13/6 vs21/9、source1=12/3 vs14/5、source2=12/5 vs18/8（各tier24）。接口差值不单独归因clipping，initial search scale同时变；不能把physical读数当强base能力上限。方法主比较A100全19model仍未齐、不据partial改研究命题。portable E20_20261004_interface_calibration.json，审计durable20261004-E20-interface-calibration-audit。

Stage1b跨节点故障校对（2026-10-04，CPU排查运行前）：三个A100队列均被warm-history pixel-exact守卫拦截；当前不使用任何该批效用读数。先完整保留各失败目录/config/log，再对锁定48个anchor逐一复算warm、重复restore和factual suffix，比较像素、真实position轨迹、SWM/pygame/torch版本与render backend。阳性是同节点fresh repeat与原factual控制，参考为原RTX缓存；不删anchor、不放宽守卫、不改目标/方法/预算。若是CPU渲染实现差异，记录差异来源；若物理轨迹也不同，先修契约再扩。可将完整方法matrix重定位到原RTX硬件并复用已完成同协议BASE/released对照，但须unique run且保持全五方法×三source，不混hardware timing。排查是工程校对，不是新science claim。

故障初步排查与安全重定位（运行前）：A100节点完整48个factual轨迹均与RTX参考逐state exact，fresh repeat均exact；46/48 warm图像仅1级uint8差异，具体CPU数值dispatch原因未确认，不能冒充软件版本不同或物理模型失真。为不靠放宽守卫推进，主闭环matrix先在原RTX硬件运行全部五方法×三个source（15×48），与已完成同硬件同代码同ledger的BASE/released physical对照配对；A100失败完整保留。新队列bounded_local_method_queue.py/new raw20261004-E20-control-{METHOD}-s{seed}-physical-RTX，固定u2000/checkpoint/hash与预算，当前唯一空闲GPU1；完整矩阵不按partial选择。原native接口保持强参考，不把physical收益独立解释成模型收益。后续只有跨节点CPU契约明确后才恢复跨节点simulator评测。

Stage1b强接口补充（追加运行前）：原native BASE/released与full AD明显比physical reference强，但初始化坐标/尺度与bounds一起变动，不能把任何方法只在较弱physical接口的收益包装成模型贡献。追加全部同15个u2000模型的原native接口48×15，不挑方法或source；同RTX、same fresh48、300/30/30、H25EX25/100step、原归一化与seed不变。physical整批保持原任务，native是预先完整新增factor，两接口分开报告及配对，不用partial选checkpoint。新native_method_queue.py/raw20261004-E20-control-{METHOD}-s{seed}-native-RTX，原Push五armqueue自然完成释放GPU3后才取得槽；不杀训练、不共占其他job。闭环gain须面对同data PLAIN与strong native，所有原阳控/tracehash/权重守卫不变。

Stage2a PushT整批完成：五arm均2000updates/no-failure，全部source/norm/helper/数据/batch RNG一致、u0查询bit-exact、freshoptimizer 297/301states全2000。actual positions+wrapped angles/native成功判据逐query独立复算及两checkpoint/source SHA核验通过。PLAIN/GLOBAL-SG/CENTER/DET/PROB=4/4/4/3/4（各12），paired-anchor开发CI均跨零（DET差−.0833，95%[−.3333,.1667]，另三个对照差0但区间[−.25,.25]）。发布source pretraining未知、仅单transfer seed、held新branch不保证新states，不能叫跨任务确认或native闭环负结论；truebank包含exactgoalcandidate。结果E20_20261004_pusht_candidate_results.json，audit durable20261004-E20-pusht-result-audit。当前不继续调center/inverse系数；完整近邻、原native强接口、新wholeepisode控制、原experience replay与真实value机制是更有信息的设计问题。

### Stage1b physical整批结果（2026-10-05记录，原20261004运行）

15/15方法组及三同协议BASE均complete，864episodes全部trace/checkpoint SHA、实际状态/动作/步数/原native成功阈值、同RTX/ledger经独立复算。每source48：BASE19/15/17、PLAIN20/32/21、GLOBAL-SG15/29/17、CENTER19/27/20、DET18/22/20、PROB16/18/21。相对PLAIN平均success差依次−.0833/−.0486/−.0903/−.1250，paired source+anchor分层bootstrap95%CI分别[−.1875,.0208]/[−.1597,.0556]/[−.2153,.0069]/[−.2986,.0417]。这些辅助目标没有稳定胜过同数据PLAIN；CI宽，不宣布普适有害。新episode、目标与controller相比小bank均改变，不能把离线→闭环差直接归因单一指标。仅physical接口，强native全15仍按既定矩阵执行；不把physical当模型上限。结果[完整JSON](../results/E20_20261004_fresh_physical_control_results.json)，audit durable20261004-E20-fresh-physical-control-audit。科学主张0保持。

## Stage3：新增经验价值与训练利用的必要对照（2026-10-05，运行前）

对应I14/P04，研究有限经验怎样改善广泛规划用途，而非为CENTER救系数。physical矩阵只提示新增branch普通训练比aux更值得理解，尚不能区分训练时间、原经验遗忘和batch覆盖。沿用同三个BASE100源u5650与原归一化、同32训练anchors/排除重复branch1、全部12开发queries及新48闭环。已有GROUPED-PLAIN作为固定参考；新增三个arms全部×source0/1/2：IID-BRANCH（32独立anchor/branch项，允许重复）、REPLAY-ONLY（32原100episode事实clip，无新增分支）、MIX（16 IID新branch+16原事实clip）。同B32/2000 fresh AdamW更新、5e−5/WD.001/clip1/bf16、五teacher future targets、八frame SIGReg.09，全encoder/predictor联合更新，不加aux、不换初始化。新branch bank一次生成后共享，不新增sim采集。MIX新branch曝光为IID的一半，明确不是同新增数据曝光因果对比；所有arm总encoder样本/计算相同。三个源是独立trainseed、共享数据/48任务，不称独立数据采集。

原事实clip必须重建每wholeepisode合法start：range(cache_row, cache_row+n−35)，像素offset0/5/…/35，35真实actions→7宏动作+第8dummy；不能复用旧n−20 clip starts，否则跨episode。重建5795合法clips、100episode边界与有限actions逐项assert；held query分支不入新增branch训练；原100事实replay包括WM已见的held分支source episodes，所以该小bank仍不是unseen-state检验。fresh48 episodes与原100和branch来源完全分离。原分支与事实history各占其自身合法indices，真实state/goal/held outcomes不进loss或sampler。取batch均匀规则事前锁定，不依held效用选样本。

主读数：固定u2000原native新48 success及source原数/配对CI、真实envsteps；physical作同接口辅助。小bank真实selected distance/success仅开发诊断，不当长任务收益。阳控实际数据索引/teacher目标五项手算/SGReg八frame一致/PLAIN aux精确0、freshopt所有297states step1且源权重不变、原native H3+5 cost parity。噪声源三trainseeds既有19–38/48，完整配对source+anchor不扩n。事前决策：IID胜GROUPED→数据组织成为候选解释而非即刻SIGReg因果；MIX胜IID→面对replay成熟近邻进一步分离训练保留和新数据曝光；REPLAY同等或更强→不能把新增sim数据当有效采集，转向更有信息的经验/预测对象；均无增益→不调lambda，读完整AD/value支点重新设计。任何一格失败保留并停对应队列，不筛种子。预算九×2000独立单GPU任务；先CPU/CUDA实际预控，值学习GPU自然释放后再用空slot，不能修改在跑源码。所有模型HF、缓存node-local，raw含代码/hash/optimizer/RNG/失败；闭环必须原RTX精确历史守卫。

跨领域来源定位：StreamMAE（arXiv2609.40333，§4/AppA）研究batch内近重复与独立shuffle控制，不能把它的MAE结论直接外推JEPA/SIGReg；MBPO（1906.08253）研究真实state分支短模型rollout以控制模型误差，和我们的真实counterfactual采集/联合表示训练不是同一方法。经验replay与batch多样性都是成熟设计，当前三arm是必要强对照，novelty仍须来自真实规划痛点及超出这些对照的有效增量。

### Stage1b strong-native整批结果（2026-10-05，独立复算）

15/15方法组与三same-hardware BASE完整864episodes，trace/初始state/步数/native成功/源训练→评测checkpoint hash全部PASS。[结果](../results/E20_20261004_fresh_native_control_results.json)，durable20261004-E20-fresh-native-control-audit。每source48：BASE30/19/26、PLAIN26/29/27、GLOBAL13/32/17、CENTER25/34/27、DET17/29/28、PROB24/19/28；对PLAIN平均差GLOBAL−.1389 CI[−.3333,.0486]，CENTER+.0278 [−.0833,.1458]，DET−.0556 [−.2014,.0556]，PROB−.0764 [−.2292,.0694]。保留全部sources和两接口。CENTER不是稳定方法gain，原生相对physical方向不同不能归因单bounds。广泛部署比较仍未支持novel方法，Stage3必要数据利用对照不因这些数字筛arm或换任务。

Stage3最终CPU/CUDA实际预控全部PASS（源码4c4d5c45d06ed5da2a54f79bf6e568b06c9c53ebc0d7055aba4273bee1b8ce4b冻结）：三arm真实B32/8frame、5795完整边界clip、原五teacher target手算/aux精确0、全部297参数finite梯度/freshopt step1、源权重不变、三源严格加载、H3+5原native成本maxabs0。预控key no_query_sampling仅指branchbank的held12不参与新增分支采样；replay原100仍包含原模型见过的held-source episode，不能当未见状态证据。CPU/CUDA artifacts durable20261005-E20-experience-{cpu,cuda}-preflight，portable E20_20261005_experience_utilization_preflight.json。完整训练只在这两预控与源码hash一致时启用。

Stage3部署补充（运行前）：固定九个u2000，全部原RTX新48、原native优先再physical，各9×2×48=864episodes；同ledger/seed/300-30-30/H25EX25/最多100steps/精确warm守卫，所有checkpoint/训练complete/hash确认才部署。experience_control_queue.py独立等待queue，不改既有matched/effect/exposure训练或bounded_control源码。训练失败持久镜像并停止，不筛存活种子。

## Stage2b：PushT新起点实际闭环（2026-10-05，运行前）

对应I14/P10/R1/R4，用真实操作控制补充Stage2a的小bank离线比较。固定48新source episodes，排除现有Push branchbank全部44与E17 train/eval开发sources；发布WM原预训练split未知，不称未见pretraining。episode从长度≥86的原专家数据均匀抽取，seed109000/109001，24短25未来/24长75未来goal；planner仍H25EX25/300-30-30、最多100新steps。不把goalspan称预测horizon。source clip用fresh reset+public7D setter，然后原合法10步warm生成三帧；goal由该实际factual continuation生成，避免用dataset图像假设接触solver恢复exact。保留全部合法clip，不能按模型/成功挑anchor；先密封source/action ledger，再生成真实goal派生表。实际factual目标replay与freshwarm跨重复状态/图像逐点exact为阳控，所有48均须过；不是完整原dataset物理状态恢复、不是原paper数值复现。

保持Push relative=True/action_scale100，真实action Box[-1,1]^2；不把它误作absolute positions。native接口保持原normalized CEM初始化与unscale，Push真实step不clip，明确issued command可以超Box，模型比较只限同接口；physical接口所有candidate/execute均clamp，作为独立factor，不因其较弱或较强选方法。成功逐实际状态按原eval_state：前4位置norm<20且angle minimum(|Δ|,2π−|Δ|)<π/9；7D含速度distance仅辅助，实际envdone须与独立成功手算一致。不让factual futureactions/物理diagnostics进planner，只有三pastpixels、十pastactions与goalpixels。初始success全保留单列，四replans/100step预算不改。

部署全部PLAIN/GLOBAL/CENTER/DET/PROB五个原锁定u2000与released LeWM，共6×2接口×48=576episodes；完整发布AD-WM另两接口96episodes参照，训练数据未匹配，不作公平loss因果。五个transfer只有一个trainseed，held48episode配对bootstrap不能升级独立trainseed或确认性结论。所有checkpoint/source/trainingcomplete/hash、runtime/task/controllerconfig、轨迹hash与成功判据保存。主读数success/newenvsteps、每goalspan原数与配对CI；阳控factual48与modelnative parity，噪声地板完整固定任务下配对离散波动。方法若只bankgain而闭环无效，重新考虑学习与任务覆盖；若操作/导航不一致，先看真实动作作用/表示/数据结构，不能调loss系数强救。CPU prepare全部guard通过再启GPU0（原任务自然释放，wrapper确认free）；单GPU独立queue、无环境改动，模型HF/raw本地。失败持久记录，不放宽物理守卫或挑能通过的seed。

2026-10-05实际运行补记：Stage3三个A100 arm队列已真实训练，各8GB，PID/原source0/1/2见当日日志；不是只写卡。Stage2b CPU48全部warm/完整diagnostic轨迹/goalpixels factual repeat exact、factual48成功，5760准备steps，全部初始success保留；portable E20_20261005_pusht_fresh_prepare.json。首本地Stage3 shell detached launcher PID3531292退出、日志为空且无CUDA/模型输出，原因未确认；它不构成method failure/efficacy，日志纠正。改独立process-session launch PID3536169（Stage3 RTXGPU3），新增Push全7参考/方法两接口queue PID3536170（RTXGPU0），均free-GPU wrapper，不重复任何有输出run。第一个非initial-success的控制决策强制执行model-native parity后才跑CEM。

Stage3九trainruns全部complete/no-failure，独立source/u0 scores、297freshopt states2000与finiteweights/moments、64k encoder样本的新旧曝光、sampler RNG/边界、全部真实candidate argmin/distance/success复算PASS。固定u2000小bank每source12：GROUPED-PLAIN8/11/9，IID12/12/11，REPLAY11/11/11，MIX11/10/10。对GROUPED差IID+.1944、paired source+anchor CI[0,.4167]；REPLAY+.1389[−.0556,.3889]；MIX+.0833[−.1667,.3611]。仅WM已见source的新branch开发、同12queries，CI不是36独立任务；近完美bank排序不是可复用闭环能力。REPLAY同样改善，新增counterfactual经验价值不能由IID alone确认，不能把shuffle改名paper。强new48两接口整批controller仍未齐，不读partial筛方法/调目标。结果E20_20261005_experience_candidate_results.json；durable20261005-E20-experience-result-audit，代码与计数完整。

## Stage4：经验与规划表示的交互（2026-10-05，运行前）

对应I14/P04与备选I09：同样counterfactual经验可能适合学习动作后果，却不适合随意改变planner使用的状态几何。该交互是待检验假设，不归因当前encoder drift/SIGReg，也不把Value-Guided JEPA/FIRM的分阶段/混合数据重新命名为novelty。最小crossed2×2：固定两已取得的encoder/projector，PRED（同data A100 ABS源0u5650）与VALUE（同data VGIQL-SEPARATE源0value_phase_u2825）；各只重新训练动力学，FACT（原100事实经验）或MIX（64事实+64新legal分支）。两个encoder有不同训练目标及5650/2825 prior预算，因此不是纯value-objective因果；数据效应只先在各固定encoder内比较，交互是conditional pilot，所有prior成本单列。

四cell同公共saved-init的predictor/action_encoder/pred_proj初始tensors，不能保留PRED已训decoder再称sameinit。encoder/projector参数与BN全部冻结eval，严格hash前后不变；93动态参数fresh AdamW5e−5/WD.001/clip1/bf16，2825updates/B128，八frames/五teacher future MSE，无SIGReg/aux；固定目标不参与grad。原事实5795合法n−35 clips，MIX newanchors0–31/排除duplicate1，全uniform独立采样，firstbatch/sampler两RNG/exposure计数保存，所有四cell的总encoder样本128×2825=361600，其中MIX各180800；FACT361600old/0new。额外sim步骤0（共享已生成bank），新增branch成本按原bank/训练实际使用anchors单列；不把FACT与MIX叫equal-interaction-cost。encoder geometry不横向比MSE能力，用真实动作后果与规划。

主读数：新48 wholeepisode两接口sameH25EX25/300-30-30/100step、各goalspan真实success/newsteps；held12真实candidate regret/endpointdistance作为开发解释（sourcestates已见，不代替control）。参考保留same-seed充分ABS24/30与VALUE-SEP33/32（physical/native各48）、full AD发布data unmatched、大data full exposure强参照，不能只赢重置后的弱decoder就称novel。阳控两geometry严格snapshot键/每tensor拷贝、同93动态init、实际B128索引/五TF target手算、frozen204无grad且BN不动/动态93finite freshstep、源checkpoint不可变、model-native H3+5 parity；CPU/CUDA均过才铺四训练。噪声先一个exploratorysource，paired48不等于独立trainseed；如signal扩既有三source/第二task/预算。

决策：MIX只在VALUE下有控制收益→进一步分辨goal geometry、数据覆盖与模块职责，并探索更强可复用设计；两geometry均收益→先保留简单data baseline；heldbank好但control差→不调少数query/λ，回看可复用预测对象与目标空间；四cell均null→用完整强baseline/两task新结果换竞争机制。母问题R1–R5持续开放；当前不切paper narrative或状态。两个空A100slots各固定geometry FACT→MIX sequential，node-localcache；模型HF/raw/durable unique20261005-E20-geometry-{PRED/VALUE}-{FACT/MIX}-A100-s0。实际timing/VRAM/I/O先由CPU/CUDA一步确认，不因为卡空就盲铺。

### Stage2b / Stage3 完整实际闭环结果（2026-10-05）

[全部Push672](../results/E20_20261005_pusht_fresh_control_results.json)14groups与[经验利用864](../results/E20_20261005_experience_control_results.json)18groups全部complete，独立trace SHA/初始真实state/native成功事件/全部48分母/≤100steps/训练checkpoint/hash/interface与sameRTX hardware校对PASS。Push native RELEASED24、PLAIN5、GLOBAL6、CENTER6、DET6、PROB3、完整AD-reference26（各48）；physical21/6/5/4/6/3/29。PLAIN对released native−.3958 CI[−.5417,−.25]，physical−.3125，原发布预训练未知、单transferseed，不能叫一般分支学习必然伤害或归因表示漂移。对PLAIN所有aux native差CI均跨0。all7模型/两接口/所有原48包括1初始success完整保留，不以失败换任务。

Nav原native GROUPED-PLAIN26/29/27；IID28/27/21，REPLAY27/33/22，MIX32/19/27，各source48。IID相对GROUPED−.0417 paired source+anchor CI[−.1667,.0833]；REPLAY0 [−.1458,.1458]；MIX−.0278[−.2292,.1528]。physical分别GROUPED20/32/21、IID25/24/17、REPLAY22/19/15、MIX20/12/26，三gain CI也跨0。新data/旧replay small-bank进步都没有稳定新goal收益，不能把12query近完美当方法成功。Stage3原三train queues及RTX18control PID3536169、Push14control3536170均自然完成，不重复unique run。raw audits durable20261005-E20-{experience-control,pusht-fresh-control}-audit，全部开发效应/分层/steps/来源在portable JSON；science claims0保持。

新增独立审计reader曾因Python3.10无hashlib.file_digest、Nav rows没有initial_success字段被拦；修为逐block SHA与从真实state独立派生initial_success（Push已有flag仍strict核对）。没有训练/任务/轨迹改动，也没有部分结果当完整结论。Push audit保存实际使用的first审计版本，Nav保存schema兼容版本。

Stage4最小crossed4cell代码geometry_experience.py已写，CPU实际B128预控正在执行；A100实际CUDA全部四cell数据索引/五teacher target手算、204frozen参数及BN buffers不变、93finite动态梯度/freshoptimizer1step、strict共同init和native cost parity均PASS。只有两预控complete/hash匹配才训练；不能将代码/预控当正式run。Stage4是对经验价值×模块职责的conditional探索，不切新paper narrative。

Stage4实际CPU/CUDA四cell B128全部PASS，portable E20_20261005_geometry_preflight.json；geometry_experience源码冻结且训练内强制双preflight/helperhash。两freeA100任务slots已launch：PRED physicalGPU2 PID3627210、VALUE GPU3 PID3627276，每条FACT→MIX各2825。log/tmp/latent-E20-geometry-{PRED/VALUE}-A100-queue.log；需查真实step，不把nohup PID当完成训练。geometry_control_queue.py固定终点后sameRTX完整4cells×2interfaces×48=384，全matrix无partial筛选。
