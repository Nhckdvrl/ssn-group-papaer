# In-Context Learning Operates as Concept Subspace Learning（2026预印本）

[主文](https://arxiv.org/html/2605.18830)，Wei Tang / Xinyan Jiang / Fakhri Karray / Lijie Hu。2026-10-11读§3.4–5.5；接受状态未核对，代码和附录未完整读。

- **问题与idea来源（RECONSTRUCTED）：** 从线性任务族的共同低维结构出发，先明确统计上能识别什么，再提出低维激活中介的可检验假设；不是从一个好看的patching图倒推出理论。
- **直接ownership：** task-conditioned输入—标签矩可识别共同子空间；无条件均值在零均值任务族中可抵消。因此“相反私人函数仍共享一个无向标准”已有直接理论参照，不属于ICES首次数学认识。
- **实验动作：** 正常与损坏上下文，投影/补空间、随机与跨任务同rank对照，关系交换。以完整功能变化检验估计空间，不只看线性可读出。
- **证据边界：** 作者区分线性统计论证与Transformer机制假设。神经实验的监督子空间及局部恢复不构成完整算法；关系/实体任务与私人判断的共享问题也不自动等价。
- **ICES切入点：** E95固定匿名input-label全序列，仅重分Source，两个世界各自合法且共同标准不同。行为可检验是否利用分组信息，但Source-aware校正检索与criterion推断都可能全对；必须让后续因果对象刻画信息的形成与部署，不能把上述数学重新包装成novelty。
