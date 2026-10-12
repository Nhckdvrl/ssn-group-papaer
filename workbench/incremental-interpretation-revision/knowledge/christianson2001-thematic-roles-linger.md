# Christianson et al. (2001) — Thematic Roles Assigned along the Garden Path Linger

**核心级别：PRIMARY ORIGINAL / 2026-10-12 主文重读。** [作者实验室提供正式PDF，40页](https://ferreiralab.faculty.ucdavis.edu/wp-content/uploads/sites/222/2015/05/Christianson-et-al.-2001_LingeringInterpretationsGP_Cog-Psych.pdf)，*Cognitive Psychology* 42:368–407，DOI [10.1006/cogp.2001.0752](https://doi.org/10.1006/cogp.2001.0752)。阅读了引言、五项实验的目的/设计/主要结果、General Discussion及Appendix 1材料选段；**未独立复算其ANOVA或重审每一项附录素材**。这篇是本workspace不可跳过的奠基作品，而不是只供引一句“人类也会GP”。

## 什么科学问题产生了这篇论文？

**AUTHOR-STATED**：此前主要看句子某词处的阅读时间或语法可接受性，默认完整解析要么修好、要么失败。作者关心的是：修订不完整时，人是否还能自信地构造一个混合解释，既懂后半句、又残留错误的旧论元赋值？

固定例子：`While the man hunted the deer ran into the woods.` 句法正确的依赖是 `ran(deer)`，而 `hunted(man, deer)` **不是由文本许可的宾语关系**。但读者仍可能基于世界推理认为男人猎的正好是鹿。作者pp371–372**自己明确承认语用推断并设计控制**。不能把我们的“三值蕴含问题”简单包装成首次指出这篇经典论文犯逻辑错误。

## 逐实验返回“尚未看到结果”的时点

| 实验 | 为什么前一个实验还不够 | 设计（原文） | 核心对照/观察 |
|---|---|---|---|
| Exp1a | 阅读难≠最终解释残留；若有残留，延长误解/世界合理性应否影响它？ | RSVP逐词、36人、42句材料；GP vs 无GP填先宾语；歧义短/长、最终事件plausible/implausible；`Did man hunt deer?`+conf 1–4 | **Table 2 正确六列**：GP-plausible短/长44.0/51.2%，GP-implausible 20.2/43.7%，**non-GP control 21.4/31.0%**。此前错误地将GP-implausible的20.2/43.7列写成non-GP，已核原PDF表2。GP-implausible对non-GP的整体超额并不可靠（F1 p>.20，F2 p=.05），不可把所有条件说成同样有稳健GP效应 |
| Exp1b | Exp1a的逐词速呈与记忆负担可能制造错误 | 整句自定步速、另36人、其余刺激保留 | **Table 3 正确六列**：GP-plausible短/长28.6/43.7%，GP-implausible11.1/31.4%，**non-GP control 10.7/16.3%**。原卡也错把GP-implausible列当control；全句阅读改变了绝对水平与交互结构，不可只比较两个被混淆的列 |
| Exp2 | Exp1只能说子句旧对象仍被接受；也可能模型完全没有给主句找到主语。长度本身也混杂材料增加 | 24人、40items；问子句对象`Did man hunt deer?` vs 问主句`Did deer run?`；调换主/从句语序；ambiguous NP的head early/late | 子句问句错误率55.6%而主句9.4%。主句正确不意味旧子句错已撤回。语序对照使语用故事不能独占差别 |
| Exp3a | 选用可自由带宾语的hunt可被语用“正在猎就是猎这只鹿”解释；能否找到无法如此推理的lexical control？ | 16人、24items（一半Reflexive Absolute Transitive：dress/bathe等，另一半可选及物动词）；GP vs 倒装序控制 | RAT的无宾语形式隐含自指，而不能默认指句中另一个新名词；GP比非GP仍多错误Yes |
| Exp3b | Exp3a语序变动同时改变许多话语条件，可能是非GP控制太不同 | 新16人，同两类verb/24items，保持从句先行，只通过逗号制造无歧义控制 | RAT仍有明显GP额外错答。两个不同无GP控制收紧“只是一般世界推理”的解释 |

表中比率为作者表2/3/5的*特定问句与聚合值*；没有从百分比推计算机制，Exp3的整体结论原文表7/8及General Discussion给出。

## 这篇论文真正强的地方和留下的未知

**AUTHOR-STATED**：
- Exp2主句关系的正问句旨在区分“读者完全没有重分析”与“读者能恢复新主句但旧子句意义未清理”。
- Exp3a/b的RAT lexical manipulation明确专门处理“旧误读只是上下文语用补全”竞争解释：`Anna dressed`常需被解释为自己穿衣，与 `the baby dressed...` 不等价。
- 作者结论是对这些英语材料中**部分修订、旧角色效应**的论证，而不是现代神经网络中可独立定位的“旧解析内存”的证据。

**RECONSTRUCTED idea来源**：先从阅读时间之外提出最终理解这个对象（构念改变）→发现原问句语用效应→早期无GP控制→担心只剩“后句根本没建好”→主句正题→担心一般世界推理→RAT严格词汇对照→担心语序混杂→comma无GP。每一步不是补一张图，而是在压缩竞争解释集。这条实验链的研究技巧可以重新用于当前LLM，**但不能机械用相同材料加模型作为创新**。

**未解决（OUR-HYPOTHESIS，不是作者结论）**：
1. 子句旧对象错误的“Yes”是否来自单一融合内容还是两个竞争内容，论文无法直接分辨；Slattery2013用下游反身与次句处理作后续区别。
2. 主句Yes正确不等于整句所有必要关系都忠实，Huang/Ferreira2021、Ceháková2023展示更细的全局问题。
3. 用口头/元语言问句识别语义仍会受到题型影响，van Gompel2006 structural priming、Patson2009 paraphrase是重要独立读数。
4. 模型实验还要区分明示完整依赖/含糊代称/事实不蕴含；不能将作者回答合同里的“否认旧角色”解释成世界没有发生过那事件。

## 向项目证据链施压

E01短/长扩展在原研究里已有现成对照，但本项目的extension词面/问句和其他因素同变，不能仅凭同方向判定时间内生承诺。E29撤除自然GP后仍保留某角色效应，说明我们至少有一部分差异来自额外界面；Christianson使用**same information、不同GP path**的对照，值得比重复prompt寻找最好胜率。E103标签里的未绑定`something`更不能自动记为明确新依赖。研究应把“新主句能建立 + 原子旧绑定依旧受诱发 + 独立新用途能否用”放到同一来源的证据图中。

**来源/可核对页**：PDF pp371–374理论与反推，pp376–380 Exp1表2/3与讨论，pp381–387 Exp2表4/5与讨论，pp388–394 Exp3 表6–8与讨论，pp394–398 general discussion；截至本次未对出版勘误或每项刺激逐字再次核真。

## 2026-10-12 表2/表3原始列校准（对先前本日深读的更正）

对照作者正式PDF pp376与pp378的表头，**每表6列顺序都是 GP plausible 短/长 → GP implausible 短/长 → non-GP 短/长**；上述两个“无GP plausible”标签是抄列错误，本段与上方直接改正，不沿用旧错。Exp1a GP implausible vs noGP的总体差异F1(1,35)=1.72,p>.20、F2(1,41)=3.90,p=.05，不能用“GP各条件显著超额”论证普适旧解析记忆。原卡最重要的理论区分应立在**对应条件的配对差/交互**而不是漂浮的单个Yes百分比。

**可核对原文**：[正式PDF](https://ferreiralab.faculty.ucdavis.edu/wp-content/uploads/sites/222/2015/05/Christianson-et-al.-2001_LingeringInterpretationsGP_Cog-Psych.pdf)，实际校对Table2出版p376、Table3出版p378及紧接正文的控制条件比较。PDF网页截图服务失败，数值系作者PDF可提取的表格文字，尚未独立复算ANOVA。
