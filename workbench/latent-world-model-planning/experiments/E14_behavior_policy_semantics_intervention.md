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

## Stage G0：相同事实经验中的目标条件策略强支点（2026-10-05，运行前）

推进I09/R1/R2/R3与P04/P05。E14已知Bellman几何far收益重复，E13A8预测对象×几何单source有交互，尚不能把所有现象归CEM或首次两表示。新增竞争设计直接从原事实轨迹学目标条件单步动作；继承公开GC-IDM 2605.08732，非novel方法或其原paper完整数字复现。vendor commit48c45b1cb2b34dd2c1c61d222c8309de567fde55已读model/dataset/train/eval：官方原始动作训练，policy直接返回原始动作；horizon=min(remaining budget,50)，逐步真实反馈；不能额外反标准化。官方CLI默认200epoch/8192/3e−4与README/论文50epoch/1024/1e−3不同，事前选后者，不结果后择优。

固定原same100事实、已有PRED/VALUE source0/1/2 FP32缓存9295帧，各自身几何冻结且全部六源Hash/BN已审；利用原cache_manifest.layout重建episode IDs/next-step合法索引，不把35stepclipstarts作next-step全集。每source两个geometry×三controller：GC-IDM（hindsight goals1…50/实际horizon输入）、GCBC-MATCHED（同goal/数据/模型capacity/init，只把horizon输入置0）、PAIRWISE（goals仅下一帧/horizon1，监督分布改变是强支点，不称horizon-only ablation）。最大未来min(50,episode剩余)，不跨episode；原生raw2D动作MSE、official1.5M MLP/3×512/LN/GELU/dropout.1/64sin+AdaLNzero，小head训练。

各source common官方head初始化115000+source、split/shuffle115200+source/goal115100+source，within-source全部六head初始相同，GC-IDM与GCBC goals/样本相同。采样全部next-step合法starts，90/10frame split只作优化diagnostic（同episode并非held-out episodes）；所有方法使用相同split与每epoch无替换shuffle，B1024/drop_last、50epoch/AdamW1e−3WD1e−4/cosine→1e−5/clip1/FP32。固定final50终点，不按validation或efficacy挑best，样本/updates/cost独立记账；不同heads训计算不同于A8，不称matched total model training。

阳性对照：重建全9295frame layout无孔/重叠、每start+goal同episode与1…50、训练source不含新48evalepisodes、phi-source/features/actionsSHA；独立officialDataset真实样例对齐raw action/goal/h；manual AdaLN-zero初始horizon无影响/解除零调制后goal和horizon真正有通道；实际B1024 loss手算/freshopt1step/finite gradients、frozenphi缓存不可变、CPU与CUDA预控过才训练。部署预控另检官方policy encode/remaining clamp/原动作返回与自写controller一致、全部exact warm pixels/states；这些部署控没有跑完之前不启动闭环，不把script准备好当结果。

主读数：完整全部source/geometry/三arms原新48、100step budget、逐step真实反馈、native success16px/trace独立复算；同raw action native及clip[-1,1] physical两输出边界版本（GCpolicy不包含CEMproposal coordinate），不得混称与CEM接口只有一个因素不同。50step成绩另保留但不选budget；near/far/overall成功与help-harm paired source+anchorCI，action MSE仅辅。要问这些经验能否经不同使用方式形成可执行控制、goal distance支持规划是否也支持policy，以及传统反馈/动作抽象能否吸收A8交互。不是局部λ优化或为已有故事补一张小表。

噪声地板：3train sources共享100train/48开发tasks，不能说144独立任务；PAIRWISE不指向远goal训练goalshift已知；paper pretrain/scaler/numerical协议未完全匹配。决策表（跑之前写）：GC-IDM/GCBC同目标数据即可强控制→提高独立policy baseline并检未来cost/shift/task复用的actual delta，不发明GC-IDM；task geometry利于CEM却伤policy/反之→设计input/output角色与训练对象的跨使用比较；全部弱且pairwise阳性好→分解hindsight目标行为可预测性/coverage，避免把CEM失效当全部世界模型上限；阳性失败→halt/留failure，不出方法胜负。独立A100slots，每head小，本地FP32 features只MB/no视频streaming、不改RESEARCH_PLAN优先/工作台状态。

