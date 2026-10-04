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
