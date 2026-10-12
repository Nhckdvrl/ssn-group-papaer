# E131：大小模型上的同一证据形成解释

- **状态：** RUNNING；451238d5首评分前启动的TF32实现数值失败已完整保留，0科学row；完整FP32精度补核后同协议复跑，当前14/18批已完成并独立核验；L70两套四卡执行剩余四批。
- **类型：** CLAIM / 跨尺度核心机制检验。
- **对应：** C21–C24、I04、P17。
- **问题：** 能力更强时，关系证据的历史形成、随后读取与Source条件使用发生什么变化？已有answer→label形成解释能否在更大模型上用相同干预与读数成立，而非仅保留小模型结论？
- **为什么现在做：** 用户明确要求先核ACL/EMNLP/NAACL如何跨大小模型检验理论。Sun ACL25附录D/Table5在7/8/70/72B上验证关键阻断、表示与label-swapping等同一链条，层位置可变；CoSToM实际解释7/8B两个架构，70B为评判者，不算其大模型机制证据。ICES14B已有原生/自然文本/函数阳性，但不能仅凭它当更大容量已经统一；E129/130的Cue接口不改变C21–23理论对象。此项检验原论文的三个核心环节，不追加字段/头/层搜索。
- **最强解释：** Cho/CTA/AddUp拥有上下文化/输入标签合并/权重与V内容；Sun拥有映射PC/匹配/解码；本文候选增量仍是合法多Source监督的关系来源、输出依赖形成操作与实际Source函数使用。同一计算解释不要求相同层编号、相同效果量或所有模型保持错误。
- **设置：** Qwen3-32B post-trained与Llama-3.1-70B base，固定可核pins；同家族Qwen3-8B、Llama-3.1-8B在新确认材料作配对锚点，14B现有证据保留。FP32权重/缓存/eager/frozen，全FP32 GEMM并记录实际TF32=False（首轮TF32加速数值不合格，全部失败记录保留），无量化、无新增训练，单节点2卡/4卡连续层dispatch，不跨节点共同forward。官方70B与Nous镜像全部30权重SHA一致；复制完成后逐文件核。模型选择预定，不按分数更换。材料为既有受控与真实SST生成器；不是新benchmark。
- **固定协议：** 原E121的43条件形成/关系内容/系数1重建；原E120的64条件无donor原生操作与受限恢复；原E123的85条件真实文本两来源功能政策。原脚本与分析不修改；E131仅生成设备分派兼容副本，必要device-local mask比较/模型revision/计时/TF32flag如实记录。逐stage保留全部条件、namespace、查询scope、方向、single与一句指令。两大模型每stage16→32；两小锚点每stage32确认，合计18个完整run。发现池使用各stage旧固定seed；确认native/mechanism/function分别使用131101/131102/131103，validation材料，新确认在大小同family/可匹配tokenizer逐字配对，无旧模型效果筛材料。
- **读数：** 三环节的既有预定核心读数：E121原生A形成的B规则幅度差及label-interface系数1K/KV/V raw/rule-double-contrast误差（对照zero，所有通道/读取背景保留）；E120 full-source native cross-answer removal signed B-rule response及gate/native受限恢复、within/private controls；E123 shared两Source平均candidate/full准确率、selective/native/all-isolation/query-only配对CI及private/gold-conflict分层。新确认大小模型在相同context做配对差，用context bootstrap，不跨任务池假称相同样本。正确率无损不当机制消失；若大小读数不一致，先分形成与读取的原接口，不以换layer挽救主张。
- **阳性对照：** 同token单Source正/反私人规则、一句指令native、same-run完整token/cached、实际每层mask消费、pristine cache与noalias/seq；答词/分隔符/label实际位置与既有定义一致。多卡数值可达图与单卡科学含义相同；模型每层cache在对应设备，禁止CPU/disk offload与低精度。原有self与graph-zero保留。
- **噪声地板 + MIE：** 保留原.001nats cached/full与self floor（实际GPU误差必须通过，不临场放宽），固定10000 context-bootstrap910，重建沿父summarize的109910（分析AST已预先冻结）；两大模型固定16数值有效即32，不按方向选确认；所有零效应、负向、接近完美性能及不可靠primitive同报。阶段计时为model-run wall hours，多卡device-hours另按实际卡数计；另记从首次模型装载到最后stage的连续驻留device-hours，含生成/分析/阶段间等待，不能继续将单卡或stage计时字段直接当总作业GPU时。
- **混杂审计：** 模型训练配方/数据与参数量同时变化，不称受控scaling law；完整对照是同计算对象在这些capacity-spanning checkpoints上的跨模型检验。两个家族非每个尺度全部架构。设备dispatch只变数值实现，需明确误差；不拿失败load/不正确graph当科学负结果。无头/层/强度调优。primitive强而最终correct时，关系影响仍可能在confidence；不将没有accuracy损失包装成没有形成机制。
- **决策表（跑之前写）：**

