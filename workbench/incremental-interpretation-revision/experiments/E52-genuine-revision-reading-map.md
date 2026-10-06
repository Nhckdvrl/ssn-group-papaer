# E52：真实 GP 修订错误的广面阅读地图（2026-10-06）

- **状态：** RUNNING
- **类型：** REPRO + CLAIM（先复现仪器，再做系统 measurement）
- **对应：** I02；C06/C07；P12（标注完整性）、P13（NEITHER）、P14（广度）。
- **问题（一句话）：** 先前角色解释被后到的句法证据推翻时，完整第二遍阅读是否比截断重复/等长无关句更能选择性恢复正确理解？
- **设置：** 先做 D0-v2：固定 Amouyal 072efefa…、SAP 15e61066…、Čeháková Zenodo16358492v1；保留原数据/问题/gold，扩统一 schema。Step Plan Messages、step-5-preview、每批≤5、共享并发≤8；T1 两遍独立随机分批（seed 5201/5202），分歧第三遍解释；T2/T3 同包，每项返回 ID 和 sentence SHA256。失败项单项重试≤2，所有请求/响应缓存。标注人员不得看到模型行为，不能按结果挑源。
- **模型与版本：** 核心 Qwen3 1.7/4/8/14/32B，Gemma3 4/12/27B-it，Llama3.1-8B-Instruct，Mistral-Small24B-2501，OLMo2-1124-13B base/其实际 Instruct；base/instruct 对照 Qwen3-4B-Base、Gemma3-4B-pt（核实可得性与合法访问再固定版本）。每模型单卡 BF16；先小批实测显存/吞吐再8卡并行；当前卡4/5有既有常驻服务，只使用可用显存、不结束别人进程。Ettin 留给 E56。缺模型记录，按可用独立族推进，不用仅 Qwen 填满面板冒充广度。
- **阅读条件：** R0 一遍；R1 S S Q；R2 S_pre S Q，S_pre 严格止于 Step 核对的消歧词前；R3 等模型 token 长度的独立填充句 S Q（不含原实体/动作）；R4 作者 cue/control 句；R5 Q S Q；R6 Qwen 原生 thinking greedy，解析 think 结束后的最终答案，token cap/未完成单独报。R0/R1/R2/R3/R5 同时测 gp/control，R4 不重复计成独立 baseline。原 reorder control 和 same-order cue 分层报告。无可靠消歧位置的项保留 R0/R1/R3/R5，R2/surprisal 记缺失。
- **提示格式：** A 完整复用作者8系统/例序×reg/rev；B 原生chat零样本。两选项题两顺序；yn题 Yes/No 保留原文；附一句“只按全句的最终语法解读，不补入未陈述事件”恢复控制（R8）；此控制结果不替代原读数。A 首先对公开重合模型逐题复现 regular 结果，不能将自己新格式当原文复现。
- **读数：** 主：完整 GP/control 同题对上正确率、候选答案序列联合 logprob 的二选归一化概率；不把首token结果当多token选项概率。主分析对象为两边 T1 都 CONTRADICTED 且 T3 acceptable 的 initial 问句；其余蕴含、NEITHER、分歧未裁决、语法边缘/失败单独报。2opt 题按所选命题审计，不机械套 yn 标准。simple/填充题与 Yes 偏置是仪器读数。概率不称 world belief。按 source lexical pair 做10000次 cluster bootstrap，95%CI；SAP跨构式共cluster，重复作者材料敏感性去重；每模型/构式/格式/提示顺序均保留。
- **关键对比：** gap_R = control_accuracy_R − gp_accuracy_R；reduction_R=gap_R0−gap_R；检验 reduction_R1−reduction_R2/R3，另报 GP 与 control 原始收益。模型与构式均衡macro及原计数micro分开；不得用 control 下降冒充 GP 修復。补报正确~condition×reading×construction+(1|pair)+(1|model)的混合logistic（分离/不收敛如实标注）。消歧词surprisal只作次要逐题协变量，正确词边界并保留上下文。
- **阳性对照：** 作者格式公开重合模型逐提示结果；simple_question、cue/control 正确率；BF16/FP32小模型固定子集翻转率；R2截断位置/题中词机械校验；候选token与序列边界自检。低control/simple的模型仍报告，不能做能力归因；不过自动科学kill gate。
- **噪声地板 + MIE：** greedy重复固定子集，两种精度；8提示的范围/方差。关注≥5pp的 GP选择性恢复或能分开R1与R2/R3的CI，不机械用阈值作判决；不做幸存seed筛选。
- **混杂审计：** 1噪声：重复/精度/提示；2工具：原格式复现；3采样：先固定全来源，标注只看文本；4自校准：候选同定义；5默认：简单题、yn/2opt、一句恢复；6字节：原文/prompt/token/hash；7种子：greedy全量、所有打乱seed；8计算：R3 token等长、R2额外token量单报，R6不称等算力；9污染：公开刺激可能被预训，未控制，模板验证另开E57；10多比较：全部切片透明，POST-HOC标记；11地板/饱和：分别报；12一般性：≥3独立模型族、≥2构式前不给宽主张。
- **决策表（跑之前写）：**
  - R1相对R2/R3选择性缩小真实GP差且control稳定 → 更新E4支持；按E54/E55机制区分编码与检索。
  - 重读无效且合理性梯度明显 → 更新E2支持；E55先测正确role可读性，再选E58。
  - 一句恢复/换格式显著消除差 → 更新E3；优先E59/E53跨用途核对，不从yn推能力机制。
  - 构式/模型异质 → 保留完整归因地图，机制追问须跨族，不挑单模型局部链。
  - D0-v2显示原“矛盾”实际多数NEITHER → 完整报告测量纠正；按可用真实条目铺图；必要时E59角色问句（先Step5审）区分同一事件与额外事件，不改原gold。
  - 接口/资产失败 → 保存失败、独立修复；确实无法解决才按§6.7(a)回人。
