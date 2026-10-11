# 本地 agent 启动提示

你在 `workbench/latent-world-model-planning/` 工作。目标是通过强基线、方法探索与实证理解发展顶会级论文，不是只做综述、审计或验证一个预设现象。

## 最少阅读

先读根目录 `AGENTS.md`、`RESOURCES.md`、本目录 `README.md` 和 `RESEARCH_PLAN.md`；再按当前任务读 ASSETS、实验卡、文献。**不要求读完整历史目录才开工。** 旧 HANDOFF、Tier/Mine、Wave、红区和“有邻居就降级”规则均已归档，不是当前指令。

本次整理不改变 PROPOSED/ACTIVE 登记。用户把本工作台交给你执行时，在已授权资源内推进；不要擅自暂停其他项目、混用机构数据或修改 ACTIVE 分配。

## 每次上下文压缩后恢复

先读本页、README当前证据、RESEARCH_PLAN的R1–R5，再读当天日志最后两条、CLAIMS/PAIN_LOG新增记录，以及正在运行的E卡和对应results JSON。核对原始artifact的complete/failure与进程后再执行，继承已锁定seed/目标/主读数，不能把pending写成结果或重复启动同run。最近结果、替代解释、失效条件、运行命令与下一组实验理由都写入现有日志/实验卡；本页负责恢复规则，不堆积逐run历史。

恢复时明确三件事：正在回答哪个重要母问题；哪些数字已核对、哪些解释仍不确定；下一组实验能区分哪些方法或解释。若连续研究动作只在同一selector/阈值/局部probe中绕圈，优先换预测对象、数据利用、任务复用、反馈/恢复等方法轴，保留母问题。关键结果后定向深读最近邻的method/data/baseline/decisive experiment，补清继承与exact delta；不因相似abstract关闭方向。

## 开始做事

1. 同步 main，盘点已有 repo/env/data/checkpoint，不重复下载。运行仓库 `python3 tools/process/check.py`；真实错误先修，不为消除流程 warning 造科研结果。
2. 查看 CLAIMS、PAIN_LOG 和最新运行输出。没有GPU结果时如实记录；有结果时继承，禁止从零重来或覆盖原始数据。
3. 按 E00 接通一个原生训练/规划闭环，记录显存、I/O、加载差异和完整episode耗时。按 E01补强基线、统一评测清单；允许同时做可比较的方法小试。
4. 当前人审优先 **I14/E20有限数据下真实动作后果学习**，并行E16充分训练/独立种子校准；**I09/E14短经验可执行组合**为备选。PBB v0、自一致性多保真与tiny-update降序，不再默认起跑；旧卡保留，R1–R5持续开放。
5. 每组实验写清实际问题、来源、改动/对照、读数与成本；已有卡可以在运行前版本化修订。不用为了新想法增加一套规则文件。

## 当前优先级（2026-10-04人审）

先读RESEARCH_PLAN §11–12：基线校准与完整训练方法并行，允许联合训练encoder/predictor；用同数据充分训练plain/inverse/强近邻判机制，不以frozen小head负结果关闭路线。以下PBB/多保真内容为保留的旧入口，当前降低追加优先级，不覆盖最新计划。

## 保留的第一波具体方法

当前最值得先试的不是“剩余空白”，而是两个**有强近邻、也有明确增量**的method hypotheses：

### A. E16 Planner-Boundary Branching (PBB)（R1）
用CEM候选的elite margin/rank disagreement找到planner可能改主意的state；在同一simulator state执行少量竞争candidate branches，把这些真实transition加入原WM训练。与IID、coverage、global uncertainty、task-relevant acquisition等预算匹配比较。**第一版只改数据，不加新decision loss。** OnlineWM、Task-Sufficient WM、ToIA、TOM、Beyond Visual Quality、D-JEPA/AD-WM是必须看的近邻，但不是禁止开工的理由。

### B. E13 Planner-Stage Multi-Fidelity（R2）
Fast-LeWM/cheap direct predictor广筛candidate，LeWM/multi-step/refined predictor只重评可能进入或改变elite set的候选。比较fixed wall-clock下pure cheap、pure expensive、random refine、top/boundary refine。Fast-LeWM已做direct prefix；2026-09-30出现的DeepJEPA已做transition-level adaptive depth——**我们的轴必须保持为candidate-stage fidelity allocation，并测试二者是否互补。**

**E13最便宜的Stage A0：** 直接用Fast-LeWM同一checkpoint的direct score vs selective/full self-consistency，在同candidate bank上测elite recall与refined-call比例；先不训练新模型。**E16最便宜的Stage 0：** 建same-reset hidden branch bank并确认selector不会看到未购买outcome。二者可以并行。不要机械等待E00全部结束才写原型，也不要在结果出来前宣布A/B就是最终论文。

## 你的研究自主权

**允许从第一轮开始做方法；文献支持的重要痛点足以启动原型，不要求先在本地发现全新异常。** 可以复用成熟原理，改训练目标、预测结构、数据选择、planner或记忆机制；说明为什么该设计可能解决当前问题即可，不需要先证明新颖失败/普适规律。

