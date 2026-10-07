# E88：晚到证据应回到动词还是名词？（2026-10-07）

- **状态：** DONE；生成器E431任何科学运行前改E88。
- **对应：** I06 / C06–C09 / P19；先前解释修订涉及早期动词的valence/voice/complement框架，首个核心pilot，不以先补齐论文证据为前提。
- **问题：** 只让早期V1源token看整句后文，是否比只让关键NP源token看后文更能恢复原关系？NPZ反身/互指、MVRR被动双宾语、NPS补语变化全覆盖；不只做17阳性条目。
- **数据：** 原E82完整892资格QA，由item ID取原E54同S/Q/Gold/analysis字段，原QA严格G2/native与模型三族Qwen3-8B/Gemma3-12B/Llama3.1-8B复用。所需干预词位置仅机械定位：原句中完整读出的有限V1 surface词表、发表元数据和精确cue同词映射；NPZ/NPS为V1后至disambiguator或relative-marker前的NP（去除up/off/down particle），MVRR为V1之前主语NP。程序assert词表候选唯一且在消歧前，全部词位置清单效果前留档；不新增自然度/语义审计。若定位有含混，仅对该缺失字段用Step Plan，不能猜；目前未发新API。
- **条件：** VERB_ONLY仅该动词word对应query rows可看Source全部keys；NOUN_ONLY仅该关键NP可看Source全部keys，余行保持因果。两种均看不到Q/答案/选项，源行任务信息不变；全层源内4D mask复用E54已验证实现。原CAUSAL与INSTRUCTION母E54按相同prompt SHA全缓存复用，不重跑；两readout/two mappings。新条件预计21408，机械资格实际数效果前登记。
- **主读数：** 原initial/final/all correct/p_correct与全注册Q joint；VERB−CAUSAL、NOUN−CAUSAL、VERB−NOUN；GP/cue/三构式全报。另输入-only source类型reflexive/reciprocal、MVRR/dative及Gold Yes/No分别描述，不靠效果选簇。冻结Source→analysis lexical cluster，bootstrap10000/seed88。
- **阳性对照：** 原cue/一句恢复；母prompt/Gold/hash核验；4D cause对母分数的固定首Source数值核验复用既有FP32阈值.001。Masks新增边只在Source，目标word原字节真实存在。原metadata如“lesson”误指noun而非learned保留并记录mechanical locator纠正，不改Q/Gold。
- **噪声地板：** 双mapping差、完整cluster CI；固定首Source数值校验，不扫层/词集合/强度。V1和NP包含token/新增edge数不同，记录而不假装预算一致；这是语义位置入口pilot，不单凭比较证明单位边效率。
- **混杂审计：** 非因果oracle是诊断工具，既有E54整源oracle未普遍修好，null可能OOD；不等于“没有verb frame”。裸stem单token、multiword verb/NP覆盖全部记录；不能把mask成功叫native隐含valence变量。E87表明常规QA真实错误保留，既有恢复对照满足行为范围参照。
- **决策表（跑之前写）：** VERB明显优于NOUN且原角色恢复/其他已正确关系保持→进入谓词重算idea方法pilot；NOUN较好→实体角色更新仍主要竞争；两者共同或不区分→本pilot未定位frame对象，不加层位网格；都破坏cue→工具分布变化，不能强讲机制。只凭探索迹象挑后续高信息量实验，不要求现在证明完整论文。
- **算力预算：** ≤3GPU·h，8独立H20 Q3/G3/L2，原离线FP32资产/eager，不碰他人服务。必须在2026-10-08 08:55释放（09:00人定硬截止）；每batch检查deadline，已独立systemd保障。原数据/输出外置E88；0不必要API。


CPU数据预检完成：151发表GP源组/302S/784QA，NPZ89、MVRR27、NPS35。缺失原physical disambiguator的1NPS源排除，原控制配套排除，不按效果选条目。独立unique same-word span能支持作者的clause reorder；先用monotone alignment误排65NPZ的预检v0保留，未有GPU效果时纠正。原S/Q/Gold/analysis字段与E54/E82全部一致。输入SHAfc606921c06ccddac080d8df14651aaecfe6df71a26e9ab27425561d5525c9e3，新增18816条件，0API；全部151位置清单效果前已核对，包含原metadata lesson误指词记录。

三族CPU6272新条件/族、全部baseline母prompt SHA预检通过。8卡PID3350586–3350593，18816条件已全部闭合；各分片4D因果对2D与母E54 LP最大差全0，FP32预算实际.468391GPU·h，完整分析器PID3368118。尚未读partial科学效应。


## 核心结果与自审

18816条件/.468391GPU·h/0API全闭合；map SHA3f4caff630e40b63e42fb68de2b183275e8345d6615e0a9de353bf0bd02e7945。[完整摘要](../results/E88-verb-frame-lookahead-summary.json)保留7560格、252joint及全部frame/Gold/edge/mapping，不按最好cell解释。

NPZ words initial VERB−NOUN Q/G/L −9.55[−15.73,−3.93]/−12.36[−19.10,−5.62]/−13.48[−22.47,−5.06]pp；名词入口比动词更好。NOUN−BASE +7.58[2.81,13.20]/+8.43[3.37,14.61]/+22.19[13.76,30.90]，final +.56CI含0/+2.81[.56,6.18]/+1.97CI含0。GP joint +7.87[2.81,13.48]/+8.43[3.37,14.61]/+15.17[7.30,23.60]；Gemma cue joint−7.87[−13.48,−2.81]保留。letters NPZ名词入口同样较好，但L letters mapping最高90%，不能称读出鲁棒完整能力。

17个initial GoldYes反身/互指关系：Q/G baseline及两oracle均0%；L baseline8.82%，NOUN17.65%，改变量CI含0。名词入口改善主要是撤销原不支持关系，未共同补出完整事件框架。MVRR无三族共同verb优势，L final words受损；NPS cue初始弱、不据null定位能力。V/NP边数与token数不等，不能叫相同预算的神经变量比较。

自审：**首个非因果工具未支持“回到动词就能修好”的简单I06版本。** 更有辨别力的候选对象是解除旧附着与重建论元解释的分离；不能把它立刻认证新机制。只再做一个语法frame信息EARLY/LATE对比，检验是需在编码时重算，还是后续读出能重建。C06–08L0/C09限定L1不变；探索idea不要求当晚完整论文证据，不继续mask/层位网格。
