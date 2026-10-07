# Incremental Interpretation & Revision

## 状态
- **注册：** PROPOSED（人授权的 baseline residency；不改变当前 ACTIVE-MAIN / ACTIVE-EXPLORE 分配）。
- **2026-10-06 人决定：**
  - 研究从暂停中恢复，并重置主线：采用 [ROUTE](ROUTE.md) 中的路线，放弃 I01/C05；
  - 先广后深；允许一开始就做白盒；
  - 标注只用 Step5；
  - 资源：同一节点上的 8 张 H20；按后续用户指定，标注消耗Step Plan套餐Credit，禁止现金账户接口。
- **执行模式：** 自主执行。本地 agent 按 [EXECUTION_BRIEF](EXECUTION_BRIEF.md) 全程推进，原人审节点改为自审；只有真正卡住，或遇到开线/关线/改状态/进入候选这类决定时，才回来找人（EXECUTION_BRIEF §6.7）。开跑前必须先完成 §1 的整体认知建设。
- **territory 卡：** [Territory Card](../../search/our-taste/TERRITORY_INCREMENTAL_INTERPRETATION_2026-10-05.md)　**目标会议：** ACL / EMNLP / NAACL（按证据成熟度选周期）。

## 一句话（当前主线）
> 强 LLM 能看到整句话，为什么仍然读错 garden-path 句？在增量编码过时、作答时选择失败、合理性组装、测量问题这四种解释之间做归因，再用机制解释模型的"修订"在哪里成功、在哪里失败（[I02](ideas/I02-garden-path-misreading-attribution.md)）。

**为什么是这条路线**（详见 [ROUTE](ROUTE.md) §0–§1）：三个社区在这个问题上互相矛盾。
- 理解问答研究：GP 对 LLM 特别难（GPT-5 非 GP 93.7%、GP 46.8%），原因留作未来工作；
- surprisal 研究：LLM 在消歧处并不太惊讶，而且同时保留两种解析；
- 架构研究：把因果掩码当作 GP 失败的原因。

已有证据（Li 中双向模型同样认同误解；thinking 的效果因模型而异，GPT-5 是明显例外）已经在质疑因果掩码的充分解释。

**已有的起点证据：** 对 Amouyal 公开的 31 个模型结果的审计（[结果](results/D0-Amouyal-released-item-type-audit.json)，无新推断）显示：
- 及物 Subj/Obj 和多数 NP/S 条目在无歧义对照句上同样被答 Yes，提示需区分句中断言与可能的额外事件；仅凭此不能完成错误归因。作者已说明部分 No 意为 not necessarily，原任务约定保留；
- 原作者 gold 为 No 的部分条目上，公开答题差距达 25–65pp（GPT-5 RR 62.5% 对 98.8%）；旧 D0 把 RR 等整类视为“确实为假”尚不充分，需 E52 双遍逐题区分 CONTRADICTED 与 NEITHER，不能直接当作真实语义错误。

## 主张与 idea
- [CLAIMS](CLAIMS.md)：新路线是 C06–C09（C06–08 L0；C09为限定协议L1因果测量）。C00–C05 是旧路线的历史测量，保留，不再推进。
- [I02](ideas/I02-garden-path-misreading-attribution.md)：当前主 idea（PILOT）。[I01](ideas/I01-event-reference-or-lexical-echo.md)：PARKED。
- [I03](ideas/I03-transferable-interpretation-repair.md)与[I04](ideas/I04-selective-relational-error-correction.md)：跨用途修订、修复与保持的选择性（SEED）；[I05](ideas/I05-premature-source-consumption.md)检验源信息消费时机（SEED）。新精读与整体画像见[知识库综合](../../library/themes/incremental-language-processing/REVISION_RESEARCH_SYNTHESIS.md)。尚未认定合格idea。
- [PAIN_LOG](PAIN_LOG.md)：P13 记录问句语义混杂，P14 记录单模型与复用 24 句的教训。

