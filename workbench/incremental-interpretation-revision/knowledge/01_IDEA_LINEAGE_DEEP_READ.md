# 论文精读与实验设计逆向推演：为什么是这组实验？

**本轮实读范围（2026-10-12）**：Ceháková & Chromý 2023 PLOS正式全文的引言、材料、Exp1–5及总讨论；Maina-Kilaas & Levy arXiv2603.23624v1 HTML §1–Conclusion；Amouyal et al. 2026 作者HTML v1 的引言、§2–4、结果表与附录选段，正式ACL PDF已读取表1/前部但图片截图接口失败，正式版方法差异尚未逐页核完；Hanna & Mueller v1 HTML §4–6、附录前部（原知识库还有正式版部分核对）；ABBEL v2 HTML 主文、方法/对照段落（原卡已记录更广附录/代码范围）。Slattery 2013 的期刊网页实验设置/结论并同历史主文卡交叉读，**不冒充今次完整逐页重读期刊PDF**。本文不把迁来的其他80余篇计入本轮新精读。

**补充原始经典主文**：本轮已取到并读取[Christianson 2001正式40页PDF](christianson2001-thematic-roles-linger.md)的动机、5项实验设计/关键表/讨论；6年后van Gompel的priming及Patson2009的paraphrasing仍只读正式摘要，不冒充全文。

## 奠基链补全：Christianson(2001) → van Gompel(2006) → Patson(2009)

最初的“旧误解在读完后残留”并非只凭一句随便问出来的Yes/No：2001原文对语用推论自有承认，也做了GP/noGP、head位置、主句/从句两个正负问题、RAT反身动词与逗号/语序控制。其真正残余不确定性是语义内容是否完整、输出题型是否诱导旧读法、旧解析是否跨任务产生功能后果；因而2006 priming和2009 paraphrase在**更改测量仪器**上有知识增量。详见[2001主文深读](christianson2001-thematic-roles-linger.md)、[2006 priming](vangompel2006-structural-priming.md)、[2009 paraphrase](patson2009-paraphrase.md)。这条旧谱系必须用于校准我们的创新距离：仅用多问句/复述来发现残留，不是新idea。

以下的 IDEA SOURCE 分 AUTHOR-STATED（作者明确写）和 RECONSTRUCTED（我们对实验设计来源的反向推理），后者不是作者自述。

## A. Slattery et al. 2013：同一种错误可以来自两种完全不同的失败

