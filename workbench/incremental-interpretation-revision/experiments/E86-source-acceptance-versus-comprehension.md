# E86：拒绝源句还是读错关系？（2026-10-07）

- **状态：** DONE；生成器E431在效果前改E86，非POST-HOC。
- **对应：** I02 / C06–C09 / P17。旧解释未修订的完整画像；E82部分现代模型initial正确而final很差，E85词义也有gap，须区分关系理解与输入判定，不开线/改状态。
- **问题：** 模型正确拒绝原初始命题，却也错误拒绝显式final命题，是否源于把GP输入视为不可接受？普通理解任务和原严格源支持会否给出不同关系？只一次核心合同变化与源接受读数，不扫提示。
- **数据：** 原E82完整892QA/356S/178clusters，全部T3双遍agreed、grammar acceptable（892/892，已在效果前核对）。原S/Q/gold/关系目标不改；每Source仅新增一个语法可接受问题，Gold Yes直接来自既有T3，无新Step调用/原数据重审。可信人类与原标注全复用。
- **条件：** QA_PLAIN采用普通“Answer the comprehension question according to the supplied sentence.”，删除严格G2“必须explicitly entails，compatible extra event不足”规则；原QA_STRICT和QA_RECOVER全部E82缓存复用，不重跑。GRAM_ACCEPT只问原句按打印形式是否grammatically acceptable，每原Source一次，两readout/two mappings。新两任务均DIRECT，E82的一句恢复完整复用作为行为范围参照（R8）；该测量不单独认证能力或机制。
- **仪器：** CPU母G2完整prompt SHA验证；普通QA/GRAM的原Source token与位置、可见之前prefix均与母相同；任务文字只在Source之后变化。有限精度不同长度可能有数值差，不冒称hidden字节相同。固定输入首Source prefix/full差≥.001全分片统一full_scores，重复LP全0；模型/native closed入口与asset SHA同E82。
- **主读数：** 三族四构式GP/cue/words-letters：QA initial/final/all correct、p_correct与joint全注册QA，PLAIN−STRICT、PLAIN−RECOVER；每Source GRAM correct/p_Yes，以及GRAM拒绝但QA不同的完整列联表。原source gold是否匹配G2、Yes/No与语义三层分别保留，普通任务兼容事件误读不当实际Source恢复。
- **阳性对照：** 原cue/T3可接受、原initial/final真实题，GP与cue同源相同Q；Min NPVP cue final弱位只能描述。含混No不得凭GRAM判定变成false。
- **噪声地板：** 两mapping flip和178 lexical cluster paired bootstrap10000 seed86；结构目标/cluster全部用冻结analysis字段。所有族/构式/负效应/模式保留，不按GRAM或QA结果选子集。
- **混杂审计：** GRAM判断是行为，不是latent syntactic parse；普通QA改变任务约定，会放宽compatible extra事件判断。若PLAIN只变Yes且害initial，不称完整理解恢复；源prefix不变只能限制可见信息的编码解释，不证明所有later任务计算不变。
- **决策表（跑之前写）：** GP拒绝GRAM且PLAIN救final又害initial→任务判定/解释选择竞争，不能写initial正确即reanalysis；GRAM接受而两QA都错→输入拒绝不足解释，回具体关系内容；普通QA共同两关系好且cue保持→验证协议引入功能失败，下一一项源消费因果检验；异质→自审结束该合同块，不继续提示或calibration网格，回正在完整闭合的E67内容。
- **算力预算：** ≤2GPU·h，14976新条件=(892+356)×4×3，0API；三族当下资产/新runtime，8独立卡Q3/G3/M2，BF16/eager/FP32 logsoftmax、seed86、固定单任务/2候选布局；资产离线/国内镜像，不进git。

## 结果

先写卡，再程序化同源/prefix/金标预检；无科学效果，尚无合格idea，C06–08L0/C09限定L1不变。

CPU三族4992新任务/族、全892母prompt SHA与Source先行prefix/token完全一致；原T3全部892 agreed/acceptable，356独立Source Grammar Gold来自旧标签不新审。data SHA2b25b5e4494d8ea70c821ca6d5f2adadab9e704db123e67065f18e5b2087b30f，8卡14976条件启动，0API；PID 3073497,3073498,3073499,3073500,3073501,3073502,3073503,3073504。先数值仪器，未读partial。

### 完整结果与自审

8分片全部完成，14976新条件，.744958GPU·h，0新API；1680QA格、96语法格、192mapping、144列联与144truth分层全图保留于[完整摘要](../results/E86-source-acceptance-summary.json)。外置map SHA54147e32eaae86674cf4ce07f8495e1e55a10f08cfe2e418941285840795cffa。统计使用冻结analysis字段；同Source/Q/mappings先平均，再词汇cluster bootstrap10000。

- words NPZ PLAIN−STRICT final correct Q/G/M +17.70[11.24,24.44]/+20.22[13.48,27.81]/+36.80[28.65,45.22]pp；initial −2.81CI含0/−26.40[−35.39,−17.98]/−12.92[−18.82,−7.58]，joint +1.69CI含0/−11.24[−20.22,−2.81]/+23.03[14.61,31.46]。不称共同完整恢复。letters同报，Q joint +6.18[1.69,10.67]但cue joint −15.17[−24.72,−6.18]；G/M initial损伤保留。
- ordinary理解不是严格支持等义：NPZ GP初始GoldYes原始mapping任务34个，PLAIN正确Q1/G0/M0，句末GoldYes176个变成166/174/101正确；以上是描述原始任务数，不独立样本或挑选效果后新主读数。不能把正确No就命名完整重析，也不能只看末句收益。
- words GRAM GP/cue：MVRR Q11.11/38.89、G16.67/88.89、M0/0%；NPZ Q0/83.71、G1.12/94.38、M0/8.43%；NPS Q48.61/94.44、G100/100、M9.72/44.44%；NPVP Q13.46/50、G40.38/82.69、M0/0%。Min整体语法阳性对照失败，Q部分cue弱，禁止解释成三族共同GP拒绝。Gemma NPS所有句子认可语法而关系仍有错误，输入拒绝不足解释。
- mapping最大GRAM M NPS cue27.78%，QA Q MVRR RECOVER letters26.73%、M NPS RECOVER words27.78%；全负效应、弱对照和原Gold不匹配层保留，不筛模型/条目。有限精度Source同prefix不等于hidden字节相同；仅行为接受判断不认证latent parse。首次完整分析器Python3.10不支持starred-subscript，编译前语法失败日志保留，改为显式tuple后完成；原学生输出未改。

自审：任务约定明显改变晚期断言和早期兼容事件的权衡，未建立可复用完整修订或共同输入拒绝机制。该任务措辞块结束，不扫grammar-license提示；C06–08 L0/C09限定L1不变，尚无合格idea。下一先检查现代模型实际生成答案是否符合强制打分所述行为，使用原提示与金标，无数据重审。
