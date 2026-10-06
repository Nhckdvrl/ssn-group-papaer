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
- **算力预算：** 初估地图12–30 GPU·h（含完整A面板与thinking，不保证几十分钟/模型）；实测后追加。Step CPU/API，原始请求本地。**实际：** 已运行，首批完成的1.7/4/Gemma4地图分别.367/.819/.781 GPU·h；其余配置逐run累计，不能把尚未完成的完整面板预算当实耗。

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

### 提示渲染校对（完整地图前）
R3改用单个完整句的程序模板库，逐tokenizer选择恰好等长句；覆盖不到的长度显式缺失，不截断一句制造额外GP。R5作者rev格式由Q S改成Q S Q，reg格式由S Q改成Q S Q；不生成Q Q S。原仪器仅R0，不受影响。

### 标注执行并行化（标签完成前固定规则）
v4四并发稳定返回完整标注后，另开四并发的独立pass2（step-pass2-v4），两driver共享8-slot总限制；不取消在途API。采用规则先固定：主driver已有的pass2请求优先，否则整包导入独立pass2的原请求/响应/report（包括失败）；按ID与请求hash盲采用，不按标签择优。主driver最终合并两遍并发起分歧第三遍，第二driver重复或失败记录同样留存。

### 标签盲计算分片（D0-v2完成前、地图推断前固定）
原协议首批4模型完成后，先在固定全部1732条公开材料上计算A/B的R0/R1/R3/R4/R5和一句恢复；这些输入不依赖Step标签，标注API不得看到模型输出。R2在两遍位置一致后补独立landmarks分片，R6单独生成；分析在D0-v2完成后按ID合并，不能按未完成标签选材料，也不能把不同切片组成变化当作恢复。这样API与GPU并行而不提前定语义gold。所有后续地图保存完整prompt、候选、token数及运行时源码快照；R3额外排除与原句共享的内容词，覆盖不足保留缺失。原校准输出只存源码摘要，其局限如实保留。

### 分析元数据校对（能力分析前）
depth-charge四组应分成正向/反向各自hard/baseline；原统一文件暂存“1 hard+3 control”的粗字段只作来源索引，分析新增analysis_condition/analysis_pair_id正确配对，原句、问题、gold和推理输入字节不改。NEITHER切片必须同问句两侧都在该语义层；每个reading对比先取同问句交集，再聚合lexical cluster，避免R2/R3缺失改变题组成。多推理分片按完整task key合并，重复task直接报错、不选更有利版本。已用已知1.0选择性恢复、语义层单边变化、整问句缺失三个数值情形独立验证。

### 原协议全量首批校准与精度原因
BF16/作者processed首步：1.7B 17808有效公开匹配/278 decision flips，4B18124/100、8B18338/103；各自746/781/808首步无候选，原公开CSV710/359/118缺失分数均保留。Gemma4B仅85首步有效、19179无候选，作者最多3步parser与模型默认top-k/top-p使首步校准不足；不把这些缺失算模型答错。1.7B固定224小样本改作者默认FP16：0 flips，平均概率差.001452、最大.013018，比BF16 processed明显接近；不据此宣称全量逐题复现通过。新条件用候选完整序列联合评分，不带采样过滤。生成另建隔离环境，原评分venv不变。

### 精度噪声扩展（能力分析前登记）
固定全部1732题，四个已就绪模型Qwen1.7/4/8和Gemma4，B格式R0×两mapping×一句恢复，共6928任务/模型，用GPU4–7 FP32与主地图同任务BF16对照；未按结果挑条目。GPU0–3同时计算主地图，8卡独立任务而非跨卡训练。逐task比较翻转及概率delta并分构式报告；若概率效应与精度噪声不可分，按accuracy优先、概率主张降级，不能把小样本0翻转外推为全量稳定。

### Thinking与词边界读数固定（运行前）
R6采用Qwen原生chat B，两选项mapping都greedy生成，cap2048；只解析最后一个`</think>`之后独立的A/B（可带句号），未闭合/格式失败/cap分别报告，主生成准确率按全部预选输入分母，失败记未作出正确回答而不说语义错误。另生成同一原生B的thinking-off R0-generation（cap32），与R6直接比较，避免把自由生成与强制候选评分的差别当thinking效果；R6不伪造候选概率，也不评分推理之前的logits。首次只用原14材料仪器smoke核对解析/引擎，完整面板随后同协议运行，不挑smoke里的成功题。

消歧surprisal按Oh & Schuler2024公式重分配词尾whitespace质量：raw log P(word)+log P(boundary|after)−log P(boundary|before)，boundary对所有起于空白的词表token边缘化（排除special）。保存原始和WT读数、两端质量、真实上下文/显示词；跨词重token化、无认可位置记缺失，不能只说“带词首空格就正确”。公开mat/matron概率树与不同长度leftpad CPU独立数值校对得到.2/.6的规范词概率。此读数是次要预测性协变量，不证明QA理解或world belief。

