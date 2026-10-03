# A08 — ACL / EMNLP / NAACL 版叙事（与 ICML / ICLR 版 A03–A07 并行保留；2026-10-04）

人的指示：投稿考虑 ACL（或 ICML）；保留现有偏 ICML / ICLR 的叙事，再对齐 ACL 系列论文和获奖论文分析做一套；不写防御性叙事，可以故意留一些问题给审稿人（我们好补）。

## 1. ACL 评审看重什么（对照获奖论文与近邻）
- **获奖论文（35 篇中 21 篇是 ACL）的偏好：**
  - 给现象起名字：Imperfective Paradox、Mind the (DH) Gap、Lying with Truths；
  - 借语言学 / 认知科学的成熟工具“降维打击”：形式语义探针、资源理性编码、构式最小对、形式-意义可学性；
  - 造一把对的尺子、暴露评测问题：MediEval、CAR-bench、CxMP。
- **ACL 系列近邻：**
  - *Language Acquisition Device in LLMs*（ACL'26，先天约束）；
  - *Developmentally-plausible Working Memory Shapes a Critical Period*（ACL'25，关键期）；
  - *How Training Data Shapes the Use of Parametric and In-Context Knowledge*（ACL'26，数据 → 上下文采信）；
  - *Understanding the Prompt Sensitivity*（ACL'26：提示模板对 logits 的影响大于问题本身）；
  - *Flaw or Artifact? Rethinking Prompt Sensitivity*（EMNLP'25）；
  - *Function Words as Statistical Cues for Language Learning*（ACL'26）；
  - *Retrieval Heads are Dynamic*（ACL'26）；
  - *Inferring Functionality of Attention Heads from their Parameters*（ACL'25）；
  - *Convergence and Divergence under Different Random Seeds*（EMNLP'25）；
  - *Robust Estimation of Population-Level Effects in Repeated-Measures NLP Designs*（ACL'25：把多源变异当作特征而不是噪声）。
- **结论：** ACL 版的主轴从“训练动力学的机制”换成“语言模型里什么是先天的、什么是从语料习得的”，用语言习得的经典争论（Chomsky 的语言习得装置 vs 基于使用的习得；Lenneberg 的关键期假说）组织全文；把“Question:”开关（提示模板行为的预训练来源、对上下文忠实度评测的影响）和语料的语言统计放到前台；SGD 温度作为“模型越大越先天”的解释，篇幅缩短。

## 2. ACL 版的主命题
> **What is innate in a language model? Not its knowledge, not its grammar — its anatomy.** 语言模型在读到语料的第一个词之前，seed 就已决定复制回路装在哪些头上；语料教会它其余的一切——知道什么、何时形成回路、如何对待上下文，甚至由 1% 的指令数据教会的一个“看到 ‘Question:’ 才信上下文”的习惯。

**标题候选（标题即结论、带名字）：**
1. **Born to Copy, Taught to Trust: What Is Innate in a Language Model**（首选：前半对应 seed 决定复制回路的位置，后半对应语料教会的上下文采信开关）
2. *What Is Innate in a Language Model? The Seed Places the Circuits, the Corpus Teaches Them*
3. *The Seed and the Corpus: Nature and Nurture in Language Models*

## 3. 摘要（英文草稿）
Is anything in a language model innate? We answer with a natural experiment hidden in public pretraining suites, in which the same random initializations were trained on up to 25 different corpora (DataDecide, 4M–1B parameters) or on two versions of the Pile (Pythia, 70M–12B). What is innate is the model's anatomy. Which attention heads become induction, previous-token, retrieval and six other kinds of heads is fixed by the seed before the model reads its corpus, and recurs on every corpus — so faithfully that a model's seed can be identified from its head layout alone (98–100%), even though its weights keep a correlation of only 0.04 with their initial values. Everything the model knows and does is learned: the corpus sets how strong its circuits are and when they form, there are no lucky seeds on 11 NLP benchmarks, and a 1% slice of instruction data teaches a habit — trusting a counterfactual context only when the question is introduced by the literal template "Question:", not "Q:" — that partly explains template sensitivity in context-faithfulness evaluation. As in Lenneberg's critical period for human language, the innate layout is fixed early, during the first 1–2.5% of training; afterwards even a switch to a new language — source code — no longer rewrites it. And it is shared across corpora as far as their content is shared: the closer two corpora's content-word statistics — what they are about, not how they say it — the more faithfully the same anatomy recurs.

