# E128 paper-critical 主张与呈现独立审计

2026-10-12；对应 C23/C24、I04、P17。本记录审主文论证与呈现，区别于[8/8原始数值封存](independent_raw_review_2026-10-12.md)。不修改科学源/claims/论文、不运行GPU、不自行升降级或改变研究状态。

当前新增段与两张附录K表的数值、冻结主域和解释范围相符；不需要因这次有界论断新增实验。Qwen3-14B有小幅真实full-argmax兼容改善，其他三模型平均准确率CI触及/跨零，四家小正T与约50–53% joint表现全部保留。此结果补充criterion相关功能的边界，不能泛称成功标准组合，也没有撤回E127同criterion私人code部署阳性。

审阅快照：

- PAPER_DRAFT SHA `71bce5f2d2f9c7020f41fb585ac676737f8e29989b70afc6528b52b58a183f03`。
- PAPER_APPENDIX SHA `f73466e69674b3cbc3233bf041619d945bd132ade4c4b59939f7a643ad171295`。
- CLAIMS SHA `0cd237d1c85743f011402c895ba0aa9a1ca9ab5baf14a0b0680184a7153575bd`。
- 独立E128 runs封存摘要 `0cf8927ac0395f2d504c60635abbf82d78459c22a3829fca9e437c6f48adab52`，没有改变原始数值。

两表12行、40个统计格、120个数字呈现逐项对照独立raw复算，全部一致；另核10项run/计时/源与冻结/复算计数metadata。主文+2.93[.59,5.47]pp、四checkpoint/两个phase、图中的00/01/10/11与own/joint范围一致。报告比较数量38764与raw38760有重叠，附录明确不增加科学样本数。1.237902 GPU·时仅八完整run计时；没有独立GPU重跑。

冻结primary为origin同code、A Food/B Service、冲突4/8query、两个Source请求等权/context bootstrap的coherent−mixed完整输出准确率。它不是四world总体结果，也不是两Source同时正确的概率。f/s按A private code定向，在完整平衡8query上T=½E[(zA−zB)(f−s)]，concordant项为0，恰等于冲突4query上两个Source的平均correct margin；这是等价输出投影，不是独立机制证据或input filtering。whole-cache接口也不固定private激活、识别新ID或排除非线性校准/上下文化检索。固定Food先Service的材料范围保留。

同primary的single值来自已评分控制的**POST-HOC描述性scope审计**，附录准确标记，并与all-query控制区分。Q8 Food46.88[40.62,52.34]%与M Service53.12[49.22,57.81]%较弱；Q14 Food68.75[61.72,75.80]%/Service78.12[70.31,85.94]%有实测能力，但coherent联合约52%，距single仍远。不能把弱平均结果自动解释为没有criterion信息，也不能用强SST单方面能力替这批双方面函数背书。E128 instruction已经在首评分前改成普通native形成，当前“pure one-sentence instruction”正确；旧E124–127复合instruction披露保持。

所需呈现澄清只有材料来源：主文§6标题为Natural-text，新增段当前“aspect-conflicting reviews”容易使读者误以为E128也是官方SST。应显式写controlled dual-aspect comments；附录K首句同样标明controlled。E128是e119生成的restaurant材料，不能借前文SST自然文本范围。另一个可选精确化：Mistral Food57.81[53.12,64.06]%虽有限，但CI已高于chance；“two matched single functions are weak”不应让读者以为两者都未过chance，可改为Food modest/Service weak。没有表中数值或冻结指标需要修改。

## 三项认识是否仍回答自然研究问题

主文仍在回答“请求某Source时，哪些来源的关系形成了可用证据，以及怎样使用它”，没有实质漂成公共表prompt技术。第一项测关系的来源，第二项测历史消息携带什么，第三项检验这些形成关系在实际Source函数与共同上下文下怎样部署。公共表是在private监督不能交换时测试共享哪些关系仍能改变部署的构造条件；E126/127信息等价背景与完整缓存组合则继续问共同参考结构下private证据能否共同使用。E128把私人code协调和输入criterion分开，正是对原问题的范围校准。它们不是每增加一张表就增加一个机制或claim。

