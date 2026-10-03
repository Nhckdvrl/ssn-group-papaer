# E38：原projection / 人类先验与speaker certainty驻留

- **状态：** DONE
- **类型：** REPRO / D1–D2；不为idea配额硬挂hypothesis
- **对应：** C02/P02/P09；读数可识别性与交际证据条件使用
- **问题（一句话）：** 原NAACL2025的背景事实先验与predicate影响speaker commitment的结构，在现代open endpoints/真实stage与同family入口下是否仍存在，还是知识或elicitation主导？
- **设置：** pennydy/llm_belief @ad2c36d75f9d14d192d193f7db919035c41619bd；main certainty原1680（20items×21verbs×2prior×2embedded）和原prior80，source不改。八已下载端点Q25Base/Instruct、OL3stages、Q3-4/8/14，完整common tokenizer与actual输入SHA；裸入口是明确声明的原system+user+Answer序列，chat是nativecommon role结构；FP32/noTF32单sequence无padding。原system typo、prior_info重复（源CSV已含一次、源码再加一次）照原保留，不擅自clean。原greedy/max_new_tokens5，thinkingFalse；完整raw/IDs/逐tokenLP保存。
- **读数：** 原0–1 numeric scalar rating（生成，非logprob读知识），固定严格parser整串numeric0–1，invalid单列。按item cluster、prior actual text/verb分开，p/not_p/polar保留；原human仅p20verbs，不虚构negated/polar norm。完整预测前80/1680唯一key、target/question/实际fact对齐human/source，所有同familyactualtoken SHA必须相同。E38不即时复现AIC/RSA必要性结论；原RSA180只有指定子集，可核对后另卡独立held-out预测比较。
- **阳性对照：** 原公开GPT输出同source keys/count与原mean可程序重建；40human prior与projection factual文本核对，sourcehuman/fact/category范围对齐，不按high/low label硬配错误行。首末原生成输出/LPrepeat相同（LP<.001），首末原源prompt完整SHA；不是新annotation。
- **噪声地板 + MIE：** 无抽样随机种子（原temperature0）；重复首末只校对仪器，不当独立实验replicates。20itemcluster2000bootstrapseed0，scale/stage平均跨谓词会混淆，不统一pool criterion。若读数invalid多或人类norm不能对齐，只记录可用性，不称能力下降。没有最小paper效应预设。
- **混杂审计：** 原stimuli.py随机speaker/holder名字未seed，固定发布CSV不重新生成。certainty/belief两个发布版本名字不同，不把两者直接prompt唯一变量对照；本轮只main certainty。prior_rate Josie高/低事实与projection/human相反，保留源字段并增加按actualfact的human-key，不silent改源或拿错误label作Δ。5token跨tokenizer非等compute，仅原endpoint协议迁移；短截断invalid不能算语用错。人类世界先验不等于speaker知道背景事实；parent显式想象设定，不能推真实沟通行动。
- **决策表（跑之前写）：** A先验及predicate稳健、human贴近→保留强成功baseline，不编缺陷；B原先验可测但speaker readout不可用→归elicitation/任务不识别，不knowledge-use finding；C stage/scale影响不同证据作用但入口稳定→候选observations须readout/独立材料/ownership再审；Dsource/generation gate失败→保留失败、0claim，不改新阈值挽救。
- **算力预算：** 每endpoint一GPU，最多八独立锁，1760×2interfaces=3520生成/model，总28160；原5token无judge/API/training，CPU源预检后接E35空槽。预计<8GPU·时，实际见config wall_seconds，不为idle重复旧结果。

## 结果
尚未GPU预测。源审计、完整预检与公开cache parity先完成；原R multilevel主回归/180RSA未复现，不能引用其结论为我们finding。

跑前1760源/840原human mean/fact全量匹配与八endpoint actualtoken parity通过，Josie四prior行源label仍保留、人类按actual fact对齐。公开三个certainty cache1680prompt逐项一致；prior GPT3.5/GPT4源一致，GPT4o prior源码prompt有差异（完整ids已audit），不可称全部三API原prior精确parity。程序只读source，不执行OpenAI client；原asset/source与strict parser已冻结。

2026-10-03 完成：八端点各3520，总28160生成，source/input/numeric repeat gates全通过，见 results/E38-projection-parent-summary.json。Q3 chat prior MAE4/8/14=.1993/.2012/.1269，projection=.1849/.4278/.4024；4B projection764/800为0.50常数，低MAE不代表能力。原human processed7436=286×26，含1716MC与5720目标；不是源错误。原5token结果不能直接排名：E42证明Q3裸入口840/840 human numeric均延长成prose；Q25Instr裸119同样无效，全部原文件保留并降级相应解释。没有d′/统一criterion finding，C01/C02仍L0。
