# Lost in the Prompt Order: Revealing the Limitations of Causal Attention in Language Models（Ok & Lee 2026）

**阅读身份：MAIN_VERIFIED_THIS_PASS（作者arXiv v2 HTML，2026-10-12；主文与附录D/E/F要点）。** [arXiv 2601.14152](https://arxiv.org/html/2601.14152)。预印本，投稿状态未核。

## 1. 未知与来源
**AUTHOR-STATED**：MCQA里把上下文放在问题/选项之前（CQO）比放在之后（QOC）平均高14.7点；Shaier 2024只观察到类似顺序效应，没有解释原因。
**RECONSTRUCTED**：这篇论文的科学动作是把一个“工程常识”变成三个可被否证的假说，再逐一用受控实验淘汰——这正是我们在E03/E07处理顺序反转时**没有**做的事。

## 2. 三个假说与判别实验
| 假说 | 判别实验 | 结果 |
|---|---|---|
| H1 训练数据偏CQO | base vs instruct差距（14.70 vs 14.12）；5-shot QOC示例仅+3.1 | 否 |
| H2 选项被遗忘（lost in the middle） | 让模型复述选项：CQO 93.5% vs QOC 94.7% | 否 |
| H3 因果掩码：选项表示在看到上下文前已固定 | 架构对比（decoder 14.72、enc-dec 2.30、encoder≈0）；去上下文后QOC≈QO；阻断选项→上下文注意力使CQO从69.26降到42.46；把CQO选项状态patch进QOC +6.0；选项重复（QOCO）+8.2；CoT把差距从14.72缩到7.47 | 是 |

模型：21个decoder-only（LLaMA3、Qwen2.5/3、Gemma2，0.5–9B）+Flan-T5/BERT族+Mamba/FalconMamba/Qwen3-Next/Dream扩散LM+Gemini。数据：LogiQA、SciQ、RACE。附录F形式化：QOC下 I(h_O; C | Q,O)=0。

## 3. 对本workbench
- 直接解释E03/E07/E08的“句先/题先”大反转为什么存在：题先时问题与选项表示先于句子固定，匹配只能在最后位置一次完成。前任把这当成待修仪器，其实它是已有owner的架构事实，E00–E12一天半的协议修补大部分可以省。
- 与我们对象的区别：他们的“旧表示不能被后文重写”是关于**问题/选项**的；我们的是关于**句内早期动词/名词的依赖**。但同一逻辑适用：GP句中“the suspect sent the file”在读到“deserved”之前已固定为主动读，后面的token可读它但不能改写它；替代依赖必须在后面位置**重新计算**。这给“重建失败”一个架构层面的候选解释，并给出预测：把替代依赖题的问句放在句后（CQO式）优于句前；思维链或重复句子应部分缓解（E52 R1重读没有缓解，是反证之一，需重看其条件）。
- 可借动作：QOCO式“重复关键片段”作为低成本干预对照；架构对比（扩散LM/双向）作为机制判别。