方法试验与解释试验互相促进。方法有效就分析收益来源与范围；解释发现瓶颈就试相应方法；简单基线特别强同样值得追。不能把“必须有异常”“必须名次翻转”“必须先匹配所有变量”变成研究许可证。

遇到近邻，深读其 method/data/decisive experiments，复用实现并明确增量。不得仅凭摘要或关键词关闭方向。只有当前主张确实重复、设计无效或证据不支持时，修改该主张/实验；R1–R5母问题继续保留。关闭方向和资源换轨按根目录的人审规则。

## 不要再犯的错误

- E14多门/绕路只是具体诊断，不是整篇论文必须讲“行为路线残差”。覆盖因素解释结果时，可以转为更好的数据采集/利用方法。
- E13先可比较同一backbone的预测目标，E19可比较变化后的更新，再扩长期抽象；不必先安装所有model-free/world-model框架，也不强制追一个“regime law”。
- E11隐藏状态oracle比同信息模型强，不自动说明模型有bug。相同历史不可辨的状态只能比较信息受限下的策略；主动探测计入成本。
- E18恢复oracle不能泄漏进部署规则；可直接先试合理阈值/反馈/适配策略，不必等oracle完备。
- 小模型参数量不等于便宜；latent距离/MSE跨不同表示通常不可直接比较。
- Bagatella `TD-JEPA` 与 Bai/Xiong `Temporal-Distance JEPA`不是一篇论文。日志用完整paper ID，不能裸简称聚合。

### C. E17 Selective Query Specialization（R3）
若已有多goal checkpoint，直接做 COST-ONLY / PRED-ADAPTER / FULL-QUERY 的seen/unseen goal小对照。不要上来引入语言模型。目标是看query specialization应进入哪里，而不是重复“query matters”。

### D. E18 Utility-Gated Recovery（R5）
先做fork ledger，不先训router：同state比较 HOLD / FEEDBACK / SHORT-UPDATE（或EXTRA-REPLAN）。只有真实 `Δutility` 因state/shift明显不同，才训练轻量utility router。

### E. E19 Selective Revaluation（R2/R3/R5）
先做reward/query-only、local transition、broad dynamics三类shift中的最小模块更新对照，找“最小充分更新集”。经典reward-vs-transition revaluation是背景，不是新发现。

## 广泛实验与确认

先测单任务和节点I/O，之后按实际授权并行独立训练、评测、seed和数据条件；全局ACTIVE容量不是pilot数量上限。避免共享盘被数十任务反复随机读，尽量节点本地缓存。

探索比较可以广，但每个条件应回答一个问题或区分一种设计。不要把几十张卡只用来重复微小参数优化，也不要求每张卡都跑完全不同的项目。通常优先保留多个方法/解释分支，再把有意义的结果扩到更强基线、第二类任务和独立seed。

把训练计算、部署计算、任务信息/奖励标注、真实环境交互分别记账。探索结果与确认结果分开；最终因果/机制论断需要额外控制，不能先把粗比较写成机制。

## 写回与汇报

只更新一套内容：新运行进对应实验卡与 `logs/`，实际痛点/成功进 PAIN_LOG，证据充分才升 CLAIMS；只有研究方向真的变化才改 RESEARCH_PLAN。原始大文件留授权节点，git写hash/config/许可范围内的路径说明，不公开内部地址。

新增 E/I编号先查索引，不能重用；历史E03/E04等归档编号继续保留历史含义。运行后报告关键结果、替代解释、与最近邻的差异和下一组研究动作；没有跑就写没有跑。

**交付标准：一个可用方法或重要认识及其可信证据，而不是不断增长的文献编号、诊断脚本或流程卡。** 日常比较和原型可自主继续；到主张升级、跨项目资源分配、进入候选或关闭方向时再按根目录流程人审。

把RC-aux作为小模型/低耦合/可并行验证的参考，而不是规定只做reachability。一天完成确认实验的可行性用实际训练+闭环评测成本计算，不承诺未经测量的GPU-hours。


## 用户追加的执行偏好（2026-10-02）

- 调用子agent默认用 **gpt-6.1-sol / high**，不使用ultra。已有agent若不符合则停止其任务，用指定配置重建；已有合格agent可followup。
- 高信息量实验应横跨数据、预测对象、任务条件化、在线控制等方法轴；允许借鉴控制/系统辨识、goal-conditioned RL、搜索/图方法，不把小型诊断当预设paper。
- 压缩恢复先读最新审计：E16旧跨方法比较因AdamW CPU step引用共享而降级，完整修复重跑才允许继续解释；旧日志保留但以最新审计为准。

## 2026-10-05最新恢复锚点（覆盖旧运行状态；历史见既有logs/卡）

