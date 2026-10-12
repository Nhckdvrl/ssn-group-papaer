# Patson, Darowski, Moon & Ferreira (2009) — Lingering Misinterpretations in Garden-Path Sentences: Evidence From a Paraphrasing Task

**PRIMARY MAIN VERIFIED 2026-10-12.** 正式发表于 *Journal of Experimental Psychology: Learning, Memory, and Cognition* 35(1):280–285，DOI [10.1037/a0014276](https://doi.org/10.1037/a0014276)。本轮实际读取[作者实验室公开的正式6页PDF](https://ferreiralab.faculty.ucdavis.edu/wp-content/uploads/sites/222/2015/05/Patson-et-al.-2009_GardenPathParaphrasing_JEPLMC.pdf)的摘要、理论动机、完整 Methods（材料、2×2设计、程序与人工类别编码）、Results Tables 1/2 与 Discussion；没有重跑participant原始数据，网页PDF截图缓存失败，数值基于PDF可读表格文字。2026-10-12前此卡仅是正式摘要；本卡现在**直接替代旧摘要笔记**，旧版在Git提交历史。

## 1. 真正的科学空缺：直接问旧关系本身可能制造旧关系

Christianson et al. (2001) 的 Yes/No 旧角色问题允许两个竞争故事：
- **A：** 人读完后仍持有先前不合法解释；
- **B：** 人读完时未必持有，但被 `Did man hunt deer?` 的问题重新激活或现场生成了旧解释。

van Gompel et al. (2006) 用 **下一句结构启动**避开了直接提问，但 priming 只说明旧句法的某种可迁移活动，仍**无法告诉我们原句最后被理解成什么**。所以AUTHOR-STATED，作者要用 **free paraphrase** 同时做到：不主动重述旧角色关系、还能检查最终解释中是否真的同时出现旧角色与新主句。

这不是“开放题比Yes/No更准确”这种平面主张，而是**替换对手解释所依赖的测量操作**；这种实验动作我们可以学习，但今天不应当成独有创新。

## 2. 受试者、材料、对照与类别定义

- 50位英语母语大学生；从Christianson(2001)取**24条自然GP项目**，每条分 ambiguous（无逗号）与 comma-disambiguated 两版；另72个填充句，每人合计96句，项目以拉丁方设计确保同一参与者不会重复同一素材的两版。
- 2×2 within-participant：歧义有无 × 动词类型：OT (optionally transitive, e.g. hunted) / RAT (reflexive absolute transitive, e.g. bathed)。RAT 无宾语形式有自指解释，不等于只是“受事省略”。
- 整句呈现，读完按键后句子消失再键入复述；指示不得直接复制原句或大幅删除主要动词短语。这同时提高表达要求，所以**自然自由叙述仍不是内部状态透明观测窗**。
- 评分 `FAILED`=仅叙述旧对象，遗漏主句；`PARTIAL`=同一歧义NP既作为旧从句宾语又作为新主句主语；`FULL`=保留主句且**不将**NP当旧宾语；`OTHER`=不可解释、重复歧义句、含糊代词等。两位助研对实验条件盲审，论文报告 interrater κ≈0.90，分歧经讨论解决（不能当盲审完全独立于 gold）。`OTHER`约4%。

## 3. 必须同时读实验组和对照组：全论文最值得保留的一张表

来自正式论文 **Table 2**（比例，按动词类型区分）：

| 条件 | failed | partial | full | other |
|---|---:|---:|---:|---:|
| GP / OT | .04 | **.69** | .23 | .03 |
| GP / RAT | .02 | **.74** | .19 | .04 |
| 逗号控制 / OT | .05 | **.38** | .53 | .04 |
| 逗号控制 / RAT | .04 | **.19** | .71 | .06 |

合并动词条件：**GP partial≈.72、逗号控制 partial≈.29**；GP full≈.21，对照 full≈.62。作者的歧义主效应：partial F1(1,49)=140.98、F2(1,23)=62.23（均p<.01）；full F1=112.36、F2=69.96。Verb-type×ambiguity的交互两类均显著；**在GP条件下 OT/RAT 的partial无显著差异，而在逗号控制里OT显著高于RAT**。不等同于“GP造成72%纯句法错误”。只把0.72当修订失败率、忘记0.29背景，是不成立的比较。

**AUTHOR-STATED最关键的自我限制（Discussion）**：逗号清楚消歧时并不发生真正的reanalysis，称这类输出为 `partial reanalysis` 本身是一种**命名不当**（misnomer）。对照下OT（如“man hunted, deer ran”）仍可因论元默认、世界知识或复述方式同时出现“hunt deer”。因此类别是**最终复述内容模式**，不是独立测得的内部 parser state；RAT对照低于OT正暴露这一点。

## 4. 将每一实验设计动作重建成竞争预测

1. **直接问句→paraphrase**：B认为错误源于旧关系由题目再次提及；去掉明确引导后旧关系应减少甚至消失。A预测仍有GP>control的旧关系表达。结果支持A的某个版本，但没有排除自然复述带来的词面联想。
2. **加逗号control**：若所有复述中旧关系表达都来自句末词汇的常识补全，GP和逗号控制应相似；但差异约.43，说明GP操纵新增影响。*重要*：逗号控制本身.29说明语用/输出本底巨大，不能把全量都解释成GP机制。
3. **OT与RAT交叉**：一般可选及物的世界推断应让OT在无GP时也更“partial”；RAT必须回收为自指。实际GP两组相近，对照差别明显。它排除了“所有GP效应只由OT语用补全组成”的简单故事，也表明**同一表面类别对应不同成因**。
4. **FAILED与PARTIAL分别报告**：若仅是“完全没有解析后半句”，FAILED会较高；实际FAILED约2–5%。自然生成同时包含新主句和旧关系，与纯解析失败的区分较强，但不代表每条事件的全局关系已独立验证。

## 5. 哪些结论要谨慎，哪些真的影响我们？

- 一条partial复述的句法内容不等于“模型内部两个完整解析树并存”；被读数确认为最终*表达*，并非神经保存位置。
- 所有成功类别互斥，做one-vs-rest ANOVA时比例**不独立**，作者明说。不能按4类独立二项实验的样本量求CI。
- 语用/表述差异并未消失：该实验的 `OT/Control partial=.38` 就是重要的 **negative-control background**，不应在综述或实验里隐去。
- 对我们 E103/E107 直接启示：`something`、代词、依赖不明导致 `OTHER/AMBIGUOUS`，不能只看是否否认old便判fully recovered；更根本地，**即便标注称“partial”也不能自动解释为一种特定因果失败**。独立语义内容契约与自然对照先于score优化。

**可利用的高信息量方法**：预先在**同一个源ID**里编码明确old/new内容；对每个条件先取原生输出，自然表达类别、outcome以及matched unambiguous背景同时报告。强迫候选logP若与自然池中的表述类别不同，不能合为同一机制主张。下一层必须区分“old被任务再激活”与“产生了两个不相容的局部解释”；只换答案模板不会自动完成这种鉴别。

与邻近工作：[Christianson 2001](christianson2001-thematic-roles-linger.md)、[van Gompel 2006](vangompel2006-garden-path-priming.md)、[Slattery 2013](slattery2013-competing-representations.md)、[Ceháková 2023](cehakova2023-diverse-reanalyses.md)。