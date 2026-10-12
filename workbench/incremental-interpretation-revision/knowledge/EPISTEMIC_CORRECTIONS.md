# 关键科学认识变更账｜不是“仓库已经更漂亮”，而是原来的想法哪里错了

> 一条已被纠正的论断不得继续通过旧卡的“下一步建议”驱动GPU；原始材料与脚本必须保留以便追溯。此表由本次2026-10-12原文再读+之前实验审计形成，**不是把103张卡全部重新复算**。

| Claim | 历史/原误判 | 原文/实验迫使何种更正 | 仍不能推得什么，研究后果 |
|---|---|---|---|
| H-C1 基准问答No | “旧No标签不等于世界not R，所以前人普遍没注意gold问题” | [Christianson 2001](christianson2001-thematic-roles-linger.md)原文pp371–372就说明语用补全，并用RAT/noGP/主句问句控制；Amouyal问答仍须区分source-entailed与世界false | 审语义很重要，但别把“首次发现前人gold错误”包装成研究贡献 |
| H-C2 Garden path后的结构是否完整 | “正确主句+错旧句=一定形成完整一致的新语义” | [Slattery13](slattery2013-competing-representations.md)测局部功能，不认证全句每条依赖；[Ceháková23](cehakova2023-diverse-reanalyses.md)qcor/qmis/qpos不同 | 回到完整语义图与多类别输出，不用单项QA决定机制 |
| H-C3 Digging-in延长 | “更长歧义必定导致更强承诺” | [Maina-Kilaas26](mainakilaas2026-digging-in.md)：原卡SPR24项为**错误**，已改为36；长度交互受critical是否句末影响，非句末未显示可靠正效果 | E01 extension不能叫时间自强化效应 |
| H-C4 Ceháková实验数 | “论文只有4个编号实验” vs “五个主体实验” | 正式PLOS包含**Exp1接受度pilot、Exp2–5四个主要处理实验**；摘要称四个处理实验 | 不把pilot当主结果，也不漏掉构造有效性的前置试验 |
| H-C5 检索模型数字 | “95% agreement = 95%准确率；九模型×十任务全测” | [Gur-Arieh v2](gur-arieh2026-mixed-binding-retrieval.md)：JSS=1−JSD≈.95（分布相似度）；九模型主要两任务，仅两模型十任务 | 迁移的是counterfactual分辨力，不是拿自然GP做另一表JSS |
| H-C6 Belief-R的then | “第三句只要有then便是语义修订点” | [Belief-R](wilie2024-belief-revision.md)是加入另一个充分条件却在自然语用上视作新必要条件的**suppression**；严格逻辑不产生撤回 | E104 then切半句不能代表一般后到证据引起的更新 |
| H-C7 reward的后验 | “重建分数自然等于完整解释正确率/后验真值” | [ABBEL](lidayan2026-abbel.md)Eq5重建最新观察，Eq6是posterior−prior；实现还有归一化差异 | E101符号分解是条件概率事实，得补语义、候选、真实行为 |
| H-C8 E103改进 | “correct roles提高就修复新关系” | E107更严格的显式依赖/模糊省略再编码使Q conservative +6.25pp CI含0，其他族不稳健 | 不因旧gold达标而认证完整新依赖/训练方案 |
| H-C9 E105多候选 | “搜索更广必定放大错误” | E105 Q多候选带+13.54pp改善 | 过去局部负例不能升级为一般搜索恶化理论 |
| H-C10 E93 forward run | “确定性重复可推断任务正确工作” | 原preflight未核是否有final答案、是否截断/模型是否正常CoT；既有Direct全cap unknown，25.70556 GPU小时缺有效输出 | 旧工程运行不能混入模型科学结论，新的双模式preflight仅是将来运行门槛 |
| H-C11 粗patch | “whole residual有作用=语法因子经源传播；不管用=无syntax状态” | [Hanna](hanna-2024-gp-mechanisms.md)把特定feature的预测功能、QA跨用途与语义对象分层；我们的E55/E64/E70混合源有影响但不识别纯关系 | 因果效应大小只归属于实际替换对象 |
| H-C12 阅读索引 | “迁入149就是精读149篇、旧86篇都重新核真” | 149是原资产总文件数，144旧paper/topic卡+5索引；后来补3新卡并合并3重复得144规范卡；旧MAIN为历史自报 | 自称全文已读只在台账准确所述范围成立，不凭新目录数量算读书量 |
| H-C13 本次深读数值错列 | Christianson2001实验1a/b先前把GP-implausible的20.2/43.7与11.1/31.4分别误标为non-GP control | [原始论文表2、表3](christianson2001-thematic-roles-linger.md)真control分别为21.4/31.0及10.7/16.3；Exp1a implausible对control整体F1不显著 | 任何“非GP也高达43.7%”或条件对比应重新按六列修正；说明我们本次新增精读本身也必须接受第二轮原文反核 |
| H-C14 Ministral strict读数 | “Ministral initial 84.55%正确、final 28.09%，说明撤回了旧关系但没建立新关系” | [独立审查§2.2/§4.3](../INDEPENDENT_REVIEW.md)：E87原始输出中strict规则下NPZ主句事实题（Gold Yes，176任务）Ministral只答24个Yes，PLAIN下100个；它在strict/RECOVER规则下是No偏置 | E82–E90、E96–E107中Ministral的strict/RECOVER读数不能当撤回/能力证据；三族叙事须重读为两族 |
| H-C15 NPZ反身替代依赖题的词义成分 | “17个反身/互指初始关系三族几乎全错，是GP修订失败” | 对照句“While the protester hid, …”下Qwen只41%、Ministral 8.8%承认“hide himself”；只有Gemma（70.6%）对照高而GP为0 | NPZ反身题只对Gemma是干净GP效应；未来须先用对照句过滤模型接受的词义，或报告对照基线 |
| H-C16 NPS两句复述格式污染 | “NPS自由复述里‘The chef remembered the recipe / The recipe required…’是初始误读” | Amouyal“rewrite as two shorter sentences”指令必然拆掉that补语；E107手读显示NPS候选被整体标INITIAL_MISREADING | E53/E67/E96/E103/E107中NPS的误读/初始标签需重标或改任务；NPS占E96–E107源的25/50 |
| H-C17 替代依赖题被忽略 | “修订测验=initial题正确率” | D0资格表中grounded_gold=Yes的initial题（NPZ17、MVRR16）是唯一直接问替代依赖的题；E87分层：Qwen/Gemma MVRR GP 0/12.5% vs 对照81/91% | 主读数应是替代依赖断言，误读拒绝与后半句事实为辅读数；见[独立审查§0](../INDEPENDENT_REVIEW.md) |

**待再次核实的边界**：
- 历史外置原始逐token/标注与原计算代码仍在旧机器/data1路径；只有Github归档/小摘要可查。无法在此声称对所有历史效应与质量标签作逐题重新独立验证。
- Huang/Ferreira2021与van Gompel2006正式主文仍有未核完的范围；**Ceháková2025**和**Patson2009**已有2026-10-12后续提交补读作者完整正文与主要实验，并分别记录未核的附录与原始数据，不再列为“仅摘要”。旧原机/data1的全部结果尚未本轮独立重算。
- GitHub card阅读范围可能互相重叠且自报版本复杂，特别旧86 MAIN或索引的时间戳；保留历史自报，**本轮仅对少量原文进行了新核验**。

改变一条核心观点时，不只改此表：同步更新[总图](00_STATE_OF_THE_FIELD.md)、[专题](topics/05_HOW_IDEAS_GROW.md)、相关[原卡](PAPER_ATLAS.md)，以及[本workbench对证据的判定](03_EVIDENCE_GRAPH.md)。