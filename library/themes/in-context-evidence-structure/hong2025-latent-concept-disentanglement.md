# Latent Concept Disentanglement in Transformer-based Language Models（预印本）[v2主文§1–2、附录A.1]

[原文](https://arxiv.org/html/2506.16975v2)。2026-10-11实际读§1–2/A.1；数值任务§3与其训练附录未深入，会议状态未核。

1. **形态：** 潜变量组成的因果解释；不只寻找任务方向。
2. **压力：** city→capital示例可由直接关联或先求country再取capital实现，正常输出不能区分。
3. **前提改变：** donor与recipient使用不同输入/输出类型；检验移植的中间信息是否按recipient输出关系被重新解释。
4. **idea来源：** RECONSTRUCTED论证链，不是作者真实发现日志。
5. **距离：** 任务向量与多跳事实定位已有；具体区别是type-corrected答案，而非字面donor答案。
6. **实验：** Gemma2-27B geography/company；末位attention输出互换。donor大学→电话代码、recipient城市→首都，若移植country应得到donor国家的首都，而非电话代码。GQA以两头为组；附录说明干预和读数。
7. **边界：** 原问题依赖预训练事实；筛出强因果头组后的结果不是所有中介都可迁移。logit差同时可能下降原答案，作者另报替代答案rank以检查。不能把其几何任务结果直接当大LM的完整机制。
8. **研究动作：** 让literal answer与recipient解释后的答案不同；把中介信息的意义和输出表达分开。失败也可能是接口不兼容，先保留功能阳性。
9. **对ICES：** 共同criterion要与recipient私人偏好组合，不能以移植teacher的yes/no判据认定成功。E96的标准-only文本接口已有功能阳性；若做神经接口，要测recipient偏好下的新答案并保留同向输入与双私人偏好，不能复制donor结论。这项通用实验原则已有，不作为ICES新意。