| 完整跨尺度结果 | 认识如何改变 |
|---|---|
| 大小模型同原生形成/固定重建/操作贡献，准确率不同 | 同一历史关系操作在不同能力下继续存在，实际使用后果可被读取补偿；用实测gate/full差判断，不靠错误持续性定义意义 |
| 形成作用保持、读取或函数政策不同 | 在同一形成机制基础上解释Source使用的容量差异；原先共享/隔离的功能预测有可测条件，不强求同一收益数字 |
| 大模型形成/重建/原生操作关键环节不成立且private函数可靠 | 现有解释不能完整覆盖这些checkpoint；检查预定形成/读取接口所区分的计算变化，回最强机制文献推理，不直接退成小模型缺陷或用局部新头救故事 |
| 只有primitive/数值/实际mask失败 | 明确不可识别范围/实现事故；不作对理论的科学判决，也不隐藏它 |

- **算力：** Q32在有缓存/空卡节点的2卡FP32，L70在同节点4卡FP32；large D/C可独立节点复用同pin材料，small锚点独立单卡。最多12张授权空卡，正在E130卡计入占用，不碰外部进程。源冻结前只有下载/CPU检查，未评分。

## 首评分前记录

当前论文正文/附录SHA1c87…/413a…保持。已停止优先压版式；本项直接围绕跨尺度理论，而不是给旧结论增加完美适用范围。所有结果都必须回主问题判断其认识增量；不自动关线、改状态、凑claim或以论文页数宣布novelty完成。

## 首评分前独立封源

[独立pre-score审查](../results/e131/independent_pre_score_review_2026-10-12.md)，JSON SHA `f704da0132cfe0a6565ce3a2bb47e6874be6bdd9cfe21adf3cb1f6b5df142098`：三engine整棵AST仅执行allowlist差、analysis相同；18批480ctx/5440prefix/12160图/30720 query masks/268800 gold槽通过。六个大小新32确认材料逐字相同；真实DynamicCache CPU字面patch48例、全layer K/KV/V/self848例通过。独立审查没有GPU rerun，actual多卡mask/cache/数值仍由首context检查。

末protocol SHA `550890014e6553290695f7fb6f35823a4b25ef06acca551649934a69d30b643f`、dispatch SHA `2e6d2d2ab1f38937408c0a60ce09c141f4ddb6abd303857311a263c1638508bd`，科学engine与父pin在manifest。Q32目标fvcrc20 /dev/shm/ices_models/Qwen3-32B逐shard已核，L70两个实际节点继续下载/核验；先提交推main才启动Q32与8B，70依同identity gate准备完执行。0科学评分、无效果筛选、三认识不改。

451238d5已首评分前推main。2026-10-12复核20全部空、21 GPU0外部88883MiB/100%不碰、GPU1空；启动20 GPU2/3 Q32固定D→C、20 GPU1 L8新C、21 GPU1 Q8新C。三worker不按效果/准确率选；最多4张本项卡，70两个quad接入后最多12。导入/加载与第一context检查尚在进行，不能称已出大模型机制结果。

## 数值实现纠正，原设计不变

首轮TF32三worker均在首context cached/full检查失败且raw空，Q8/L8/Q32最大误差.039123535/.005498886/.003240585nats，原阈值.001保持。累计驻留.075811325GPU·时单列，不算科学结果。全部失败raw/log/worker及原pre-score seal保留在results/e131/failed_tf32/。只将dispatch TF32 True→False，恢复与父协议一致的完整FP32 GEMM；三engine/分析、18材料/种子、所有条件和读数不变，不扩大控制或缩主张。独立补核、再次commit/push后重新跑同固定作业。

独立精度补核已封：主pre-score seal更新`374a5ce4f50304fddf7bd8f02796c961aa0111d620c4e5dd48432e557cf6c899`；[单行修正审查](../results/e131/independent_precision_fix_review_2026-10-12.json)确认仅TF32 True→False及注释变化，protocol/三engine/18材料SHA全部不变，原f704 seal完整保留。全FP32 dispatch末SHA`5abd14f91ac0cd56f40e714413d83d066ff4173af5a24e0de1cd4788a5f0beb9`；再次commit/push前仍0科学row，原floor不放宽。