## 4. 结构（ACL 长文 8 页）
1. **Introduction：** 语言习得的先天 / 后天之争 → 对语言模型可以直接做实验（同一初始化 × 25 个语料）→ 钩子（权重忘了 seed，回路记得；1% 的数据教会一个模板习惯）→ 3–4 条贡献。
2. **A natural experiment：** 语料与 seed 的交叉；尺子（“哪一层 / 哪个头”拆分）；一句话的对称性引理（语料原理上不能选择头）。
3. **Innate: where the circuits live：** 9 种头角色；14 个尺寸、2 个家族；出生证明（seed 识别）；权重忘了、回路记得。
4. **Acquired: what the model knows and how it uses context：**
   - 4.1 强度与出现时间；no lucky seeds（11 个 NLP 基准 × 14 个尺寸）；
   - 4.2 **“Question:” 习惯：** 1% 的 Flan；只认字面模板；PopQA、NQ-Swap；OLMo 2 中期训练；60M–1B；出现于预训练 3.6%；对评测的含义：问答格式的上下文忠实度 / 知识冲突评测部分测的是这个模板习惯；提示模板敏感性有预训练数据来源。
5. **A critical period：** Lenneberg 的类比；1–2.5% 锁定；之后换成代码这种“新语言”也改不动；两个尺寸的受控模型 + 公开套件。
6. **What the corpus is about, not how it speaks：** 语料距离规律（每个尺寸、去混杂）；**E64：起作用的是实词分布（讲什么），不是虚词分布（怎么讲）——虚词在英文语料之间几乎不变，控制实词后没有额外作用**；自然语言 vs 代码；SGD 温度一段（模型越大越先天）。
7. **Implications for NLP：**
   - 评测与可复现性：seed 匹配的比较；no lucky seeds；混合效应设计（呼应 ACL'25）；
   - 可解释性：结论按 seed 迁移；
   - 数据研究：数据解释回路是否出现，不解释在哪里；
   - 提示敏感性评测：模板习惯来自预训练数据。

## 5. 贡献（ACL 风格，4 条）
- **A natural experiment on what is innate in language models**: seeds × 25 corpora at 14 sizes and Pythia to 12B.
- **Innate anatomy, acquired function**: head placement is inherited from the seed and identifies it; knowledge, timing, benchmarks and behaviour are learned; no lucky seeds.
- **A critical period shaped by what the corpus is about**: the layout is fixed in the first 1–2.5% of training and shared across corpora in proportion to their content-word statistics (not their function words); code re-draws it.
- **A template habit learned from 1% of pretraining data**, with consequences for context-faithfulness evaluation.

## 6. 图（6 张）
1. 钩子：(a) 25 个语料中最强头的分布（innate）；(b) “Question:” vs “Q:” vs “Query:” 的上下文采信（acquired）。
2. 先天 / 后天地图。
3. 关键期。
4. 讲什么而非怎么讲：距离规律 + 实词 vs 虚词（E64）。
5. “Question:” 习惯：跨尺寸、OLMo 2、出现时间。
6. No lucky seeds。

## 7. 留给审稿人的问题（两个版本共用：正文点到为止，rebuttal 再拿出）
| 审稿人可能问 | 我们手里已有 / 能很快补上 |
|---|---|
| 注意力分数不等于功能 | 只看权重的 OV 复制分数（E59）、消融图与迁移（E42） |
| 只在 DataDecide 上成立？ | Pythia 70M–12B（E44、E58） |
| 是不是数据顺序在起作用？ | E44b、E46 B、E62 只换顺序的对照 |
| 为什么规模越大越先天？ | E62 SGD 温度、E46b2 固定温度放大模型 |
| 开关是 “Question:” 还是问答格式？ | E32 线索拆解（“Q:”“Query:”不触发） |
| 指令微调 / 其他语言 / 其他架构下还成立吗？ | 正文不提；被问时用受控 S 模型很快补（微调、非英语语料） |
| 权重相关 0.04 在十亿参数上也能识别 seed，解剖识别有什么特别？ | 区分“权重的微弱残留”与“可解释的结构”；被问时补权重相关的识别对照 |
| 为什么偏偏是 “Question:”？ | 写成开放问题（E53 暂停），让审稿人问 |
| 出生时什么决定哪个头胜出？ | 写成开放问题（E39 / E41 阴性），用关键期与温度回答 |

## 8. 两个版本对照
| | ICML / ICLR 版（A03 v5） | ACL / EMNLP / NAACL 版（本文件） |
|---|---|---|
| 标题 | The Seed Picks the Slot, the Data Fills It: Nature and Nurture in Language-Model Circuits | Born to Copy, Taught to Trust: What Is Innate in a Language Model |
| 主轴 | 回路的先天 / 后天；对称性破缺；SGD 温度 | 语言模型里什么是先天的；语言习得的关键期；语料的语言 |
| 前台结果 | 继承、seed 识别、关键期、温度、语料距离 | 继承、“Question:” 习惯与评测含义、关键期、语料的语言（虚词） |
| 理论部分 | 对称性引理（一段） | 一句话带过 |
| 跨学科类比 | 发育生物学（protomap、关键期） | 语言习得（LAD、Lenneberg 关键期） |
| 后果 | 可解释性、数据归因、模型比较 | NLP 评测与可复现性、提示敏感性评测、可解释性 |
