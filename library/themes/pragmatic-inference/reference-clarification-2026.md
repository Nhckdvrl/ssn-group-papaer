# Reference Games as a Testbed for Alignment of Model Uncertainty and Clarification Requests — arXiv2601.07820v2

[原文](https://arxiv.org/abs/2601.07820v2) · [repo](https://github.com/Manarali-bit/reference-games-clarification) · [持久资产](https://doi.org/10.5281/zenodo.20158390)

- 9页全文/Appendix A–F已读；repo网页仍release soon，但PDF给Zenodo，新版资产未下载核验，不能根据空repo判不可复现。未运行VLM，也不增加视觉模型榜单。
- 来源DOCUMENTED：开放对话何时该clarify缺gold；自包含reference game使候选集合/歧义明确，再比较固定选择、允许澄清、实际澄清后信息使用三阶段。问题是能否将不确定转成有效沟通行动。
- 197 games×60rounds，三color-grid难度；Qwen2.5VL7/72B、GPT5mini，API子集500，19null剔除。5samples majority/self-consistency，不是透明内部belief。72B量化、温度.7，API温度无法对齐；人类有60轮共同ground，模型仅初始描述，human比较不匹配。
- 结果：72B原subset accuracy .77/full .71；CR rate .24，CR-only 116项只有42%问题task-relevant。human答澄清后CR-only acc .776→.741/conf .871→.902；full .767→.759。仅一个expert标/回答，不能把成功/失败归真实自动user population。
- 数字校对：正文说subset nonCR .73 vs .77低但full .71不变；图表conf .92/full等需按具体split读，不混同。Relaxed accuracy把任何CR当对仅是上界，不能声称澄清本身有效；source回应可能改信息量。
- 已拥有：uncertainty–clarification脱节与有效clarification不足，不能把“什么时候停止脑补”换成“该问但不问”就称新。suffixedprompt改变行为仍不是knowledge机制。
- 对我们视野：停止推断不是只能选literal，可保留多个解释、问关键问题、按成本暂不承诺。未来若进入互动对象，需要建立歧义/证据/动作的同设定联系；当前静态矩阵无法claiminteractive competence。
