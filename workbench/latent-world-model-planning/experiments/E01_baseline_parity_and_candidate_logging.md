# E01｜强基线与共用评测

- **状态：** RUNNING；完整发布AD-WM参照DONE，同数据三arm×三seed重训进行中；不称论文数字复现。
- **对应：** 建设与R1–R5；不强挂论文claim
- **来源：** S1–S4及ASSETS原生协议。
- **阳性对照：** 先在熟悉ID任务检验native表现；真实轨迹回放和目标匹配检查。
- **噪声地板：** 独立train/eval/planner种子分开；探索可少seed，主结果再增加独立训练seed与区间。
- **决策表（跑之前写）：** 基线偏弱→查加载/协议/训练量并补强；原生可用→开展对应方法；诊断不足→补必要字段，不冻结所有研究。

## 问题
建立足够强的对照和可复用读数，使新方法收益可解释。

## 首轮方案（可在运行前修订）
至少一个trainable baseline和一个按需要选择的强参照。保留native协议，另存共同eval manifest。分开input、data、train budget、goal source、H/K、action repeat与cost。轻量记录候选与实际结果，不先建全功能logger。允许原生复现与方法试验交叉推进。

## 读数与资源
任务成功/代价、训练与推理成本，必要时固定候选regret/真实终点编码；大trace节点保存，git只存manifest/hash。

## 结果与修订
最新状态见下方Stage0及实际config/预控/进程记录；此前未运行段落是原设计历史，不覆盖当前训练。

## 2026-10-04｜AD-WM完整发布模型接续（运行前）

I14/E20的raw inverse只是组件对照，新增官方AD-WM完整模型参照以避免弱替代品。官方代码7c27ebfdc4a2ba8e5a16268f2e4aa852fda72144，HF31ab745259718946aa83f2d6df19dfebb0c8ebd4；仅下载TwoRoom/PushT seed3072与config/manifest到标准HF缓存，不拉Cube/Scene全套。先在专用新Python进程AD代码namespace加载，核对object class/predict residual/inverse+MI heads/config/hash；同真实pixels/actions的cached rollout与AD原生get_cost parity。不能在已经import LeWM或Fast的jepa/module namespace里pickle加载AD，避免同名类静默套错predict。若dependency冲突，先在现venv做最小隔离import，不能改正在运行训练的环境。完整checkpoint加载仅工程证据；数值replica/官方eval与fixeddata同数据训练未完成时，不claim战胜AD-WM。新48source开发集released训练episode未知，不称unseen于官方模型。

完整AD CPU控首次失败于native input contract：info缺dummy action，官方get_cost对goal.pop(action)触发KeyError；此前object class/residual/inverse/MI/strict/finiteness加载已过。原源码/log/failure durable20261004-E01-adwm-cpu-preflight-failed，未生成方法读数。retry1补真实原生输入dummy action，不变dataset/source/动作/模型，不覆盖旧failure；不把接口缺key误判方法预测不一致。

AD-WM retry1完整CPU控PASS：TwoRoom/PushT两个完整object均exact官方JEPA/module namespace、residual formula原式exact、完整inverse+MI heads、strict321keys/19,220,654 params、全部tensor finite、H3+future5原生cached cost导航差0、操作maxabs9.5367e−7（rtol/atol1e−5内）。两checkpoint SHA与官方MANIFEST一致；未删aux后冒充完整加载。portable E01_20261004_adwm_cpu_controls.json，raw durable20261004-E01-adwm-cpu-preflight-retry1，原missingaction failure保留。后续GPU完整闭环/同数据训练仍待执行。

GPU完整参照（运行前）：专用AD namespace fresh进程，官方seed3072 TwoRoom/PushT完整object，先用实际像素/动作/native_control校对，再保存E20全部held12×12真实候选读数（Nav position成功<16；Push原生pos+角成功）。TwoRoom在同新48source development/100newsteps/H25EX25上跑physical与native接口两个完整controller，300/30/30/共同planner resetseed105400+j×100+d；完整真实actions/state trace与statehash不可变守卫，失败保留。不混两发布trainseeds或删辅助head后冒充完整SOTA；当前两任务均同publishedseed3072，训练数据/充分训练量与E20不匹配，因此仅external strong reference，不做同数据优劣claim。原paperbenchmark协议未运行，不能称完整paper numeric reproduction；新scope/data/planner参数全存raw。