0a50bbb1已再次先push后复跑：同原空卡分派，实际Q8/L8/Q32第一context均通过完整FP32数值检查，max1.91e−5/7.63e−6/1.14e−5，self0；固定全部phase继续。fvcrc11/13的70D/C接入任务已等待各自完整资产与4空卡，C另外只等D首ctxnumeric，不看科学方向，当前下载中。


## E131首轮大模型机制结果：回到原研究问题

**事实（pilot，非新32确认）：** Qwen3-32B在真实SST两私人方向的single功能均100%，A形成条件作用2.8006[2.0147,3.6204]nats；实际label-interface、B共享读取背景的固定系数1 KV重建raw r=.86750、RMSE=.90072/zero1.73944，rule双差r=.93875。原生跨Source答案→A label阻断减少B规则作用1.8158[1.2704,2.4089]nats；受限路径恢复在A-only为1.0852[.6022,1.6600]、full-source为−.8221[−1.2109,−.4300]。同框架三通道、两个重建目标、正/反private与未确认stage交互均保留，不把单个交互CI0当其他形成效应失效。

**解释更新：** 当前大模型支持原计算操作及其读取环境依赖，而非只有小模型性能异常；模型完全能够学单规则，仍需解释多来源时关系怎样进入Source证据。不同通道权重/幅度并不自动意味着不同理论，也不能将r当完整算法。Q8/L8新32 Source函数targeted收益分别7.6172[5.1758,9.9609]/8.8867[6.5429,11.1328]pp，复现对共享/隔离方式的功能预测。

**下一判断：** 完成Q32同新32材料配对和70两phase三环节，再判断同形成过程与后继使用的关系；不以pilot与不同材料的8B作数值scale比较，不开新字段/层/更细控制。主问题、三认识、C21–23级别保持；当前[滚动raw审计](../results/e131/independent_raw_review_2026-10-12.md)8/18 stage，224ctx/112000评分、最大数值差8.55e−15。未完成部分不提前得结论。

### E131三环节大模型pilot完整（2026-10-12）

Q32三个D stage均独立raw-first封存，9/18批240context/122880评分。真实SST shared词表、两Actor平均full/candidate：native86.9141%、targeted95.8984%，gain8.9844[5.8594,12.5000]pp；targeted−all21.0938[19.3359,22.6563]pp，query-only−native8.7891[5.4688,12.1094]pp。两私人方向single本批100%，targeted在相反规则+18.75[12.50,25.78]pp、同规则−.78125[−2.34375,0]，全85条件保留。准确率平均不冒充joint。

**整体解释更新：** 同一形成操作、原生贡献与实际函数政策在32B首轮连起来，支持当前主问题是Source证据怎样形成并使用，而不只是一项小模型能力缺陷。单规则已正确仍有关系形成效应；不同读取环境的恢复方向和不同规则是否冲突的政策作用可由同一形成/读取解释分别理解。保留原C21–23与三个主文认识，不把pilot写成所有容量已统一，也不要求每个checkpoint的通道比例与restore数字相等。Q32新32材料三stage正在运行，70固定权重传输后执行同一链；大小配对只纳入新确认，当前D不与不同材料的8B配对。

### E131：同新32材料的形成确认已完成

Q32新确认n32的A形成signed/absolute2.67564[2.26579,3.09561]nats；label-interface B0固定系数1 KV raw r=.882834、RMSE=.864484/zero1.856570，rule双差r=.922132。完整12 K/KV/V×目标×读取背景保留；single两个私人方向本批full100%。B读取signed3.48458[2.59559,4.34803]；stage signed交互CI0而absolute+.95308[.16203,1.74936]，不将平均符号抵消当形成操作没有作用。

与Q8逐字相同的32context配对：A形成abs large−small+.48496[.02565,.94531]，signed+.32451[−.14989,.81070]。这不是受控scaling law，但直接支持相同形成解释继续适用于32B；相同理论允许幅度与通道比例变化，不由partial Cue或单个signed交互收缩C21–23。新32原生操作/函数stage与70同链继续完成。滚动独立审计10/18 stage、272ctx/133888scores，本批1041数值差1.89e−15；[全报告](../results/e131/report.md)。


