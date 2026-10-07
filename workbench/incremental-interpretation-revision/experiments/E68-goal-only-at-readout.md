# E68：提前问题只进入后续作答，是否保留或增强收益？（2026-10-07）

- **状态：** RUNNING；先卡后代码/运行。
- **对应：** I03/I04、C06/C09/P16；E66完整地图使假说从源修订入口转为编码/作答相反或joint依赖；这是POST-HOC新机制选择，E68输出前预定。与先前解释修订关系：错误旧关系的目标进入源编码和用于后续选择是否产生相反的修订后果。
- **核心唯一新条件：** READ_ONLY。原NONE/INITIAL/FINAL prompt不改，在全部decoder层移除Reading goal区间及其源前传播token→所有S query的边；保留目标→全部source结束后的Task/answer边、源→消费者边及source内部原因果边。源前传播区间与E66同一locate，避免经Sentence标记泄漏目标到S。E65 BOTH与E66 SOURCE_ONLY完整分数复用，不重跑科学baseline，不追加NEITHER/层窗口/提示措辞。三路径不能当可加的完整factorial。
- **数据：** 完整E65 892QA/356源/178clusters/四构式与GP/cue，SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b。原S/Q/gold/目标全部保留，三族各10704新评分，总32112。P16严格input goal truth及evalGold层作为已明示POST-HOC补充，与full主矩阵一起报告，不借source question_target命名正确/错误关系。可信数据不重审。
- **读数：** 三族四构式两侧/两later目标正确率/p_correct、words/letters×两mapping、精确同Q与其他Q、转移及所有源Q共同正确；READ_ONLY INITIAL−NONE/FINAL−NONE减BOTH同差，另与SOURCE_ONLY同差并列。E65同unit→S→cluster权重、10k bootstrap、seed68。不能把mask引发的结果自动叫潜在parse或语法因素。
- **阳性对照：** READ_ONLY NONE匹配去Sentence前缀自身影响；完整cue任务能力；全目标原生基线来自E65 SHA核对。弱cue面板不能承担机制null。
- **噪声地板：** 首四input source全goal小仪器，4D native复现E65候选LP<.001；切边仅Source query/预定prefix key、无新未来边、所有层确实运行；Goal及其他preSource hidden在切Source入边前后保持<.001或rel1e−5。S hidden此处允许改变（正是干预），不能把消费者语义当另一个role输出。
- **决策表（跑之前写）：** READ_ONLY保留native INITIAL收益→源goal编码非必要；READ_ONLY好于native且SOURCE_ONLY差→goal编码/作答有相反功能效应，有具体预期可跨自由用途追；READ_ONLY也差→原生joint协同或mask分布效应，不能说source encoding伤害；NONE/cue地板崩→路由不可用于强机制判断，不以null否定源状态。三族/构式差异完整保留，没有sole Llama链。
- **算力：** FP32/eager/pinned/offline、seed68，GPU0/1/2（三卡E66已结束），每族预算≤2GPU·h；E67独立GPU3/6/7继续，4/5服务不动，无新文本无需额外Step审核。
- **定位/意义与护栏：** Ask Twice Q-first编码不足需echo，Lens task视角对齐；本次新假说是自然关系修订中goal源写入与后续使用可能反向，而不是一般目标正确率改善。§6.3已在E66完整自审更新假说表/审稿价值，不能通过加一堆控制来固守原“源修好”叙事。E68一个对称切分直接区分joint必要/直接补偿/源路径妨碍；之后结合E67完整用途结果做结构化再审，不接措辞网格。

## 结果
尚未运行，C06–C09 L0。

- 三族仪器已全部通过：native候选LP对E65最大差Q.000417/G.000228/L.000117；干预前所有preSource/Goal hidden逐层最大abs差0，切边仅S query和预定prefix key、不增加未来边。科学32112评分在GPU0/1/2开跑；完整source before task与所有原目标保持，不读部分效应。

- 路径语义限定：READ_ONLY去掉的是目标文本/源前传播状态→S的attention入边，原token位置/目标长度保留；不称源编码对目标的所有统计量绝对独立。核心因果比较BOTH vs READ_ONLY在完全相同Goal prompt/token/位置上，仅Source入边不同；不另加位置网格。
