# The Atlas of In-Context Learning: How Attention Heads Shape In-Context Retrieval Augmentation（NeurIPS 2025）`[v2主文§3–7；附录未全面复核]`

[作者论文v2](https://arxiv.org/html/2505.15807v2)、[代码](https://github.com/pkhdipraja/in-context-atlas)。Patrick Kahardipraja等。

1. **形态：** 归因定位→功能干预→来源追踪。目标主要是RAG问答中的上下文/参数知识选择。
2. **idea来源（RECONSTRUCTED）：** 只看注意力难以知道哪些头在解析问题、哪些在复制答案；作者用AttnLRP的贡献给头分工，再通过function-vector注入和attention修改检验。
3. **重要设计：** 生物信息QA中移植task FV与parametric FV；needle里放不必是合理答案的诗名，改变retrieval头注意力检验复制功能。QA发现的task头不能直接迁到翻译，重新定位后才能诱发翻译。
4. **来源读数：** §7用retrieval-head输出对候选词的logit-lens及注意力定位答案span，同时用probe区分参数/上下文来源。已有高质量source tracking，不能声称此前无人关心内部证据来源。
5. **限制：** 作者明确承认跨层token信息混合。定位span的成功针对答案复制；这不自动说明从一组示例推断的分类关系只来自那个span。也不能反过来说作者所有source tracking无效。
6. **与ICES的距离：** E48已经把foreign位置attention与答案方向贡献拆开；E90进一步保持当前来源原始证据不变，只改变另一来源规则，并阻断整个query对另一来源位置的访问。它检验规则信息的功能来源，尚不是一套胜过本文的新归因算法。
7. **可迁移动作：** 两种功能即使同属in-context heads，也需要使它们预测不同内容的干预来识别；跨任务失败要区分旧头不通用与能力不存在。

## 对研究尺度的提醒

“Attention不是解释”不是ICES的新发现。可能的增量必须落在多规则ICL实际怎样形成和选择来源特定规则，以及何种测量能预测功能干扰；不能只展示另一张不同的attention热图。
