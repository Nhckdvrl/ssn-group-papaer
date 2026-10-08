# E14：事件回指是否改变GP历史对后文患者选择的影响？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT / competing-account measurement；非已确立idea
- **对应：** C01 / C02 / P09 / P10
- **问题（一句话）：** 在没有诊断题的后文中，继续原活动与另起活动是否改变GP历史对原self/reciprocal与初始对象NP的相对支持？
- **设置：** Slattery2013原24源组中22组有字面self/reciprocal span；source9/10没有该span，不做此替换但保留原E13。22组×作者2NP options×GP/comma×无桥/继续先前活动/另起活动×原reference/原coreNP，共528变体，全部评分。S1精确保持作者展开，桥来自独立Luna字段标注；S2只替换首字面ref span，coreNP包含源冠词至源choice末端，不重复整个relative clause。构造文本与标注cache-only，copyright不变；没有新comprehension题/语义gold。frozen Qwen3-8B FP32/TF32 false/SDPA/seed0，普通raw text。
- **读数：** target原词span总bits；R = bits(coreNP)−bits(original reference)，正值表示相对更支持原reference，不称correctness。D_anchor = R_GP−R_comma。主交互I = D_same−D_separate；7组独立外审episodic/activity-match clear/episode-link clear作为事件指向主分项，两个原NP option先各报、both在每source平均后bootstrap。22组eligible/clear-reference完整分项与source first12/last12同时报；D_none及same−none/separate−none为对照。source-cluster paired bootstrap10000/seed20261005，每项actual pair IDs/n；没有target长短raw偏好当能力分数。两target pre-span chars与causal token context逐项相同，GP/comma配对使用相同词汇alternatives。
- **至少两个解释：** (a) history-specific event binding interference：GP相对cue在继续同一活动时更偏初始对象，D_same比D_separate更负；(b) supplementary event inference/permission：明确继续同一活动限制额外事件补全，GP偏初始对象更集中于separate或无桥，I更正；(c) nonselective lexical/semantic priming或general repetition：两个桥同样改变或不改变D，I接近0；不能仅凭一个signed preference证明内部event graph。不同scope仅描述性比较，源scope未随机化。
- **阳性对照：** 88个无桥原reference文本与E13原输入字节相同；和已存E13 tokenhash/逐词值比较，报告数值漂移。库masked-label target loss独立核对shift/indexing。cue+same的相对患者偏好完整报告，不要求任意正确率通过；source verb与action名词、原句parity由外审/机械检查分别处理。
- **噪声地板 + MIE：** FP32已知小batch漂移，baseline 88重现给本次word-bits噪声；报告实际量级，不用2×noise/显著性作自动停步gate。7源主分项CI可能宽；结果若不支持明确解释，不能靠挑target窗口或增加模型/模板找赢家。
- **混杂审计：** source self与core NP长短不同，分析同source/anchor GP−cue以及跨anchor交互；全full-vocab概率，首词null。桥same/separate同actor/eventNP且等词数，但continued/began/that/a等词汇语义不同，故I仍可能含aspect/lexical expectation，后续若有信号需针对性替代操作。源NP真实性/合理性用option0/1，不自行标绝对plausible gold。原22后文并非全episode：外审7 episodic/11 generic/4 modal，主/全分项在模型结果前固定。语义不合是有意counterfactual，不当作语法错误筛掉。独立model审计不是人类gold。
- **决策表（跑之前写）：** I明显负且主要episodic → 保留同活动绑定历史解释，下一匹配aspect/lexical-reference操作；I明显正且由same限制作出 → 保留额外事件/推断许可解释，下一操作直接限制/许可新增episode；D_same≈D_separate而二者都改变 → 追general recontextualization/lexical重复，不叫event-specific机制；所有D小或CI不确定 → 报完整结果，降低本材料上lingering功能影响叙事，不扩大模型/窗口sweep。人类blended表示、Slattery下游后果与LM downstream binding已有owner，任一方向均不能自动称novel。
- **算力预算：** 一张独立卡，528短raw文本预计<.02 GPU·h；无资源下载，复用已有env/model；独立标注/两组review用用户授权GPT Luna。**实际：** 待跑。

## 数据与审核（任何E14模型分数之前）
- 外部字段v1发现裸choice漏冠词，v2恢复源完整NP，v3自然countable event noun与数字option；版本全部保留。母亲source S2内嵌主语小写、桥句开头大写，仅允许首字符大小写对应，无实体改写。
- 两位与生成者分开的reviewer，各11交替source/264变体，opaque IDs隐藏条件名称；原S1 parity、target转写、grammar/bridge reference逐ID、句hash核对。528均acceptable/faithful，bridge none/same/separate各176。另独立source scope标注22组，7明确episode，主ID Slattery:1/3/4/20/21/22/23；该分项不是事后根据模型挑选。
- candidate SHA db17d68b80b237b34cb819167cba748b7118cf13e99c0d4fa6885062adf4846b；adopted SHA 3afa0089ff50ce9c8d06d881918e07aa095070d3a8cc6116e077eff5a4064704。[来源与审核统计](../results/D0-E14-preparation-v1.json)。

## 结果（跑完后填写，不改以上预测）
- 待推理；C01/C02仍L0，没有内部两个event或revision failure主张。


### 首轮完整结果
- 完整528原/派生raw输入，21.949s / .006097 GPU·h；masked target loss差1.07e−7 nats。88个无桥原reference与E13完整token IDs一致，2168词数值max差5.51e−5 bits、mean1.26e−6；输入/模型版本保持。
- **预登记7明确episode主交互**I_same−separate −2.6079 bits [−3.7788,−1.0900]；D_none −11.7096 [−14.8653,−8.6700]、D_same −11.2440 [−13.8886,−8.8043]、D_separate −8.6361 [−10.8183,−6.5973]。two-option在source内平均，n7，不把44/176样本当独立组。
- 全22源组同交互−2.1459 [−2.9844,−1.2897]。R绝对值同时报：无桥GP −7.207、comma +2.184；same GP −5.386/comma +3.783，separate GP −3.801/comma +3.223 bits。长coreNP与短ref不同，不能以raw符号单独作能力准确率；但GP/cue的词汇替代固定，强paired差不是whole-S2 mean≈0能否定的。
- [完整摘要](../results/E14-summary.json)、[config](../results/E14-config.json)、[CSV](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E14-scores.csv)、[E13同输入校对](../results/E14-baseline-reproduction.json)。变化更支持history/reference条件有区别的测量线索，尚不能主张event-specific机制，因为continued/began与同一/另一referent一起变化。
- 下一信息实验E15只加continued a separate，同aspect比较same/separate、同separate比较continued/began；若差来自aspect/presupposed continuation则会改变候选account，不扩模型或窗口。主张仍C01/C02 L0；这是待解释测量，不把GP存在叫novelty。