压缩后先读README当前证据、PAIN_LOG末尾、log2026-10-05末尾、E01/E14/E20最新stage及raw complete/process。研究目标持续active、PROPOSED/C00工程L1/science0不变；没有确认novelidea，不自动关闭R1–R5或换paper narrative。所有方法/低seed/null/失败完整保留，不救CENTER/PBB阈值。

原matched22groups1056、经验利用18groups864、Push14groups672、freshBASE1000两组96 DONE并独立trace/hash/native-success审计PASS，原RTX队列自然退出，禁止再启动unique run。NavIID/REPLAY/MIX vsGROUPED三个CI均跨0；Pushnative发布24/48→joint3–6，physical21→3–6，单transferseed/pretrain未知，机制不能直接叫encoder遗忘。original及new bank pixels实际均224，未发现224/256失配。

E14全部三sources ABS/JOINT/SEP，18groups864独立控制审计PASS：native ABS30/23/24、JOINT17/2/7、SEP32/34/39；physical24/18/24、17/4/15、33/33/40。SEP native对ABS整体+19.44pp CI[2.08,36.81]，far13/17/18 vs9/6/5（每tier24）；已有Value-GuidedJEPA机制，不是novelty/原paper复现。完整15trainendpoint/hash/初始化/optimizer/frozen BN与params/firstbatch/finalRNG PASS。原3574468和两A100value队列均退出；3573734 firstlauncher mapping error CUDA前/无outputs，旧log保留。

E20Stage4四geometry×data各2825、八控制384均DONE/独立endpoint与traceaudit PASS；native PRED-FACT/MIX29/26、VALUE-FACT/MIX36/36，physical25/24、36/33；MIX within-geometry与interaction CI均含0。两个prior5650/2825目标与budget不同，不能当objectiveonly因果。geometry_experience冻结，COMMON reset93 dynamic init、frozen204phi/BN、2825B128、fiveTF/noSIG/aux、两RNG重生，原四train/八controls自然退出。

E01完整RC-aux actualCPU/CUDA四cell bit-exact原native criterion/完整head/manual预算、全312keys与官方scaler控PASS；八control groups384与独立trace/head/scaler/checkpoint audit DONE。H1 ON/OFF native38/33、physical34/31；H3 37/34、35/32（各48）。weight.85是pinned object/README，附带旧.35config区别未筛；H3原criterion含pastframes且预算clamp5，不擅改。原50step预算与本地100step不同、发布训练data不匹配，非paper完整数值复现/同data比较。原RTXGPU2 PID3579990自然完成。

E20Stage5 Push DYNAMICS-ONLY/GEOMETRY-ONLY，各2000A100 actualCPU/CUDA与独立93/204optimizer×2000/frozenparams-BN/共同初始/firstbatch/RNG64000items全部PASS，两个训练3631153/3631219退出。新完整192闭环已DONE，原RTX physical0 PID3584419与physical1 PID3584420自然退出，logs/tmp/latent-E20-pusht-module-{ARM}-RTX-control.log；pusht_module_control.py strict303/ABS同原namespace、same原48/native+physical、first-active nativeparity0、精确完整25D初始state/pixels。接续必须检查actual complete/queue是否自然退出，不把PID永久当running；全matrix齐后独立轨迹/源hash审计再解释，不读partial选择。

源码m0400260f…/effect_training e8b2dee8…/transfer42285bb9…/experience4c4d5c45…/bounded2271de3d…/geometry feeb74fa…/Pushmoduletrainer36da53b9…/RCcontrol均冻结。venv缺包RC预控首次失败前无efficacyrows，失败durable完整保留；只--no-deps补sklearn1.7.2/scipy1.15.3/joblib1.5.2/threadpoolctl3.6.0，Torch/NumPy/SWM不变。大模型HF、node-localdata、raw durable，git summaryonly/full auditpaths，不提交大rows/checkpoint；git只显式WB文件、不碰其他project dirtytree。

研究下一步以真实fullRC/三seedvalue/两task模块结果为支点，继续跨R1–R5比预测对象、目标/动力职责、数据覆盖、goal-policy/层次与变化后的复用；不锁12query/单导航。USB+ATR2610.00676/GCB/CRL/PAVE2608.30378等新近邻已定向method/baseline/限制读回到CORE，分角色/动作条件未来价值/两类经验监督已成熟，下一增量须实际benefit。还没复现这些policy/标准OGBench，不能说它们失败；无新主旨/状态决定待人。main最后hash以git核对并小commit push。

E13A8四cell固定PRED/VALUE geometry×官方Fast共同capacity/init DIRECT prefix vs LOCAL一步teacher/部署递归各2825已全部DONE，独立endpointauditPASS。prior budgets不同，不作pureobjective因果；same100事实5795starts/current第10步+future15…35/25actions、frozenphi FP32 features9295/无outcome、部署T1相同，port非Fast原数值复现。四actualCPU/CUDA B128手算/casualprefix/grad-freshstep/frozenphi/fullcost0/batch-subset控PASS。首precontrol API-name Model.training撞Torchbool，在loss前失败，原log/source保存；只rename方法，缓存没改，正式retry1/hash冻结，无训练读数改写。两原A100queues3634140/3634194自然完成，禁止重启同unique run。

