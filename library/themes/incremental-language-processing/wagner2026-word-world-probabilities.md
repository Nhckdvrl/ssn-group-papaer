# Express Your Doubts — Probabilistic World Modeling Should Not Be Based on Token logprobs（ICML2026 Position）[证据级别：部分正文]

[primary proceedings](https://proceedings.mlr.press/v306/wagner26b.html)，Eitan Wagner、Omri Abend。无代理下载PDF到本地cache（1,141,217bytes，SHA256 a25927d095b9c127ea6f5bfc4392475d29f21f8ae267790098dcd5dc905a3096），用已有fitz读取；实际读§1–4及§5部分定义/推导，其他例子/附录未完整核对。

1. 形态：position与形式化任务分析，不是新behavior benchmark。
2. 压力：字符串分布、最优回答与真实事件概率经常被混用。
3. 前提：pretraining估计语料分布，response prediction可能合理地偏向mode。
4. 来源（DOCUMENTED）：由不同训练/推理任务对应不同目标分布提出。
5. 距离：source/target估计及second-order概率表达，不能注册为我们新概念。
6. 方法：分别分析训练阶段、inference格式与用户目标；举coin/reporting-bias例子。
7. 边界：position不证明所有概率读取无用，也不对我们的角色干预给机制结论。
8. 可迁移动作：先固定测的是字符串预期、grounded答案还是显式概率，再谈错与对。
9. 对我们：E38即使公平选择下raw相对bits非0，也不能写模型不知道1/2；fair与unknown程序只校对角色影响的语境边界。具体event/action方向结构仍可研究，generic概率/QA差本身不新。