### E131：原生操作的新32确认与完整读取环境

Qwen3-32B与8B逐字相同的新32材料中，Full-source历史跨来源答案→本来源标签移除效应1.97202[1.46707,2.49960]nats；受限恢复在A-only为+.77513[.32126,1.28387]、Full-source为−.54448[−.83270,−.27605]。两个私人single方向本批100%，cached/full最大误差1.14e−5，self与graph-zero为0。全部64接口、within扰动、私人方向与指令对照保留；A-only恢复的absolute1.03131不是signed均值，不混用读数。

**对原问题的更新：** 同一操作在32B仍有原生因果贡献，且读取环境改变恢复作用，与新8B确认的功能方向一致。大小配对的移除和Full-source恢复差CI含0，A-only恢复large−small−1.36822[−2.29903,−.47407]；允许贡献幅度不同，不由此拆成细小新理论或收缩三条核心认识。研究对象仍是关系证据的形成与使用，非要求强模型持续答错。11/18完整stage、304ctx/150272评分；本批1217数值max0、18个同材料配对读数独立raw-first校对。完整[报告](../results/e131/report.md)/[独立校对](../results/e131/independent_raw_review_2026-10-12.md)，无独立GPU重跑。Q32函数确认与L70完整同链继续。C21–23 L3/C24 L2及formal状态保持。


### E131：32B完整三环确认改变了什么

Q32新32确认的真实SST shared/full两Actor平均87.9883→95.7031%，targeted gain+7.71484[5.76172,9.57031]pp；相对all-cross+20.4102[18.1641,22.3633]。A/B各+7.42/+8.01，opposite+15.82而same−.39CI0；mean95.70不是joint92.19。far all-cross candidate95.31而full52.64%、joint9.96，所有私人方向/other-word均保留。Q32−Q8同32材料gain差+.09766[−3.22266,3.32031]，不据CI0宣布增益等价；query-only差+8.39844[3.80859,13.08594]。

**全局解释：** 同一历史形成、原生路径贡献和Source功能政策已在32B首轮及新确认接成链，读阶段贡献能单独变化；这支持现有形成/读取解释跨当前容量，不要求同头/层/幅度或强模型持续失败。主文6.6/附录M已加入，与原三认识连续；C21–23 L3/C24 L2及formal状态保持，不由partial Cue收缩核心。第三环不是再增加一张性能表，而是形成预测的原生功能检验。

完整12/18stage、336run-stage ctx/172032scores、6.835413科学stage GPUh；新function1893数值max0、actual36864层mask调用、全批numeric最大6.68e−5/self/graph0。三组36同材料配对/144数值、9/12确认图点独立核；余L70不算0或证据。报告/全部85条件见[完整报告](../results/e131/report.md)与[raw审计](../results/e131/independent_raw_review_2026-10-12.md)。70双副本全30SHA完成，11的两卡外部占用后只移动资源：D13四空卡执行，C11/13fallback原子claim避免双启动，科学source/materials/analysis不改。

**05:31资源接入更新：** fvcrc10四卡空出，11 pinned L70副本进行peer复制至10可写本地大盘（统一/tmp模型入口symlink）。全部30预定SHA核验后同confirmation一次启动；与11/13原队列共享atomic claim，无重复科学writer。固定FP32/四卡单节点/材料/读数/全phase执行不变；分发helper与日志在results/e131/，未将传输或partial计为新科学结果。

**70B形成发现完整独立核（13/18）：** n16/5504scores、80层四卡FP32/eager，A形成+.99314[.61212,1.37253]nats，单源两个私人方向100%；label B0 KV rawr.54212/RMSE.63233 vszero.70481，B1r.85433/RMSE.82462 vszero1.47212。冻结通道/目标/背景全部保留，K在B0的RMSE略差zero、V优于KV，本批不支持统一KV最佳或随容量重建增强。固定词answer关系abs+.23662[.11647,.36828]、signed−.22883[−.38226,−.08503]完整报告。private能力与历史关系形成共存，机制贡献跨容量仍可测；通道贡献和阅读背景差异据预定同确认继续检验，不另开head/层/强度。独立1041数值差6.66e−15，旧12stage和配对对象直接字节/数值保持；本批n16不与新L8 n32配对。来源/运行/报告与read-order例外见raw-first审计，五70B批仍待完成。