A8完整384控制已DONE/独立trace/checkpoint/native-success审计PASS，原3590795/3590796退出。native PRED-DIRECT/LOCAL31/29、VALUE39/22；physical20/21、44/19（各48）。withinVALUE native+35.42pp CI[22.92,50]，physical+52.08[37.5,66.67]，PRED CI跨0。旧SEP32/33、RC38/34保留，VALUE-DIRECT native未稳定胜RC；prior目标/训练budget与旧H3/targets/sampling混杂，不称非Markov因果或novel方法。VGJEPA App7与ProWorld已有预测/规划两角色设计，不能换名claim首次。

A9八新source1/2×PRED/VALUE×DIRECT/LOCAL2825全DONE、actualCPU/CUDA与独立endpoint auditPASS。head113000+seed/sampler113100+seed各独立，within-source四cell共同init/capacity/样本，同100事实与共享48开发tasks。首版repeat_control把train seed覆盖成plannerseed，首版全部输出排除，旧日志/used source/故障路径保留20261005-E13-object-repeat-controller-seed-shadow-failure；A8与八训练没改。自有旧3597258…61停止，禁止重启/引用partial数字。

A9最新覆盖running：v2全部16groups768 DONE，原source0+v2共24groups1152与强参照全hash/trace/native-success/source/scaler审计PASS。PRED nativeDIRECT31/42/36 vsLOCAL29/39/35；VALUE39/40/34 vs22/13/32，physical44/41/34 vs19/13/32。VALUE within native+31.94pp CI[4.17,56.25]，但source2仅2/48，physical交互CI跨0；VD对oldSEP/fullRC两interface均CI含0。不是novel强baseline胜利，不让平均抹掉seed异质。原3599941…4自然退出，禁止重启unique-v2。

E14StageG0已prereg，公开GC-IDM vendor48c45b1…，官方head+原raw动作，same100/six源FP32features；GC-IDM maxgoal50、GCBC-MATCHED samegoals/horizoninput0、PAIRWISE nextgoal1。各source共同init/split/sampler，固定50epoch/B1024/paper-README LR1e−3/cosine，不用CLI200/8192默认或bestval择优。18heads全部50epoch/400updates/409600items训练DONE、12实际CPU/CUDA训练预控与独立initial/optstep400/finite/full50epoch sampler终点审计PASS；见E14_20261005_goal_policy_endpoint_audit.json。原A1003641046/7/8自然结束。源/encoder/projector frozen，与旧CEM不同训练目标/容量/训练compute，不冒称原论文复现。

E14G012实际部署预控/18训练endpoint/全部36控制groups1728 DONE，原RTX3603665/6/7自然退出。full独立trace/native16/source/动作raw-vsclip与同source24CEM参照audit PASS；portable E14_20261005_goal_policy_control_results.json正式来自audit-v2。PRED GC-IDM43/46/44、GCBC43/44/44、PAIRWISE14/19/22；VALUE38/38/39、41/41/41、42/30/40（native每48，physical所有动作实际相同）。PRED GCI对DIRECT+16.67pp95CI[4.17,29.17]，是已知更强baseline，不是newidea。GCIDM/GCBC100步无稳定差，geometryprior价值不能由弱LOCAL排序决定。success_by50是100-budget前缀、不是fresh50-budget policy；首audit含糊budget字段保留/v2改controller_budget100+evaluation_prefix_steps，全数字/CI/动作不改；不把慢速度现象叫novel期限机制。

PushG1 source86事实9374帧retry1 encoding COMPLETE/native encode bitexact/subset≤2.15e−6/全部303weights-BN frozenhash。首A100节点打开HDF失败，无编码结果，failure+used source/log durable20261005-E14-goalpolicy-pusht-RELEASED-features；实际46GB原HDF只在RTXcache，不跨节点搬。新RTXGPU3 featurePID3608590已自然退出，cache20261005-E14-goalpolicy-pusht-RELEASED-features-retry1；所有first86/excludedfresh48不变，发布pretrain未知，HDFexport没重哈全文件，只source+encoded array全SHA。

G1三个released-phi raw-action policyheads source0三arms全部50epochs400 DONE，两个actualCPU/CUDA训练预控PASS。actualRTXGPU3 queue3612320已自然退出，log/tmp/latent-E14-goalpolicy-pusht-s0-RTX-training-queue.log。goal_policy_pusht_adapter.py显式覆写数据load、复用冻结G0真实官方training组件，wrapperSHA写feature metadata/usedsource；不改Nav任何权重或源码。其checkpoint继承组件legacy“A100”目录名但实际RTX，不混timing表；publishedencoder split未知/只有一个headseed，不当三source或完整paper复现。独立goal_policy_pusht_endpoint_audit.py三个head全部PASS（firstbatch/50epochRNG/共同savedinit/400optsteps/allfinite/409600items）；portable E14_20261005_pusht_goal_policy_endpoint_audit.json。新RTXGPU3部署queuePID3615194，log/tmp/latent-E14-goalpolicy-pusht-s0-RTX-control-queue.log，goal_policy_pusht_control.py/queue.py对全部288/source0原fresh48/full25D warmstate-pixels/nativeposition-angle/原Policy raw动作先CPU和CUDA全部控才运行；目前尚未确认部署预控通过，不报Pushpolicy效用。整批6groups齐后独立trace/source/success/issued动作边界审计，再与发布CEM24/21及原joint5/6作capability比较，不冒称singlefactor因果。研究目标active/C00工程L1/science0/PROPOSED不变。

