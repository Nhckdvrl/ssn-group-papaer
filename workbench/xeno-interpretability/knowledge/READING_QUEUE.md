# 文献核查与精读队列 — Xeno

**首轮核查：2026-10-12。** 下表是**索引与 triage，不等于深度读论文**。同一篇论文每次升级状态要附正文、图表、实验卡与对应判断，绝不凭标题写技术细节。

- 推荐顺序：先两篇基础综述建立全域地图；其次 NeurIPS 2026 直接近邻与 ICLR/ICML 2026、2025 的强实证；最后才是新 arXiv 最新趋势。遇到概念近邻必须追到 parent 与后继，而不是只引用原论文。
- 原则：venue 要核验 primary/main/spotlight/workshop/position；NeurIPS 的 Downloads 页面列出标题，不自动证明主会身份或质量。
- 状态说明：INDEX=沿用仓库已有知识索引；ABSTRACT=本轮核查公开摘要； TITLE_ONLY=仅标题确认； FULL_TEXT=读完方法实验附录； REPRODUCED=代码数字复现。

| 优先级 | 论文 | 场所/形式 | 本次核查深度 | 为什么读 |
|---|---|---|---|---|
| 01 | [Xeno-Interpretability: Investigating the Alien Minds of LLMs](https://arxiv.org/abs/2609.20408) | arXiv 2609.20408 | SOURCE-PAPER | abstract/outline + supplied first page checked | 问句的原始提出；不是已验证 xeno 发现 |
| 02 | [Interpreting Language Models Through Concept Descriptions: A Survey](https://aclanthology.org/2025.blackboxnlp-1.8/) | BlackboxNLP 2025 | ABSTRACT | 先建立语言解释与自动评估谱系 |
| 03 | [Unboxing the Black Box: A Survey on Mechanistic Interpretability for Algorithmic Understanding of Neural Networks](https://link.springer.com/article/10.1007/s10994-026-07129-4) | Machine Learning 2026 | ABSTRACT/INTRO | 机制解释的定义、工具分类与因果标准 |
| 04 | [Revising and Falsifying Sparse Autoencoder Feature Explanations](https://papers.neurips.cc/paper_files/paper/2025/hash/5b6ce2529a79862a2d8ac57ac0e01d90-Abstract-Conference.html) | NeurIPS 2025 Main | ABSTRACT | 负样本反证宽泛解释、结构化描述 |
| 05 | [Are Sparse Autoencoders Useful? A Case Study in Sparse Probing](https://proceedings.mlr.press/v267/kantamneni25a.html) | ICML 2025 | ABSTRACT | SAE 对强简单基线是否真有实际优势 |
| 06 | [Concept frustration: Aligning human concepts and machine representations](https://arxiv.org/abs/2603.29654) | 2026 preprint; appears on NeurIPS 2026 listing | ABSTRACT | 真正直接的近邻：任务相关几何识别已知概念体系遗漏 |
| 07 | [Concept-Based Mechanistic Interpretability Needs a Concrete Evaluation Paradigm](https://zenodo.org/records/20444131) | Zenodo 2026; appears on NeurIPS 2026 listing | METADATA/TITLE | 评价范式的新问题；需读全文和确认会议轨道 |
| 08 | [Conclusions from Circuit Extraction Depend on the Level of Description: A Controlled Comparison](https://neurips.cc/Downloads/2026) | NeurIPS 2026 listing | TITLE-ONLY | 解释结论可能取决于描述层次，尚未阅读论文 |
| 09 | [Mechanistic Interpretability Needs Philosophy](https://neurips.cc/Downloads/2026) | NeurIPS 2026 listing | TITLE-ONLY | 概念与解释的哲学基础，须核查全文 |
| 10 | [Mechanistic Interpretability Should Prioritize Feature Consistency in SAEs](https://aclanthology.org/2026.acl-long.99/) | ACL 2026 | INDEX/ABSTRACT | 跨训练一致性与表示单位有效性 |
| 11 | [MIB: A Mechanistic Interpretability Benchmark](https://proceedings.mlr.press/v267/mueller25a.html) | ICML 2025 | INDEX/ABSTRACT | 因果介入的标准 baseline 和 failure analysis |
| 12 | [SAEBench](https://proceedings.mlr.press/v267/karvonen25a.html) | ICML 2025 | INDEX/ABSTRACT | SAE 多维度实用性评价与负对照 |
| 13 | [Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability](https://www.jmlr.org/papers/v26/23-0058.html) | JMLR 2025 | INDEX | 从相关性到干预保持的抽象 |
| 14 | [The Non-Linear Representation Dilemma](https://proceedings.neurips.cc/paper_files/paper/2025/hash/dbb98528c9870377f3f0d133aae6050b-Abstract-Conference.html) | NeurIPS 2025 | INDEX | 表达过强导致伪因果对齐；必备负对照 |
| 15 | [Sparse Autoencoders Trained on the Same Data Learn Different Features](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3c1fe56b043848b211030c202764c6a7-Abstract-Conference.html) | ICLR 2026 | INDEX | SAE 字典不唯一；模型表征 vs 分解器输出 |
| 16 | [Bypassing PC1 Makes SAEs More Reproducible](https://chenhaot.com/papers/) | NeurIPS 2026 (author-listed) | TITLE/SELF-REPORT | 排除数据方向/优化假象，官方轨道和全文待核 |

## 精读出入账
每篇阅读卡（`papers/`）必须答：背景→parent→压力→具体 idea 来源（DOCUMENTED or RECONSTRUCTED）→精确近邻与增量→设计强弱→关键混杂→我们能模仿的研究动作。

## 随读随更新的专题检索池
- 优先检索 **NeurIPS 2026** 已公开论文中 interpretability, SAE, representation alignment, circuits, concept discovery, probing, causal abstractions；逐篇核验论文身份、全文和公开评审。
- 同口径看 **ICML/ICLR/NeurIPS 2025–2026, ACL/EMNLP/NAACL 2025–2026, CVPR/ICCV**；多模态概念发现尤其查 CV 与 VLM。
- 2026 最新 arXiv 作为召回补充；记录日期、版本、强近邻及可复现性，不凭名校作者直接相信结论。
- 对每条新提出的 idea，必须有 3–5 篇最近邻的对照表和真实的压缩风险诊断；不要求零近邻。
