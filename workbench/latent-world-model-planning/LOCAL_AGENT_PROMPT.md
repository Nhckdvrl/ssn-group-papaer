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

## 2026-10-04当前恢复锚点

压缩后先读RESEARCH_PLAN §11–12、E20最新stage、log2026-10-04末尾和raw进程。15/15 Nav joint训练DONE，PLAIN8/11/9、CENTER12/11/8、PROB10/11/11（各12），开发CI跨零，科学主张0。全部三个A100闭环队列均在warm-history守卫失败、没有效用rows；失败已durable保留，不重启原unique run。跨节点CPU完整48factual位置轨迹exact，warm像素仅≤1级差异、具体原因未建立；RTX全部像素exact。physical/native全15方法已在原RTX完成并独立trace/hash/success校对，见fresh_physical/native_control_results.json。physical PLAIN20/32/21、CENTER19/27/20；native PLAIN26/29/27、CENTER25/34/27，各48。CENTER两接口CI均跨零；PID3484913/3501959自然完成，禁止重复启动。

PushT全部五arm已complete并校对（4/4/4/3/4，各12），PID3468517已退出；Nav strong-native全15也complete，log /tmp/latent-E20-native-method-all-RTX-queue.log留档，官方完整AD-WM reference已DONE（Nav原native近24/24、远18/24；physical20/24、8/24；offline Nav12/12、Push3/12），源训练data未匹配，不能作loss因果gain/论文数字复现。独立trace/source/native parity审计通过，见E01_20261004_adwm_full_reference.json。曝光GPU2 PID3415599继续固定100epoch终点，不读partial挑checkpoint。正在运行的effect_training/effect_transfer/bounded_control/data_exposure源码freeze；修改另版本+卡段。下一动作除完整结果读回外，应推进完整近邻同data训练和真正Bellman/value/goal-policy机制，不能围绕CENTER阈值或旧self-consistency追加局部救援。

E01同data完整AD分解与E14真实Bellman支点已通过最终CPU/CUDAretry3，见results/E01_E14_20261004_matched_learning_preflight.json。matched_learning.py SHA0400260fc47d21629414582d266eb39bca47693905f118b6e1782cdff666d077、queue均freeze。A100四slots source0/1/2三队列PID3607587/3608467/3608830依序ABS→RESIDUAL→FULL-AD各5650；value PID3608831依序VGIQL-JOINT→VGIQL-SEPARATE各5650（Sep两阶段2825+2825），logs /tmp/latent-E01-matched-s{seed}-A100-queue.log与/tmp/latent-E14-value-s0-A100-queue.log。全部checkpoint HF、cache node-local，不在A100作sim efficacy。初次CUDA预控seeded constructor74/75 tensor不是crossCPU exact，失败保留；正式每arm显式strict-copy同保存initial303并全tensor exact，不能擅改init或恢复旧版本。原VF采用gamma.98/tau.8、imageSHA identity、absorbinggoal、SGtarget；不是frozen时间回归或fullGCIQL/标准OGBench复现。两个value训练效用尚无，不能只用joint null否定value。


2026-10-05恢复：E01/E14固定终点部署queue原RTX GPU1 PID3513761，log/tmp/latent-matched-control-RTX-queue.log；11model×两接口×fresh48，源码matched_control_queue.py，显式完整AD namespace/各arm结构strictload，不修改bounded_control。全部组齐前不筛方法或改训练。E14 joint/sep训练5650已complete；E01 ABS/RES三个seed已complete，FULL-AD三个继续，进度查A100日志/实际pid，不能重启unique run。E20 Stage3新三arm×三source数据利用必要对照已运行前写卡，experience_utilization.py；CPU/CUDA预控及GPU队列是否已实际启动必须查最新log2026-10-05，不把写卡当训练。不得围绕CENTERλ连续局部调整，完整近邻/value/跨任务与数据利用共享母问题，当前没有成熟novelidea。

Stage3接续2026-10-05：experience源码4c4d5c45…freeze；实际node13 queues GPU3 IID3613956、GPU0 REPLAY3614306、GPU1 MIX3614357，每条source0/1/2各2000，logs/tmp/latent-E20-experience-{ARM}-A100-queue.log，全部源/低seed保留。原RTX GPU3 deployment首launcher3531292退出且emptylog/nooutputs；独立session实际新PID3536169/native→physical864episodes，log/tmp/latent-E20-experience-control-RTX-queue-retry1.log，禁止重复启动。E01三FULL与E14两value训练全部complete；matched controller仍自己完成11×2×48，不篡改splitqueue。新PushStage2b先查prepare日志/实际CPU契约，尚未GPU launch的状态不得写成完成，接续以最新log为准。

PushStage2b fresh48 CPU所有warm/完整diagnostic轨迹/goalpixels actualfactual repeat exact，5760steps，结果E20_20261005_pusht_fresh_prepare.json；独立session部署queueRTXGPU0 PID3536170，log/tmp/latent-E20-pusht-fresh-control-RTX-queue.log，全部五方法+released与完整AD参照两接口672episodes，只有一个transfertrainseed/pretrainunknown，不称confirmedgain。实际context/rows必须读log，不能重复启动。

最新训练状态覆盖以上in-progress：E01/E14全部11终点已独立audit；E20经验利用九run全部2000 complete并audit、A100三个新queues已自然退出。开发bank IID12/12/11、REPLAY11/11/11、MIX11/10/10 vsGROUPED8/11/9，不能把replay同样gain叫新增数据价值，也不能把iid当novelmethod。GPU0 Push672、GPU1 matched1056、GPU3 experience864均实际control中，整批未齐；GPU2曝光锁定100epoch继续，最后98/u55370未endpoint。上述源码freeze，不新启同unique run；接续读log2026-10-05和各controller日志。main已pushfdeeb000，checkpoint审计后小commit接续待最新git核对。

曝光状态再次覆盖：GPU2 PID3415599已实际达到100epoch/u56500，正在旧原48完整终点评测，尚未整批complete；不再称训练未到98，不读取partial决定方法。原队列自己负责持久镜像。三controller全matrix等待目标为matched22组、experience18组、Push14组；原始成功/配对CI与各source完整读回后再科学解释。