2026-10-05最新覆盖G1pending：Push策略288已全部DONE并独立auditPASS，native/clip GCI1/GCBC2/PAIRWISE2，每48含initial1；releasedCEM24/21。不是接口bug复现或memory唯一因果，一个headseed/86facts/phi预train未知，science0/PROPOSED不改。A10新增六OPEN-ROLLOUT BPTT model2825全部DONE、12actualCPUCUDA/full independent init/opt/sampler/frozenphi auditPASS，见E13_20261005_rollout_endpoint_audit.json；原A1003647978…81/3649070…1自然完成。RTX新controlqueue3623769/70/71（source0/1/2），logs/tmp/latent-E13-rollout-control-s{seed}-RTX-queue.log；0/1等history释放卡，3实际运行，全部576待齐，immutable train_seed/planner_seed分开。

G2四historypolicies50epoch350/358400items DONE/独立endpointPASS，见E14_20261005_history_policy_endpoint_audit.json；old control module import JEPA source namespace collision拒绝/效用0，故障usedsource/log durable20261005-E14-history-control-import-failure，严禁运行原control。新v2 import原Nav组件在先/unique-v2 artifact，无权重/目标/guard变动，RTX0/1 PID3622514/15，logs/tmp/latent-E14-history-v2-control-{nav/pusht}-RTX-queue.log；预控actual48/11warmframes/source/manualraw/CPUCUDA过后384controls，先查complete/failure不看partial挑winner。G3 dataset×compute独立校准卡已prereg：actualPushHDF18685episodes/2336736frames（不是旧233673），860 fact cache104261frames COMPLETE/nativeencode exact/303weightsBNsame/first86exact，ROOT20261005-E14-goalpolicy-pusht-860-features。新GPU2四headqueue3621998，log/tmp/latent-E14-coverage-RTX-queue.log，86/860×400/4000；新with-replacement采样/per-update cosine，必须用new86×400作matched对照，不能借旧G1 2/48当同实现baseline。终点独立audit与384closedloop未完成；下轮继续实际deployment，不停在asset/prepared。研究三axis是strong rollout、dynamicstate、experience coverage，不改paper narrative/人审优先/母问题。

G3最新覆盖trainingpending：四86/860×400/4000全head DONE，actualCPUCUDA/独立init/完整samplers/finalRNG/fullfiniteAdamW/scheduler auditPASS，见E14_20261005_coverage_policy_endpoint_audit.json。原3621998自然退出，新GPU2部署queue3626303，log/tmp/latent-E14-coverage-control-RTX-queue.log；全部384先实际full25D/warm/原官方Policy rawreturn CPUCUDA预控，complete齐后用goal_policy_followup_control_audit.py coverage独立读整批。G2对应该reader history，需两个task pipelines全complete才读整批384。训练结果不当部署效用；当前控制进程状态每轮实查。

G2完整384已独立trace/checkpoint/全11warm/raw-vsclip/native-success审计PASS：Nav HISTORY/COPY44/45（near24/24、far20/21），Push3/2（near3/2、far0/0），每48均含initial1，两接口实际逐动作相同。Nav差−2.08pp95CI[−8.33,4.17]，Push+2.08[0,6.25]，一个headseed不含训练方差。见E14_20261005_history_policy_control_results.json；不会把一条额外成功叫memory修复，弱Push原因仍竞争，G3完整数据×计算在跑。原v2两个queue3622514/15自然完成；已等空的A10 source1/2 queue3623770/71实际接管各卡，未重启任何unique run。


### 2026-10-05覆盖旧pending：完整四组结果与INTACT版本边界

G3全部384 DONE/独立auditPASS，86/860×400/4000=2/2/4/5（各48/native和clip同动作/initial1），数据、compute、interaction CI均跨0；旧3626303自然结束。A10完整576 DONE/独立auditPASS：PRED OPENnative27/42/38 vsDIRECT31/42/36，VALUE25/18/11 vs39/40/34；withinVALUE OPEN−DIRECT−40.97pp95CI[−56.25,−25]，physical−40.28。旧3623769/70/71均自然结束。不是新方法胜利，不关闭R2/R4，不把冻phi头当完整policy。

