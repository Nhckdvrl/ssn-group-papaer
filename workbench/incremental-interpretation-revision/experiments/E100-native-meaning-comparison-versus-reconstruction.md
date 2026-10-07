# E100：现代自然解释的实际比较与重建credit

- **状态：** DONE；计划范围与完整/仪器不可用范围详见下面结果，不把UNAVAILABLE记零分。
- **对应：** I07/P20；先前解释的修订生成由E96原社区GP-cue两句自然输出承担，评价是否复制难观察的误解。
- **问题：** E96自然cue-P比GP-P更忠实，原难句的inverse重建credit对其不敏感或反向：是model不理解参考句，还是实际语义比较与inversecredit不同？旧E95候选均残缺/tie高；本块直接用同代原生writer候选，不重复旧候选格式网格。
- **数据：** E96冻结50发表pair/100Source/三当前family，每family用自己原greedy GP-P/cue-P两个候选，不改P、不按已读质量筛；未完输出也保留并给未知界限。全部原共同问题定义语义对象，Source和Q不重审；教师标签沿E96完整封版匿名T1。
- **条件：** 原E95实际A/B/C=tie比较prompt、native和同一句RECOVERY两P顺序、greedy64cap/nonthinking/BF16/eager；3family×100Source×2mode×2order=1200真实输出。匹配writer/grader，两个Source参考均测同一对固定P；不额外扫更多wording、交叉grader或reward形式。
- **读数：** 真实比较rank相对E96原共同QA语义fidelity/pattern的alignment及lower/uppercorrect；actual-minus-originalraw、actualcueSource-minus-GPSource、unknown/cap/tie，两order统一语义方向。all/三ct、所有eligible和changed/tie预定诊断全部；Source→原paircluster10000bootstrap seed100。无Goldclass结构NA保留，不编缺的命题。
- **阳性对照：** 100Source/pair/Psha与E96完整sealed predictions逐项链接，模型revision相同；实际题首固定repeat tokenexact/parseable+stopped；一条RECOVERY为R8。Gold不传给模型，仅分析才joinE96T1。
- **噪声地板：** 同已验证native工具、固定64cap不增长，不用LP argmax冒实际行为。若真实比较也不分候选，则不声称理解已完备；若只cueSource能judge就定位参考句解释，不能叫inverse单独有错；若actual原Source强但raw反向，则形成更有辨别力的credit接口对象。
- **决策表（跑之前写）：** actual原句正确择P且raw不对齐→支持inverse接口问题；actual与raw同误、cue共同修复→评价依赖观察解释，方法动作需针对状态/观察语义而非评分表面；全tie/unknown→此接口不具辨别力，同报不以加格式控制补成故事；现代三族/ct混合→限定，不自动关线。
- **算力：** 估≤1GPUh；0新模型/0LP/0API。8slot等各E98同slot sealed cfg，并等自己完整E96P；Min已可启动，其他六继续排队。08:55release/09:00硬stop优先，持久timer覆盖，0新Source数据构造。

05:21完整Min族400真实比较已sealed，在读取效果前登记首完整族INTERIM（原三族主图继续），逐条joinE96首完整族既有T1。默认metric/全100Source/两候选顺序不改，未读其他partial。

05:24完整Min INTERIM400输出/.04679GPUh/1648panels SHAce135d2e8642c5ebf58725a09a14607c61387b902a7d1c0277f2f1b02108fb01，原Source changed fidelity实际tie68%、correct2%[0,6]%/alignment−.28[−.42,−.14]，cue tie84%、alignment0[−.14,.12]；actual-minus-raw非共同改善。原句judge亦无法可靠区分，不能声称理解正确仅inverse错。全3族继续，R8/其它ct全部同报，不加wordinggrid。

05:37POST-HOC核心解释诊断（0新输出/标注）：E96同Source共同Q逐条correct vector定义dominance，避免整体定性judge与scalarfidelity权重歧义。完整Min50pair：cue逐条dominate30、GPdominate1、equal19、tradeoff0；原Source NATIVE60个cue-dominate顺序决策中42tie/18选差P/0选好P，cueSource51tie/4选差/5选好。不是两候选各有不同错误的tradeoff造成tie；但依然只是原已注册Q有限语义，不把OTHER未测内容称full equivalence。诊断文件E100/posthoc-pointwise-dominance-Min-v1.json，两parentSHA明示，不升级能力/C。R8 pooled GP patternalignment delta bounds[−.161,−.130]且CI负，Tie减少不是修复；不再追加更强grammar措辞。

2026-10-08T06:22:28.509912+08:00 完整范围自审：原计划1200输出实际528：Min完整400+.04679GPUh；Q只有原shard0 128输出，其余Q2/G3的固定首instrument失败0科学输出，共672 UNAVAILABLE。终态外置full-scope-instrument-unavailable-v1.json保留所有cfg/log/pred SHA，等待全8shard的CPU分析器已终止，Qpartial不用于主效应。Min完整原INTERIM有效，POST-HOC原Q向量逐项支配cue30/GP1/equal19/tradeoff0；cue支配30的native GP-target60决策42tie/18选坏/0选好，不能解释为两个P不同Q的质量tradeoff，亦不认证所有未问事实。
