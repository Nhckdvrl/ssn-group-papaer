# E80：会回应的玩家、角色取舍与可靠原生执行（2026-10-16）

- **状态：** DONE；4800逻辑episode/200图全部收齐，37642本地调用/3.61979观测GPUh/峰8卡/0API，本轮GPU均释放。
- **类型：** REPRO / I04探索；恢复有实际回应的强交互基线，不把技能包装成新方法。
- **对应：** I04 / C06 / P12。
- **问题（一句话）：** 玩家真正回应并采取合法行动后，NPC怎样坚持、协商或改变目标；可靠执行能解释哪些履约差，又保留哪些角色取舍？
- **动机：** E77将社会回应、当前角色和目标实现分开，但单次请求后的静态对方不能表现履约/改约。工业PUBG Ally/FACUL已提供语言决策＋可靠技能/状态反馈的强起点。本轮直接恢复这个基线并观察联合后果，不再添加保护句、扫层或先定新架构。
- **源设置：** 全部E55/E63原200个作者世界，直接复用`e63_native_dependency_qualification/snapshots.jsonl`中的原graph/全部NPC动机与原目标，源物品本来由NPC持有。不按对话/模型效果抽图；与E75地面102图分开，不混池造N。玩家无中生有的交易资产为0，合法Steal/攻击/取其他物保留。请求为该数据已有源物请求；它是实验赋予模拟玩家的目标，不冒称该B的作者quest。
- **角色与观察：** NPC全程同原persona＋纯trait F/A；玩家使用原requester persona和自己可见的look/inventory/原生事件，只知道自身请求目标，不读NPC私有动机、绑定goal或隐藏状态。双方同一被测本地模型，玩家不施加F/A；模型身份是整套配置，非纯NPC模型效应。固定初始请求以原生Say送达，然后NPC先动，双方交替各8次原生机会；不在首次goal/Give停止，保留返还、消费、装备后再交付和变化。
- **共同强决策层：** NPC可自由选择原作者后果、履行请求、真实说话或任意原生合法行为。两执行臂的策略输入/schema/seed相同，不告知后台。只显示当前可达后果的名字，不提示前提命令；一步已合法时两臂直接执行所选确切命令。玩家始终普通本地LLM＋真实状态/反馈，无脚本替它接受或履约。每次真实错误/已block/已完成事实明确反馈，只有Say/Tell/Whisper发送utterance。
- **唯一配置比较：** 当NPC自己选择了当前需要前提的后果时，`model_steps`由同模型选下一个合法原生命令；`native_skill`只取经原生fork验证的短路径下一步（Get/Remove→精确目标），不替NPC选目标/给谁。每个primitive占一个相同机会，玩家在两步之间照常行动；下轮双方看新状态，NPC可改选，不自动承诺把宏跑完。无可行路径时目标选项不可用，其他原生行动/谈判仍可选。技能可行性只用NPC可见源实体状态，不用对方私有动机。
- **样本：** 全200图×两trait×三seed8001/8002/8003×两执行器×两模型Gemma3-12B/Qwen3-32B，4800完整episode。首profile为源序首Give和首非Give两图的全部24episode/model；随后输入完全相同才精确复用，不按效果改图/seed/条件。已有E75/E77是机制背景，不与新harness分数差申领单一玩家回应因果效应。
- **读数：** 图级联合结果为NPC原绑定goal-ever/物理后果-ever、NPC实际Give源物给B、玩家自己Get/Steal或其他角色转移后取得、源物最终持有/装备/消费、NPC其他物Give、双向物品流、两方HP/死亡、全部错误/协议失败/成本。另报后果选择次数、首次选择与真实实现、两步选择/技能触发、原生Say/Tell/Whisper与非speech虚载荷。完成goal再交付可同时发生，历史完成和最终利益状态分开。文本协商只保留raw和有限等距案例，不用语义API定义gold或把等待统一判错。
- **阳性对照：** CPU全部源ID/goal绑定、200初态两用途原生见证；fork路径每个primitive真实合法且不改实图；同一一步后果两臂命令/输入精确一致；初始请求实际发送且玩家输入不含NPC私有目标/动机字段。全部原生状态变化与事件读回，无云fallback/自动重试/脚本选目标。
- **噪声地板 + MIE：** 固定三seed先源图内平均，4000图簇bootstrap95%逐项区间，全部200/原Give与非Give及小类并报。独立单位为源graph而非episode/调用；不新增科学去留bar，不按是否触发技能筛因果样本。选择前提的分支是处理后子群，仅描述。
- **混杂审计：** 两臂共同selector已是强结构基线，不把model_steps称完全原始LLM；可靠技能改变低层实现并可能通过世界反馈改变后续取舍，主量为闭环配置作用。held初态大多一步可行，多步机会由后续角色/玩家行动内生产生，不预设技能有增益。8+8机会不等于相同token；报实际成本，技能不折叠步数。模拟玩家既可能合作也可能自取/偷取，不用其拿到物品定义唯一NPC成功；无真人体验主张、同引擎/已曝光图范围保留。私有利益不等于原子goal，不能凭较低分判自毁。
- **决策表（跑之前写）：** 可靠技能增履约且角色资源去向保留→已选方案实现是可剥离负担，再看互动中剩余取舍；双方均好→接受普通强系统解决范围，研究具体新增玩法，不继续修提示；双方仍多未实现→按实际可行性/目标改选/对方行动读回，不能统称能力差；玩家自己取得/偷取主导→说明交互策略与权限重要，分开自愿交付，不人为禁止；模型/任务族方向不同→用世界与动态轨迹解释整体关系，不强求普遍两阶段故事。后续实验只针对能改变这些判断的真实失败。
- **算力预算：** 优先现有Conda fgvd和模型缓存，CPU→两卡完整profile→依据实测成本固定全队列，预计4–12观测GPUh；单卡独立worker、全时≤8且先查空闲，不干扰其他任务。0API/训练/patch/新平台。实际成本随后记；若资源不足只调整分片/排程，样本和读数不按结果改变。

