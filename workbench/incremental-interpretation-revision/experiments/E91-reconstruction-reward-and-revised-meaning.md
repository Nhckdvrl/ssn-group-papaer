# E91：重建原观察的奖励能分清忠实解释与语义误读吗？（2026-10-08）

- **状态：** DONE；生成器E431在任何科学forward前改E91。
- **对应：** I06 / P20（重建奖励是否识别替代论元的保真），C06–C09；E88–90的frame/源局部块已收束，转向内容reward这一新对象，不继续Hint控制。
- **问题：** 自然观察重建的likelihood与语义保真是否配对一致？ABBEL Eq5/Algorithm4给内容credit的研究动作启发此pilot；模型看得见同一个Source的正确/错误实际解释，重建评分可能更偏爱保留旧关系的文本。这是猜想，不是已证ABBEL问题。
- **数据：** E70完整648 BASE_BANK/TARGET_BANK实际自由输出、三旧generator族×108Source，原1280原子Q已双盲/183裁决完整闭合。原全部Source/Gold/文本/条件保留，既有API标注直接复用，0API；原成熟材料不重审。unfinished/capped缺失保持unknown，不用结果筛pair。Source从E63母文件逐字核SHA，文本由E70packet与E64完整原输出核对；packet不含Source/gold，教师盲法不改。
- **评分条件：** 三当下grader族Qwen3.8/Gemma4/Ministral3，在同一固定raw reconstruction trace上打分原Source：Global Instruction=Maintain a concise faithful interpretation of observed events；new belief=P，prior belief=No prior information，past action=Read the next sentence；past environment feedback=<environment>后接原S。648×3=1944评分。全同Source paired、无QA/Gold入grader。这是固定未训练观察重建analog，不是ABBEL训练/ColBench轨迹原样复现；raw trace为Algorithm4式顺序，不扫native/prompt格式。
- **主读数：** 同Source同generator TARGET−BASE的观测token logP总和、平均token logP；Source目标长度相同，两者的排序相同。另报原Algorithm4形式max(sum,−.9)的clip ties，不将本文字cap自动当作者实际code。各grader×generator/构式/GP-cue完整报告。
- **语义对象：** 对原GoldYes：P ENTAILED比例是正关系保留，CONTRADICTED/NEITHER分别错误/遗漏；对原GoldNo：P ENTAILED比例是源未支持的过度断言，CONTRADICTED和NEITHER保留区分。保真summary=正关系保留−源未支持断言；两维始终单列，不能把不说一切当正确解释。若一侧无GoldYes/No，单列NA、保留Source不硬造0。
- **关键配对：** Δreward与Δ保真/Δ正关系/Δ错误断言的相关及符号一致比例；以Source→固定lexical cluster bootstrap10000/seed91，generator或grader不是新独立语料。全cohort是主；按已有Δ语义提升/下降/不变分层属于解释图，不按奖励筛成功样本，不宣称独立验证集。具体错接可作为例子但不只报例子。
- **阳性对照：** 输入固定首个Source：目标S全token ID与上下文边界核对，sum=逐token logP相加，确定性repeat值逐字相同；不含Source/Q/Gold在belief之外的prompt。已知E70改正与破坏两侧均保留，梯度reward排序是否与它们一致是被检验对象，不假定阳性。
- **噪声地板：** 固定single-sequence BF16/eager full teacher forcing，raw两重复LP完全一致；不使用prefix/full单token布局对比、不给看效果后另换score。输出目标最少1token；token长度/解释长度全部留记录。CI及tie完全报告，低相关不独自证明训练损害。
- **决策表（跑之前写）：** 奖励倾向语义更坏且正关系损失跨grader稳定→内容reward缺口值得追，下一在社区真实update轨迹检验并设计修订保真credit；奖励主要tied/不辨别→reward缺少辨别力，不称推动错误，下一测试具体能产生分辨的内容评价；reward随语义改善→反驳当前失配猜想，回实际论元重建规律；只某grader/构式异常→如实定位，不硬说一般定律。只有ranking pilot，不为赶deadline开始大训练或要求完整paper proof。
- **混杂边界：** bank生成文本是既有功能干预输出，不是现代grader原生记忆；source-support Gold不是完整世界truth。未对解释语法/字面copy率造新标注，记录长度与source word overlap描述，不能仅凭相关因果归于copy。三构式以实际E70输入为准、不补造缺失构式。clip、不同顺序joint的Bayes一致性未核code，绝不说ABBEL被证伪。
- **算力：** ≤1GPU·h，8独立H20 3/3/2，现有国内镜像离线模型；每任务deadline guard，08:55释放/删权重、09:00硬停。0新API/0新model下载。

