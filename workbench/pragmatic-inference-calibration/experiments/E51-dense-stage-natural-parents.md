# E51：dense-stage-natural-parents（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2，匹配训练谱系与自然parent条件测量
- **对应：** C02/P02；不注册预设结果方向的idea
- **问题（一句话）：** 在输入完全相同的较强dense开放谱系中，post-training对自然含义区分的改变，能否同时被原人类分布、同问题不同回答和候选概率质量约束？
- **设置：** 官方OLMo-2-1124-13B Base/SFT/DPO/最终Instruct(RLVR)，先固定revision与训练继承关系。四stage×IQAP/Circa八独立GPU作业，FP32/eager/noTF32，全部使用完整SFT tokenizer与相同bare/common-chat输入。IQAP原150development、30判断/item、四完整候选，300/model distributions；Circa严格复用E34跑前hash选出的全部原pair/两order/两入口，不重新挑题。不是原论文所有现代模型数值复现，也不声称达到2026前沿上限。
- **读数：** IQAP主full interpretation sequence likelihood含原terminal，secondary content-only，保存完整绝对candidate mass与无QA词汇prior；polarity、四类human分布Brier和definiteness分开，后者是听者解释不确定性，不命名speaker certainty。Circa主原顺序八类完整数字content likelihood，逆序为既定诊断；同问题两原回答的relative weak-class变化、原gold、全candidate mass，不把内容/难度同时改变当因果context flip。stage paired CI按相同item/question，不将stage当独立training seeds。
- **阳性对照：** 所有source原字段/人类counts/hash重新核对；四模型完整token vocabulary、特殊tokens、bare/chat全量candidate IDs逐项相同。全prefix与terminal检查，首末/各入口/各order：独立完整model logits teacher forcing与target-span scorer LP<.001、prob<.001、argmax相同；repeat<1e-6。context最长必须<4096，不截断；任何gate失败先保存且0科学预测。单句格式要求继承原E33/E34，不追加救分prompt。
- **噪声地板 + MIE：** 数值gate独立于任务分数；bootstrap2000 seed0，以item/question为单位，IQAP另给source-cluster sensitivity。候选mass与顺序差异必须与准确率同报；不以归一化分数单独归因能力。至少两个独立source的可用读数与条件区分共同成立才考虑跨任务解释；.95/2×noise不作自动判死规则。
- **混杂审计：** stage的算法、数据和训练预算共同变化，不能纯DPO/RLHF因果归因；Base套chat是控制入口，不叫native。IQAP四选项并不穷尽自然意义；Circa五人一致筛选是源标签的预先条件，不筛模型正确item，不能推full-population分数。比较以前结果是已知后设计的边界实验，不冒充完全独立发现；所有stage/入口/metric报告，无选择幸存种子。
- **决策表（跑之前写）：** A两source的含义区分改变且质量/顺序/terminal控制可用→保留条件结构，回到parent的交际证据解释并扫描近邻；B只有候选质量/格式/入口改变→仪器和elicitation解释，不升能力；C不同source方向不同→反对全局scalar，先列边界而非挑成功source；D整体都强或无新结构→报告成功/null，不靠新metric造贡献。任何结果不自动关线或升状态。
- **算力预算：** 新资产预计约120–170GB，本地盘足够；八独立锁单卡、预计≤8 GPU·时，0training/API judge/子agent。先下载固定权重并CPU预检，禁止为占卡而绕过gate。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

已核对官方model card四stage列表及最终Instruct包含RLVR；revision、完整token输入与数值gate未完成，尚无模型结果。此前E49/E50结果已知；本实验不用其source也不追加其prompt修补。C01/C02仍L0。

资产准备：metadata并行下载被tqdm内部锁异常中断，0模型预测；禁progress bar后顺序metadata完成，四revision固定。公开SFT只有PyTorch index/bin，safetensors-only downloader在该endpoint被asset gate拦截；独立使用既有download_models.py --pytorch-only，原文件/revision不变且torch weights_only=True。其它三endpoint的既有下载保留，不终止。四native backend完全相同的额外CPU证明见results/E51-tokenizer-backend-audit.json。CPU全source gate通过：IQAP300/model、max151tokens；Circa1732/model、max162tokens；总8128。队列已启动等待资产，未宣称八卡正在计算。