## 结果

编号工具因历史未来编号引用生成E80；E78/E79仅为旧设计讨论，不代表已运行实验。下文保留先验设计、运行异常及POST-HOC读回的实际顺序。

### 首模型前独立审阅补充

共同selector/机会/私有观察/停止与技能调用审阅通过；200成对输入与400初始原生短路径检查通过。原生菜单还有`EquipObjectEvent`，其`equipped='equip'`与Wear/Wield的精确mode不同。保持bound主结果与strict-mode物理副读数，另独立报告源物generic equipped事件/最终mode，不把真实Equip叫完全未行动，也不未经引擎对照直接当目标等价。全部79装备世界的原生状态/stats比较属于CPU语义见证；不新增模型条件或用其挑轨迹。

### 完整profile与固定扩展

控制范围明确为NPC与请求者两名活跃角色，其他源世界角色保留原状态/规则但不加载自主policy；Give原目标的第三方接收者可能被玩家另行Steal。该去向与NPC自愿Give分列，不能从玩家最终获得物品推断NPC顺从或完整多人游戏均已验证。历史goal完成也不自动代表最终状态仍维持该目标，源物的装备mode/消费/最终归属独立读回。

两模型各2源图/24完整episode收齐：Gemma168新calls/216精确复用、50.404s推理＋23.825s载入；32B211新calls/184复用、82.326s＋33.603s。两者全部episode均跑满16机会，0原生拒绝/死亡/协议失败，32B原生Steal失败12次和Reward无奖励3次保留。每模型408事件（含opening）独立CPU重放、384/395真实input-key/schema/messages重建、12对共同初始输入/动作和72/97玩家私有目标隔离检查通过。profile只做闭环/成本，不用2图估计普适角色效应；所有成功和失败保留、输入匹配才复用。

源装备CPU对照确认79/79的Equip与Wear/Wield actor stats相同，完整状态唯一差异为源equipped字符串；继续分列exact/strict/generic，不静默替换主口径。依据profile成本，固定全200图×原三seed×原两trait×两backend×两模型，在fvcrc20/21现场空闲的8个独立单卡槽扩展，每模型4片，全部profile精确复用。两节点同一driver/data/Conda路径与SHA核对通过、时钟差<5s，不复制修改raw时间戳；profile先结束再启动full，峰值≤8。driver SHA `bd2e5ac631795a18cf03a27bf33bfb41722143ca6ae93333a81a028270073e8a`，skills `8665d31e6f36c5ac3501d8cfc0e6963aab2b85cd9bf890ec52786333c764bc0a`，data `feead76418153432da37a4ce7bf869215c6dbf004f396ca7bab44836181c3a0f`。不改变条件、评价或seed。

### POST-HOC补充读回（完整profile后、全样本结果前固定）

除原全图主读数外，额外核对成对执行器首次共同选择两步后果的分叉点。该点以前后台尚未改变实际事件/可见历史，两臂应共享状态、选择、原生见证。CPU重放共同prefix，重算Get/Remove前提，再比较model_steps的下一真实命令与native_skill实现。首次激活子群以共同prefix形成，与分叉后内生触发次数分开；只回答同状态已选后果的实现，不用它替代全200图结果或估计跨trait能力。此分析明确POST-HOC，不追记为首模型前预注册，不新增模型调用。

