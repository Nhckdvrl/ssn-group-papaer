# 情境理解与绑定：全文定向论文卡

核查日期2026-10-03。原文数字均为作者报告；主文、相关方法和关键附录定向阅读，未逐项复算。领域卡见[上下文信息组织](../../../search/sasano-taste/CONTEXT_BINDING_TERRITORY_2026-10-03.md)。

## Mixing Mechanisms: How Language Models Retrieve Bound Entities In-Context

[ICLR2026正式页](https://proceedings.iclr.cc/paper_files/paper/2026/hash/2eeff35664016c7f0f8aa704f0d9a83e-Abstract-Conference.html)；[全文v2](https://arxiv.org/html/2510.06182v2)；[代码](https://github.com/yoavgur/mixing-mechs)。本地corpus Poster8.00；未完整读公开评审，不据分数解释接收原因。

1. **形态：** 旧机制解释的条件性失效 + 替代解释的干预分离 + 简洁因果模型。
2. **背景/改变前提：** 短list上“根据位置找到相关对象”工作良好，不代表它解释更长、更多实体的输入。
3. **idea来源：** DOCUMENTED：论文指出增加实体组后位置机制在中间变模糊；RECONSTRUCTED：把failure放在多个候选检索地址上，设计反事实让位置、词汇、反身指针指向不同答案。
4. **与近邻距离：** Feng/Steinhardt2024给binding IDs；Dai2024定位子空间；Prakash2024跟踪回路；Prakash2025 lookbacks。本文不否定这些机制存在，而是说明单独使用它们不足以预测输出分布，增加混合机制和更复杂输入证据。
5. **实验：** 九模型不是每个都跑十任务：九模型主要两个任务，Gemma2-2B-it/Qwen2.5-7B-it跑十任务。干预组合得到8,000组平均分布，70/15/15拆分拟合简洁解释模型；主要例的JSS约0.95，对单一位置解释约0.44。**0.95是分布相似度，不是95%任务正确率。** 大量反事实forward仍有成本。
6. **证据与短板：** 互换干预和分布预测比只画表征图更强；加入entity-less filler仍不是完整自然长文理解。混合系数与位置条件的规律不能直接外推所有关系任务。
7. **可迁移动作：** 让几个解释对同一个受控输入给出冲突预测；用公开现成模型测量，不先训新LM。凡已涉及位置失效、词汇/反身补偿及padding边界的主张均有ownership。
8. **资产：** 主脚本、grammar与可运行示例已在仓库，README仍提示整理中；依赖与小模型显存待实际复现，不能保证开箱即跑。

## Do Language Models Track Entities Across State Changes?

[ICML2026正式页](https://proceedings.mlr.press/v306/tang26ah.html)；[全文](https://arxiv.org/html/2605.30233v1)；[代码](https://github.com/PootieT/entity-tracking-mi)。corpus Poster4.50，未全文审稿核验。

1. **形态：** 自然操作的机制研究 → 预测旧评测遗漏的失败 → 部分因果修复。
2. **背景/前提：** 静态对象绑定不能回答新增、删除、移动后怎样更新。动态成功也不必意味着逐步维护完整世界状态。
3. **idea来源：** DOCUMENTED：从绑定parent加入现实需要的状态变化；RECONSTRUCTED：先将几类操作拆开，发现删除信号的作用单位，再用这个单位预测错误，而非先用新benchmark找低分。
4. **近邻：** Kim/Schuster2023 boxes提供行为对象；Prakash2024描述绑定回路；Gur-Arieh2025/ICLR26混合机制；toy permutation-tracking理论研究深度与步骤限制。增量在非toy预训练模型的动态操作和可验证失败机制，不是又一次绑定probe。
5. **方法/实验：** 七盒子、PUT/REMOVE/MOVE，Gemma2-2B、CodeLlama13B、Llama3.1-70B；local/global/mention线性读出、path patching、子空间干预。新失败情形每类300条；对共享标签、无效删除、删除后重引入分别测行为与修复。
6. **不能省略的限制：** 线性probe失败不排除分散或非线性表示。部分干预只取原先答对100条；修复表报best single layer，不是独立选层后全分布稳定收益。70B在重引入例DR仅0.01而13B为0.62，不能一概说大模型同样失败。删除回路未完整定位，作者明确保留负结果。
7. **可迁移动作：** 行为→机制→独立可检验预测形成闭环；先检测同一名词在不同关系位置是否会被混淆。但“global removal”和这三个failure模式属于本文，不能拿来作本仓库新发现。
8. **资产/成本：** 数据生成、行为、probe、patching脚本公开；冻结LM分析可起步，probe/mask需要轻量拟合；70B远程NDIF配置需替换为自己的单节点路径。不要在弱I/O上保存完整所有层全tokenactivation。

## How Do Language Models Understand Tables?（补充近邻）

[全文](https://arxiv.org/html/2602.08548v1)；NeurIPS2026目录已见，main分轨/最终版本未核。定向读§1–6及部分附录。

这篇把二维表格序列化后的cell定位拆成语义绑定、坐标定位、信息传播，使用patching/probe/ablation/向量干预；五个开放模型，主例Qwen3-4B，500条合成样本。DOCUMENTED动机是解释结构读取；RECONSTRUCTED研究动作是选最小但有实际含义的原子操作，再看多cell怎样复用机制。仅“列索引可线性解码/按分隔符定位/多查询复用head”均已有研究。它不是整个表格推理的完整机制证明，未核到可复现代码，因此不取代上述两个首入口。