已有所有权与具体增量应分开呈现：

| 主文认识 | 已有工作直接拥有的部分 | 当前具体反事实/预测所增加的证据 |
|---|---|---|
| 输出编码影响历史形成 | [CTA](https://arxiv.org/html/2504.00132v2)已因果检验跨demo contextualization及output空间信息；[Cho](https://arxiv.org/html/2410.04468v3)已讨论输入/label语义合并并做操作去除 | 固定A监督，在两个合法Source间改变B输出编码/关系；系数1、无拟合的历史answer→A-label预测针对actual接口counterfactual，独立新材料验证并保留残差。无donor原生去除及受限图恢复测其条件性贡献。一般contextualization预期不能代替这些具体预测和边界。 |
| 历史消息携带关系 | CTA也已有保持语义空间却破坏功能关系的干预；“关系不只是label token”本身不是首次发现 | B labelstream、Source、位置与输入多重集固定的跨类/同类配对，在A保留其合法规则时测试进入A形成的关系内容；full-source读取及真实SST私有正反功能控制确认其有界作用。Code关联与双criterion响应不同接口的负/正结果进一步限制完整规则运输解释。 |
| 形成与读取的功能约束不同 | [AddUp](https://arxiv.org/html/2605.16591v2)已有contextualized QK/V因果分解、选择与函数向量组合；一般缓存依赖也由PCW/CacheBlend覆盖 | 对两个合法私人规则的冻结政策比较：selective answer形成、all-cross形成、query-only在同cache双Actor下产生具体不同收益/代价；私人监督隔离时public relation经形成改善部署、swap也改善；同事实/同private位置/同输出的配对cache组合识别联合非加性，并报告强local函数与未恢复的joint差距。已有论文的广义兼容解释不能直接替代这些反事实及其实际正负预测。 |

这些增量是已有框架内更具体的Source关系形成与部署解释，而非新的contextualization、首次QK/V区别、首次关联运输或首次binding分解。其价值不能由计数通过或与宽理论兼容自动判定；当前报告只核证据是否回答主旨，不宣告整体研究意义已完成。

目前唯一须守住的因果连接边界是：E125–128公共schema/兼容作用尚未归因到§3同一条answer→label原生运算。whole-cache与形成mask给出形成条件影响部署的因果事实，没有重建这类效应的唯一内部实现。当前主文把它们写作形成/读取约束与构造性后果，足以支持有界三认识；若以后写成“同一个已识别算法完整解释公共背景协调”，缺的就是这一机制连接，不能拿已有系数1 namespace重建直接替代。当前措辞无需为完整逆向新增实验。

阅读范围：本次读当前主文摘要/Introduction/§2–9与新增§6.5段，重点全文读附录K；原主文/附录其它数值沿用E115–127已经封存的独立审计，并未再次从所有旧raw重跑。E128新数字由本次独立raw与scope-matched描述控制直接重算。再次核CTA§3.1–3.3/G、Cho§4/5.1及AddUp§3–6相应正文，未独立运行近邻代码或审其全部训练；Hendel/JIT/Dong及binding/cache近邻范围另见E129设计审阅和E127既有paper-critical记录。没有新科学矩阵、grade或状态建议。

## 最后快照复核通过

作者已只修两处范围文字：主文E128显式controlled dual-aspect comments；附录K将Mistral Food的modest且CI高于chance与Service interval含chance分开。两表数值/冻结primary/原科学源不变，前述材料来源呈现缺项已解决，不保留为未完成要求。

最终PAPER_DRAFT SHA `bf16c1bd20bc4408e9083b96784f01f38eef4d3063e234c4d7f112b33a495e6f`；PAPER_APPENDIX SHA `f51ba4d7281dcc0b90c66a21f4c2b8263e21403bb17baa9c3d6ad2b7faa92819`。原审阅快照与对照记录保留。新增段/K呈现与有界三认识通过本次paper-critical校对；这不自动宣告整体科学意义、原生完整程序或投稿流程完成。无新GPU、实验门槛或状态变化。