- **算力预算：** 初估地图12–30 GPU·h（含完整A面板与thinking，不保证几十分钟/模型）；实测后追加。Step CPU/API，原始请求本地。**实际：** 尚未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 无新推断结果，无新CI。C06–C09 L0。
- 资产根：/data1/xiangding/work/incremental-interpretation-revision/E52/。
- 实验卡生成器因 brief 中未来 E53–E62 引用跳号生成 E63；本次跑前重命名为尚未占用且用户指定的 E52，未更改历史卡编号。

### 跑前协议修订（Step5 smoke后、能力推断前）
5项第一遍全部ID/hash/JSON完整（124s、6818输出tokens）；但T3把缺省逗号导致的自然度和语法合在一起，NPZ全部marginal。full-v2分开grammar与1–5 naturalness，并明确处理难度不等于不合语法；这不是根据模型能力结果改切片。max_tokens32768，pass3增加rationale，两遍grammar/position分歧均报告；原smoke-v1全部保留，不能复用为新协议通过标签。一般自然高认可数据不做全库复审，本次仅GP新增标签。

### 跑前数据仪器修订 v3
full-v2首次5项有两个T2索引/词不匹配（非T1科学反证），整体批失败后单项重试，其他请求耗时约200–247s。为保证质量并减少完整性失败，转full-v3：明确提供每个词的零基index、实际批大小2（≤5）、严格词字节核对；每项仍两遍、分歧第三遍。v2所有请求/响应及未收到响应清单保留，未采用作能力gold。不以已看到的模型行为改题/读数。

### 数据接口修订 v4（能力推断前）
终止v2客户端后服务端仍有未结束请求，v3遭HTTP429；旧driver立即拆单重试，形成无效请求扇出。所有429保留，未作为标注结果。修正：429/暂时5xx使用12次有界传输退避，每次原始响应独立保存，不触发语义单项重试；持续接口错误停止driver，归类资源问题。客户端并发暂降4，批大小2，two-pass/third-pass与语义读数不变。v4是首个可采用的indexed-word全量协议，v2/v3不混为通过标签。

### 仪器小样本（不是地图科学结果）
原格式1.7B 224逐提示行匹配公开结果，2次decision翻转（0.89%）、平均概率差.0573、最大.2013，概率仍需校准默认generation温度。原生B固定14材料×2mapping×repair共56项，BF16/FP32 0翻转，但最大正确概率差.2848；不能把零accuracy flips当概率精度稳定。CPU随机Qwen小模型批量leftpad、单项、完整logits手算三种序列评分差<2e−6。所有原输出/config留E52资产，C06–09不升。
