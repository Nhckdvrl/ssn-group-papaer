# E02：新监督内容覆盖 × 可复用跨语言桥接（2026-10-02）

- **状态：** PLANNED
- **类型：** EXPLORE（训练端发现pilot，不声称新idea）
- **对应：** P03；E01有效学习baseline之后
- **问题（一句话）：** 相同CPT预算下，英语新任务学习的迁移是否要求桥接覆盖新监督实例，还是同领域内容不重叠的桥接也可复用？跨语言条件连接是否改变选择？
- **设置：** 同起点MWB 34K、HF revision继承E01。四cell：new_paired/new_split/reused_paired/reused_split。new从E01固定32768训练池选8192；reused同一MNLI/XNLI翻译源，但排除E01 train/dev和XNLI val/test premise组；CPT不输入标签。原始EN文本/label/索引校对，不靠label相同推断配对。reuse按EN/DE长度及类别匹配，语言预算差≤1%，未达停止准备。paired为EN→DE同内容上下文；split对同一输入用文档隔离causal mask，不构造错误pair，边界BOS不计loss、完整自然文档保留。两条件输入/位置/label mask/步数相同，估计cross-document conditioning，不冒称所有unpaired组织。CPT8192单位/256 updates、effective32、micro4×8、max512、AdamW lr2e-5/wd.01、warmup26、clip1、FP32 master+BF16 SDPA、seed17。之后按E01冻结recipe重初始化分类头，英语NLI适配0/2048/8192/32768全曲线，不用目标分数选recipe。
- **读数：** 主要EN/DE绝对accuracy、paired−split与new−reused及交互；全预算点报告。paired-item bootstrap10000，promptID cluster敏感性；同时报告EN能力/input/token hash，不只transfer ratio。E01 MWB17是零CPT锚点，不是等预算竞争方法。CPT前后固定XNLI validation前128组DE conditional NLL、train loss、时间/显存，NLL仅诊断不独立当能力claim。新实例指任务监督覆盖，不是未见过的预训练新事实。
- **阳性对照：** E01任务gate通过。mask干预单元检查：替换EN prefix后split DE logits不变，paired应改变；target BOS不从EN EOS预测，loss计数相同、mask无非有限值。CPT loss有限并下降；任务EN source≥55%、三类有效。paired CPT若heldout NLL无可测效果，不能用null宣布桥接无效。
- **噪声地板 + MIE：** seed17四cell先识别；E01终点DE contrast seed SD0.14–0.40pp，早期1.98pp，item CI不能替代seed波动。约2pp或明确EN/DE代价权衡优先扩展，非自动判决。有后果差异须补29/43；pilot不升L2。
- **混杂审计：** paired/split同文本/token/位置；new/reused同源MT、长度/类别匹配，内容不同是变量；独立信息/源语重复不同须报，不直接称纯alignment。预算容差、相同dense tensor及实测时间，未控有效attention FLOPs；单预训练模型/seed，质量残差/污染未控。task dev继承E01 pair-disjoint及已披露premise重叠；target不用来停止/选recipe，全失败保留。
- **决策表（跑之前写）：** conditioning与new/reuse有实际后果→补联合seed29/43并定位，区分覆盖/重复/桥接，再考虑第二任务/强家族；接近→报分辨率，确认干预有杠杆，不宣布等价；source损伤→记录真实代价，优先同预算内容/时序修复，不换评分；CPT无有效学习→先修训练，加预算先amendment，不靠冻结probe救；仅普通已知差异→保留资产、转另一真实训练决策，不缩小到评分方向。
- **算力预算：** 四cell CPT+task FT≤8 GPU·时，独立单卡，白天并用≤8；先一cell确认mask/显存/CPT再铺其余，最多4卡。**实际：** 待测。

## 结果（仅追加）

尚未训练。数据和mask先校对；PreAlign/AdaXEval/LINK/XLDA覆盖母问题，当前无novelty声明。

启动前数据校对：两pool各8192完整单位；new EN/DE loss token355452/465877，reused355115/465794，差0.095%/0.018%，低于1%阈值；7670/8192单位逐语言长度完全匹配。31个超512完整单位、87个原始EN与XNLI索引文本不匹配的候选被排除，不猜测其German对应。所有选中单位原始EN文本（NFKC/casefold、HTML解码、忽略tokenization空格）与XNLI EN索引一致，labels也一致。new额外排除dev/val/test premise；reuse排除全部后续task train/dev及val/test premise。准备manifest见 `results/e02_data_manifest.json`，原始token corpus在 `artifacts/bridge_learning/data.json`，未进Git。准备过程没有GPU训练。

启动前mask阳性检查通过：A100/BF16模型中更换同长度EN prefix，paired DE logits最大变化2.0234375、split为0；非有限值与边界loss检查通过。`results/e02_mask_check.json`记录设备与脚本hash。该检查仅证明conditioning干预生效，不证明学到跨语能力。先启动new_paired seed17，原CPT与E01 task recipe不因目标读数改变。
