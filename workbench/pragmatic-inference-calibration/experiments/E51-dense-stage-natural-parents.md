# E51：dense-stage-natural-parents（2026-10-03）

- **状态：** RUNNING
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