G0部署启动前校对：18个固定50epoch训练全部DONE（各400updates/409600samples），12个actualCPU/CUDA训练preflight全部PASS。官方Policy组件以AST完整抽取原GoalConditionedPolicy类，避开同文件不相干缺失PairwiseIDM导入，类body不改；实际source/encoder/projector/动作返回与0/50/99步remaining clamp对照、6个source×geometry各CPU/CUDA预控、全部48exact warm守卫先过才闭环。GCBC输入0/PAIRWISE1覆盖与官方Mode wrapper相同，三个方法raw动作，无错误逆标准化。controller保存success_by50及100完整轨迹，明列逐步反馈与CEM25承诺差别；1728完整source×geometry×arm×interface×48，正式summary等全部36groups齐后独立复算。

### G1：操作任务目标条件策略支点（2026-10-05，数据编码前）

不把G0导航比较变成单环境结论。先为PushT建立真正可训练的原事实goal-policy数据：固定发布LeWM encoder/projector，原HDF首86episode全帧、下一primitive action与1…50未来goal（原raw动作），与fresh48源episode全部disjoint。原发布encoder预训练split未知，明确这是head训练未见episodes而非整个系统unseen。只一次节点本地HDF顺序读/FP32 frozen encode，禁用DataParallel/跨节点stream，保存每episode row边界/episodeIDs、source模型SHA、HDF文件路径与既有hash参考、各encoded arraySHA、full frozen weights/BN不变。

G1首先只编码资产与阳性控：真实原224RGB、同ImageNet normalized、encoder/projector严格303源、native encode与手算投影/小batch一致容差，first86frame ranges不重叠且future目标不跨episode、actions原样保存（terminal NaN保留/训练排除，不能标准化后再按raw执行）。编码pipeline若失败保留source/log，不出方法效用。下一GC-IDM/同goal GCBC/PAIRWISE各至少1训练seed，沿G0预控后完整原Pushfresh48/真实success角度+位置/100steps两输出bounds审计；仍未部署或确认Push方法gain，不以资产生成代替实验。对照已有发布CEM24/21与joint5/6，后续实际模型/采样/部署预控另补启动记录。没有增加sim训练steps，不支持模块冻结本身是novelty。

G1节点可行性修正：A100 source-loader通过后打开原HDF失败，该节点没有/tmp PushT文件；无encoder样本/训练/效用输出，旧source/log/failure完整durable保留。原文件46GB只在原RTX节点localcache，不跨节点复制/重复下载。新独立features-retry1源码仅改unique路径，在实际含该文件的RTX physical3运行，同first86/模型/输入/全部guards，不重抽episode或移除起点，hardware按实际记录。

G1编码已完成retry1：86episode/9374实际帧，发布全303参数与BN hash不变，三个原始pixel批次native encode bit-exact、subset误差≤2.15e−6；只有打开文件的节点改变，数据没有重抽。新增source0 exploratory三head GC-IDM/GCBC-MATCHED/PAIRWISE，训练沿G0已控的官方组件/FP32、50epoch/B1024/400updates、raw2D单步action、samegoal/初始115000/split115200/goals115100；用9374frame独立episode map重建合法next-starts，90/10frame validation不当held-episode；固定final50，不选bestval。新Pushadapter只复用冻结G0函数，通过显式输入加载替换接入实际Push数组，source_adapter SHA和used原组件/adapter完整记录，所有Nav源/原script不改。实际CPU/CUDA官方Dataset/LOSS/AdaLN/梯度与sampler前控全部PASS才允许三head训练；部署尚未启动，须另Push真实角度/位置成功、full25D exact起点/像素与原Policy raw动作控。


G0整批1728控制已DONE，36groups+24对象参考轨迹/源/全成功事件独立审计PASS，见E14_20261005_goal_policy_control_results.json。PRED GC-IDM43/46/44、GCBC43/44/44、PAIRWISE14/19/22；VALUE38/38/39、41/41/41、42/30/40（native各48；output-clip physical全部同数且逐动作相同）。PRED GC-IDM相对同geometry DIRECT +16.67pp CI[4.17,29.17]；geometry对GCBC无稳定差，GC-IDM对samegoal GCBC在100步无稳定增益。所有低结果保留。新增成熟策略支点阻止把DIRECT对弱LOCAL收益当新方法成功；policy逐步实际反馈/不同容量与target/compute等都是联合改变，不叫CEM单因素因果。

时间读数精度校正：保存的success_by50是100步budget controller的前50步（GC-IDM前50步h输入一直50），**不是另跑50步预算policy**。first audit effects的budget字段过于含糊，原full artifact/source保留；v2只修正metadata为controller_budget100/evaluation_prefix_steps50或100，并重新独立全trace校对，实际成功/权重/动作/CI未改，未结果后新增读数。前50步GCBC明显更快，但不能因此claim它胜GC-IDM在独立50step-budget协议；该独立协议尚未运行。

