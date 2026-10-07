# E68：提前问题只进入后续作答，是否保留或增强收益？（2026-10-07）

- **状态：** DONE；先卡后代码/运行，完整地图自审后不追加目标/掩码网格。
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
32112评分全部闭合，三族GPU·h Q .229526/G .362497/L .270960，共 **.862983**。原E65/BOTH和E66/SOURCE_ONLY分数复用；没有科学失败/幸存条件筛选。C06–08仍L0；C09为E55/E64限定协议L1因果测量，E68不升级潜在parse/能力/novelty。

- 三族仪器已全部通过：native候选LP对E65最大差Q.000417/G.000228/L.000117；干预前所有preSource/Goal hidden逐层最大abs差0，切边仅S query和预定prefix key、不增加未来边。科学32112评分在GPU0/1/2开跑；完整source before task与所有原目标保持，不读部分效应。

- 路径语义限定：READ_ONLY去掉的是目标文本/源前传播状态→S的attention入边，原token位置/目标长度保留；不称源编码对目标的所有统计量绝对独立。核心因果比较BOTH vs READ_ONLY在完全相同Goal prompt/token/位置上，仅Source入边不同；不另加位置网格。

### 完整结果与自审

下表为words、原gold与源支持一致条目；共同正确使用全部原问题，均以词汇cluster bootstrap 10k、seed68取95%CI。单位pp，Q/G/L依次三族。完整四构式、cue、letters、概率、两gold资格及POST-HOC语义层仍全部报告，不用此表替代全图。

| 构式/读数 | Qwen | Gemma | Llama |
|---|---|---|---|
| NPZ INITIAL旧问题收益 | 73.60 [65.17,81.46] | 50.84 [41.29,60.67] | 31.74 [23.31,40.45] |
| NPZ INITIAL最终问题收益 | −5.40 [−10.23,−1.42] | −.57 [−4.26,2.56] | 4.83 [−.85,10.23] |
| NPZ INITIAL共同正确收益 | 56.74 [46.07,66.85] | 44.94 [35.39,55.06] | 17.42 [10.11,25.28] |
| NPZ INITIAL共同收益READ_ONLY−BOTH | 41.57 [32.02,51.12] | 33.71 [21.91,45.51] | −10.67 [−18.54,−2.81] |
| NPS INITIAL共同收益READ_ONLY−BOTH | 27.78 [12.5,44.44] | 9.72（CI含0） | −36.11 [−51.39,−20.83] |
| NPZ FINAL最终问题收益 | −62.22 [−70.45,−53.69] | −23.58 [−32.39,−15.34] | −43.18 [−52.27,−34.09] |
| NPS FINAL最终问题收益 | −40.38 | −28.85 | −38.46（均CI负） |

不能只报INITIAL旧No改善：NPZ INITIAL最终关系相对BOTH，L损失23.86pp [−31.25,−16.76]；NPS损失71.15pp [−92.31,−50]。NPZ FINAL的cue最终问题也损失22.44/9.09/73.58pp（均CI负），所以不是选择性修复GP。MVRR INITIAL共同收益12.96/9.26/−3.70均CI含0；NPVP仅Q共同收益23.08 [7.69,38.46]，且最终问题/原cue显著损伤。NONE匹配源切边基线与原生差异保留在route地图，不能因within-goal对比相同位置就把全部绝对效果称目标文本的纯作用。

第二读出不是完全同结论：NPZ INITIAL letters最终问题L +11.36 [6.82,15.91]，words概率+3.04 [−.26,6.43]；NPS INITIAL L最终letters−7.69（CI含0）、words概率−15.75 [−25.42,−6.59]。完整报告保留这种依赖，不挑mapping或读出。

P16 input-only POST-HOC canonical NPZ71组中，INITIAL共同正确Q/G/L +69.72 [58.45,80.28]/56.34 [45.07,66.90]/21.83 [12.68,30.99]；真final Yes收益−6.34 [−11.97,−1.41]/+2.82（CI含0）/+4.23（CI含0），FINAL则−72.54/−24.65/−50.70（均CI负）。NPS26组INITIAL共同+75/+23.08/0，最终Yes L−25pp；MVRR8、NPVP23全部非稳定共同修复。不能以旧target名称代替撤销/建立语义；全部非canonical同时报告。

**假说改变：** 源目标编码普遍必要被Q/G INITIAL反驳；只读目标普遍更好被L INITIAL最终关系损失和三族FINAL严重损伤反驳。最具体的现证据是目标的源写入与直接消费，对不同关系/模型产生不同方向的后果。它尚可能是任务组装/答案策略，不证明原模型拥有唯一错误或正确parse。没有合格idea，不将切边涨分当方法贡献。

**三句当前故事：** 提前目标带来的正确答案，不等于已经形成可复用更优解释。源写入和直接使用可以相反，也可以共同支持某个关系。值得研究的对象是这些成功/失败到底有没有改变后续自然关系表达，以及哪种关系改变能够预测迁移。

**如果为真审稿人为何关心：** 若能证明作答成功仍带着未修订的关系、并解释/改善其后续使用，会改变纠错对象的选择；现有单纯QA路由不够支撑这种认识。一般目标条件/任务特异表示已有近邻，不以局部相似关闭探索，也不靠新命名建立novelty。

**反证与最高信息量下一步：** 读取已运行E67无Yes/No自由角色整图，以及校正后E63/E64同源跨用途结果。若自然关系都随QA恢复，“成功掩盖未修订解释”被削弱；若只有答案恢复，调整研究对象为用途依赖的关系构建，并从失败内容提出下一核心实验。E65→66→68这块停止追加目标/层/提示措辞控制，先让真实语义结果改变问题。

出处：外置E68 `goal-by-question-read-only-v1.json` SHA ecf362ca4fdcce4b07200e281fea8517e036b2b5e756d9683ceab785d014cd54；`read-only-minus-native-v1.json` SHA b1d50f81e880039498bc5f5027f1239739a8d99b22ee2638f7918dc4ebe57d57；`read-only-minus-source-only-v1.json` SHA 4ab8348030ef40d1ef2583afac4fbc6b012a1591001b762dbeef3c486f8004f5。小摘要：[E68-goal-readout-summary](../results/E68-goal-readout-summary.json)引用全部文件与POST-HOC完整SHA。
