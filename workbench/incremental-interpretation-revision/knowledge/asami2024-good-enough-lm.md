# What Makes Language Models Good-enough?（Asami & Sugawara 2024, Findings of ACL 2024）

**阅读身份：MAIN_VERIFIED_THIS_PASS（作者arXiv v1 HTML，2026-10-12）。** [arXiv 2406.03666](https://arxiv.org/abs/2406.03666)。Findings，不作投稿尺度，作为数据/方法参照。

## 1. 未知与来源
**AUTHOR-STATED**：人类good-enough加工（Ferreira 2003，Christianson 2001/2006）被归因于有限工作记忆；他们问什么架构特征（层数、头数）使LM学到人类式good-enough行为。
**RECONSTRUCTED**：把心理语言学理论里的“资源有限”翻译成Transformer的两个结构超参数，并通过先采人类数据再用匹配分数评估，而不是用金标准确率。

## 2. 设计
- GELP数据集7680 NLI项：8种**无歧义**构式（及物、被动、双宾语、与格、受益DOC/for、经验者主/宾），2种合理性（动物性换位制造不合理），3级记忆负荷（1/2/3命题）。**不含GP。**
- 人类：304名MTurk受试，Christianson式整句消失后Yes/No问答，准确率86.6%；Yes题96.7%、No题76.5%；合理性无效应；记忆负荷92.8/86.2/80.9%。
- 模型：24个BERT微型（L∈{2..12}×A∈{2..12}），SNLI+MNLI+HANS微调；读数是与人类多数答案的匹配率。

## 3. 结果
- 最佳匹配L12–A12 74.3%；层数从8到12几乎不涨；头数作用不清。被动43.5%、三元谓词7.0%的非蕴含项极差；补800个被动/双宾语样本后匹配升到84.3%。

## 4. 对本workbench
- 它把good-enough从GP推广到无歧义结构，并证明“人类No题更差”是一般现象（76.5%）。所以我们在GP上看到的No偏置/Yes偏置要有无歧义对照才能归因到修订。
- 与Emura & Sugawara 2026（双任务）同一谱系：资源约束→合理性启发。我们的对象不是资源，而是晚到证据后的结构重写；两条线可以互为对照。
- 方法启发：用人类多数答案而非逻辑金标评估“人类式”，与我们D0的NEITHER/ENTAILED分层互补。
