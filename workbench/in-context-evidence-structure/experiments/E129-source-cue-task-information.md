# E129：来源选择信号只是地址，还是在新输入之前携带任务信息？（2026-10-12）

- **状态：** DONE；两checkpoint固定16→32完成，四raw独立复算有效；57ca241a/a177前评分freeze保持。
- **类型：** PILOT / CLAIM。
- **对应：** C24/C23、I04、P17。
- **问题：** 同名来源从不同demos推断不同criterion时，模型处理新评论之前的Source选择块是否只标出recipient中的来源位置，还是能携带改变新评论功能响应的任务信息？
- **为什么现在做：** E127同词下私人code部署已确认；E128小模型标准选择准确率效应弱、小margin作用与冲突primitive限制提示不能把code选择等同criterion。这里直接检验选择信号的功能内容，不继续磨共同表的行序。既有E118/119完整criterion×code observer用于新因果对象，旧C21–23不以此为新资格。
- **最强近邻：** Hendel2023§2–5已拥有输入独立task representation及覆盖冲突recipient demos；JIT2025拥有局部/可迁移task状态；Dong ICLR26拥有representative-demonstration解释与单向/双向函数的区分；Feng/Dai/Mixing拥有身份/位置绑定及多检索机制。不能声称首次task vector/criterion transfer。增量候选是多Source推断规则时，**身份不变的条件选择块**能否在新输入之前承载criterion×code功能，而不仅指定证据群。读取policy与独立完整程序仍是强替代解释。
- **设置：** 固定Qwen3-14B、Llama-3.1-8B两个checkpoint（已有E119/122 criterion能力和架构范围依据，不按E128coherence效应挑正模型），16/129001 discovery→32/129101 validation，FP32 eager/no training。沿用冻结双方面材料与四B world：A固定food；B service/food×同/反private code，两个Source完全共用no/yes；完整四格8query、8A8B，private方向及新Source别名全部平衡。冲突query的single能力本批单独呈现。
- **操纵：** query写为`Annotator: <B>\nComment:`，先处理这段Source前缀，尚未看到任何测试评论。donor/recipient的Source名字、前缀tokens/positions、B labelstream、输入多重集均同，只改变B示例的criterion/code对应。截取该完整Source选择块每层K/V，替换recipient对应位置，**所有recipient demo K/V与后续新评论保持原样**。不移植答案/测试输入，不搜head/层/强度。
- **主因果图：** private形成完全隔离，无public schema；Source块允许读取两个Source，由模型凭名字作条件选择，不能通过oracle mask替模型完成选择；随后body primary只读recipient B＋Source块＋HEAD。recipient B私人形成不含A，donor信息唯一经所交换的Source块到达。另从同donor context的A选择块提取辅助Cue，注入完全相同的recipient B位置/body图，检验B世界变化是否仅形成一个与请求身份无关的global task信号。A/B块长度在CPU匹配；原始B Cue同名/同token跨criterion的对比为主内容测试，A Cue是身份条件的辅助对照。原global positions保留；recipient两种criterion同code（origin、food_positive），每种接受四donor criterion×code。joint body可读两Source为secondary，测试是否必须有其它可用证据。原生完整形成early/late Source字段、纯一句指令与single各criterion/code为功能参照，不等同主图。
- **读数：** 对每recipient r，
  \(\delta_t^r(q)=\frac12[z_{cue(t,+)}^r(q)-z_{cue(t,-)}^r(q)]\)，t=food/service；f/s按A private code定向，得到2×2 M_r[t,feature]。分别求donor CueB与CueA的M_r；两个co-primary **先每recipient/context分别算signed det(M_r[CueB])与signed det(M_r[CueB]−M_r[CueA])，再对两个recipient等权平均及context bootstrap**：前者检验CueB本身是否具有不同criterion方向，后者检验来源条件的功能方向。不能仅因两rank-one矩阵的差det正而称CueB方向分离。原始两M全部保留；不能仅因差矩阵det正就称CueB正确执行criterion，需同时核CueB两行匹配selectivity/实际任务表现。secondary两行匹配方面selectivity、J、normalized det（行norm≤.001时置0保留context）、完整bias/product、criterion-only双向作用、Code方向、recipient与donor真值各自的full/candidate/actualargmax与margin（不拿recipient准确率独自判断donor任务运输）、原生/指令/Source-only/single all与discord4。矩阵两行同方向只不同gain时det0；positive det不自动表示correct-code，两行selectivity与实际函数能力必须一起解释。
