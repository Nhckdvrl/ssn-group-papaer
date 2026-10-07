# E86：拒绝源句还是读错关系？（2026-10-07）

- **状态：** RUNNING；生成器E431在效果前改E86，非POST-HOC。
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