### Thinking仪器v1–v3校对（完整R6前）
v1错误地要求thinking-on的prompt已含`<think>`，实际模板由模型生成此标签，assert失败及28个off输出保留；v2改为验证没有off的空闭合块，56个两mapping输出全部完成、cap0。严格裸A/B parser误把54个清楚的`A. Yes`等标作格式失败；v3机械重解析全部56个缓存，接受label与当前显示选项文本严格一致的`A. option`，冲突/多标签/非literal文本仍失败，不看gold、不重采样挑输出。全部56可解析（off28、on28），旧parser结果保留在每条previous_answer_status，原始v2整目录不改。完整R6从v3协议起跑。

### 仪器自审：precision与batch layout（地图归因前）
1.7B全量B固定6928项：BF16/FP32 60 flips（.866%）、平均概率差.007679/max.845305；相同BF16、B子集独立批次布局相对全A/B地图35 flips（.505%）、平均.004911/max.864055。后者不是完全相同batch layout的重复；极端概率噪声仍存在，不能称greedy等于数值完全一致。假说表E1/E2/E4仍未得到能力证据，E3已有读数风险；当前仪器异常只是测量限制，审稿人不会把精度修正本身当科学增量。停止围绕1.7B做局部链，继续强模型/三族面板；小效应概率归因须经稳定精度复核。

### 汇总与supplementary模型（能力分析前固定）
主cluster-bootstrap之外，补充有限面板macro：每模型内均衡构式、每族内均衡模型、再均衡族；所有模型/构式共享同一lexical cluster重采样次数（SAP跨构式保持依赖）。缺失cell不填0，非可估bootstrap draw数量另报；模型不是随机抽样，CI只表示当前面板的材料不确定性。已知5个Qwen值1、Gemma/Llama各0的例子仍给1/3，不能被Qwen计数主导。混合logistic补充采用statsmodels BinomialBayesMixedGLM VB，固定效应含条件×reading×构式及mapping，随机截距cluster/model；固定系数Normal(0,2²)、log随机SD Normal(0,1²)，maxiter200、gtol1e−5，收敛/警告全报；其95%区间是近似posterior区间，不能冒充主bootstrap CI。无合格观测明确不拟合、不补0。R8恢复与R6对matched-generation的对比均独立报告。

统一分析额外保留SAP的source_disamb_word_index；作者位置不自动冒充“两遍Step确认”，无两遍可靠位置时R2缺失。Čeháková的ambcor与ambmis都归initial，discor/dismis归final，保留推理输入中的粗target字段并新增analysis_question_target；原句/问题/gold不变。

### R3输入补审（POST-HOC时点，效应分析前）
发现R3程序填充句尚缺独立T3，补审全部当前三族使用的20种不同完整句，两遍Step Plan/step-5-preview、batch2；审计只看填充句，不看任何模型输出。两遍20/20 grammatical acceptable，全部naturalness4–5，没有临时GP消歧点。T1字段是固定NEITHER兼容占位，不能把其100%一致率冒充语义审计一致率。记录补审晚于R3计算、早于任何阅读效应解读；R3分析强制要求独立filler审计，失败/未知不进入R1/R3对比，不能静默通过。未来tokenizer如引入新填充句须增量补审。API辅助任务阻塞获取共享第0slot以免饥饿，仍与其余调用总共≤8，不取消GP在途请求。

### 作者Gemma仪器未通过（继续独立修复，不作能力结论）
公开Gemma4B 19264 regular行中4631两候选同时0（24.0%），不能当有效概率或错误。原首步数据、BF16三步fallback、FP16尝试原样保留：FP16 generate出现非有限概率，属于数值失败；BF16三步15766有分数但与未剔零质量的公开值仍大幅不一致，不称复现成功。进一步核对原base_inference：Gemma直接加载Gemma3ForCausalLM且未指定dtype（默认FP32），不是Qwen的FastChat FP16路径。正在按此类/精度完整对齐；public comparator剔开blank/nonfinite/zero-both并报告缺失数量。旧比较文件保留，重算用新文件，后续新阅读条件暂不依赖未校准Gemma A的概率叙事。

### 三族FP32确认面板（效应分析前登记）
固定Qwen3-8B、Gemma3-12B-it、Llama3.1-8B-Instruct，全部1732题、B两mapping、R0/R1/R3/R4/R5及R0一句恢复，FP32独立单卡复算；不按已看到的效应选材料。FP32与BF16作为独立面板分析，不混为重复样本；R2在完整Step位置资格后补两种精度。此扩展是前述probability/layout敏感性尚未解决的确认测量，不围绕弱1.7B继续局部研究链。原BF16全面板仍完整保留；若效应在稳定精度下不成立，降级相关概率主张而不筛选更有利版本。

