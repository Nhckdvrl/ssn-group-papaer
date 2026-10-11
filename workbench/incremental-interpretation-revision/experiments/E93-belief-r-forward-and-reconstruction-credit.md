# E93：社区Belief-R的真实前向判定与观察重建credit是否一致？（2026-10-08）

- **状态：** DONE；生成器E431在任何科学forward前改E93。
- **对应：** I07 / P20，C06–C09；E91/92观察surface二步块已收束。此为独立领域与真实原任务检验，不继续surface/score模板网格。
- **问题：** 在新前提下选择正确结论，与由结论重建新前提是否为同一能力/同一内容reward？若重建判定在前向已做对时仍错，才提高“内容credit继承解释/打分接口偏差”的优先级。经典逻辑与作者语用任务不可混淆。
- **数据：** 官方HKUST Belief-R EMNLP2024，GitHub固定treee9cec77b14e7deea9d26b3b04c41fc08ab2094e3，1912 time_t及1744 time_t1。完整1744修订问句/人类Gold a/b/c/204atomic_idx、modus ponens/tollens原样用，0API、不bulk审计；readme/code/PDF已核任务。它是人类suppression/语用Gold，不当纯经典蕴含GT，不因当前模型不同意重标数据。
- **先验与观测：** time_t1原前三前提切成旧两premises/新第三premise，原questions正文不改。reward context的旧belief=原旧两premises的文本状态，不假装已正确推断结论；new belief=原数据a/b/c三条候选陈述；goal=原结论问题（无选项）；action=读取新的premise。重建目标仅新premise。1723条与time_t母条目可通过前提/候选的metadata规范化关联，21条不能精确关联：仍保留全部1744新阶段任务，旧人类prior Gold标NA，不补猜。关联规范化只用于metadata，不改模型输入。
- **条件：** 3当下模型族。FORWARD_DIRECT使用作者官方ZS_vanilla formatting（Final Answer [a/b/c]），原Q/原选项顺序；FORWARD_COT追加官方一句“Let’s think step by step.”，原生thinking入口（Q/G支持时开启），作为R8一句恢复。生成上限DIRECT64/COT256，greedy，真实输出/未停/cap独立上下界。原官方不交换选项，此pilot不加入mapping/温度校准网格。
- **重建评分：** 同3模型以E91式固定raw trace，旧两premises/goal/行动保持、分别以原a/b/c候选作新belief，full teacher forcing新premise sum/mean LP；约1744×3候选×3=15696评分。正确候选不是输入prompt中的Gold，只于最后分析对齐。它是未训练类比，不是ABBEL训练复现，也不把不同序列排列自动当同一Bayesian joint。
- **主读数：** 10464真实前向输出（2条件×1744×3），15696LP；原人类Gold准确率/BREU（原语用更新/保持分组、matched initial Gold未知者单列）、modus/所有Gold类分别报告；forward与reconstruction top1的配对差、同题选择一致、reward rank/Gold差，条件于forward正确者仅辅助诊断，完整全cohort为主。不挑强族/幸存题，cap/unknown的上下界完整。
- **统计：** 原逐行任务为Source单位，atomic_idx为公开seed group，Source→seed cluster/bootstrap10000/seed93；macro BU/BM与raw1744准确率分开，不把任务变体当独立世界。重复原question保留原行ID/Gold并单列，不按结果挑条目。
- **阳性对照：** 三族CPU全文/Gold/候选边界/目标是新premise核对；输入固定首个row actual native重复token完全一致、Source LP重复逐字一致，sum=逐token相加。前向原任务是能力锚；官方COT作为恢复，弱human-task锚不能证明latent belief能力不存在。
- **噪声地板：** 单任务BF16/eager固定layout，不以forced-choice LP充当实际行为；原native assistant/thinking边界注明，COT未给最终答案标UNKNOWN而不猜。完整输出/每tokenLP与配置哈希保存，不看到结果后改parser、换标签或切预算。两mode输出长度/cap全量报告。
- **决策表（跑之前写）：** 前向原任务/恢复足够高而reconstruction明显失配→I07在独立域更值得追，下一设计能恢复语义credit的核心方法；前向也弱→只有域困难/语用task差异，不能说能更新但被reward误奖，重新对齐问题；reconstruction相当/更好→修改目前reward-blindspot解释，不硬叙事；仅Gold c弱或mode异质→明确未知/新旧信息与task范围，下一由具体关系对象决定，不续格式控制链。找到探索idea优先，不要求今晚补齐成稿。
- **算力：** ≤20GPU·h（思考输出的最坏预算），8独立H20 Q3/G3/M2，现有离线国内资产0新下载/0API；每任务deadline guard，08:55独立停卡/删权重，09:00硬停，不自行恢复。若cap高，按预注册报告未知，不再事后增思考长度。

CPU三族完整5232重建/3488实际输出条件各通过；data SHA5477a87d5a03b2382cddc54058b0a9787e35bdeb17d97ecfff83241c2c7ccf41。三族native two-mode实际suffix逐一保存，Qwen开启think、Gemma按官方template选择thought频道、Minstral无单独强制thought入口。全26,160条件在8卡启动，0新API/0下载；完成全部scope前不读partial科学效应。

2026-10-08 01:58运行时算力估计修正（只读进度／elapsed，未看partial效应）：8任务运行约32min，各Q/G分片约70–85／486–666 Source，Min更快。原20GPU·h是估计，不是人规定硬配额；按实测速率预计约25–30GPU·h，修正估计上限32GPU·h，输入／模式／cap／parser／读数完全不变，0新下载/API。预计在08:55之前完成；08:55释放timer仍优先于任何实验完整性。不能事后提高256cap或挑快速条目。

2026-10-08 03:57，任何科学effect读取前prospective分析次序调整：Min族全部shards已完成 Belief-R全1744原题，可先生成**完整单族探索地图**指导假说；其余固定Q/G任务继续，三族完整主图／所有原指标／CI／cap／data／parser均不改。独立interim文件及scope只供假说生成，不叫三族共同finding、不挑Source或已做对题；这覆盖前述等待全模型才读取的次序约定，原因是尽快利用已释放卡做核心追问，符合用户探索阶段／不防御推进要求。原primary map仍只全三族到齐后生成；未看任何partial Source/teacher labels。

05:34全三族/八shard闭合，10464 actual+15696LP/25.70556GPUh/1362panels，mapSHAf3953fb34e12f094633ae7c130ef57c904933a1f4bcc846328575c68b1b0fd8d。所有DIRECT各1744cap+unknown；CoT Q1489cap/1027UNKNOWN、G1744/1744、Min1715cap/1743UNKNOWN，仅已停止+valid保能力下界，其余UNKNOWN上下界，不将0下界叫能力0%。原instrument未要求validfinal是测量失误，E97一句FORMAT只Min通过完整science，Q/G首仪器仍cap，无进一步grid。Raw原人类语用Gold各约30–32%，与BASE task能力的三族对照不可辨，不能认证I07understanding intact。原modality/Gold/priorNA21与所有strata保留，0新Source/老师调用。
