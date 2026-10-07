# E96：当前模型自然生成的解释，是否受到同模型内容credit的错奖？（2026-10-08）

- **状态：** DONE；完整注册三族已封版，旧INTERIM版本保留。
- **对应：** I07 / P20；新scope由已完成E91/E92出发，未读取E93/E95任何partial effect。不是第三个suffix／模板／mask控制。
- **问题：** 旧模型经Source-bank干预的P上已见语义与重建失配，该对象是否也存在于当前模型自然生成的解释？现代模型若已不产生相关误解释或credit能分辨它，则显著降低当前适用性；若出现，才有更现实的self-supervision对象。
- **数据：** 原E92预先固定的50发表pair／100Source（MVRR／NPZ／NPS），原GP与社区cue句直接使用，不生成新Source。原4pair因共同Q Gold不一致被input-only排除，今晚不重开资格。仅保留原两侧共同Q/Gold支持，明确不是认证全句逻辑同义；原P完全不复用。新P来自三当前模型各100原句、原native chat、不做hidden transplant／不提前指定QA。原Source／question／Gold资格保持，明确8项更正版本并保留旧来源。
- **条件：** 唯一已有Amouyal自由解释任务，要求Rewrite as two shorter sentences，greedy／native thinking=False／96token cap事前固定。两个Source版本本来在原社区数据，不添加新hint试探；300新实际P。一个model同时作为writer和reconstructiongrader，两个自身P（GP／CUE）的content context一样、逐一重建同GP或同CUE Source，150pair×4=600新LP。只selfgrader，不加crossgrader矩阵。
- **标注：** 新P的原共同Q逐项Step Plan step-5-preview T1匿名2遍＋分歧第三遍，batch≤5／共享8slots；teacher只看到P和Q，不见SourceGold／model／Source版本／reward／旧P。新输出才需要标签，正常社区Source不bulk重审。完整句外未认证语义、不把modelgrader当新Gold。未停/cap仍保留、schema／API失败unknown上下界。
- **读数：** 所有50pair主图、各构式、原共同Gold极性／source condition。P_CUE−P_GP的balanced semantic fidelity（正关系retention−unsupportedassertion，缺某类原Gold则NA明确）及全Q source-pattern accuracy；两个固定target下reward−semantic方向alignment／opposes／ties／margin及Source→publishedpaircluster CI10000 seed96。完整记录所有NA／未停/cap；semantic changed为inputlabel确定诊断不选奖励幸存者。对同P换观察surface的alignment差亦全量报告，与旧E92不同在当前自然writer/selfgrader，原数不覆写。
- **阳性对照：** 输入全Q/P/Source SHA；当前native模板三个族正确非thinking边界，固定首任务actual重复token完全一致，固定LP重复一致及逐token求和；同P重建不同target只有观测目标变化，context逐字一致。已有cue语义保真／同registeredQ是自然锚，不将其当全部latentstate。
- **噪声地板：** BF16/eager／seed96固定、greedy；token sum/mean同目标排序等价，exacttie1e−12，不加clip／温度／长度分位控制。R8一句恢复已在E93/E95测，此处数据对象为实际生成保真而非单prompt能力认证；不以单native提示失败宣布能力缺失。
- **决策表（跑之前写）：** currentGP P仍较错且selfreward不能识别较正确cueP→I07具有当下自然生成对象，下一由具体错奖操作设计机制核心；GP与cueP同样正确／ties→旧干预P不足代表当下痛点，调低适用范围；reward明显正确区分→修改当前机制优先级；只有一族／一构式→明确限定，不接续一串生成提示重试。今晚找到值得追方向，不要求完整RL训练证明。
- **算力：** ≤2GPU·h估计，8独立slot Q3/G3/Min2；每slot等相应E95完成后取既有锁，GPU4可立即开始。同process每pair先生成两侧自然P，再评分4个固定目标组合；分数不进入任何后续生成prompt；原pair在shard内两侧俱全，不持GPU等别族/审核。0新模型／无HF直连；只有新P语义标签用Step Plan，无现金API。08:55系统独立释放和每任务guard／排队waitguard优先，09:00硬截止。审核CPU不作为GPU启动gate。

先CPU三族逐输入／Q资格／source pairing校对，后启动，原E93/E95mode与输入不改。

启动前data SHA387f20470b08b24c70f43d1b99b9fa00a3f18b72c04980a06fbfd1c89f072666，新P审核按每model 250个原共同Q assignment构建；Source原数据0新审核，4排除pair资格固定。初次builder误用无pandas系统python在0forward／0HTTP前退出，已改用既有CPU环境，未安装依赖或改data。

03:55，首Min族100自然输出与200LP全部完成，仅metadata。为缩短新数据标注等待，在任何E96 HTTP/科学标签读取前调整审核流水线：按**完整model族**固定输入做匿名原子双遍，完成的精确P/Q packet以SHA去重复用，所有三族仍进同最终主图；未完成族绝不提前抽样。每个phase独立data/summarySHA，最终合并只复用已有有效同packet标签，UNKNOWN仍保留；主Source资格／读数／模型／cap不变。原finisher全族等待在0HTTP前退出，仅流水线改变而非挑结果。

04:50 在任何新P语义效果读取前，完整Min族100自然P+200评分+232完整双遍/31裁决/0unknown可生成INTERIM all-scope供假说探索；全三族主图继续，不按Source/label筛。延续03:57 E93/E95完整族先读的prospective顺序调整，原指标和所有共同Q不变。optional analyzer参数只变完整族scope，默认全三族主图不变。

04:51 完整Min族INTERIM 520panels自审：100P/200LP/.0344569GPUh，232packet两遍/31裁决/0unknown/0Pcap，map48aa680d625c8cb1e8e59a8c6d9577ca6fb04c92f599b049e0a30f9db7ff50af。共同原QA pattern GP50.2[40.8,59.3]%→cue84.5[76.6,91.7]%；fidelity36eligible/14structuralNA，GP.051[−.144,.241]→cue.806[.653,.931]；同固定P credit alignment原GP−.028[−.306,.250]、cue+.472[.250,.694]，paired改善+.500[.167,.833]。MVRR17pair pattern alignment GP−.412[−.765,−.059]→cue+.529[.176,.824]，NPZ/NPS改善较弱。自然输出与同grader中出现恢复后的内容更保真但原难观察更偏旧误读，强于旧hiddenbank版本的实质对象；仍一完整族，不认证三族规律、RL实际训练后果或全句等价。Q/G全范围待封版，不补多reward模板。

2026-10-08T06:22:28.509912+08:00 完整范围自审：完整三当前族300自然P/600LP/.150377928GPUh，750原子assignment/434 distinct新packet两遍及分歧裁决0unresolved；主map modern-native-belief-credit-map-v1.json SHA aa4a4824ee62f89e6953e8354ccaaceaefaf0cc4173e40689140752f9b4474c0。固定同P更换GP→cue target，fidelity alignment增量Q+.444[.167,.722]、G+.500[.222,.778]、Min+.500[.167,.833]；MVRR pattern增量三族皆+.941[.471,1.412]，NPZ/NPS更弱且CI含0。GP自身P pattern46.94/52.26/50.17%对cue77.60/79.17/84.48%，不说理解完好；fidelity为正保留减unsupported的有符号指标，不能误报准确率。全部50留主图/14fidelity结构NA保持，0新Source重审。