A11全18模型/8712query DONE/full independentauditPASS，见E13_20261005_full_branch_matrix_results.json。VALUE direct−open含goal+39.67ppCI[29.20,50]，leave-goal-out+21.49[17.70,25.41]；PRED direct含goal反而弱且后果归一MSE更差。每484query其实44state×11goals/3sourcescluster，非8712独立state；onlyNav完成，Push H3reference待补。bank0 ZERO/2 FACTUAL/1duplicateZERO，正式reader校正冻结producer描述错误，预测与选择未改。Nav实际diagnostic10D后8sameanchor分支恒定，native前2position。第一次shapeguard失败、第二次CPU/CUDAcuDNN-TF32差.01812失败都保留原source/log，v3关闭TF32原2e−4/1e−5容差不变，freshsamebackendsubset6.437e−6；旧3636982自然结束，不能重启unique-v3。

A12 Push3matchedFast DIRECT/LOCAL/OPEN全部2825 DONE、actualCPUCUDA B128/五target/梯度/RNG/frozenBN與独立endpointPASS、288闭环fulltrace/source/nativecriterion审计PASS：native2/2/1、physical2/1/1，每48含initial1、far0；publishedH3 CEM24/21。旧训练3633756/7/8及部署3639061/2/3都自然结束。一个headseed/86facts/T1/phi pretrain未知，不称direct普遍优胜或数据无用；不继续小head阈值救援。

INTACT完整公开模型资产已verified：vendor653ee222、HF paper-e5-goal-v1解析0430df6f、两个84.7MBseed0shards和全部config.json/yaml/multitaskmetadata在HFderived/intact-e5-goal-seed0。paper_runtime五槽actordelta_condition_product与rootclean四槽不同，严禁套类/strict=False。初次preflight缺stable_pretraining；第二次strictencoderkeylayout旧transformers vs发布5.9不兼容，efficacy0、failure/source/log保留各original/v2CPU目录。官方0.1.7 wheel只读提取vit_hf函数，未装入旧env；新隔离latent-wm-intact system-site venv+transformers5.9，pinnedconstructor/runtime/全weights严格加载，各CPUCUDA五chunk/manual/rawlast5standardization/全部48warmexact过后完整192两task H1 DIRECT/nativeclip。只有实际执行过的warm/actions[-5:]进输入，goal未来不偷渡。发布50 vs本地100、pretrain未知、Torch/SWM现有差异显式列账，不冒numericpaper复现。

INTACT v3源码+independentreader已写，隔离依赖安装后才能启动新unique-v3；v1/v2全部排除效用，旧3642047/3642882已退出。最新PID/log必须实查，不把这里未更新pending当真实进程。下一步：完成完整强邻并审计、补A11Push真正H3参照；从经验后果标签语义/预测对象×表示用途/任务复用分别设计实际方法pilot，面对AC-MTM/INTACT/FIRM/CoCo与成熟control，不宣称首次动作或分角色。状态PROPOSED/science0/C00L1保持，goalactive。所有结果与工程失败写卡/log/CLAIMS，不新handoff或survey。


最新覆盖INTACT待启动与A11Push待补：INTACT v3在新隔离venv fullstrict共享encoder/hash/CPUCUDA五chunk手算/raw5norm/全48恢复exact全部PASS，192闭环及独立causal trace/source审计DONE。Nav37/48（22near/15far）、Push25/48（22/3），两个native/clip相同/initial1。见E01_20261005_intact_published_control_results；旧3644522自然退出。新envtransformers5.9/Torch2.7.1cu128/NumPy1.26.4/SWM0.0.6，.pth只复用旧sitepackages依赖，原env不改。官方0.1.7wheel精确提取vit_hf供构造，不安装稳定预训练全栈；original/v2strict失败efficacy0完整保留。

A11Push fullH3 RELEASED+五joint2000，2904query/全部六CPUCUDA原get_cost手算bitexact/immutable303/TF32off/fullindependentaudit DONE；旧3645888自然退出。见E13_20261005_pusht_full_branch_matrix_results，branch_query12含goal69/62/54/53/49/44（每132），没有newmethodgain。leave-out物理native支持只有8/132=6.06%，chosen3/2/1/2/2/5、true-latentoracle5/4/3/3/3/4；低support不得被误当cost坏。32branchtrain/12query、一transferseed、unknownpretraining完整披露，七维norm不当成功。Nav/PushA11都完成，禁止重启旧unique artifacts。

E18F0在运行前新增card，完整INTACT同H1/H25plan/同actualpast5/rawnative/budget100，只改执行prefix EX5/EX1；原EX25native37/25为HOLD参照。新两task192全部旧48，EX5/EX1均保留，每decision保存full25proposal+causalpast5+actualstates+CUDA同步solver时间，首decision与旧EX25逐项bitexact，所有preflight通过后才效用。新RTX1/3 PID3648207/3648208，logs/tmp/latent-E18-intact-feedback-{tworoom/pusht}-RTX.log。阶段不是router/gate新方法；若fixedfeedback统治先用strong固定策略，若有help/harm异质下一步same-state replayforkledger，不把futureutility做deploymentfeature。科学主张0/PROPOSED/goalactive不改。当前进程和预控每轮实查后更新，全部192齐再独立audit，不能报告partialwinner。


