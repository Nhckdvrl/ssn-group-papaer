# E75：两个原版本在编码时相互消费，还是在回答时重新组合？（2026-10-07）

- **状态：** DONE；先卡后运行。E74异常第一个因果追问。
- **对应：** C09 / I03，原cue与GP的先前关系解释保留。
- **问题：** E74已提供原无歧义证据，却不能统一保持关系。干扰发生在第二Source读取第一Source时，还是Task同时消费两Source时？
- **设置：** 原样E74发表175对/四构式/原两Q/gold/全部真假模式；三族离线manifest，FP32/eager/seed75，8卡固定pair SHA分片，0新API/不改原数据。输入SHA52412e9222a885eb0b115bdd301767758dc64e837983a62dd824303630037c6a。
- **唯一核心对比：** 完全相同CUE_GP及GP_CUE文本和task，CUT_CROSS只删第二Source query→第一Source keys，所有层；第一Source计算不改，Task/答案query仍正常读两Source。NATIVE整面板复用E74全LP，固定首pair native2D/4D与旧LP核对≤.001。不是让Task忘掉早句，不加位置/层数网格，不开放未来。
- **主读数：** initial/final正确率及正确概率，两个Source order分别全报，native/cut/delta，所有三族/四构式/五truth层；pair lexical cluster bootstrap10000/seed75。完整分片覆盖与SHA闭合才读效果，不筛首句答对条目。
- **阳性对照：** 全量CPU原first-source prefix与E74一致；固定首pair四任务native2D/4D LP误差≤.001、first-source每层hidden差0；被删query仅第二Source token、keys仅第一Source、Task行不删。E74单cue参考完整保留，不新跑控制矩阵。
- **噪声地板：** cluster CI；nativeLP误差实测，弱cue不归因。5pp仅参考，不自动科学判决，不重复种子。
- **混杂审计：** cut使第二Source独立于第一Source源token，但仍读原固定header；Task自由组装两者，不是latent parse oracle。干预是全层消费移除，可有分布改变；没有恢复不证明没有信息。两个原版本可有不同措辞/语序，但同pair两问题gold一致。相对原单cue的负效应不能单独排除重复语篇影响。
- **决策表（跑之前写）：** CUT共同恢复受损关系且不伤另一关系→编码时跨版本相互消费是可预测入口，继续自然用途检验；无共同恢复/依然一样错→源间消费不足解释，优先Task关系组装/自然E70/E71，不加mask细分；大幅伤害→正常跨源整合重要，但不能认定GP-specific机制；异质如实报，不能筛一族或pattern包装idea。
- **定位与意义：** E66/68是goal路由，E73是答案label，这里第一次把两个发表source的相互编码与Task同时访问分开。一般context干扰/partial interpretations已有owner，只有修订的关系特定、可预测后果才有叙事价值。E74+75后更新假说与价值自审，近邻不桌面关线。
- **算力预算：** ≤2 GPU·h，2100新条件task/4200候选，8独立H20。原资产外置E75，代码/小摘要进git。

## 结果

全2100任务/4200候选闭合，实际.125256GPU·h，全1440格/全部真假模式已读。

全部三族700task/族CPU非重叠source spans校验通过；8卡按E74原分片运行，first-source/source-task界面保持，0API。PID/配置见外置E75。

### 数字与自审

map SHA2902ebe6a76df5774741511ec4312c1bafb8462ac0cf002d43ae7c8c99362efe。8卡native2D/4D最大差0、旧E74 LP最大差.0001487732，first-source hidden最大0，Task行mask不改，0API。

NPZ89 CUE_GP初始概率cut−native Q/G/L −2.17 [−8.71,4.26]/+9.25 [−.10,18.61]/−7.86 [−13.72,−2.16]pp；GP_CUE −5.76 [−13.43,1.99]/+16.70 [9.54,24.19]/+1.46 [−3.08,5.97]。final两order三族概率均受损，CUE_GP −2.85 [−6.41,−.04]/−1.09 [−3.25,−.01]/−15.93 [−22.46,−9.59]；GP_CUE −2.82 [−6.15,−.15]/−1.17 [−3.44,−.01]/−25.90 [−32.43,−19.62]。不取Gemma正效应称共同解释。

MVRR24 CUE_GP initial+15.56/−8.95/+4.64（CI含0）、final−17.73CI负/−29.13CI负/−5.71CI含0；GP_CUE initial−8.37CI含0/−16.53CI负/−5.04CI含0。NPS弱cue、NPVP异质/损伤，全部truth模式/No/Yes及missing保留，完整CI/[摘要](../results/E75-cross-source-consumption-summary.json)。

按决策表：隔离跨源编码没有共同修复，正常整合也对正确final重要；不证明consumer是唯一原因或latent正确解析已存在。E74+75块价值自审：当前不是令人兴奋的新叙事，不扩层/位置/格式网格；转E76方法动作，模型先按main-event-first写关系，再答原QA。原句/gold不变，先检验端到端效果，不依赖新输出审计完毕；未审核输出不能用于角色机制归因。C09L1/C06–08L0不改。