G1完整三个head终点独立审计PASS：共同官方CPU initial exact、每400AdamW state/finite、全部50epoch goal/shuffle RNG重生/firstbatch/409600items核对，portable E14_20261005_pusht_goal_policy_endpoint_audit.json。actualRTX，而目录A100是复用组件的legacy basename；源码/feature metadata/cfg/launchlog标明，禁止pool硬件timing。现在启动原Pushfresh48×三policy×raw/clip两个边界共288 controllerpipeline；预控先AST官方Policy对0/50/99 remaining/raw return exact、全部48/full25D warm state-pixels/native成功定义，CPU+CUDA六head对照齐才允许任何闭环读数。
### G2：策略输入的动态状态对照（2026-10-05，运行前）

推进P04/P05、R1/R4：强GC policy在导航可用，不自动说明单帧配置足以支持接触操作。继承FIRM配置/动态记忆与GC-IDM从真实观测提动作，先作高信息量matched history对照，不claim首次memory或新方法成立。任务Nav原PRED source0与Push published source0；各2arms TRUE-HISTORY与CURRENT-COPY。固定原训练facts缓存，合法starts要求同episode有此前10primitive帧，当前动作finite/下一帧合法；两arms使用完全相同starts、head初始化115000、shuffle115200、futuregoal115100、训练量50epoch/B1024（实际update数按两task合法starts披露）、原raw动作/MSE/LR1e−3/cosine/WD.0001/dropout.1/clip1/FP32。

官方GC-IDM配置embed_dim576：当前输入concat(phi(o[t−10]),phi(o[t−5]),phi(o[t]))；COPY三个位置均phi(o[t])，goal输入三个位置均单幅goal embedding，horizon输入恒0（沿strong samegoal GCBC）。容量和初始完整tensors严格共同；真实history与COPY原始goal/action/采样indices逐例一致。不是训练联合encoder或完整belief/FIRM复现，head训练episode disjoint但Push published phi pretrain未知。未来hindsight跨度1…min(50,剩余)不跨episode，不用true物理state、goal velocity/outcome作为policy feature。

阳性控：CPU/CUDA实际B1024 loss/gradient/step1finite，history-lag准确到原episode缓存边界，人工置换旧帧只改变HISTORY输入/COPY不变，同init原AdaLNzero/官方classbody不改，goals一致，phi缓存hash不改。部署必须重新实际warm replay记录11primitive帧，逐帧历史更新，抽0/5/10帧与既有bank3帧exact/fullstateexact；goal设置不改动力学。前10步不能用未来帧或重复goal填充。deployment100steps/raw与clip两输出版本原fresh48/near-far/完整trace/native success与独立审计，四methods所有弱结果保留。单seed×两taskpilot，不以48共享开发tasks报确认。

主读数同task HISTORY−COPY paired success/near-far、真实action误差仅辅，既有GCBC/GC-IDM及完整CEM作capability参照（训练合法starts与容量不同明列）。noise为24+24开发任务配对CI/单headseed有限。history改善Push而Nav相近→下一完整WM方法加入可学习动态状态、动作后果监督与任务配置职责；COPY吸收→容量/训练解释优先；两者均弱→进一步数据覆盖/多模态策略与长任务组合，不依据这个冻结head负结果关闭R4。不调lags或挑弱baseline证明history，固定10/5/0作为已有LeWM三frame接口参照。

### G3：策略数据覆盖与计算的独立校准（2026-10-05，编码前）

G1全部288控制及独立trace/hash/native-angle审计PASS，GC-IDM/GCBC/PAIRWISE1/2/2，各48且均含一个initial-success；发布CEM24/21保留。不能从只86条head训练与成熟publishedphi的失利断言策略范式或memory因果。G2历史对照已独立运行；G3另测经验覆盖×计算，不等它来为history故事挑数据。实际HDF为18685episode/2336736frames，不是既有summary误估233673；禁拉全量。固定同publishedphi，缓存现有first86的9374帧直接复用，再append最小编号774个不在fresh48评估来源的episode（共860，含原86），一次节点本地顺序编码/原逐episode B64/FP32/全weights-BN frozenhash。只有事实pixels/actions，不含物理states/新goal/outcome。所有source/array/layout/SHA与first86subsetexact审计；HDF全hash未重读明确披露。