CPU全量prefix/source preflight已通过；完整source结果不按方向改readout。Circa全部单token content时作精确共享prefix分解以减少重复forward，再与独立完整model logits比对，不用首token代替多token。运行脚本冻结，所有原失败/raw保留。

下载调度补充：为避免最后Instruct等待前两个endpoint，另启既有download_models.py的固定revision下载；HF文件锁/cache复用，未改checkpoint或实验输入。八任务各自等待对应完整资产marker，不必等全部四stage才开始。collector有限等待并仅做原定汇总，不开新实验或升级主张。

2026-10-03执行补充（不改科学协议）：Base pinned权重超过原队列2小时等待上限，预计需要仅对缺失Base两作业重排。先保留原超时，再用同一冻结worker/source/readout/seed/output basename；重排只在原两个Base waiting任务均打印超时、且原输出目录不存在时允许，不能重复启动或覆盖。SFT/最终Instruct已完成，DPO已下载并等GPU。旧collector若因队列下载超时退出，只能另开完整8作业gate后的有限collector，不汇总partial、不改原frozen summary SHA。

执行排程审计：五original jobs已完整、两Base真实超时、DPO Circa仍等待固定GPU5；/proc核对0活动E51 scientific worker后，仅终止原waiting coordinator，保留日志与其它队列。DPO Circa改为任意空闲卡，同worker/输出basename/完整preflight；原collector与summary SHA不动，全8logical jobs gate后才总结。结果E51-scheduler-resume-audit.json，未杀训练/推断worker或他人进程。


## 完成（2026-10-03）

8 logical作业/8128读数完整，原source/actual输入/完整teacher-force/数值gate全部通过，成功合计.6629GPU·时；原下载/队列失败永久保留。结果[完整summary](../results/E51-dense-natural-summary.json)，冻结SHA 5aac66d3577213083aa8370379162ff3fd2f4b87fdc4d7e747700e2c197972e3。Base最后1.690GB通过mirror/CDN直连续传，新shardSHA校对后才发布marker；传输不改变revision。

- IQAP common-chat方向accuracy Base/SFT/DPO/RLVR=.800/.740/.7333/.7467；四类human Brier=.3306/.5210/.8338/.8550。SFT→DPO方向差−.0067 CI[−.0400,.0267]，Brier差+.3128[.2772,.3475]，source-cluster敏感性[.2527,.3568]。没有把accuracy近似不变叫等效。
- post-SFT chat完整candidate mass=.9216/.9324/.9782，full/content Brier差很小；SFT→DPO bare也Brier+.2340[.2056,.2612]。因此仅terminal改变不能解释全部变化；但无QA prior的四候选分布也从[.0918,.4695,.1535,.2853]变到[.0014,.6648,.0164,.3174]，仍有候选措辞/全局政策解释。
- Base chat候选mass仅.000117、Circa两序语义argmax一致率0，Base与post-SFT差不能当能力因果。不是为了保住后面DPO局部差就删除Base，全部原入口/阶段保留。
- Circa post-SFT数字质量高却顺序敏感：SFT/DPO/RLVR chat argmax一致率.7483/.6998/.6998。negative weak acc DPO源序0、逆序.8846；不能当推断倾向。conditional strong acc SFT→DPO源序−.1094[−.1641,−.0625]、逆序−.1562[−.2266,−.1016]，但relative弱class分离差源序−.1006[−.1313,−.0696]、逆序−.0077[−.0354,.0211]；排名/概率构念仍依赖入口。
- 按决策B/C：保留不同读数/条件的变化，尚未识别统一latent criterion；不作d′、speaker certainty或纯DPO因果claim。IQAP目标写的是听者对B意图的definite/probable解释，不能重命名为B自身的知识概率。下一鉴别必须有候选措辞与不确定性referent的控制，以及独立原source的条件预测；不再简单多跑同一ranking表。C02仍L0、贡献0、状态PROPOSED。
