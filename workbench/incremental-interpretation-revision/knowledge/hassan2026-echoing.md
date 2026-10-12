# Ask Twice, Look Twice（arXiv 2607.15565v1，2026；接收与公开评审未核对）`[证据级别：全文核心 + 附录 A、D、F、G、H]`

[正文](https://arxiv.org/html/2607.15565v1)；直连 PDF/hash/实际读取范围见 READING_LEDGER.json。

1. **形态：** 一个位置反转异常 → 两阶段解释 → 干预与实用修复。
2. **压力：** VQA 理应提前告诉模型看什么，但提前问反而更差；内容相同，只换顺序。
3. **改变前提：** 指引编码与访问问题需要不同位置；知道任务并不保证答题时使用它。
4. **idea 来源（DOCUMENTED）：** 反直觉 ordering 观察；人类 adjunct-question 文献提供呼应，不是机制证据。
5. **近邻距离：** Re-Reading Improves Reasoning、Prompt Repetition、Lost in the Middle 已有重复/距离效应；本文增加视觉编码、直接读出边的因果证据与重复图像。
6. **实验：** 五个开放 VLM；三个主要 benchmark + 开放生成；单一构建器、固定系统提示。相关分析用150个顺序分歧项；因果 knockout 另用250个不按结果选的项；问题、图像、等长随机 span 对照。重复内容、padding、短cue、图像顺序拆解释。
7. **证据与短板：** 非按效果选的干预样本比漂亮的热图更有解释力；只切直接注意力边，relay 信息仍存在。图像分辨率同时改变距离与视觉证据质量，不能称纯距离识别。部分定位图只有一张图；开放生成的 whole-word 匹配也不是完全严格原评分。
8. **可迁移研究动作：** 保持最终读取需求，分别干预前段编码与后段访问；加“看似增加同等计算、实际不提供相同证据”的控制。保留例外模型，不把效果统一性写得过满。
9. **对我们：** 通用的 early-question / late-readout / echoing 故事有强 owner。E08目前也不支持独特 GP 的初始−最终关注交互。增量必须来自真实语言修订的稳定预测及后果，不能只把图像换成GP句子；研究对象继续是 interpretation revision，不关闭 territory。
