# Lingering misinterpretations ... arise from competing syntactic representations（2013）

[作者机构托管的出版PDF](https://faculty.wcas.northwestern.edu/myo507/Papers/SlatteryEtAL_GoodEnough_Published.pdf)。实际读两实验rationale、methods、results及discussion；appendices仅检查有完整材料。版权©Elsevier2013/all rights reserved，不当成MIT数据发布，不复制全文进git。

1. **形态：** 两个互补实验，分别测新结构建立和旧解释对自然后文的作用。
2. **压力：** GP错答可能来自未建立新parse，也可能来自旧解释未删除；理解题可能再激活旧命题。
3. **动作：** E1同句下游gender-mismatch reflexive；E2次句reflexive事件承接，避免把所有证据放在显式问答。
4. **来源（DOCUMENTED）：** Christianson lingering结果与Good-Enough/serial-parallel reanalysis理论的分歧。
5. **增量：** 新parse功能证据 + sentence-external hangover，且第二句开头和末尾是内部region控制。
6. **方法：** E1共32项目、GP/comma×definitional gender match/mismatch；E2共24项目、GP/comma×初始对象plausibility，四Latin-square lists。E1reflexive go-past/total mismatch在GP和cue均见，交互不显著。E2关键次句first-pass为341/301ms（GP/cue plausible）、310/316ms（implausible），不是一般全句uniform slowing。
7. **限制与竞争：** 不显著交互不证明完全同等重分析；E2语义/旧结构trace与memory机制仍竞争。作者讨论LTAG overlay、SOPARSE与记忆命题，未给唯一机制。局部binding正确也不充分证明全句语义图正确，后续Huang/Ferreira2021与Ceháková2023正讨论此事。
8. **可迁移动作：** 用有功能依赖的后文区分“新解释可用”和“旧解释仍影响”；region特异性/合理性对照排除global slowdown。
9. **对我们：** “后续处理还有旧解释影响”在人类已明确拥有，Cao2025已测LM downstream binding。可用原材料作为后续readout基线，不能换Qwen即叫novelty；当前E11先确认role引用是否有效，之后从证据类型、传播边界和实际后果找增量。

## 2026-10-07复读补充（不计新增论文）

证据：[作者接受稿](https://eprints.bournemouth.ac.uk/22639/3/SlatteryetalJML3final.docx.pdf)主文pp1–38完整，后置长材料表未全面核对；[发表稿](https://ferreiralab.faculty.ucdavis.edu/wp-content/uploads/sites/222/2015/05/Slattery-et-al.-2013_GardenPathCompetingRepresentations_JML.pdf)两实验与讨论交叉阅读。接受稿SHAfd343f67815cf4a8b5e7a0b6d939ec442b1ef09d871f6c5b3350339b06006df8。这是人类机制近邻，不能直接外推为LM机制。

1. **idea来源（RECONSTRUCTED）：** Christianson发现误读持续→究竟没建立新结构还是没有抑制旧结构？→借Sturt reflexive binding的在线gender mismatch敏感性作为新结构功能用途→再接一个只与正确解释相容的第二句，避免问旧误读命题主动激活它→结构建立与语义清理拆成两项过程。
2. **规模与方法：** E1 24人/32项，GP逗号×匹配/不匹配2×2，possessor名字始终性别匹配，head kinship改变；reflexive在第二VP conjunct避免直接消歧spillover。E2 28人/24对，GP逗号×初始宾语合理性2×2，第二句相同。EyeLink1000；first-pass/go-past/total分别检验，没有真实神经路径切断。
3. **证据：** E1 reflexive gender成本出现在GP/cue，ambiguity×gender未显著；GP firstpass单侧simple effect不全可靠，不能把interaction null当精确等效。E2第二句critical firstpass结构×合理性交互F1 p<.05/F2 p<.01，只plausible GP慢，go-past/total未显著；第二句开头无明显结构主效应。没有直接GP理解问句：E1问句不问reflexive/歧义，E2仅约1/3trial一般问句。
4. **机制边界：** 作者由reflexive binding推完整结构，再推旧树未清理；这是功能诊断与竞争模型解释，不是每trial全parse显式认证。自己的discussion仍保留LTAG overlay、记忆绑定错误、noisy-channel源字符串不确定性多种解释。不能把它当“人类一定有全局正确解析”的因果定理；Huang/Ferreira2021随后质疑局部树是否足够（该文全文尚未取得，只摘要/发表页节选）。
5. **与近邻距离：** Good-enough不是简单“不做结构”；Sturt2007已有semantic persistence，增量是修订后句内结构用途与跨句语义用途分离。LTAG/自组织parsing/记忆绑定/Levy source uncertainty给出的不同延迟预测是理论背景。
6. **对我们：** 建立新关系、撤回旧关系、正确选择后续使用是不同对象。E70不能由原No未表达就叫完整修复；E71不能由正确P1与错误P2共现就叫表达干扰，必须看cut是否改变后续。一般“local trees未协调成global parse”有人类近邻，增量要来自LLM自然修订的具体因果规律与后果，不关掉领域。