- **阳性对照：** 同一批early/late原生与纯一句指令、single每criterion/private code及discordant能力；pristine/self Source块交换与原forward一致；full-token/cached/默认causal/no-op≤.001；all layers实际mask/合成/seq/ptr消费，Source块未含任何测试输入或答案；B世界不影响A private形成；donor/recipient保留跨B-world相同names/ID流/词集/位置（辅助CueA换name，加性且world不变的词法主效应在其B-world code差中抵消；name×world交互未被排除），全部gold与input-map独立核。Source-only零可达身份控制不作隐藏模块证明。
- **噪声地板 + MIE：** same-runFP32 .001、10000context bootstrap910；所有context/private方向保留，不筛能力阳性种子。最初16数值有效即固定32，不按det方向筛确认；无独立单向函数失败后无限改格式追阳性。
- **混杂审计：** 完整多层Source选择块不是低秩/单向量，也不是只name token；whole-KV改变可用任务信息及检索policy。matrix方向可检验纯address/共同gain的受限解释，不排除criterion-conditioned retrieval、预训练方面能力或已知task-vector算法。标准的语义与固定方面词序尚未分离；early query格式与demos格式不同，early/late行为不能单独证明输入过滤。若只有部分logit功能运输或原生能力弱，照实保留，不称完整抽象program。单task-state移植的一般版本已被Hendel覆盖，只有Source条件的具体过程与旧形成链结合才构成候选增量。
- **决策表（跑之前写）：**

| 完整结果 | 更新认识 |
|---|---|
| 两个co-primary det正、CueB两行criterion selectivity正确且功能阳性 | Source选择块在看到新输入前承载可部署criterion×code信息；纯固定Source群地址或一条共同功能方向不足。不因此称完全不检索/新task-vector构件 |
| Code/共同gain可转移，criterion方向不分离 | 此接口主要承担输出约定/共同响应调节；不把它称独立criterion状态，保留recipient规则/后续读取解释 |
| 仅joint有criterion作用、own弱但函数有效 | 选择信号可能主要改变后续证据使用，需要recipient匹配证据；不是独立完整规则传递 |
| early/late函数或冲突primitive弱 | 本图只得到有界响应/任务可行性信息，不能以移植失败判定无criterion表示或迫使旧证据缩叙事 |
| 数值/几何/身份控制失败 | 保留事故，修正0-score版本后重新freeze；不能科学作阴性 |

- **算力：** 两checkpoint固定16→32、四单卡独立；已有21本地权重，先全CPU source/token图审查与前评分commit。空卡可用，不为填12卡扩大配置；E128全确认之前不GPU评分。

## 结果
0科学评分。接口与observer在首评分前写明；详细条件计数与末版源SHA随CPU实现独立核对后补齐，不把事后新增读数伪装预注册。此项回到最初“来源地址与判断标准信息”的自然问题，用输入独立反事实区分功能；不将一个已有task-vector技巧换名字称新机制。

**0-score设计核对：** Cue阶段不做Source-only mask以免oracle预先替模型选B。CueA/B在同一recipient B阅读图比较；private形成仍隔离，body own/joint仅控制移植后可访问的证据。精确条件计划32cue组合＋32功能/格式/指令/single参照=64×8/context，17独立prefix与8Source准备块；末版CPU实现核数后freeze，尚未GPU评分。

**格式参照的0-score范围说明：** native early/late保留相同全Source形成与query读取，仅换字段次序；independent early的Cue读两Source、body own，而independent late全query own，因此后者差值同时改变可达图，不能称纯字段顺序效应。功能matrix非共线不等于latent维数≥2，whole-layer/whole-block移植也不等同单个task vector。两个co-primary均为完整functional operator的有界检验。

