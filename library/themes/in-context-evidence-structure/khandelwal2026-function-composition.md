# How Do Language Models Compose Functions?（预印本）`[证据级别：全文指定章节]`

[2510.01685v2](https://arxiv.org/html/2510.01685v2)，Khandelwal / Pavlick；2026-10-10读主文§2–5、附录A/B/D/H/I/J。接收状态不据第三方确认。

1. **形态：** 行为测量＋表示/因果分析。
2. **压力：** 两个原子都能完成，是否保证组合成功？答对是否保证组合式计算？
3. **改变前提：** 原子/组合、行为/过程需分别测；中间量词汇可见性与正确率不是同一指标。
4. **idea来源：** RECONSTRUCTED于正文，从已有composition gap追到不同处理方式及几何预测；非原始发现日志。
5. **近邻：** Press组合gap、latent multi-hop、patchscope；增量是跨函数比较及机制选择预测。
6. **动作：** 常见函数的10-shot组合；logit lens、token-identity patchscope、embedding/unembedding平移比较。
7. **限制：** J的因果交换选中间量RR≥.5样本，改变donor后续函数区分中间量/答案；范围有限，移植也可能携带后续信息。“未检测到中间词”不证明没有非词汇中间状态。
8. **可迁移动作：** 固定可读出中间量、改变donor后续计算，让两种解释预测不同答案。
9. **对ICES：** 一般原子/组合或分数/算法分离已有所有权；E79未测同context原子，不可宣布新组合缺陷。保留近邻，不把其整套任务变成主线新增门槛。
