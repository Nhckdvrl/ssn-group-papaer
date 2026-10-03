# When Role-playing, Do Models Believe What They Say?（arXiv2026）

[原v3](https://arxiv.org/abs/2606.11502v3)。**阅读范围：** 正文引言/related work、方法、主要结果、discussion/limitations pp1–12；p8图表未逐项审、附录pp14–39/原代码未核对，不宣称39页全文或复现。

1. **idea来源 DOCUMENTED：** Persona Selection Model说行为由选择角色解释；truth-probe与belief-depth研究能测另一层。“讲话像角色”与“在后续推理/受质疑时维护角色的事实”可能不同。选历史人物是为了把现在的真假固定，同时改变角色会否赞同；不是找一个历史题bug。
2. **改变的前提/距离：** 不再把成功persona输出视为内部worldview改变。prompt/ICL/SFT、OCT、EM区分训练方式；topic-matched era-believed/era-false共享当代false，era-true/era-disbelieved共享当代true，因而选择性支持与全局true shift可拆开。预算匹配与中间OCT使结果不是训练更多就更深的平凡比较。
3. **测量：** neutral与native truth probes校准均值false0/true1，因训练会旋转方向；另challenge/generalization、身份adoption控制。probe与行为有statement级而非只均值对齐。采用较深层是因raw→chat transfer在浅层可能chance，不只挑最大效应。
4. **局限：** belief是操作简称，probe可能测coherence/likelihood；跨训练重新probe/calibration可能改变尺。文字生成/标注/身份验证/behavior judge大量依赖闭源模型，不能不审源就迁移到我们主评估；本文未做完整独立复现。
5. **对我们：** 模型自身的truth representation、角色说出的内容、听者归给说话者的意图与社会承诺是不同对象。generic representation–behavior dissociation已有ownership，speaker/listener gap也已有，不能简单换成pragmatics命名。E49必须保留两个task各自成功与接口局限，不用输出自称reasoning解释内部机制。
6. **发展动作 RECONSTRUCTED：** 同事实跨交际目标，多读数相互约束，目标/时代/真假配对使解释可被推翻；未来机制干预只能接在可靠行为边界之后。当前不训练persona、不转去模型belief territory。