GPU reference运行源码7c45a38f775b889386110a4090ec8deb9e0b9c64b53c2ea510a31689e76b2d38；两CPU原生控通过后启动专用RTX槽，新raw/durable20261004-E01-adwm-reference-RTX-s3072。没有先读其query读数改方法或目标。

完整AD-WM reference已DONE：原native近24/24、远18/24，physical20/24、8/24；共96导航episode全部保留，两task各12offlinequeries（Nav12/12、Push3/12）。RTX GPU native cost maxabs均0；CPU Push约9.54e−7的旧读数保留不混写。完整trace SHA/初始位置/原native距离阈值成功复算/源checkpoint重新hash通过，见E01_20261004_adwm_full_reference.json。一个发布trainingseed/未知未匹配训练data，不能称同data loss增益或原paper数字复现；它是必须面对的full strong reference，而非raw inverse头替代。

## 完整AD-WM同数据训练分解（2026-10-04，运行前）

对应P04/I14与R1/R4：发布full reference强，但训练未匹配；需要区分residual结构与learned-action inverse/normalized recovery本身。锁定同BASE100的100episodes/9295rows/7295 clips、原norm、四frames0/5/10/15与20真实actions、joint encoder/predictor、fresh AdamW5e-5/1e-3/clip1/bf16/128batch/5650updates。三独立trainseed0/1/2全部保留；同各seed backbone303初始化和shuffle33000+seed。三arm ABS / RESIDUAL / FULL-AD，各seed顺序完成全部arm，绝不把已训练absolute权重加residual当同initialfunction。ABS/RES共有初始化weights，函数差异是显式结构干预。FULL-AD增加官方两个完整192dim embedding-recovery heads，目标SG/batch ddof0 normalize/fixed-unit NLL按192维sum/KL.01，权重inverse.1/MI.01/SIGReg.09；不用raw10dim替代。

直接从固定官方train.py提取pure paper_forward/inverse_features/normalized_recovery_loss三函数，保留源码SHA；不安装完整Lightning到live环境。模型组件仍官方AD namespace，严格303公共tensor/新增headkeys校对。恒定LR是本地匹配训练协议，非原Lightning scheduler数值复现。CPU/CUDA预控须通过loss逐项手算、ABS与原LeWM源objective一致、SG目标无梯度、fullencoder/predictor/action+heads梯度finite/freshoptimizer源state独立、H3+future5官方cost parity、正确cache真实索引；然后启动九独立single-GPU训练。模型与optimizer/RNG存HF，训练raw/cache本地；节点render有1LSB差故训练不进行simulator efficacy评分。完成后在原RTX用同新48 wholeepisodes/同plannerbudget比较所有九model，两个接口均面对强参照；fixedu5650未完成前不挑checkpoint。

主读数：matched native success、新envsteps、same-bank真实candidate regret（开发readout）及独立trainseed原数；每pair episode/source CI，不扩candidate为n。阳控ABS回到原同data训练实现、officialloss手算；噪声baseline38/19/36说明不筛弱seed，数据/encoder维度间MSE不横向排能力。决策：FULL-AD稳定胜RES→进一步动作后果/数据组织设计；只RES有效→识别结构效应；均不胜充分plain→改变监督/表示/数据机制，不扫lambda。第一批为complete-method baseline calibration，不是novelty确认。训练预算九×5650，四A100独立slot至多，先实际单step/峰值再确认并发；不占其他工作。

GPU启动前再校对：CPU实际完整loss/gradient控制通过；A100初次GPU预控在构建初始化对比处失败（没有训练步或效用）。源303 saved-init完全保留，不能要求不同CPU的seeded构造浮点结果bit-exact；新版每arm显式strict-copy同一保存的initial303 tensors，随后逐tensor exact断言，记录constructor mismatch数量与saved-init SHA。不是用不同initial放宽公平性守卫。old CUDA失败log/源码durable保留，retry3实际CPU+CUDA再跑后训练。

