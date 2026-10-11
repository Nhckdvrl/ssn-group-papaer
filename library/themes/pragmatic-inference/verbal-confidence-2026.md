# How do LLMs Compute Verbal Confidence?（ICML2026）`[证据级别：正文全文、关键方法与limits；图/源码未独立审计]`

[原文v4](https://arxiv.org/abs/2603.17839v4)，2026-09-18更新。作者PDF42页，已读正文pp1–9、C.1.1–3/C.1.8–10、D.4–5；其余补充、图逐点、代码未完整审计，不称42页全读或复现。

- **idea来源 DOCUMENTED：** neuroscience一阶/二阶confidence争论＋Geva2023缓存事实属性＋末层confidence-expression神经元。前人知道能报confidence；本篇追问何时生成、从哪里取出，提出cached与just-in-time的不同干预预测。
- **实验逻辑：** steering→corrupt/restore→noising→异trial swap→attention blocking→跨模型/数据，读数与因果作用分开；相邻位置无效控制和same-confidence swap比仅probe高分更有解释力。Gemma27B主分析，Qwen2.5-7B/Magistral24B边界。
- **具体边界：** 完整类别prompt中CC→PANL阻断无效，精简numeric才显现；中间template可冗余路由。六项logprob summary解释约10%confidence variance，PANL约38%，但这只排除这些线性summary，不穷尽所有probability信息。activation可解码并不意味着控制行为。
- **需保留的审计：** Phase0答案生成时confidence说明位于开头；Phase1答案后的表示虽因因果attention不见后续指令，不等于已验证完全无confidence任务经历的自然生成。25高/低correct trials取向、尺度经验选择、test confidence分层均需公开。norm/cosine在自然范围不能证明所有干预语义在分布内；这限制外推，不否定多个互补控制。
- **ownership/如何发展：** 自己答案的confidence表示、缓存与retrieval已有主会ownership；NMI2026再研究其行动使用。我们的世界事实、别人意图、社会承诺不是这些量的别名。现在优先使自然条件效应可识别，不能先做pragmatics confidence neurons；成熟后需要目标之间的选择性迁移与正确行为控制，才有机制问题。