## 近邻与可借的研究方法（完整定位见 ROUTE §1.3）
- Amouyal ACL'25/'26：人机行为比较、GP 特别难；
- Hanna & Mueller NAACL'25：2B 模型上 GP 特征共存，QA 不复用；
- Zeng Findings'26：词汇修订的推迟机制、非因果 oracle；
- Guo et al. 2026（CICM）/ Tang ICML'26 / Prakash ICLR'26：显式更新中的"保留但未选中"、查询时汇总、lookback；
- CASTLE / Prompt Repetition：因果掩码有害的前提、重复输入。

从广面实验和意外结果找叙事，近邻的局部发现与方法可以复用。完整故事形成后，说明证明它为何值得兴奋、带来什么新认识，以及是否被近邻完整覆盖；不寻找完全空白的空间，不因局部相似关线。

## 历史与资产
- [DIAGNOSIS](DIAGNOSIS_AND_REDIRECTION_2026-10-06.md)：51 个实验为什么没有得到好 idea（执行为主因，数据为次因，领域本身没有被证伪）。
- [PROGRESS_SUMMARY](PROGRESS_SUMMARY_2026-10-06.md)：E00–E51 逐项结果、失败与勘误。[FILE_INDEX](FILE_INDEX.md)：文件入口。
- [DATA_PLAN](DATA_PLAN.md)：数据来源、许可与审计；新路线的数据方案见 EXECUTION_BRIEF §4。
- 本地 cache：`/data1/xiangding/work/incremental-interpretation-revision/`（upstream / normalized / models / runs）。原始数据、模型和逐条输出不进 git；复现入口见 [scripts/README.md](scripts/README.md)。
- 当前自主执行：[E52](experiments/E52-genuine-revision-reading-map.md)，1732公开QA/309 GP pairs；全文综合和“我的理解”见当日日志/领域地图。Step5全部走Step Plan，≤5项/批；HF资产只走镜像，本地推理离线。E52完整资产在上述cache的`E52/`，精度/接口失败同样保留。
- 数据资格：原双轮/裁决资产`E52/step-full-v4/`保留；反例世界双轮复核完成，最终主分析入口`E52/qualified-v3.jsonl`保留原S/Q/gold和独立T2/T3。严格矛盾仅覆盖2个NPS词汇组，不代表全部理解错误；`qualified-v2`仅为历史资格。
- E52完整14模型/5族地图、[E59](experiments/E59-source-grounding-versus-world-question.md)三族源支持测量、[E54](experiments/E54-prequestion-oracle-and-revision-selectivity.md)三族问句前可见性干预均已统计。明确源支持任务中仍有差距，可见性干预未有稳定选择性恢复；控制损伤与GP修复分别报告。尚无合格idea，能力/解析主张仍未建立。
- **2026-10-07 执行调整：** 根据用户提醒停止追加实验与标注，在途API已收束、资产保留，重新审视科学问题与研究价值；注册状态不变。诊断见[当日日志](logs/2026-10-07.md)。
- **同日继续：** 用户要求由综述、最新顶会与arXiv重建认识；新增[73篇精读卡](../../library/themes/incremental-language-processing/REVISION_READING_INDEX.md)。[E55](experiments/E55-natural-cue-source-patching.md)自然cue源位置替换已完成；[E60](experiments/E60-source-consumption-depth.md)保持源计算不变的消费时机干预已完成，初始收益伴随正确关系损伤；[E53](experiments/E53-faithful-two-sentence-paraphrase.md)10260复述的原完整T4双盲审核已恢复，未解读部分标签。[E63](experiments/E63-shared-source-cross-use-patching.md)同一任务未知源缓存的三族QA/角色生成已全部完成，495新文本完整双遍和74分歧裁决已结束；初版未支持三族共同角色恢复，MVRR的语态/施事v2纠正已闭合，三族共同正向角色恢复仍未建立。[E64](experiments/E64-source-bank-route-decomposition.md)以核心源位置分解检验用途路径，三族完整问答/生成已结束，QA和role-v2完整地图已自审，MVRR反向cue角色损伤跨三族、正向整体恢复不稳。[E65](experiments/E65-goal-conditioned-cross-question-reading.md)三族四构式的提前目标→未询问关系完整矩阵已自审（892QA/178clusters）；NPZ INITIAL联合收益跨三族，但跨关系修复不统一；E66完整路径切分已自审：源路径不能保留原生目标收益；E68对称路径整图已自审：纯直接作答也非三族关系修复，停止追加goal/mask网格，E67完整四构式自由关系迁移并行，与角色纠正独立推进。注册状态不变。
- 新资产：上述cache的`E59/source-scope-final-v1.json`、`E54/prequestion-oracle-map-v1.json`与`E54/figures-v1/`（PNG/PDF），E55的`natural-cue-patch-map-v1.json`、E60的`source-consumption-depth-map-v1.json`，以及E60的`figures-v1/`、E63输入/仪器/全部失败版本和`T4-full-v1/`审核缓存；git的小摘要引用完整结果SHA。