最终CPU/CUDA retry3全部PASS：ABS/RESIDUAL/FULL-AD/VGIQL-JOINT/VGIQL-SEPARATE actualbf16 loss/手算/finite梯度/fresh step、learned-action target SG、Bellman absorbing/duplicatepixel语义、Sep完整两阶段、源three savedinitial加载exact与原生H3+5future成本maxabs0。代码SHA0400260fc47d21629414582d266eb39bca47693905f118b6e1782cdff666d077，GPUconstructor74/75tensor不bit-exact但saved303权重显式strict-copy之后全exact。实际启动同A100节点四独立slot：source0/1队列已真实1900/500updates、各14.8GB/95–97%利用率，1→2没有failed或共享数据stream；再启动source2和value队列到4，各node-local同41MB压缩cache解压1.4GB、manifest/原7文件SHA验证。三source每条依次ABS/RES/FULL-AD，共九5650；value sequential JOINT/SEP共二5650，全部完成前不筛方法/seed/readout，所有model/HF/raw unique。不是novel方法confirmation或跨节点simulator评测。

同数据训练终点部署（运行前锁定）：九个E01模型与两个E14模型全部u5650，原RTX/new48部署physical和strongnative两接口各一次，总11×2×48=1056episodes；原ledger/300-30-30/H25EX25/100steps/seed/actual history与success/trace guards不变。发布LeWM/AD参考独立列，训练data未匹配，不纳入同data gain。value两arm单seed，必须相对同seedABS，不能跨三个source拼n。训练可早到的固定终点先入队评测，但整批齐前不按partial效用修改训练或筛方法。

使用matched_control_queue.py专用AD namespace，明确构建各arm residual/fullheads，再strict load其已固定终点；暂时传给原controller的architecture callable，finally恢复，仅当前独立进程，原bounded_control/live scripts不修改。保存matched arm/loader SHA/checkpoint/schema与判定traincomplete。队列原RTX GPU1 physical matrix自然完成后取槽；不杀训练或抢GPU。首次ABS actual native parity/完整episode守卫通过后按既定全部11model展开；加载失败保留unique failure，不改任务/预算。value单seed/两阶段曝光差异维持原范围，未得结果不称收益。

2026-10-05全部十一train终点独立audit PASS：九matched ABS/RES/FULL三source与两value支点5650，common init/saved全部303（FULL含新增head共321）逐tensor exact，source内首128clip/finalshuffle一致，原官方loss脚本hash固定，所有weights与AdamW moments finite；ABS/RES/JOINT297states5650、FULL309states5650、SEP first204states2825/last93states2825，完整init与accounting均校对。结果E01_E14_20261005_matched_endpoint_audit.json，durable20261005-E01-E14-matched-endpoint-audit。只是初始化/训练预算证据，完整控制效用仍待原RTX全部22组，不当paper数值复现或science claim。

### 2026-10-05同data完整训练与闭环整批读回

[全部22groups/1056episodes](../results/E01_E14_20261005_matched_control_results.json)独立trace/source SHA/native成功/48分母审计PASS。ABS physical24/18/24、native30/23/24；RES8/17/16、8/20/20；FULL-AD23/19/23、24/20/28，各source48。FULL对ABS总体physical−.00694 CI[−.125,.1043]、native−.03472[−.1875,.1111]；对较弱RES的+16.7pp不能替代对ABS的比较。共同100data/5650constantLR/完整官方learned192D actionheads与pure loss的本地matched开发，不是原paper训练schedule数值复现。全部seed和原失败守卫保留，science claims0；value结果/三个seed重复详E14。

### 完整RC-aux发布邻居：实际GPU代价与新48闭环（2026-10-05，运行前）

这是D1必要基线支点，支持I09/P05/R3，不是新idea。使用已严格CPU加载的官方312keys/完整ReachabilityHead object（HFbiubiu116/RC-aux pinned1cb0e604，SHA56979b8791dc76bab066c8c7a5aaa1c2947be8911b7a50202b69be46ab866099；官方code cbdf3786），不以LeWM terminal-only wrapper丢掉head。训练split/完整训练schedule未匹配，不称公平loss因果或原论文numeric复现。normalizer按官方eval.py全dataset finite-action StandardScaler，用本机节点cache一次读取并记录dataset引用hash/源码/实际statistics，不擅用ownBASE100norm。