后续锁四独立heads：同goal/horizon0 GCBC-MATCHED、同initial115000、B1024/AdamW1e−3 WD.0001/cosine eta1e−5/dropout.1/clip1，数据86或860 ×400或4000updates，从头各自freshopt；固定终点而非bestval。每update均匀有替换sample合法next-starts、hindsight1…50，indices采样115200、goal115100，固定验证90/10frame split的局限。新400与旧G1虽曝光相同但采样/调度参数化不同，要保留新86×400作匹配基线，不能直接借旧结果当公平对照。4000增加计算十倍、860增加episode十倍，报告实际帧数/样本曝光/总updates，不伪称完全固定epoch。CPU/CUDA原官方loss/raw-action/目标同episode/first86共同subset/sourceexact预控先过才训；四全head终点独立opt/RNG/weights审计后原fresh48/100steps/raw与clip完整384闭环，singletrainseedpilot。

决策表：更多数据在4000有效而400无效→强调足够曝光与覆盖耦合，下一方法考虑行为多模态/可执行组合；增加计算足以吸收→训练校准优先，不把86弱policy包装成WM必要性；两者都弱而CEM强→history、动作分布、真实warm分布及预测查询支持都是竞争设计。G2与G3并行回答不同解释，不调若干局部action阈值，不更改I14/E20优先/状态或scienceclaims0。

G1执行结果覆盖pending：全部六控制组288/native criterion/全25D起点/trace/源checkpoint/真实Policy CPUCUDA auditPASS，见E14_20261005_pusht_goal_policy_control_results.json；GCI1/GCBC2/PAIRWISE2（native及physical各48，含initial1），released24/21。单86facts headseed/phi预train未知，跨任务未成立，未确认novel方法。

G2四50epoch350/358400items endpoints全部训练/actualCPUCUDA/独立opt与RNG审计PASS；首controller vendorimport identity assertion在import前控拒绝，效用0。原source/log/failure保留，不改训练/guard；v2 import正确官方Nav namespace在前，新unique-v2 paths，实际CPUCUDA全部48/11warm/fullstates exact/rawret控PASS才跑。两task384闭环当前未齐。G3原860cache104261/first86 exact/frozen303BN/nativeencode PASS；四86/860×400/4000全训练终点DONE，actualCPUCUDA与独立init/完整RNG/fullAdamW/调度endpoint auditPASS。独立原RTXGPU2部署queue3626303，log/tmp/latent-E14-coverage-control-RTX-queue.log，384控制预控正在进行，未有新的可解释效用矩阵。

G2完整384已独立trace/checkpoint/全11warm/raw-vsclip/native-success审计PASS：Nav HISTORY/COPY44/45（near24/24、far20/21），Push3/2（near3/2、far0/0），每48均含initial1，两接口实际逐动作相同。Nav差−2.08pp95CI[−8.33,4.17]，Push+2.08[0,6.25]，一个headseed不含训练方差。见E14_20261005_history_policy_control_results.json；不会把一条额外成功叫memory修复，弱Push原因仍竞争，G3完整数据×计算在跑。原v2两个queue3622514/15自然完成；已等空的A10 source1/2 queue3623770/71实际接管各卡，未重启任何unique run。

G3完整覆盖pending（2026-10-05）：[全部384](../results/E14_20261005_coverage_policy_control_results.json)实际CPU/CUDA部署、八组trace/全25D warm/pixels/原raw policy返回/100budget/native成功、源与动作核对PASS。86×400/4000成功均2/48，860×400/4000为4/5，native与clip所有实际动作一致，每48含initial1。数据增益400为+4.17pp95CI[−4.17,12.5]、4000为+6.25[−2.08,14.58]；86增加训练0[−6.25,6.25]、860为+2.08[−6.25,10.42]，交互+2.08[−8.33,12.5]。一seed anchorCI不包含训练方差；更多事实覆盖/优化没有稳定恢复releasedCEM24/21能力，不把该端点差直接归因几何/多模态。新86×400 anchor为本轮replacement/perupdatecosine配方，不借G1充同训练baseline。原G3和A10自有队列均自然退出，原始全部弱方法保留。后续对齐真实后果、预测对象与policy抽取，非继续调同head步数。

### H0：控制器诱导的真实后果，运行前（2026-10-05）

对应I09/P04/P05/P08/R1/R2，保持人审I14/E20优先，不替换narrative。承接SPlaTES/option models、PLDM、PlanningLimits、INTACT：高层要选择的对象如果是feedback policy，原始开环action consequence并非它的真实后果。假设是学习/使用可执行经验组合是否能在少数据下改善长任务，H0先建立正确训练对象与强支点，**不是新skill方法或先证明tracking有效**。

