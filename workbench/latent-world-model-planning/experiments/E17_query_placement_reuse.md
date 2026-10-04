# E17｜Selective Query Specialization：任务条件化与复用

- **状态：** DONE（PROPOSAL-ONLY pilot）；adapter/full-query仍未运行。
- **对应：** I10 / R3。
- **来源：** S18 + I10；这是第二波方法线，不阻塞E13/E16。
- **阳性对照：** query-agnostic COST-ONLY baseline；FULL-QUERY specialized reference；seen目标上query信息确实能被模型利用。
- **噪声地板：** 固定goal split、训练量、query信息与planner预算；seen/unseen目标严格分开，测试目标不参与调参。
- **决策表（跑之前写）：** selective adapter改善seen且保留reuse→扩seed/task；cost-only已足够→保留简化结论；full-query无unseen损失→该任务无明显specialization tradeoff，换更异质目标或停此方法；所有差异由参数量解释→做capacity match。

## 决策表（跑之前写）

具体方法pilot的决策与替代解释见下方2026-10-02运行前锁定协议；不以单次无显著差异判母问题失败。

## 核心问题

一个compact world model需要多少query/task specialization，才能既对当前目标更好，又保留跨目标复用？

## 第一轮任务设计

优先用已有可多goal评测的TwoRoom / OGBench Cube：

- **seen goals**：训练时出现的goal families / task IDs；
- **held-out goals**：同动力学下未参与训练的目标组合；
- 可选 **query shift**：同一state-action dynamics，换cost/goal定义而不换环境物理。

首轮不用自然语言；所有方法看到等价的goal/task信息。

## 方法矩阵

1. **COST-ONLY**：action-conditioned predictor完全query-agnostic，query只进入goal/cost。
2. **PROPOSAL-ONLY**：predictor不变，query用于candidate proposal/initialization。
3. **PRED-ADAPTER**：predictor末端轻量query adapter/residual。
4. **SELECTIVE-ADAPTER**：只对planner boundary candidates或高query-relevance latent tokens/channels调用adapter。
5. **FULL-QUERY**：query注入主predictor，作为强specialized reference。

第一轮2–3个最容易实现的版本即可；不是必须一次跑齐五个。

## Fairness

- query表示和维度对齐；
- total train steps / data相同；
- adapter额外参数单独报告；
- deployment compute单独报告；
- COST-ONLY不能偷偷拿更强goal encoder；
- FULL-QUERY若需更多task labels，单独计task information。

## 主读数

### Performance
- seen-goal success / task cost；
- held-out goal success；
- query shift后的zero-/few-shot性能。

### Reuse
- 不更新predictor时新goal适配成本；
- 只换cost/head与更新adapter的差距；
- old-goal retention。

### Specialization
- predictor output在不同query下变化量；
- candidate ordering变化；
- seen gain / unseen loss ratio；
- 额外params与wall-clock。

## 最小可投叙事的条件

至少要有一个**设计决定**被清楚支持，例如：

- query只放cost/proposal已足够，full query-conditioned predictor没有必要；
- 轻量selective adapter保留大部分seen gain，同时显著改善unseen reuse；
- specialization的收益只集中在long-horizon / ambiguous candidates，形成可解释使用规则。

“query-conditioned比baseline高”本身不够。

## 结果
proposal pilot全部320episodes完成，见下方实际记录。


### 2026-10-02 P05/R3 query-in-proposal pilot（运行前）

原协议的PROPOSAL-ONLY先做，借用标准future-relabelled GCBC（强baseline，非新方法）和SWM0.0.6原生CEM `init_action`。近邻Planning Limits §7已做VLA proposal→WM selection；PLDM/SoRB是方法来源。本pilot判断目标条件化放在proposal是否有互补价值，不能把GCBC+WM改名当创新。

两released Fast backbone冻结；各100官方episodes：TwoRoom继承E16 seed0 exact base100，PushT从len>76整episode中seed68000抽100，排除E13 prepared两strata全部64+native source anchors。TwoRoom排除本pilot两strata前16+source anchors；旧g75全64中episode5613被base100见过，未纳入本pilot16，禁止称对旧64全部held-out。新head评测episode与训练不重合；released WM预训练是否见过这些episode未核对，公开object没有split provenance。

所有合法同episode起点/未来goal offset25:5:75，标签为下25真实动作；无padding/no oracle deadline。head输入仅current192+goal192，MLP384→256→256→50；冻结encoder，原source mean/std规范化25×2动作。2000updates/b128/AdamW3e-4/WD1e-3/clip1/seed68000，记录数据/feature/checkpoint hash与全部训练成本，checkpoint HF cache。

