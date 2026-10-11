# Racing Thoughts（NAACL 2025 Main）`[证据级别：正文与指定附录]`

官方记录与PDF：[Lepori, Mozer, Ghandeharioun](https://aclanthology.org/2025.naacl-long.155/)。2026-10-12核正文§2–4.2/6、Limitations及backpatching定义；附录F/G/H用于核范围，未将层扫描当独立确认。

1. **论文形态：** 自然上下文化现象→计算过程解释→构造干预；不是仅定位token或报告能力不足。
2. **背景与压力：** bank在第一轮正确解作河岸，下一轮却回答可做ATM；模型可能知道context含义，但回答读取该表示的时序不对。研究polysemy、资本改名、性别cue三个域，WikiText distractors改变难度。
3. **改变的前提：** 表示最终正确不保证下游计算已用上；上下文化的两个并行过程存在依赖顺序。主张subject先被cue解释，然后question读取subject；若后者先结束，晚形成的信息无法进入回答。
4. **idea来源（RECONSTRUCTED）：** 论文自然对话例子→两个进程的依赖预测，是从论证重建，不知道作者发现时间线。不是先凭空扫描layer，而是先问“正确表示必须在何时可用”。
5. **最近邻距离：** Patchscopes提供功能读出工具；已有backpatching提供后层→前层技术；ICL与知识冲突研究提供context问题。本文新增的是依赖时序解释及额外计算替代的检验，不以首次使用patching建立所有权。
6. **实验链：** distractor/位置行为→attention/logit lens定位读取窗口→cue/distractor attention ablation→subject自然语言patchscope→无distractor cross-patch→同prompt晚层backpatch→冻结被移植subject中间表示，阻断“更多更新计算”替代→高次数Gaussian扰动搜索控制。主体Gemma2-9B-IT，另一相近开放模型与Gemma2-2B复现；约50 A100 GPU·时，三个语义域。pair正确须两问均正确，chance25%。
7. **证据短板：** 每model-domain选择约50% pair准确率slice，patch扫描每pair层组合并以任一成功计正确；不是一个固定部署干预。冻结backpatch结果支持相对顺序，不能排除所有状态分布变化。主文严格区分correlational读取窗口与causal patch。
8. **可迁移研究动作：** 第一次恢复不能区分表示内容与额外计算，就保持同一内容、改变后续允许更新的过程；不继续只做正常分布分数重复。方法与读数的搜索/最佳值要明报。
9. **对ICES：** 已有时序上下文化宽解释不能重命名。E120不扫描层，直接native形成operation→有限图恢复，两种query环境给不同方向；E122把它变成双来源整体使用预测。形成阶段隔离/读取阶段隔离可不同，但不得因此声称ICES首次发现正确形成≠正确使用或新“race”算法。具体增量仍是output-dependent Source关系形成及其功能来源。实验模式可学习，不据此增开layer timing矩阵。

**定位记录：** venue corpus nearest“source evidence formation contextualization in context learning”返回该NAACL Main；检索结果还含大量词汇不相关项目，不能将其它近邻未召回当无人研究证据。2026-10-12 web检索核官方PDF，而非依赖alphaXiv/ResearchGate的二次解释。