### 非标准final答案独立审计与源parser仪器
四个已完成Qwen thinking/off中63个非标准但结束的final回答，交Step5两遍匹配显示选项（两批独立打乱、分歧第三遍）；只看post-think最终文本及选项，不提供句子/问题/gold，未闭合thinking不送审，label与文字冲突保留UNKNOWN。不改原prediction，独立审计映射在分析时核hash采用，所有未知/失败仍单列。两遍字段中的T1/T3固定兼容值不作世界语义/语法gold。
Gemma精度/class/fallback仍不足以重合公开值；source复现改用未改写的上游parser函数AST、原generate(max_new_tokens=3)与默认采样、逐prompt无padding，固定14材料×16提示，seed52/53都报告、保存实际3token上下文，不筛seed。这是E52标准仪器校准，不以其局部波动作科学finding。已从hf-mirror.com获取不重定向的元数据，两权重SHA与ModelScope完全一致，未直连HF；对应镜像revision093f9f388b31de276ce2de164bdc2081324b9767，未证明与作者当时revision相同。
最终资格额外要求两遍grammar都acceptable，第三遍不能把两个marginal升级为accepted；T2采用原两遍共识，第三遍位置冲突记缺失。未裁决的T1分歧同样保留两遍标签供一致率分母，不能因裁决失败使一致率虚高。

### Gemma A复现自审后继续
未改写上游parser、FP32 text model、逐题无padding、固定seed52/53：193个两seed都有效的任务仅1个decision flip/平均概率差.01654；与公开有效记录342个匹配仍131 flips/平均.37752，明显不在本地采样噪声内。原始3token上下文、两个seed及所有先前失败保留。不宣称复现通过，Gemma A暂为描述读数、不支撑与原文对齐的能力叙事；不按更有利版本选输出。停止围绕该局部校准异常连锁，假说表仍无E1/E2/E4能力证据，E3的问句问题仍待完整D0-v2；该软件/版本差异本身不是科学finding。三族B FP32确认与其余族/格式的系统测量继续，尚无资源级真正卡住。

### 重复来源与R3计算资格（效应分析前固定）
输入字节检查发现SAP与Čeháková共享24个MVRR GP句，只有其中5组原问句也相同（10个gp/control QA）。主bootstrap将完全相同GP句连接既有lexical cluster，并传播到该cluster全部问句/构式；原cluster_id保留，新增analysis_cluster_id，365个来源cluster连接后为341个。去重敏感性移除完整的重复question pair：只看句子、问句、选项集合与gold文本，固定SAP优先、Amouyal其次、Čeháková最后，不能因语义通过或模型表现换来源。主结果与去重结果都报，不把共享框架当独立材料。
R3虽然孤立填充句token数等于S，少数任务在完整prompt的词边界合并后仍比R1少1token；按完整任务身份逐一比较prompt_tokens，不相等的任务保留原输出、从R1/R3等计算对比排除。每reading的gp/control cell及原始收益先取同问句两侧交集，不能由缺失组成制造差距。补充mixed模型读取同一主分析的validated-task ledger，使filler质量、实际长度与去重排除一致。新tokenizer引入的3种filler正做增量Step审计，固定复用此前20种的全部标签，不重标挑有利版本。

### 原生模板token仪器修正（真实误读主分析前；描述图暂不采用）
为安排高信息量追问，在D0进行中先算了三族FP32按原数据答案约定的initial_all描述图；genuine/NEITHER未估，不作能力归因。低control触发token检查，发现我把已含BOS的native template再用add_special_tokens=True编码。完整14-tokenizer输入检查确认5个受影响：Llama8、Mistral24、Gemma4/12/27-it；Qwen、OLMo和base路径按实际token序列核对，不因成绩选择版本。
所有旧输出与interim图保留，受影响B暂不采用；改为已渲染chat不重复special tokens，普通文本A/base仍由tokenizer加所需special。五模型全部1732题B×全部阅读/repair在runs-native-v2重算；三族FP32确认中Gemma12/Llama8在confirmation-native-v2重算，Qwen8实际token序列一致、保留原固定面板。旧完整run的所有A任务用输入格式投影保留、不按结果筛。完整prompt长度/精度比较纳入prompt_tokens，防止仅文本SHA相同就混合不同输入token。
三族14材料/28任务2D与等价4D因果mask分数完全一致，证明掩码仪器的一致性，未开放任何未来边；其输入尚为旧BOS政策，后续mask使用纠正native输入。这不是oracle的科学效果或能力证据。source/special-token完整性修复本身不作finding。官方[Transformers v4.51.3说明](https://github.com/huggingface/transformers/blob/v4.51.3/docs/source/en/chat_templating.md)在GitHub核对，未直连HF。
全14 tokenizer的R3 catalog仍只23种filler，增量v3没有新文本，无新增API调用；WT保存sentence-final/punctuation标记，按原公式条件于trailing whitespace，不能当document-EOS概率或人类读时。