锁定两task×goal25/75各前16、5methods=320episodes；ZERO300、ZERO900、PROPOSAL300、GOAL-SHUFFLED300（同stratum环移1goal，仅proposal换goal，cost仍真goal）、GCBC-direct。所有控制器看到同当前/目标图；真实budget50/150，执行25后真实反馈。native H1 macro25/K30/30 CEM，init_action为[1,1,50] normalizedmean，采样std/nativeeliteupdate不变；N900单列计算，head额外训练/部署compute不假称免费。

主读数：分task/range成功、vs ZERO900及GCBC-direct的help/harm和episode bootstrap CI；native距离、真实steps、candidateeval/encode/headtime作次读数。nativeCost allclose、trainingfinite、整episode隔离断言为正控，保留全部起点/方法，16episode CI非train-seed CI。PROPOSAL胜search/direct且goalshuffle退化→扩独立headseed/dataregime；GCBC已胜组合→研究何时WM selection有价值/可靠cost，不硬救组合；全部弱→对比cost/query placement，不否定R3。raw `20261002-E17-query-proposal-RTX-s0`，checkpoint HF `E17_query_proposal_RTX_s0`，单授权空RTX。


### 实际320episode结果（2026-10-03 00:00 JST）

[summary/config/hash/每method paired CI](../results/E17_20261002_query_proposal.json)，19,951真实steps；177,202参数head，训练各2000steps：TwoRoom47,450pairs/9,295编码帧/10.36s GPUtrain，PushT91,069pairs/13,279帧/9.47s，prepare/编码另计。顺序ZERO300/ZERO900/PROPOSAL300/GOAL-SHUFFLED300/GCBC-direct，各16：TwoRoom25=13/15/16/15/11、75=10/14/15/14/12；PushT25=14/16/14/14/6、75=3/4/6/5/0。

组合的导航增益相对900候选各只有+1goal，CI含0；操作long为+2goal/help4-harm2，CI[-.1875,.4375]。打乱proposal goal几乎达到组合结果，尚不能建立query信息的独立作用；GCBC-direct在操作明显弱，不能宣称击败强imitation基线或新颖的WM+policy组合。保留所有methods/goals；对比cheap train与部署开销，不把dataset/预训练预算混成equal-totalcompute。下一步比较state-only/action-trajectory结构prior与learned cost/query placement，及更强head data regimes；不局部调head层数救当前叙事。

### R3 cost placement：demonstrated continuation evaluator（2026-10-03，运行前）

推进P05/R2/R3，而非继续微调proposal。重要问题是goal距离是否给planner可用的进展排序；继承temporal-distance/value/HER成熟思想、Hidden Failure Modes的value/controlmetric强邻居，不声称学到minimum reachability或首次value-guided planning。真正待测design issue：在真实latent上训练的goal evaluator，进入WM imagined terminal后是否失准；把同监督输入换成imagined endpoint能否改善控制。

冻结原Fast两task全部weights/encoder/norm。复用E17精确100episodes及缓存latent/pairs，(t,h)为h25:5:75；同expert25action，REAL输入[z[t+25],z[t+h]]，WM-CALIBRATED输入[Fast(z[t],a[t:t+25]),z[t+h]]；MIXED对同pair两个inputs的MSE取mean。三head共相同random init/fresh AdamW、batchpairids、2000updates/b128/lr3e-4/WD1e-3/clip1；MLP384→256→256→1+Softplus，不额外输入goal时间/环境预算。标签(h−25)/50只指demonstrated suffix length，不当最短路径/return/反事实可达性；额外future labels训练使用相同三head，部署不读future。

五方法RAW-L2/RAW-COS/REAL-COST/WM-CALIBRATED-COST/MIXED-COST；RAW-L2复刻E17ZERO300，RAW-COS仅换归一化cosine。两task×g25/g75全部前16，H25/N300/K30/30、每25真实steps再observe、seed68000/resetseed同E17，budget50/150；320episodes。cost之外不加proposal、branch、newWMloss、cadence/router。缓存/数据来自原E17 hash，head模型HF E17_continuation_cost_RTX_s0，raw `20261003-E17-continuation-cost-RTX-s0`，完成durable同名。MIXED平均loss多一个headforward，匹配updates不是墙钟或headtraining FLOPs。