最新恢复：E18F0两task四新频率groups192全部DONE，full独立audit PASS，portable E18_20261005_intact_feedback_frequency_results.json。原RTX1/3 wrapper3648207/8自然结束；EX25/5/1 Nav37/28/30、Push25/29/27，各48含initial1；EX5 Nav−18.75ppCI[−35.42,−2.08]、Push+8.33[2.08,16.67]，wholepolicy异质尚非same-state/gate证据。main bc616543已push。新E18F1 prereg两task全部48×3conditions×3response=864，forkt10/15stepwindow/t25后统一EX25，shift从t5开始，features先于全部future保存，不训router。原RTX0/2实际wrapper3652205/6，logs/tmp/latent-E18-intact-forks-{task}-RTX-retry1.log；先查raw20261005-E18-intact-forks-{task}/preflight/complete/failure与进程，不能重启unique run。首语法launcher错误effect0原source/log/hash保留，check=True编译后重新启动。后续补独立fullreader/native/causal/shift/prefix/source/CI，再决定下一实验。目标active、science0/PROPOSED和人审优先保持；不把固定chunk优化预设paper。


F1上述retry1状态已被v2覆盖：原Gaussian tuple API误用被anchor0 guard阻断，正式rows0，原source/failure/log保留raw20261005-E18-intact-forks-{task}。正确dictionary API已核对，v2 unique当前raw20261005-E18-intact-forks-v2-{task}；0/2 wrapper3652843/4，logs/tmp/latent-E18-intact-forks-v2-{task}-RTX.log。两task各144prefix/control全部preflight PASS，全部864continuations实际运行；不得重启，待两complete用intact_recovery_forks_audit.py独立审计全matrix。science0/状态与母问题不变；plannedtracking只是待试研究动作，不是newidea确认。


覆盖F1 pending：两task全864 DONE，v2 full independentaudit PASS，portable E18_20261005_intact_recovery_fork_results.json；原0/2 wrapper3652843/4退出。HOLD/REFRESH15/5 Nav nominal37/37/37、gain32/33/33、wind34/36/33，Push25/26/28、16/19/21、moment20/22/19（各48），onlyPushgain反馈+10.42ppCI[2.08,18.75]，oracle比bestfixed最多3条，不训复杂gate。reader原小delta NumPy/CUDA reduction失配故障保留，v2校对component后精确scalar减法，轨迹/模型/守卫不改。最新F2 actual1/3 wrapper3654985/6，logs/tmp/latent-E18-intact-waypoints-{task}-RTX.log，raw20261005-E18-intact-waypoints-{task}：真实typed CPUCUDA/144prefix/48reference全PASS，完整576待齐用intact_waypoint_recovery_audit.py审计再解释。不重启unique，不将RWM已有reference原则认领novelty。继续借baseline/数据/预测对象/反馈结果生长方法，science0/PROPOSED/人审优先保持。


覆盖F2pending：两task全576 DONE/fulltyped-query CPU/native/causal/source audit PASS，portable E18_20261005_intact_waypoint_recovery_results.json；原1/3wrapper3654985/6退出。feedback/open Nav nominal37/37、gain35/33、wind37/35；Push28/26、gain23/15、moment20/19；vsstrong REFRESH5只有Navwind正区间且REFRESH15已36，Pushgain23vs21区间含0。只是候选线索，不能宣布novelmethod/可投级signal或换humanpaperpriority。接续E18F3新的48episode×三published独立seed0/42/3072/fullpolicy强固定反馈；先资产HF hash/config/源manual/新的真实factualbank控，再铺全部署。所有故障和弱条件保留；RWM是NeurIPS2025 accepted corpus命中，不重新认领reference-control。科学0/PROPOSED/目标active。

### F3运行恢复（2026-10-05）

main bf01e70b含F2全576独立审计，仍无confirmed novel method。F3六完整部署pipeline实际在原RTX四fixed queues3661470/71/73/74；logs `/tmp/latent-E18-intact-F3-RTX-g{0,1,2,3}.log`，scripts/intact_full_recovery_queue.py固定GPU0导航0/3072、GPU1导航42→操作3072、GPU2操作0、GPU3操作42。先核对raw `20261005-E18-intact-F3-{task}-s{seed}-preflight/controls.json`、12cell complete/failure和pipeline.json，不能重启unique。新seed42/3072资产和两task新48bank已DONE，F3完整3456尚无整批数字。producer/intact_multi_seed_source只编译、当前actual预控进行；强GOAL5优化horizon1与full首macro exact才部署。全3456+独立reader齐后汇报，不筛condition/seed，不把CPU保存embedding actor重算称逐query视觉重编码。

