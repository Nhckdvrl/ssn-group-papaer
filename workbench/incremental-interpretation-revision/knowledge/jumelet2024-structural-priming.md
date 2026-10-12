# Do Language Models Exhibit Human-like Structural Priming Effects?（ACL Findings 2024；全文部分，作为近邻）

[主文](https://aclanthology.org/2024.findings-acl.877/)。实际读§3数据/两种PE定义、§5的divergence与词级解释、§6预测因素/结果、§7讨论；§4图只结合文中解释，全部附录未通读。

- **形态与来源：** 解释priming的方向、不平衡与具体token来源，来自既有句级统计无法定位效应的压力（DOCUMENTED）。不是我们的目标venue。
- **资产/动作：** Prime-LM dative每条件15,000pairs，core/no-overlap、nouns/verbs/functions overlap、semantic相似；GPT2-large及多种7B base/aligned模型。把sentence PE分解为word PE，指出两结构分叉前概率贡献使句级相关结构受到限制；限定分叉后的读数仍透明报原指标。
- **已拥有：** lexical dependence、inverse frequency、模型偏好结构调节priming；共享verb可增强下游semantic-role entity预期，function word尤其preposition/determiner强。所以“患者位置更易预测”“换actor还在”“词频非全部”不能作为本线独立novelty。
- **最有价值的迁移动作：** 在matched entity/role读数中检查效应从何处出现，控制source常规结构预测与关系记忆。E25是history×style×用途交互，必须证明它涉及修订的对象及范围，不能只给这些因子起新名字。
- **边界：** 作者自己区分teacher-forced固定target与实际generation；我们的E23功能后果不稳，不能把likelihood等同生成错误。其隐式学习解释来自模式匹配，不是已证成参数更新；本线完全冻结。

16页PDF，718,471 bytes，SHA256 `eb62233765c18ff528835d24f36cbcfabc49bac84f2b6b9c93de7164d1c47acf`；直接无代理下载，cache-only。未核对公开评审/分数。