阳性对照：REAL/WM同pairs/labels、source episode不重合actual评测16、encoder不变、common head init/batchids隔离、Fast same expert prefix与原生terminal一致、RAW-L2复现既有success/envsteps/distance；nativecost与gradfinite。噪声地板：单releasedcheckpoint/单headseed、每task/range16episode bootstrapCI宽；WM原pretrain未见性未知、PushT restore memory限制继承。primary各task/range closed-loop success/paired help-harm/native distance对RAW-L2；train fit与真实/imagined held-out factual-pair误差只作辅助，不能替代utility/对counterfactual泛化。

决策表（跑之前写）：WM/MIXED胜REAL且两task有utility→确认 imagined-evaluator训练域这个设计，再扩counterfactual/secondmodel/独立headseed；REAL已有效→先用强temporalcost baseline，不能称calibration贡献；COS已有同收益→简化几何解释；all弱→记录null、改变预测结构/任务信息/goal progress，不连续调head层数或缩任务包装。当前只是高信息method pilot，不是novel claim。GPU待A5后授权空卡，代码CPU预控与root审阅后才启动。

运行前action接口修订：precision独立audit确认TwoRoom物理commands真实clip[-1,1]、模型cost未clip，已生成plan实际issued超界41–73%；PushT env relative step并不clip。尚未GPU costhead运行、未见读数，不依据方法success更改。主5methods改名EXEC-L2/EXEC-COS/REAL-COST/WM-CALIBRATED-COST/MIXED-COST；TwoRoom全部5使用physical denorm→clip→renorm后输入模型，训练expert25计算imagined cache也同transform。TwoRoom额外NATIVE-L2完整保留原生未clip评分，与E17核对；PushT只原5methods且EXEC-L2等原NATIVE。合计352episodes。primary headgain对EXEC-L2；NATIVE→EXEC是经典interface repair（FlexiWorldE.2强邻居）而非方法贡献。真实发出的原command继续由env处理，scoring使用其实际动作效应；不悄悄改变noise/proposal或PushT动作支持。

最终CPU预控/root审阅已完成（GPU前）：236行独立脚本，真实E17pairs47450/91069、uniqueendpoints6795/10779；label/pair边界/commoninit/ids/梯度与TwoRoomcanonical physicalclip/Pushidentity/nativeCEMreturn50+30calls/352null统计全PASS。cost-onlytransform，native raw elite mean与分布更新不改变（不先transformcandidate再计算elite mean）。MIXED2headforward同meanloss，架构384→256→256→1共164609参数。即将GPU0空卡独立运行，其他运行源不改。

### Continuation cost 完整读数（2026-10-03）

[352episodes/23,859真实steps](../results/E17_20261003_continuation_cost.json)，raw/durable complete与summary/pairedCI已独立核对。导航近NATIVE/EXEC-L2/COS/REAL/WM/MIX=13/13/11/13/14/14，远10/6/6/9/9/8；操作近EXEC/COS/REAL/WM/MIX=14/14/7/7/8，远3/3/2/2/2，每组16。导航远head相对EXEC的+3/16未胜保留的NATIVE10/16；NATIVE−EXEC配对CI[.0625,.5]，所以不能把接口修订后的更弱baseline当整体增益。操作近REAL/WM各−7/16、CI[-.6875,-.1875]，MIX−6/16、CI[-.625,-.125]。WM-CALIBRATED未显现优于REAL的控制效果。

三个head共同init与batchids hash相同，各freshoptimizer/2000updates；native32/task成功与envsteps复现。last100 train MSE导航约.022、操作.005，heldout factual real/imagined输入误差相近，不证明反事实candidate泛化或utility。该小数据demonstrated-time head没有成功，不能推广为goal value/RC-aux无用；RC-aux还更新representation、用budget hard negatives与L2耦合（本pilot均未做），不能称同方法负复现。下一步变预测对象/representation训练与跨backbone验证，不连续调temporal head层数。

### Task-factor evaluator（2026-10-03，GPU运行前）

推进P05/P08/R3/R2，不连续调已null的demonstrated-time scalarhead。继承HiddenFailureModes physicalmetric、经典可观测state decoder/多目标控制；不是首次geometrycost/imagined calibration。E11 POST-HOC显示短score改善agent位置而block/angle tradeoff，作为新pilot来源，不登记mechanism。新的额外监督来自原100episode H5可观察geometry：TwoRoom pos_agent/proprio xy（物理extent224，success<16）；Push agentxy/blockxy/sinθ/cosθ（extent512，success位置<20与角<π/9）。训练用GT labels，部署只有real current/goal images与候选动作、不能读state/velocity/physics；不宣称无监督或与nativeequal-totalinformation。