F3 pending覆盖：六全3456 pipeline DONE，full-matrix-only独立audit3667312/log `/tmp/latent-E18-intact-F3-audit.log`正在跑；只有portable E18_20261005_intact_full_recovery_results.json completed后才有效用结论。E14H0事前卡与源码controller_consequence_bank.py：原44/task×11去重branchgoal×三固定controller×25budget，2/3空卡wrapper3666938/39 actual完整precontrols全PASS，raw20261005-E14-controller-consequence-{task}/rows逐步生成，完整2904待齐、outcome模型未训练。这批用于I09/R1/R2的可执行经验/预测对象方法，不替换I14科学priority；继承locked44/GOALS0,2–11/三方法，不筛partialgoal。

F3最终覆盖：完整3456/9071localquery独立auditPASS，portable E18_20261005_intact_full_recovery_results.json有效。NavnominalREF5=36/27/15 vsBASE25=36/34/34，平均−18.06pp crossedsource×anchor95CI[−42.36,2.78]；PushgainvsGOAL5+2.78[−3.47,9.03]。未形成最强fixed稳定优势，不能继续挑source/window或改λ救，science0。所有F3/CPUaudit队列自然完成。实际 E14H0 controller后果bank2/3在跑，完整2904待齐、没有训练outcomehead，必须生成独立reader再读整matrix；下一模型训练与highlevel实际部署，用strongGC/value与primitive-imagination匹配，不把bank自己当idea。
最新H0/H1/H2恢复覆盖：H0全2904 COMPLETE，独立逐primitive replay/逐B1视觉encoding/explicitactor+world/kernelreader在RTX0 PID3674985（父3673539）继续Push审计，Nav1452/3303visualqueries已PASS；全result未齐前无H0efficacy结论。H1两B1cache各1452 COMPLETE，训练事前固定32/12、两arms同128000sampler和吸收/完整macro语义，Nav单A100 queue3668245、Push553548（不同已授权节点，log `/tmp/latent-E14-controller-outcome-{task}-A100-train.log` 需在对应机器读），等待wholeaudit后1000updates两arms；本地原等待队列3674604/5在无训练输出前移走，已停止，不是失败训练或重复run。H1RTX2全矩阵endpoint/held选择readerqueue3678982，log `/tmp/latent-E14-controller-outcome-evaluate.log`，正式portable `E14_20261005_controller_outcome_learning_results.json`尚无。

新H2A两个RTX1/3 producer3677593/3678129，logs `/tmp/latent-E14-fixed-controller-experience-{task}.log`，raw `20261005-E14-fixed-controller-experience-{task}`：NEW F3bank48、TRAIN H0memory0–31、finalgoal+8nearest+8uniform共17imagequeries×OPEN25/GOAL5，source0，1632轨迹/task。其controller25步collector不改最终taskgoal、不用子目标native终止并继续采集full25（native最终hit仅离线记录）；真实闭环仍首次finalgoal success吸收。这是避免H0 task吸收直接移植到option部署的语义混杂。H2B还未训练/实现，下一步必须独立审计bank、固定训练budget，并预测下一option必需的actual command history，实际多段samecandidate闭环，不清零未知历史、不用heldfuture图，不锁one-stagegreedy。I14人审优先/science0/PROPOSED/goalactive不变；未confirmed idea。


### 用户要求暂停全部任务（覆盖此前 active/pending 记录）

暂停时间：2026-10-05T10:06:30.095585+09:00。持久目标已 paused；不再启动实验、读文献或追加分析。已向本地 H2A 独立审计队列及其子进程组 3684338 发送 SIGTERM，保留全部完整银行与中断审计原文件，未完成审计不算 PASS。远端 H1 训练此前已完成，停止状态逐机核对。

暂停快照：H0 全 2904 后果轨迹与独立逐物理/视觉审计完成；H1 两任务四个固定 1000-update 训练及独立读数审计完成，DIRECT 冷启动头没有胜过强 FINETUNE-WORLD，不能据此关闭母问题。H2A 两任务各 1632 full25 轨迹完成，完整独立审计被用户暂停；H2B 尚未训练或部署。E01 temporal-contract 预控实际失败：编码数值 parity 最大绝对差 0.00102761 超过事前 0.0002 容差，正式比较无有效结果；原 source/failure/log 保留，不在暂停期间修复或重跑。science claims 仍 0，C00 工程 L1，workbench PROPOSED 不变。

完成结果与新原型存在本地未提交修改；最近已推送 main 为 a5982dd2。恢复时先读本条及对应实验卡，核对真实进程与 complete/failure/interruption，保留失败与中断尝试，不能重启已完成 unique runs；仅在用户明确要求恢复后继续。

暂停核对补记：本地审计父/子 PID 3684338/3686503 均已退出，nvidia-smi 无计算进程；fvcrc10/13 SSH 实查无本 workbench 队列或运行进程。fvcrc11 当前 SSH 连接失败，不能冒称实查完成；本轮没有在该节点启动任务。无活动子 agent。

其余授权节点核对：fvcrc12/15 SSH 实查无本 workbench 进程；fvcrc21 当前 No route to host，未核对成功，本轮未在该节点启动任务。暂停后未启动任何新研究任务。