### 启动异常与原配置恢复（不产生科学样本）

fvcrc20四个首attempt均在模型初始化失败，无model calls/episode。机器实际为RTX PRO 6000 SM120；FlashInfer默认发现`/usr/local/cuda`的12.8工具链，规范化SM120f要求CUDA≥12.9而架构列表为空，最终误报sm75。没有证据是继承了旧ARCH环境变量。仅为该四worker指定现有Conda内cu13工具链（nvcc13.2）、PATH及真实`FLASHINFER_CUDA_ARCH_LIST=12.0f`，同一driver/skills/data/seed/条件恢复。失败目录/log/launch以`_init_failed`保留，每片约4.8分钟实际占卡另计；不作为低效果种子删除。

第二次四attempt因现有pip工具链nvcc13.2与头文件13.0不兼容而在采样JIT失败，仍0调用/episode，保存为`_init_failed2`。不继续修编译环境；fvcrc21的s0/s1完成并GPU释放后，同slot滚动执行s2/s3，目标、代码、精度、seed与输入不变。共8次失败实际占卡0.49244632GPUh，成本工具逐attempt纳入；峰值始终≤8。所有8个成功分片launch元数据按实际host/PID更新，后续不重复启动已在运行的片。

### 原生help依赖兼容与完整同配置恢复

Gemma s3在252条完整episode后合法选择HelpEvent，LIGHT原views.py使用emoji已弃用的`use_aliases=True`导致worker异常退出。全部2149新calls/2315cache trace/252完整episode及794.450204s观测槽时封存在`e80_gemma_s3_native_help_failed`。异常退出未序列化最终载入/推理timer，明确null而非补0。只将help渲染关键词换为当前API的`language="alias"`；全200图help全文与历史接口等价适配逐字一致、完整graph/material不变，见`results/E80_help_render_compatibility.json`。driver/skills/规则/模型/seed未变。

相同driver以profile＋partial全部原输入决策缓存恢复原s3，旧252条须canonical逐字匹配才通过全样本核对。ABORTED runtime明确标真实部分计数；统计加载器仅增加partial trace依赖与精确去重支持，不更改主读数/CI/样本，profile核心输出逐值回归一致。监控补充全日志前部异常与父进程退出核对。此问题不解释成人物/策略机制，也不以删除help动作规避。

### POST-HOC恢复合并规则（全样本主效应读出前固定）

partial252与恢复版有245条canonical一致、7条不一致，均源图`21a99f36ade488f8`。相同player input-key/parsed `examine Blacksmith`因原生set候选同名NPC/房间、对象地址hash与等长排序tie可解析至不同ID；旧partial内两backend也已发生，不能称恢复之前所有prefix确定相同。保持native parser/规则与全部图不变，不将此当科研新发现。

主合并统一按实际时间取每个(case,seed,trait,backend)最早完整序列化episode：profile→原partial→恢复/full补缺；旧252条全保留，不按结果选轨迹。所有重复保留exact/nonexact审计，完整恢复版替换仅作敏感性，主全200/4800不变。POST-HOC首次激活核对按实际记录验证共同prefix；在第一次两步选择之前已分歧者标无共同prefix资格，不能对其假报不变量PASS或纯实现效应。因本次技术假设被原生记录否定，加载/资格处理透明修订，模型条件/读数/CI不变。

### 全部结果与本轮判断

全200图/4800逻辑episode完成；主全图模型下层A−F绑定goal为Gemma −9.00pp [−13.50,−4.50]、32B −12.50 [−16.67,−8.67]，NPC请求Give +10.50 [6.83,14.50]/+12.83 [9.17,16.50]pp。可靠技能总体goal仅+.17/+.50pp，但首次共同两步选择中原生前提从3/12、38/124恢复为12/12、124/124；下层改选与路径实现是竞争解释，不用它定义纯潜在能力。任务、最终归属、消费、返还/偷取及作者更高目的分别读回。

[完整E80续报](../PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)、results/E80_{gemma,32b}_complete.json、E80_first_activation_POST_HOC.json、E80_cost_accounting.json及两张科学图提供全部结果。原792完整partial全部优先保留，恢复784exact/8nonexact；全图主值不变的敏感性与20对不满足共同prefix均公开。firstactivation汇总曾有同名counter重复success，已修正并核原始bool/类别和/概率界限，主完整结果未变。

实际37642新本地calls，47822360输入/920604输出tokens，1次parse导致2个primary协议终止、0死亡，8init＋2中途异常完整计费，3.61978671观测GPUh/峰8卡/0API。全部worker退出；C06 L2/I04 PROMISING不变，不机械开E81，正文暂缓。