同一完整INTACT publishedseed0、原legal common-reset44/task、每anchor全部11去重branch endpoint goal（0 ZERO、2 FACTUAL、3–11合法分支；1重复ZERO排除），三固定controller OPEN25/GOAL5/REFERENCE5各预算25。goal image来自原保存的真实experience；nativegoalstate只在evaluator设置/判成功，不进policy。先恢复原goal下完整warm10，再设给定candidate goal；全部controller同query起点state/pixels/past5完全相同。initial/中途成功吸收保留，earlystop计实际steps；不是额外持有全部future轨迹或把policy获得goal看作免费action后果。生成2×44×11×3=2904固定controller continuations，source0探索数据；以前11goal不是独立anchor，bootstrap以44anchor聚类。no-shift，固定25一次，不做chunk/horizon sweep。

阳性对照：原bank全trace SHA/88ledger/去重含义；actualwarm3image与完整Nav10/Push25diagnostics exact；三个querycontroller首5bitexact原H5首macro/原H1，actualCPU/CUDAtypedhead与手算；相同goal/setter不改agent/object dynamics，三controller各reset replay至query起点exact；不改source/weights/BN。source选择/prediction函数只能拿currentimage/goalimage/causal发出commands/imaginedreference，不读branch futureoutcome。原真实branch成功上界只是diagnostic，原bank含训练开发episode/发布prior未知，不能作独立确认。

保存start/fullcontroller轨迹、每5steps的observedpixels与发出commands、modelreference/queries/returnedmean、hash/controller descriptor，供后续在trainanchor0–31和heldanchor32–43明确分离下学习option-outcome model。主读数每task/controller全484query的实际达到goal比例、budget/early-success、leave-self-goal后的可支持最终goal集合/候选oracle覆盖、三controller成对help/harm及clustered95CI；oracle只离线不部署，latentprediction误差待真正训练后才有。噪声：44sourceanchor、一个modelseed；同anchor多个goal不独立，相关全保留。

决策表：反馈controller本身强→保留它作最强directpolicy、不能把额外head讲胜利；反馈后的后果/可连接性与open plan明显不同→下一H1比较同数据的primitive-rollout、直接policy-outcome预测与可执行性监督，并实际高层部署，对强GC/value方案；相同则不包装新抽象，继续I14数据/表示方法。若接口guard失败，在任何正式效用前保留唯一failure，修接口，不降低阈值/筛goal。单卡/task原RTX新空2/3优先，本地bank缓存，预算实际报告，raw机器留、git仅config/hash/summary。未启动，H1未训练。

H0原RTX2/3空卡actualwrapper3666938/39启动，logs `/tmp/latent-E14-controller-consequence-{task}-RTX.log`；原全部44/task完整warm/factual25diagnostics/pixels、sourceSHA/去重branch/actualCPUCUDA五槽typedglobal/local和short/full首macro预控已PASS，两个完整1452continuations正在生成。没有读partial结果/没有训练outcomehead，原bank大raw留机器。
### H1：训练可执行后果与原始动力学的匹配比较（运行前，2026-10-05）

对应I09/P04/P05/P08、R1/R2，并服务人审优先I14的数据语义问题。继承SPlaTES/DADS/LEAP与INTACT，不认领首次技能模型、feedback预测或层次规划。假设：当候选是固定视觉反馈控制器，而非已知完整动作串时，直接学习该控制器的实际后果可能改善候选排序；原始动力学的同数据BPTT更新是必要强对照。

固定H0全部2904与公开source0；训练anchor0–31，held32–43，两task同划分，held图像/目标/结果不参与训练或归一化。三控制器都保留，初始已成功完整报告但不计主要排序效应。所有结果是development，非新的确认episode；未知公开pretrain overlap照旧。

比较FROZEN-WORLD、FINETUNE-WORLD、DIRECT-CONTROLLER、GOAL-COPY、CURRENT-COPY。FINETUNE只训练完整公开predictor/pred_proj，phi/projector/action_encoder/actor冻结，真实已执行五步macro的五前缀BPTT，不能用deployment未来真实动作；不足完整5步的吸收片段不伪造zero-action物理训练。DIRECT为当前z、给定子目标差、过去真实5command、三控制器one-hot→五前缀实际z残差，两层512/GELU，每前缀loss等权；到达子目标提前终止后按已观测终点吸收填充，明确其任务停止语义。数据与目标形式的差异是方法差，非单loss因果。两训练各固定1000 AdamW updates/B128，LR原predictor1e−4、新head1e−3、weight_decay.01、clip1，无best-checkpoint择优，seed0 exploratory；同时记录有效样本/active params/时间。