[正式期刊摘要与实验节](https://www.sciencedirect.com/science/article/pii/S0749596X13000247)｜[历史主文卡](slattery2013-competing-representations.md)

**上一个共识与认识缺口。** Christianson等的提问表明旧误解会残留。但观察到“读完后说错了”无法区分：
- H1 重分析没建立合法完整结构，读者只有碎片；
- H2 已建立正确结构，却未能彻底清除旧结构/旧语义。
两者对普通 yes/no 都预测错误，却对后续结构约束预测不同。

**为什么 Exp1 不是再做一份问答？** AUTHOR-STATED：把歧义×反身代词性别一致性组合成2×2设计，在消歧后位置测gender-mismatch的第一遍眼动成本。若读者确实建出了句法许可的依赖，反身代词应该对正确主语的性别敏感；若只有不连贯局部片段，难解释稳定的句法许可效应。这把“最终正确结构是否形成”从旧误解读数中独立出来。限制：眼动结构敏感性并非整句话语义完整无缺的形式证明。

**为什么还要 Exp2？** 仅证明Exp1的新结构可用，不能排除旧读法已经完全消失。因此让第二句的阅读依赖前句的错误语义，对照旧解释所预测的干扰。看到下游局部干扰、而非一般性持续慢速，支持旧痕迹对后文的影响。RECONSTRUCTED：Exp1服务于新结构存在，Exp2服务于旧解释仍可干扰，二者交集才让“竞争表征”变得可识别。

**若结果相反该怎么办？** Exp1无选择性匹配效应但Exp2存在旧意干扰，更支持失败修复/碎片；Exp1成功Exp2无干扰说明旧意未必残留；二者都成功也仍不能断言旧痕迹以独立神经实体储存。对我们的教训：不能拿两个自报问题的不同百分比冒充这组证据结构。

**反向近邻**：[Huang & Ferreira 2021](https://doi.org/10.1016/j.jml.2021.104288)以在线阅读和按问答是否正确进行条件化，认为合法局部结构不一定能形成忠实整体解释；对Slattery的“完整重分析”并非简单重复，而是挑战该推断在不同材料/层级的普适性。

## B. Ceháková & Chromý 2023：真正不够的不是更多均值，而是对错误种类的可观察性

[正式完整开放文章](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288817)｜[原卡](cehakova2023-diverse-reanalyses.md)｜[数据与R代码](https://osf.io/98g26/)

**认知压力**：Christianson式持久旧分析、Slattery式新结构完整+旧记忆，以及Huang式局部而非整体重分析都能解释一些理解题失误。作者明确指出，聚合均值和单一 yes/no 问题无法判断错在何处。

**不是“四个总实验”**：实际编号 Exp1 是**70人接受度预试**，确保新捷克语形态歧义刺激本身可理解；Exp2–5 才是四个主要理解实验。其关键变量不是英语NP/Z：捷克语同形的宾格/与格名词在后来真正宾语出现时，需要重新绑定原名词的格及所有者/受益者关系。若只写“GP是否答错”，会丢失最珍贵的具体语义结构。

| 步骤 | 新改变的未知 | 因而需要的新读数 |
|---|---|---|
| Exp1 acceptability | 无歧义版本会不会本身难懂？ | 基线接受度；否则后续差异不归因于garden-path |
| Exp2 整句×yes/no | 旧宾语错配之外，真宾语、与格解释各能否正确？ | 三类独立问题，而非一个No |
| Exp3 逐词×yes/no | 表达失败能否与消歧时的加工压力相连？ | critical region + spillover RT；与最终答案分开 |
| Exp4 整句×open | yes/no错误背后是旧宾语替换、没说够、不知道、两种混在一起吗？ | 自由描述与错误类型，人工规则一致 |
| Exp5 逐词×open | Exp4的类别会不会只是整句呈现/回视造成？ | 交叉呈现方式与题型，回到具体失误 |

**关键结果/边界。** 消歧区RT变慢、旧读法残留有证据；但正确新关系、替换错误、无法确定、不充分表达在不同问法的分布不相同。Exp3在线RT里歧义×animate interference不显著，不代表后一问答中不存在干扰。Exp4/5的所有者问题可能比旧错误问题更难，且不同问句类型改变缺省/替换的比率。作者不把全部错误折成一个处理机制。

**对E103/E107的直接提醒**：先在语义层说明完整正确关系包含什么，再编码“错误旧角色”“正确新关系”“省略/未绑定”“不确定”“语义混合”；看问句/自由输出的条件分布，不能把 unspecified 自动叫做 recovered。这里的设计动作比“人类也有GP”重要得多。

## C. Maina-Kilaas & Levy 2026：选择能裁决理论的测量位置

[完整作者v1 HTML](https://arxiv.org/html/2603.23624v1)｜[原卡](mainakilaas2026-digging-in.md)

**两组竞争理论**：动态自强化解释认为歧义保持越久，修订代价越大（positive digging-in）；surprisal解释认为只有词分布改变才能改变代价，可能是反向趋势。此前后到消歧词往往恰好是句末，RT可能含 wrap-up 而非实时承诺强度。

**实验生成逻辑（RECONSTRUCTED）**：若仅复测“延长歧义”，结果仍被句末混杂解释。Exp1用Maze减少spillover，30项、191招募/167通过筛选，并报告comma与object的不同基线；但其finality仍部分between item。因为Exp1暴露finality差异，Exp2转回原始SPR范式，用36项与233招募/225保留，句末/非句末×长短×歧义×消歧方式内对比，并用16个LM的surprisal拟合 filler RT 后预测 critical，避免把计算预测等同人类结果。

**读取结果注意**：Exp1 critical ambiguity×length 11.71ms、posterior方向概率70.83%；非句末为反向小量且不确定，句末正趋势。Exp2非句末反向趋势而非稳健正digging-in；三因素交互的pd=96.63%，未达到作者97.5%阈值。作者说的是“没有找到强的实时digging-in证据”，**不是形式证明人类没有时间积累承诺**。LLM预测在GP critical普遍低估人类RT；句末wrap-up仍是可争论解释。

**本工作最值得学习的动作**：当一个经典效应被认为支撑某理论时，先找出“该指标对理论是充分的吗”，再选一个会改变竞争理论预测方向的因子。对我们的E01/extension/then：不是继续增加长度，就能称作解释锁定；先把长度导致的后续词概率、语义变化、句末性与测量负担拆开。

## D. Amouyal et al. 2025→2026：统一标尺之后，仍需定义构念

[ACL2025](https://aclanthology.org/2025.acl-long.403/)｜[ACL2026](https://aclanthology.org/2026.acl-long.1040/)｜[2026作者v1全文](https://arxiv.org/html/2510.07141v1)｜[旧25卡](amouyal2025-garden-path-humans-llms.md)｜[旧26卡](amouyal-2026-processing-difficulties.md)

2025论文把GP理解问题拆成结构复杂度、动词论元需求和plausibility预测，并增加释义/图像等其他输出任务作关联验证。2026论文改问更宏观的“七种结构在人和不同模型里是否难得一样”：四类GP+double-center+interference+depth-charge，31模型、五家族。同项配一个目标句和更易基线；人类5380条单次实验回答（每句题10个参与者），逐词400ms、空白100ms、问句限5秒；LLM为8个few-shot提示变体（思考设置受成本限制只有一个提示）。**两者在任务对象与呈现方式上仍有差异**，统一正确率不是统一加工算法。

定量例：文中GPT-5四种GP平均46.8%，非GP平均93.7%（作者给定的关闭/低thinking条件），thinking可显著改善某些模型/结构；不能把这数字解释成所有GPT-5输出设置均“半数不懂”。论文的“GP更像人类因为模型需要扔掉旧解释”明确是推测，没有直接干预旧解释记忆来识别该机制。

**我们必须额外做的语义审计**：作者Table 1把 “While the man hunted the deer ran into the woods.” 后的 “Did the man hunt the deer?” 记为No。文本没有断言他猎鹿，并不逻辑蕴含他没猎鹿；同样“The chef hired last month worked overtime”不推出厨师一生从未雇过人。No在测试合同里通常应解释为**文本不支持这个关系**。这不等于论文的基线/GP差分无意义，却限制以这些Yes/No推断内部排斥/矛盾的力度。2025旧卡已有这项 caveat；2026新统一数据也需要逐构式按 entailment / contradiction / unknown 审查，不能因为会议正式发表就把标注语义自动当自然事实真值。

**可迁移设计**：用严密的baseline+跨任务检验阻止小样本偶然效果；同时给每种构式记录具体要恢复的依赖，避免“更大benchmark”掩盖机制混杂。

## E. Hanna & Mueller 2025：从行为定位到局部功能因果变量

[NAACL正式版](https://aclanthology.org/2025.naacl-long.164/)｜[arXiv v1 HTML](https://arxiv.org/html/2412.05353v1)｜[原卡](hanna-2024-gp-mechanisms.md)

作者的问题不止GP分数：P1 模型使用结构特征还是启发式，P2 有没有多解同时竞争，P3 早期局部特征在消歧后是重新计算（reanalysis）还是加以修补（repair）。通过模型的下一词偏好定义早期解析倾向，再定位可解释特征、干预输出，最后问这些特征能不能支撑另一个QA任务。

**三个方法步骤是互相防止过强推断的**：可解码性→预测用途的因果贡献→消歧后问答复用。作者§6的操作化以特定选定特征是否在后续影响为标准；该选定集合不充分复用，不等于所有内部表示不发生修订；Pythia QA接近constant答案也限制了它的负结果价值。其“repair/reanalysis”定义是针对 feature reuse 的 operational hypothesis，不应与心理学上认知重分析的全部含义画等号。

我们E55/E64替换whole residual而非一组SAE特征；效应的存在不能直接支持/驳斥他们的细粒度机制。想研究更深一步，必须定义一个能跨用途中产生选择性变化的**语义关系**，而不是先扫描最有响应的层再取名。

## F. ABBEL v2：如何从“信息瓶颈”长出训练目标，同时为什么E101的解释太快

[作者v2 HTML](https://arxiv.org/html/2512.20111v2)｜[带代码核对的原卡](lidayan2026-abbel.md)

论文先比较Full Context、FC beliefs、只有belief的摘要路径，在五种环境中区分“多一次调用”与“记忆缺信息”；再把每步更新belief与选action分离，定位遗漏/错误更新/冗长等不同瓶颈。只有识别信息损失是问题，作者才发展重建式或域特定grader和PBP。这是**问题诊断→可监督中介→方法**的生长过程，不是先发明一个reward再寻找适用场景。

信息重建打分是给定新旧belief、动作，重建**最新观察**，其概率分解含posterior与prior的差；作者代码卡进一步指出伪代码的sum、clip与实现的归一化/截断有差异。E91–107是冻结模型的类比诊断，未训练ABBEL，也没有证明真实agent中错误belief更高回报。

**尚未闭合的真正科学问题**：在同一个完整、自然生成的候选池中，正确替代依赖的缺失来自生成器还是选择器？若来自选择器，具体目标中的信息增益、词面概率、长度和旧belief先验哪个承担可区分的作用？真实action结果是否受害？未分开这些对象不能说“发现reward复制旧错”。

## 从论文生长动作提炼的设计原则（不是固定实验菜单）

1. Slattery：先挑出两个假说**会不同**的功能后果，再各造测量；单个正确率不够。
2. Ceháková：先确认错误本体是混合类别，而非用平均数押一个单一机制。
3. Maina-Kilaas：把指标中可能伪装为理论效应的**时间/测量条件**转为实验因子。
4. Amouyal：共享问题与基线可提高比较性，但不替代对 gold 语义的逐项校验。
5. Hanna：因果干预的粒度决定结论尺度；输入有信息、模型可用与实际使用不同。
6. ABBEL：从下游失败回溯到哪一类**有后果的中间内容缺陷**，之后再设计训练信号。

进一步阅读名单及缺失附录见 [阅读议程](05_READING_AGENDA.md)。