**已有E88的实质区别（0-score补记）：** E88相同姓名输入前字段交换已有隐式标准弱/显式强的结果，不能把本项冒称首次提出地址vs标准。那时改变两Source demo标签、约50%原生冲突能力；未正交criterion×private code、未锁B labelstream/input multiset，也未独立私人形成或在同recipient图用CueA排除共同行为调节。本项保留旧阴性，使用后来E119/122验证的四世界与Llama/14B一次固定复核，主功能两方向与实际donor/recipient函数共同判断。不靠搜更长字段或强层来追E88阳性；若依然只有code/共同gain，就终止此接口追加而回到全链已建立的形成问题。

**近邻检索：** 2026-10-12运行venue corpus nearest Source-conditioned task preparation（k8），词面召回含Symbolic Working Memory与criterion-conditional视觉任务，未直接召回Hendel/JIT；不能凭这个检索无命中宣称新颖性。全文补读Hendel§2–5、JIT§3/4、Dong§1–7与Xiong2024§1–9/附录C。Hendel已有recipient冲突覆盖，JIT已有query前局部运输，Xiong已有多任务向量混合/插值；本项只是将这些强基线方法用来检验多合法Source条件选择的具体功能，结果才能决定增量。

**0-score真实实现计数：** 每context64×8=512评分接口、17prefix/8Cue/64body；两checkpoint各16/32合计96contexts。四CPU真实token全部通过，独立实际源码mask执行检查见PRE_SCORE_CPU_FINAL_4_OF_4 seal；源SHA `a177434cf425889df1fcc8b3607e6d5057a26080ad467e7999d002e6504b00bd`。矩阵observer synthetic对照不计科学评分，0 GPU尚未变。

**前评分seal已完成：** [独立实际源码/CPU审计](../results/e129/independent_review_2026-10-12.md)核1632prefix图/768Cue图/6144query集合/1536整层合成/73728双gold槽；observer synthetic5145数值max3.55e−15。科学源a177434c…无科学评分；随后commit并用21已核空卡运行两checkpoint×固定16→32，确认仅等首context数值floor，不按效应方向。

**实际执行：** 57ca241a/a177434c…已在首评分前push main；21 GPU0 Llama16、GPU1 Llama32等待首context数值floor，GPU3 Q14固定16→32。最后复查GPU2被外部任务占86GB，不使用/不杀作业。操作helper只固定phase与SHA，不改科学引擎，模型载入等待/异常与原raw保留。

## 完整结果与判断

E129两checkpoint固定16→32完成，pre-input Source Cue来自完全隔离私人历史、保留recipient全部示例时，两模型两个co-primary功能det的确认CI均跨0；不是数值失败。Q14仍有小标准相关响应，不能称Cue没有任务信息。单函数冲突能力L约69–74%、14B约77–80%，故这项运输接口不足不能由任务全不会解释；也不外推模型没有criterion表示或默认原生Cue无效。96ctx/49152评分、.413184完整run GPU时、20580独立raw数值max3.33e−16。

确认Llama CueB det +2.492e−6[−5.264e−6,1.097e−5]、Source-specific−1.259e−6[−3.316e−6,4.967e−7]；Q14 CueB +3.740e−5[−1.643e−5,1.014e−4]、Source-specific−1.148e−5[−4.553e−5,1.924e−5]nats²。所有mean-det先context再recipient，negative/两private方向全部留。Q14 J+.00160[.00024,.00300]nats是小响应，不是两标准成功运输；pure instruction origin B candidate84.38/full44.14/in-label55.08%，保留实际输出成本。

依据[完整报告](../results/e129/report.md)、[raw独立seal](../results/e129/independent_raw_review_2026-10-12.md)与各analysis/run。all-run数值max5.5313e−5、graph/self0，不以失败格式隐藏结果。C21–23L3/C24L2和formal状态不改。下一步首先读当前结果与近邻：该Cue来自F0全私人隔离，不是默认原生Cue；有限候选是直接问native/选择性/全隔离历史怎样影响Source信号形成，而非加字段/层/强度寻找阳性，尚未启动。