## 决策记录
- **2026-10-05：** 人选择本 territory，授权 training-free baseline residency；取消 agent 自加的停步 gate；构造与语义审计改用 Step。
- **2026-10-06：** 人要求暂停并归档（E51 后）。同日，人接受诊断，决定重置主线、采用新路线、恢复研究、标注只用 Step5、先广后深、允许白盒，并上传 main 交给本地 agent 执行。随后人决定采用**自主执行模式**：本地 agent 全程自主推进，原人审节点改为自审，只有真正卡住或需要人做的状态类决定时才回来找人；这条决定覆盖 AGENTS/EXECUTION 中"决策点请人审"的默认规则。

- 核心新节点：E69原发表45sets语义×结构图已完成（10944评分），合理性与GP差距并存，不能统一归为早期编码过时；E70只对既有BASE/TARGET自由输出标原Q的断言脚印（1280原子项、≤5/批）；E71原发表40对的新正确子句先盲审，再检验正确第一句的后续消费。E67三族3204自由输出已全部完成（6.530GPU·h），T4完整双遍运行中，批5/共享8/分歧裁决不变。所有新结果尚不等于合格idea。

- 最新核心块：[E70](experiments/E70-atomic-repair-footprints.md)1280原子双遍/183裁决与完整地图已自审；[E84](experiments/E84-source-key-versus-value-revision.md)5664 K/V条件、.237GPU·h/0API完成，无共同完整修复，统计勘误保留。[E82](experiments/E82-current-open-model-baseline.md)复用原892QA的当下强模型测试三族8分片全21408条件完成（1.271GPU·h），已完整自审；[E85](experiments/E85-lexical-semantic-recovery-transfer.md)复用人类词义48框架/192句原coherence金标，8卡全4608条件完成；不新增原数据审核。

- **最后一晚（人2026-10-07晚决定）：** 先找值得追的探索idea，不要求现在补齐成稿证据。[I06](ideas/I06-late-verb-frame-reanalysis.md)问早期谓词论元框架是否需重算；[E88](experiments/E88-verb-versus-noun-lookahead.md)复用151发表源组/784QA，18816条件/.468GPU·h已自审；E89的9408实际答案/.626GPU·h也完成，均0新API；每两项核心实验重新[对齐](REASSESSMENT_2026-10-07_2225.md)，不继续防御提示网格。
- **最新探索切口：** [I07](ideas/I07-self-supervision-inherits-interpretation-bias.md)问自监督内容reward是否继承观察解释偏差；E91/E92已闭合（1944＋1800评分/0新API），固定P的原/消歧观察改变credit语义对齐，主要MVRR与一个generator，尚未认证一般机制。下一社区Belief-R原1744修订题直接用，不bulk审计。
- **资源硬截止：** 2026-10-08 09:00北京时间前停止本工作全部GPU；持久timer 08:55提前释放、监测到09:02，不触碰他人服务。已删除11个完成实验模型的可再下载权重294.97GiB及8.64GB残片/安装缓存，项目约198GiB；剩余6模型权重停卡后也释放。全部tokenizer/config/revision/manifest、科学数据/结果保留，外置删除清单与国内镜像下载脚本可用于重建；原manifest不表示当前权重仍存在。