锁定四成本条件：H1（官方eval history_size=1）和H3（当前统一实际三pastframes的port）；各HEAD-ON=.85（同官方object与pinnedvendorREADME eval调用）/HEAD-OFF=0，同全部权重。此前HF附带config曾记录.35，与当前README/object不同，本批不靠held效用挑weight、不搜索λ；明确实施.85版本且不称消除发布配置差异。H3原criterion按pred[1:]计分包含两pastframes，horizon7..1/headclamp至5；保留官方原生计算，不能偷偷对齐paper公式后称publishedbaseline。

CPU actualpixels37同候选与CUDA两H完整model.get_cost vscached整段rollout+原criterion parity；HEAD-OFF bit-exact terminalL2，HEAD-ON逐step sigmoid/head真实预算与multiplier手算、全部weights/buffers不变是阳控。37个physicallegal候选fixed RNG，不用hidden outcomes。两预控都PASS才GPU2顺序四成本×两接口×fresh48=384episodes；原b.restore精确warm/初始position/factualguard，两CEM300/30/30/H25EX25/最多100newsteps均freeze，seed105400与现有strongrefs一致。H1只给最后pastimage且无pastactions，H3给三frames/两pastmacro；goalimage正当任务输入、未来factualactions不进planner。

主读数分层success/steps、同checkpointHEAD-ON/OFF paired48CI、H1/H3全部原数，primary原nativeH1+.85公开协议与H3port保留，不以胜的接口替代原协议。只一个publishedsource，共享48tasks不能当independenttrainseed。对已充分ABS/value/AD-reference只作能力参照，训练数据/预算不同。失败原raw完整保留，no threshold/λ rescue；源码/checkpoint/config/轨迹SHA与envdone逐真实state独立成功一致。决策：若head同encoder有效则作为后续完整strongneighbor，若无效也不能否定joint RC training/value母问题；后续增量需同data完整训练与newgoal/task证据。单freeRTXGPU2、不占新ACTIVE状态，不改原环境，模型HF。

### 完整RC-aux原criterion控制结果（2026-10-05）

[actualCPU/CUDA预控](../results/E01_20261005_rcaux_full_preflight.json)四条件native criterion vs cached rollout cost bit-exact0、reachability fullhead/logit/sigmoid/预算/clamp独立手算exact、weight0退化L2 exact。严格原发布object312keys含9head、SHA56979b8791dc76bab066c8c7a5aaa1c2947be8911b7a50202b69be46ab866099；官方StandardScaler完整finite actions归一化，不用own100norm。

[全部384实际闭环](../results/E01_20261005_rcaux_full_control_results.json)八groups、48全部anchor、真实初始state/trace hash/所有native成功事件/checkpoint/完整head/重新计算scaler/source审计PASS，GPU2原PID3579990自然退出。H1 head ON/OFF native38/33、physical34/31；H3 ON/OFF native37/34、physical35/32（各48）。H1 native ON−OFF+10.42pp paired-anchorCI[0,20.83]、H3+6.25[−2.08,14.58]；未确认跨训练seed新机制。所有近/远及真实envsteps保留，不按partial选择history或weight。

规范以pinned object/vendorREADME weight.85为准，HF附带另旧config.35差异显式记录，未调权重。H1原history与H3port使用同原criterion：后者也评分两pastframes/预算7…1并clamp5；未擅改成另公式。原官方预算50、本任务100，发布训练数据/分割未知且与own100不匹配，所以是完整功能/开发能力比较、不是原paper数字复现或同data因果。依赖预控先因缺sklearn/scipy失败，无efficacy rows；只补既有环境缺包 --no-deps（sklearn1.7.2/scipy1.15.3/joblib1.5.2/threadpoolctl3.6.0），Torch/NumPy不变，失败原log保存20261005-E01-rcaux-dependency-preflight-failure。

### INTACT完整联合训练公开支点（2026-10-05，运行前）