复用E17冻结Fast/100exactepisodes/latent+pair映射，endpoint从25改为5匹配EX5评分。两commoninit geometry MLP192→256→256→2/6，各2000updates/b128/Adam3e-4/WD1e-3/clip1、samepairids/freshoptimizer/冻结encoder与WM。REAL=.5真实endpoint5几何loss+.5真实goal(t+h)几何loss；MIX=.25真实endpoint+.25imaginedendpoint5+.5真实goal，标签两methods完全相同，MIX多一个headforward不称训练FLOPs相同。Goal真实域明确受训，不能让WM-only decoder未见realgoal制造域差。物理位置归一到extent，角度sincos；几何评分按native成功阈值归一位置平方与anglechord平方，agent/block/angle固定权重1。JOINT额外加nativeL2/192固定系数1，先不调weight/sweep。

六methods NATIVE25/PREFIX5/REAL-GEO/MIX-GEO/REAL-JOINT/MIX-JOINT；两task×g25/g75前16=384episodes，SEED78000与A5/E11同、budget50/150、CEM H25/N300/K30/30。各anchor先共同native25plan；NATIVE25执行25，其他同first5真实prefix，此后EX5shiftwarm/scorefirst5；真正首prefix由共同native而非head选择，全部早成功保留。native动作评分与A5一致，不改elite/noise；TwoRoom已知rawscorevsphysicalclip限制共享，PushT不clip。两已有强controls完整复现A5NATIVE25（64rows）和E11近goalPREFIX5（32rows）。

正控：原exactepisode/row/cachehash/pair枚举、两head标签/ids/init/realgoal权重一致、无velocityfeatures、goalphysicalstate只离线label/evaluator；nativePrefixcost/CMEMwarmshape/强baseline成功步数distance；所有source/hash/HFheadcache/fullrows保留。主读数各task/range success/pairedhelp-harm/bootstrapCI对PREFIX5与NATIVE25，两强对照都报；原native distance保留，位置/angle分解此批事前锁为aux，不以aux替换primary。单headseed/16anchors CI不是trainseed，extra tasklabel与预训练overlap未明单列。决策表（跑之前写）：GEO已有稳utility→强taskcost baseline并进一步比较representation/predictor入口/未见rolequery复用；MIX优于REAL且跨task→候选域输入问题值得扩但仍需强邻居；JOINT优于GEO→理解共享几何与taskmetric配合，不重命名classic mixture；all弱→换训练预测对象/历史或数据，不调decoder层数。源task_factor_cost.py约180行，raw `20261003-E17-task-factor-cost-RTX-s0`，head HF `latent-wm-trained/E17_task_factor_cost_RTX_s0`；CPU真实控/root审后独立空GPU3运行，当前未GPU/无读数。

02:25 JST GPU前预控完成：最终187行SHA `0c4dcbc1d7c7b107f7f607fd2aa2c83e8c72b4d995e0467547d338cb825987aa`。CPU实际native/prefix/CEM300×30/commoninit/freshoptimizer/有限梯度/全部384统计控制通过；CPU缓存重编码原tol2e-4失败（Navmax.02153、Push.001735）完整保留。按原CUDA路径、原每episode局部128chunk的first/mid/last复验，两task三帧与缓存maxabs全部0，原tol未放宽；不将CPU误差解释为科学现象。预控JSON、raw CPU/CUDA/cache vectors与pixels在持久artifact `20261003-E17-task-factor-cost-preflight`。root全文审后GPU3空卡free-wrapper运行原384矩阵；仅公共first5后采用新代价，报告为continuation干预，不称从首动作使用新head。


2026-10-04上传核对：[完整384episodes/24005steps](../results/E17_20261003_task_factor_cost.json)，404个raw/durable文件SHA一致、96条既有baseline reproduction guards全PASS、全部24组各16、summary success计数复算通过。NATIVE25/PREFIX5/REAL-GEO/MIX-GEO/REAL-JOINT/MIX-JOINT：导航近13/15/16/15/15/15、远10/7/11/11/12/12；操作近14/11/9/9/10/9、远3/1/1/1/1/1。MIX没有稳定胜REAL，head未形成跨任务胜强baseline的结果；保留所有methods。完整独立trajectory/statistics audit待做，不升级科学主张，不据此关闭R3。
