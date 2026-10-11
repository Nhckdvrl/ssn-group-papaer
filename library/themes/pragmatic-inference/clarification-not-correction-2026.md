# Clarification Is Not Correction: LLMs Fail to Let Go（arXiv2609.25337v1）

[原文](https://arxiv.org/abs/2609.25337v1)。正文/related work/限制与附录A–C已读；17页PDF取得并解析，未审代码/raw/judge或图片。venue/评审未核对。

- **形态与idea来源（DOCUMENTED）：** 从多轮任务变差转向“已获明确澄清之后仍残留什么”。以旧解释残留作为行为对象，区别记忆可用与状态失效处理。
- **距离：** 接Laban2025多轮退化、clarification与传统belief-state tracking；不是首次发现早期猜测。生成290任务＋20pilot＋30adversarial，两个Gemini，约7160trials，同Gemini-Pro judge。没有自然人类解释norm。
- **证据：** 同最终信息换顺序、summary/ledger/CoT、rollback/两阶段等干预；coding残留较大。acknowledgement–revision aggregate差不一致，细类更明显。补充rollback效果来自小样本，不是通用解法。
- **ownership：** 过早承诺、明确纠正后残留、保留uncertainty的系统agenda已有。输出残留只是有效状态代理，不是内部posterior直接观测；作者承认recency、位置、指令执行没有全分离。
- **可迁移动作 / 我们的距离：** 先固定最终证据再操纵路径，另查成功与残留。模型“保守措辞”与实际证据更新不能互代；行为不同若不能区分表示与回答策略，保持未识别。不同问题有近邻不判死，但也不能只换openweights复测叫创新。