对应D1/P04/P05/R3：冻结GC-policy在导航强、Push弱且86/860×400/4000没有显著恢复，不能代表end-to-end动作条件塑造表示。新增官方paper-runtime完整INTACT E5 goal-displacement seed0两个task，code653ee222、HF revision0430df6f、SHA/companions已经verified。paper-runtime五槽actor与当前clean四槽不同，严格使用发布config.json实例化全部encoder/predictor/projector/actor，全部state strict/finite，绝不用新root类套旧权重。metadata/sharedencoder/full runtime hashes记录；两任务数据与训练预算未匹配，发布pretraining split未知，仅强能力参照、不称paper numeric复现。

先CPU/CUDA真实像素完整get_action五chunk与逐步手算actor语法/mean/递归history匹配、原BlockStandardScaler与实际最后五primitive动作匹配、任意future target action不进入info、参数BN不变、full48 state/pixels恢复exact。标准单观察H1：当前actual pixel加严格执行过的五primitive history，与官方StatefulActionHistoryPolicy输入语义一致；不能把相邻dataset目标action当prevaction。新环境已有10真实warm动作，无需padding。get_action horizon5；25primitive承诺执行，再反馈/规划，最多100。原official50-budget与本地100不同，不poolheadline。

锁定两个task×native raw输出/physical输出clip×原fresh48=192，全部近/远/initial-success保留，native原位置/Push角度criterion，完整轨迹/源hash与每decision真实history记录。原官方primitive StandardScaler全dataset统计复用已审计缓存，而非自己的100训练norm；五槽actor特征手算和真正未来预测手算均先于efficacy。阳性factual原复放成功；噪声地板仅paired48task-anchor bootstrap，不含三个训练seed。单空RTXGPU2，独立单卡，env不升级。失败保留并停在相应guard，不放宽它。

决策：若完整INTACT恢复Push，则后续数据/表示增量以完整联合模型为强支点，不能围绕弱冻结头救故事；若仍弱，先核对发布输入/数据/控制接口差异，再设计完整matched训练而非宣布policy不适用。next method必须有复用或真实控制收益，不把direct controller、intent-actor共享、分角色称首次。只有完整192与独立审计才报告效用，两个task都保留。

INTACT第二preflight失败记录：发布transformers5.9的encoder.layers/q_proj/mlp与现环境encoder.encoder.layer/query/intermediate keylayout不兼容，strict=True拒绝，无模型效用。官方stable_pretraining0.1.7 wheel的vit_hf函数已下载读源/哈希，与tiny192/12/3/768/patch14构造一致，旧env不安装。新latent-wm-intact system-site-packages venv只隔离发布transformers与必要依赖，runtime/heads/weights不改；新唯一v3接续加载、原失败保留。新环境仍使用原SWM0.0.6/NumPy/Torch，若环境恢复/图像不exact则停止效用，不放宽guards。

INTACT v3隔离venv已成功：transformers5.9.0、Torch2.7.1cu128、NumPy1.26.4、SWM0.0.6/pymunk7.2.0，旧env未变。使用提取的官方vit_hf函数、paper-runtime全部head；两个shard full state strict、sharedencoder SHA05c6b2f0…与manifest相同，CPU/CUDA full五chunkactor/递推手算bitexact、全部state keys以result实际记录、原full48state/pixels恢复exact。全部192完成/[独立causal trace与source审计](../results/E01_20261005_intact_published_control_results.json)PASS：TwoRoom37/48（near22/far15）、Push25/48（22/3），两interface相同且均含initial1；native执行1750/3030 envsteps。前述source/版本失败都保留、不择checkpoint/seed。完整joint强参照显著高于Push冻结head的1–5，不能把冻结策略失败认定为policy家族失败；不同data/pretrain/容量/100 vs官方50，不称训练causality或paper数字复现。不能拿Push25 vsreleased24的1条差值当methodgain。


2026-10-05 E18F3前置资产（运行前）：接续完整INTACT source0，在同HF immutable revision0430df6…下载官方trainseed42/3072 archives，仅取Nav/Push权重与对应config/epoch5meta，按PAPER_E5_GOAL_MANIFEST bytes/SHA/sharedencoder验。已有source0/cache/env不改，无GPUtrain/efficacy；新的跨sourcefullcontrol归E18F3，不从官方下载headline生成本地主张。raw资产ledger unique20261005-E01-intact-three-seed-assets。
