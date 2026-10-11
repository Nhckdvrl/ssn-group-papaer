# E85：从句法旧关系到词义旧解释的现成材料迁移（2026-10-07）

- **状态：** DONE；生成器E431在任何模型结果前改本线E85，非POST-HOC。
- **对应：** I02 / C06–C09 / P17。依据EXECUTION_BRIEF §3 E62菜单扩充同一“先前解释能否随晚到证据修订”的画像，自主模式自审后执行，不开新workbench/改状态。结构GP仍是主问题。
- **问题：** 当前结构GP的修复和保持不能共同成立，是否连自然词义garden-path也同样不能恢复？若词义在强模型上容易而结构仍难，下一机制要解释具体功能差异；不能从平均难度直接命名架构瓶颈。
- **数据：** Blott/Rodd/Ferreira/Warren2020已发表、人类norm与96人实验的48句框架，每框架原coherent ambiguous/unambiguous、anomalous ambiguous/unambiguous四noun版本，全192句；原PDF/Appendix I现成缓存。程序提取核对48编号/4nouns/原region与两dominance norms，仅移除版面换行与ROI斜线；不改措辞/原coherence gold，不新造问题，不API重审。原bridge/region的人类分析排除只备注，全48句输入保留。
- **任务：** 原Meaning Coherence Judgement：句子是否make sense，普通意义兼容性；保留原Yes/No gold。它不是Source显式蕴含或直接word-sense金标，不能与E82正确率直接当同一能力量。
- **条件：** DIRECT与既有ONE_RECOVER一句恢复指令（R8），两readout words/letters、两mapping。原模型native closed非thinking入口；Qwen3.8-27B/Gemma4-31B-it/Ministral3-14B三个族，用E82本地核验资产/runtime。0API，原192数据全跑。
- **主读数：** 每族/四原条件/两格式correct与p_correct、RECOVER−DIRECT；coherent ambiguity gap=unambig−ambig的paired cluster CI与恢复变化；另报所有anomalous保持、mapping flip。按48原词框架bootstrap10000 seed85，不筛native错误/优势种子。
- **阳性对照：** 原coherent unambiguous与原anomalous两条件；母task语义连贯标准而非反事实世界否定。源PDF SHA844420d9d1ee8c939c7c18953c9f38d99ca387c347d51381320f10e73362aabb锁定；固定输入字典序首Source的prefix/full仪器，差≥.001时全分片统一full-sequence评分；最终重复LP完全一致，候选/mapping一致。
- **噪声地板：** 两mapping flip、paired95%CI；中等norm词与原桥牌词完整保留，不从效果后筛dominance。
- **混杂审计：** 人类norm不是模型最初一定承诺的证明；coherence任务成功不证明具体词义状态建立。E82结构QA与本任务输入/读数不同，跨域差异仅定位，不能自动认证“词能改、角色不能改”。自然词义不恢复已有Blott，后到计算已有Zeng，换数据本身非novel。
- **决策表（跑之前写）：** 三族词义gap很小且结构错误仍在→宽“因果架构不能修订”不足，选实际功能差异追问；三族词义也有gap且一句恢复不了→需要共同后到证据机制而非独有角色故事；仅prompt恢复/读数异质→保留功能/任务边界，不扩prompt/防御控制；不单独认定idea。
- **算力预算：** ≤1GPU·h，共4608新条件，3族/8独立分片按E82空槽复用，BF16计算/FP32 logsoftmax、eager/seed85，Ministral原作者FP8 dequantize到BF16；模型/源缓存复用，raw外置E85，不进git。

## 结果

先写卡，接下来仅程序化提取既有原材料与输入检查；无科学效果，C06–08L0/C09限定L1不变。

CPU三族1536任务/族全部通过，max tokens Q93/G95/M605；全部48表行与四noun/两个norm核对，192句data SHA50ada5e61baa4ade9bd0def26780f25145b200e82082b07af90b9899d173ca6c。8卡全4608条件启动，先数值仪器后评分，0API。PID 2996912,2996913,2996914,2996915,2996916,2996917,2996918,2996919；published bridge/item23 ROI保留，不从模型结果筛选。

### 完整结果与自审

三族8卡/4608新条件完成，.266861GPU·h、0API，180完整格全部读、48mapping/48长度行已核对，原48框架192句/gold不改。map SHA011ac4e742f945c22b7e0d99110c1514a5c376b33872ae222e72f16b41686b76，data/sourcePDF/model/config/raw与仪器引用齐全。全部分片按预注册统一full_scores，prefix/full最大Q .207744/G1.906697/M.122223、最终重复LP全0；不是prefix一致<.001。

DIRECT coherent ambiguous correct Q/G/M +57.29 [+42.71,+70.83] / +65.62 [+52.08,+78.12] / +42.71 [+29.17,+56.25]%，原unambig +95.83 [+89.58,+100.00] / +94.79 [+88.54,+100.00] / +72.92 [+60.42,+84.38]。配对歧义gap +38.54 [+23.96,+53.12] / +29.17 [+16.67,+41.67] / +30.21 [+14.58,+45.83]pp，三族都明显存在；letters同向，不能再预设词义容易修而角色独有困难。Min unambig只有72.92%，基线弱位同时保留。

ONE_RECOVER−DIRECT coherent ambiguous correct +3.12 [+0.00,+8.33] / +15.62 [+6.25,+26.04] / -1.04 [-6.25,+5.21]pp；anomalous unambig -5.21 [-11.46,-1.04] / -16.67 [-27.08,-7.29] / +0.00 [-4.17,+4.17]，anomalous ambig -6.25 [-12.50,-1.04] / -28.12 [-39.58,-16.67] / +3.12 [+0.00,+7.29]。Q/G提升部分真连贯句同时损真正异常句，M没有可靠恢复。不是共同选择性修复；意义连贯任务不能认证具体词义或与E82直接等量比较。

当前最好三句：自然词义和结构GP都能出现晚到证据未充分使用，困难不独属角色关系。恢复指令有不同任务下的决策倾向与损伤，不足单独定位源编码故障。下一只有一个核心E86：同原Source/Q换普通理解判定，并用原T3可接受金标检验输入是否被否定；严格G2与一句恢复E82全部复用，0数据修改/0新API，不扩prompt网格。C06–08L0/C09限定L1不变，尚无合格idea，无需人决定。