**05:54:56并行启动：** fvcrc10第三副本全30 pinned SHA通过、官方mirror匹配；21.45分钟peer传输后confirmation获得共享atomic claim，10/13各四卡执行C/D。11/13旧fallback保留为互斥等待，不新增科学writer；实际最多八卡，精度/模型/全部阶段执行保持冻结。

**70B原生发现完整独立核（14/18）：** n16/8192scores、80层四卡FP32/eager，full-source答案路径移除signed+1.54209[1.09627,1.97003]nats；受限恢复A-only+1.01095[.63720,1.40072]、full-source−.43969[−.65350,−.20772]；cross-vswithin+2.55987[2.06511,3.05854]。A单源两私人方向candidate/full均100%，far词表signed及恢复零向结果全部保留。独立1217数值误差0，38400实际mask调用、cached/full9.54e−6/self/graph0。原13批未重算，368run-stagectx/185728scores/14.977382科学stage设备时；余D函数及C三批继续，等级与formal状态不变。

**新资源准备：** 复查fvcrc21四张空卡（低占用/0util），/tmp本地NVMe容量充足且预定模型目录未占用。11 pinned副本向21独立peer复制，逐文件核验同30官方SHA；本次仅资产分发，不读部分分数、不改18批/种子/精度/条件，当前science仍10/13各四卡。后续如拆分独立阶段，需互斥科学writer并记录调度，不把数据复制当新实验。

**独立stage调度（评分前，已纠正）：** 初版helper的stage claim不被旧10 worker读取，存在检查与写入之间的竞争；独立审查发现此问题，初版未运行。原审计保留，不以既有behavior断言声称自动互斥。修正版只在已结束D、四卡空闲的fvcrc13运行：核验10的owned父子PID与准确命令，短暂暂停旧worker，在确认其尚未完成native且未进入function后建立连续canonical空behavior交接fence，立即恢复旧worker；13在隔离输出ROOT执行原function，完成后逐文件发布，behavior始终存在、run.json最后发布。旧10继续完成机制/native，未来function guard必然看到fence，退出记录保留为调度交接。四卡FP32/85条件/n32/seed131103、材料、原五科学source与分析完全不变，独立驻留journal不覆写10。修正版需再次静态独立核，尚未启动；不读partial效果作排程或判断。


### E131：70B发现全链完成，第15批独立核

L70 n16真实SST shared/full两Actor平均86.7188[83.2031,90.2344]→98.4375[96.4844,100]%，gain11.7188[8.0078,15.4297]pp，A+5.8594/B+17.5781；opposite+23.4375、same0，targeted−all+23.4375[21.875,25]pp。query-only+10.5469[5.6641,15.0391]pp；targeted joint97.2656%与mean不同。far all-cross candidate99.0234/full51.1719/joint3.9063%，其它Source词48.2422%，来源非对称保留。single A98.4375/100%、B95.3125–100%。

**认识更新：** 70B的同一形成操作、原生贡献与真实文本政策后果已在发现批接成链；高单函数能力与共享形成的影响并存。选择性限制和全面隔离具有不同后果，不将改善准确率等同完整criterion程序。新32确认仍按冻结三批执行，无新读数、种子或微观分支。C21–23 L3/C24 L2及formal状态保持。

独立先raw后作者，1893数值差0、80层4卡FP32、23040prefix mask调用、floor2.28882e−5/self/graph0。15/18完成、384run-stagectx/196608scores/23.259151科学stage设备时；pre-author封签84dca94b…、rolling4bdafb69…，见[完整报告](../results/e131/report.md)、[独立raw](../results/e131/independent_raw_review_2026-10-12.md)与本批run/analysis。旧14批不重算，L70发现不与新L8材料配对。


**2026-10-12T09:00:29.414644+00:00实际并行交接：** 新helper先核四空卡/pinned镜像与旧10 owned父子PID，10短暂停后建立连续empty behavior fence并立即恢复；首13入口因NFS负缓存尚未看到该文件而0-GPU初始化退出。旧PID/空fence/无staging核验后，明确resume同reservation，补cwd为repo与可见性等待，最新helper802f85c7…独立静态通过；没有修改五科学源、材料、种子或数值floor。13隔离ROOT运行同function n32/seed131103，完成再逐文件发布且run最后；10原机制/native继续，未来function guard退出留作交接。首attempt与失败stderr保留、0科学rows/0GPU设备时；不把调度初始化失败当负结果。原raw连续fence从未删除，所有驻留分开记录。当前仍15/18独立核，partial不作判断。
