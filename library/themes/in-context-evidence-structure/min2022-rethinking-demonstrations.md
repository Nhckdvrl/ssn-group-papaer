# Min et al.：Demonstration 的关系、词空间与格式

- **来源/核对：** [EMNLP2022 Main](https://aclanthology.org/2022.emnlp-main.759.pdf)。重读§3–6，含direct/channel、随机标签与错误比例、OOD inputs、随机label词、无pair格式和meta-training；未复现代码。
- **idea来源/实验链：** 从gold关系被破坏后性能仍保留的结果出发，将示例贡献拆成输入分布、label space、pair格式和关系，再分别改动。重要的是用保留格式的无信息替代而非只删字段；删除本身可能改变模型如何识别任务。
- **证据尺度：** 同样的扰动在direct/channel与不同模型可能作用不同，宏平均变化不等于每个任务完全不学关系。“不学新任务”的强概括依赖所采用的learning定义与测试任务，不是所有ICL算法的定理。
- **ICES定位/借鉴：** output space与格式重要不是我们的新发现。固定word stream、token位置和input multiset的关系反事实，以及真实private反向约定阳性，可检验具体关系作用。公共schema效果还须让信息与形成背景分离；E126/127提供这种配对干预。不要仅用最终预测提高解释新增关联。
