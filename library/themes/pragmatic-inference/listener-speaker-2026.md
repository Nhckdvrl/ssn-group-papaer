# How Hypocritical Is Your LLM Judge? Listener–Speaker Asymmetries（ACL2026 Findings；用户指定参考）

来源：https://aclanthology.org/2026.findings-acl.372/；目标投递仍主会，review未核对。

1. **形态 / 阅读：** comparative behavioral finding；intro、三任务、results/discussion/limits、B关键tables4/5已读；A生成细节未全读，code未复现。Table5原PDF视觉核对。
2. **压力：** judge是否能自己生成符合自己判断的表达？
3. **改变前提 / 来源：** 标量competence→role和item-level依存；DOCUMENTED：judging versus production与presupposition范式。
4. **证据：** 14models，German false/antipresupposition与English deductive，judge给标签而speaker填词。角色方向按任务/模型变化，部分item-conditional关联为负。
5. **校对：** 正文称Olmo13 speaker parsing约5%，Table5却在Deductive Listener列写5.6、Speaker100；Claude正文listener5%/speaker55%，表列相反。不是PDF文本抽取错误，已看原图；需code校对角色对应，不能拿某个gap为精确能力证据。任务格式/语言/候选不同，有些大gap由instruction reliability限制。
6. **近邻 / ownership：** “判断不等于生成”、item-level asymmetry已有claim；不是换一个role名就有novelty。
7. **动作：** matched output support/invalid bounds/一条格式恢复；先排parser再谈knowledge-use。
8. **对我们：** 能作为S3压力，但MCQ的角色差异不能推latent表示相同或不同；多个parent的direction不能直接拼因果。
9. **边界：** 本轮不以该paper自动判死；若做joint boundary需新稳定结构，不能只是复制judge/speaker leaderboard。
