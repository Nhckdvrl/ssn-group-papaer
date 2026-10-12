# Christianson et al. (2001) — Thematic Roles Assigned along the Garden Path Linger

**核心级别：PRIMARY ORIGINAL / 2026-10-12 主文重读。** [作者实验室提供正式PDF，40页](https://ferreiralab.faculty.ucdavis.edu/wp-content/uploads/sites/222/2015/05/Christianson-et-al.-2001_LingeringInterpretationsGP_Cog-Psych.pdf)，*Cognitive Psychology* 42:368–407，DOI [10.1006/cogp.2001.0752](https://doi.org/10.1006/cogp.2001.0752)。阅读了引言、五项实验的目的/设计/主要结果、General Discussion及Appendix 1材料选段；**未独立复算其ANOVA或重审每一项附录素材**。这篇是本workspace不可跳过的奠基作品，而不是只供引一句“人类也会GP”。

## 什么科学问题产生了这篇论文？

**AUTHOR-STATED**：此前主要看句子某词处的阅读时间或语法可接受性，默认完整解析要么修好、要么失败。作者关心的是：修订不完整时，人是否还能自信地构造一个混合解释，既懂后半句、又残留错误的旧论元赋值？

固定例子：`While the man hunted the deer ran into the woods.` 句法正确的依赖是 `ran(deer)`，而 `hunted(man, deer)` **不是由文本许可的宾语关系**。但读者仍可能基于世界推理认为男人猎的正好是鹿。作者pp371–372**自己明确承认语用推断并设计控制**。不能把我们的“三值蕴含问题”简单包装成首次指出这篇经典论文犯逻辑错误。

## 逐实验返回“尚未看到结果”的时点

| 实验 | 为什么前一个实验还不够 | 设计（原文） | 核心对照/观察 |
|---|---|---|---|
| Exp1a | 阅读难≠最终解释残留；若有残留，延长误解/世界合理性应否影响它？ | RSVP逐词、36人、42句材料；GP vs 无GP填先宾语；歧义短/长、最终事件plausible/implausible；`Did man hunt deer?`+conf 1–4 | GP短/长错误Yes 44.0/51.2%；无GP plausible短/长20.2/43.7%，说明问题本身有明显语用基线；比较交互而非把No当绝对truth |
| Exp1b | Exp1a的逐词速呈与记忆负担可能制造错误 | 整句自定步速、另36人、其余刺激保留 | GP短/长错误Yes28.6/43.7%，无GP plausible11.1/31.4%；降低绝对错答，但差别保留 |
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