原E70全部648文本/324matched pairs/108源逐SHA核对，unknown atom0；构式MVRR228/NPS312/NPZ108，三族grader总1944LP评分。data SHA95b6bf228c19ac29a1264f5f274961e3ae298006fa1b9829895021ec285fc380。CPU每族全部目标token边界/无Source在prefix（唯解释可含观察语词）核对通过，最大完整127/129/126tokens；8卡已铺开，API0。

## 完整结果与自审

1944评分/.080626GPU·h/0API全部闭合，972 matched grader×文本对、72全族/构式/GP-cue图，map SHA42068895256021dcdbf2023adcf4702c3bb641e7af4ed7e362c258898f6dccb9。已读72细分/ALL的方向、相关、排序counts及GP主CI；原完整Source记录保留，不筛样本。初版分析少sentence_sha256统计key，在任何效果输出前失败；日志v0保留，加原metadata后完成，不改科学输出/读数。

原Gold两维齐全的GP39源：TARGET−BASE保真Q/G/L+20.9[3.8,39.3]/+26.5[8.5,46.6]/+32.1[13.2,51.7]pp，但不少来自源未支持断言减少；正关系保留Q+3.7CI含0/G+15.9[6.1,28.0]/L+8.9CI含0（该维41源）。三grader完整GP raw reward趋势：Q-generator三个grader−.52/−6.45/−.79，其中GemmaCI[−12.09,−1.32]；G-generator+.92/+.39/+.96均CI含0；L-generator−.94/−5.49/−.37均CI含0。不能以reward全54源均值直接对比保真39源均值。

按同39源的POST-HOC分母对齐，G-grader对Q-generator reward−6.91[−14.16,−.48]；另8组合CI含0。GP changed保真Q12/G12/L17源中，raw reward三grader分别与之相反6/8/6、3/4/6、5/9/6，亦有大量一致；cue多格相关正（如Qgen三graderρ.674/.639/.690，CI正）。不支持“奖励普遍偏爱错误”的强解释，仅发现reward未稳定表达GP修订的语义收益。

### POST-HOC作者实现校对与界限

原伪代码形式max(sum,−.9)全ties，**不当作作者实际训练reward失败**。固定作者源码8ed3bf8：sum/token数或64、`min(...,ceiling)`上限、下限−5；source selected code已读，完整默认config/训练未复现。复用原mean分数的敏感性单列外置`posthoc-author-code-score-and-matched-denominators.json`，保留原主登记。上限clip有些ties但不是全体；GP同39源例如G-grader/Qgen31ties、2一致/5相反，与raw结果不混成新主读数。

**下一核心：** 同一P固定，只把重建目标改成发表的配对消歧观察（反向也报），检验reward与语义一致是否随观察surface变化。用现成控制句、既有Gold，0API；input common-Q Gold冲突的4pair提前排除，仅做Gold一致的等价注册关系，不按模型/效果筛。若一致性不改善，此猜想降低，回真实关系更新；不做reward prompt/calibration网格。当前探索idea尚未形成稳定新叙事，C06–08L0/C09限定L1不变。
# 2026-10-08 POST-HOC逐token诊断（先写口径，非新GPU实验）

已知完整E91/E92结果后，分析E91保存的逐token分数：TARGET−BASE的总分差，是否主要来自观察第一个token，还是继续存在于其余token。保留全972配对及全构式／两侧／九generator×grader，不挑错例；固定first/rest及按相对token位置四等分，不依据效应找边界。原Gold/主读数不改，不把相对位置称句法disambiguator；原论文与Step5位置存在缺失／分歧，今晚不为这份诊断再审位置。记录总分可加性、同一观察token数、全部scope的alignment与语义质量完整cohort；语义变化条件计数只作诊断。0新forward／0API／0GPU。若首token界面效应能解释原信号，收窄I07；若多段混合也不直接宣告解释机制成立。本诊断不给新主张等级。