启动前进一步锁训练采样：两方法都只采train anchor且至少执行5步的行，使用同一seed、同128000个row IDs；不足5步与initial行数量完整披露，held readout保留它们并另报告noninitial子集。DIRECT吸收prefix与BPTT有效完整macro的监督量不同，分别记账；主要解释必须同时看执行满25步与提前吸收两层，不能将停止语义优势称物理动力学改善。归一化只从该train子集拟合。

阳性对照：缓存B1真实visual encoding与CPU/CUDA原容差；future-action graph索引独立手算；world一次prediction与官方rollout相同；headzero→CURRENT-COPY；held输入或label修改不能改变train采样/归一化；optimizer仅active参数，冻结全部weights/BN；实际梯度非零/finite。噪声地板：44/32/12是anchor数而非数千独立样本；CI按held anchor配对bootstrap，单trainseed不包含训练方差。

主读数：held同candidate bank真实latent-cost regret、native选中成功与oracle支持、排名（含/去掉候选子目标=最终目标分别报告），五prefix误差按成功/未成功分层；不只报告MSE，不拿goal-copy败给弱head当新方法证据。用于给定controller子目标的真实query允许，但bank含同起点真实经验子目标，不能把该offline支持当部署可用信息。

决策表：若DIRECT排序不超过FINETUNE/FROZEN/GOAL-COPY，保留负结果并理解support/停止语义/表征，不调head宽度反复救。若有排序信号，立即比较实际闭环：候选只能来自TRAIN经验池和给定最终目标，禁止held未来中间图；同候选/同controller执行对照，强BASE25/GOAL5同时保留。offline信号不能替代closed-loop。若closed-loop仍弱，跨goal候选支持、长时value与数据覆盖是竞争解释，不关闭R1/R2。全部预控后独立单GPU铺两task×两方法；模型HF缓存，encoded数组和raw在node-local cache，不需大训练框架。
### H2A：与高层部署一致的定长控制器后果（运行前，2026-10-05）

H0/H1给定候选任务、native子目标吸收；该语义不能直接当最终任务固定的层次option。新H2A采**定长物理后果**：环境保持原最终任务目标，不设候选物理goal，不因子目标或native最终goal命中中断collector的25-step counterfactual轨迹；done只作离线评价，逐步native hit保存。该forced continuation只用于模型训练，真实closed-loop仍第一次最终任务成功立即停。原H0/H1有效范围不变，不事后更改其轨迹/读数。

两task采用E18F3新48episode（与H0/训练memory source episodes互斥，公开pretraining overlap未知），每起点17给定image子目标×OPEN25/GOAL5=1632完整25-step轨迹，共3264/81600新envsteps，加真实10-step warm restore成本另记。17候选为给定最终goal+TRAIN H0 anchor0–31去重经验图的8 nearest-to-final-goal和8 uniform剩余，固定seed131001/131002+j，不读任何branch真实future/hiddenstate；最终goal的nearest只是proposal，不是learned acquisition。所有候选和顺序在first rollout前sealed，train/held source anchor0–31/32–47，近远层分别保留。新48曾用于F3评价，属development而非未看过确认集。

阳性对照：全部48真实warm pixels/full diagnostic/factual goalbank控；每个候选共享完全相同初始physical state/currentpixels，collector final-goal不变；OPEN和GOAL首5issuedactions exact，global plan/CPUCUDA/kernel控从完整公开source继承并核第一actual新query；future outcome不进候选selector；all25命令有真实对应状态，重复branch replay exact，native hits逐步核。噪声地板：唯一48physical起点/单source，method大量行不作独立样本。

主读数先是完整轨迹/信息权限校对与真实candidate support（anytime、terminal，final-only与memory分别报告）；这一步是可执行经验资产，不是新方法。H2B训练前将固定预算/模型/读数另写；DIRECT若组合多段必须预测未来实际command history供下一controller使用，不能凭空清零或偷真实未来动作。部署比较同一完整三option路径bank、原始动力学与controller-outcome预测，独立强BASE25/GOAL5和无WM近邻作为参照；不使用held未来子目标、不将one-stage greedy失败当hierarchy上限。不因H1或H2局部null关闭R1/R2/I14。
