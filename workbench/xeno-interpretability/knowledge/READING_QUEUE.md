# 阅读进度和待核查的近邻（2026-10-12）

**阅读事实单独记账**，不能把搜到标题、摘要、方法片段写成读完全篇。所有 `MAIN+METHODS` 也不意味着整个 appendix 已核。

| 优先 | 论文（原文链接） | 会议/形态 | 阅读范围 | 下个问题 |
|---|---|---|---|---|
| ✓ | [Feldhus & Kopf, concept descriptions survey](https://aclanthology.org/2025.blackboxnlp-1.8.pdf) | BlackboxNLP 2025 workshop | **MAIN+METHODS** | 描述→模拟→干预三种标准；见精读 |
| ✓ | [Wang et al., CBM survey](https://www.ijcai.org/proceedings/2026/0892.pdf) | IJCAI 2026 Survey Track | **SECTIONS**（分类、方法、挑战） | 自动概念发现的“发现”到底定义为何；见精读 |
| ✓ | [Ma et al., Revising and Falsifying SAE Feature Explanations](https://papers.neurips.cc/paper_files/paper/2025/file/5b6ce2529a79862a2d8ac57ac0e01d90-Paper-Conference.pdf) | NeurIPS 2025 main | **MAIN+METHODS**、表1/图3–5、部分 appendix | 解释精确度和计算功能脱钩；见精读 |
| ✓ | [Ma et al., Do SAEs Identify Reasoning Features?](https://arxiv.org/pdf/2601.05679) | ICML 2026 main | **MAIN+METHODS**、附录 E/G 部分 | **用 v7，勿抄更旧的 v1 数字**；见精读 |
| ✓ | [Torop et al., Inverted Detection and Control in Steering Vectors](https://arxiv.org/pdf/2608.02957) | **NeurIPS 2026**（官网名单和作者信息可核） | **MAIN+METHODS**、实验与部分附录 | 强检测≠同向控制；见精读 |
| ✓ | [Parisini et al., Concept Frustration](https://arxiv.org/pdf/2603.29654) | 2026 preprint | **MAIN+METHODS**、附录设置与统计表 | 真实任务的 C3 是预先选定；见精读 |
| △ | [Song et al., Feature Consistency in SAEs](https://aclanthology.org/2026.acl-long.99/) | ACL 2026 main long | **ABSTRACT + 可得早期版本片段** | 读全篇 PW-MCC 与随机种子预算；见精读摘录 |
| → 1 | [Concept-Based Mechanistic Interpretability Needs a Concrete Evaluation Paradigm](https://zenodo.org/records/20444131) | 2026 Zenodo，NeurIPS 官方题目目录可见 | **TITLE/METADATA ONLY**，PDF 下载未成功 | 直接 ownership！必须全文核查，再判定会议 track |
| → 2 | [Conclusions from Circuit Extraction Depend on the Level of Description](https://neurips.cc/Downloads/2026) | NeurIPS 2026 名单 | **TITLE ONLY** | 找全文；与粒度/归因风险直接相关 |
| → 3 | [Bypassing PC1 Makes SAEs More Reproducible](https://chenhaot.com/papers/) | 作者列 NeurIPS 2026 | **TITLE ONLY** | 如何区分优化/几何伪影 |
| → 4 | [Sutter et al., The Non-Linear Representation Dilemma](https://proceedings.neurips.cc/paper_files/paper/2025/hash/dbb98528c9870377f3f0d133aae6050b-Abstract-Conference.html) | NeurIPS 2025 main | **ABSTRACT** | 非线性匹配过强的无效性定理与对照 |
| → 5 | [Paulo & Belrose, SAEs Trained on the Same Data Learn Different Features](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3c1fe56b043848b211030c202764c6a7-Abstract-Conference.html) | ICLR 2026 main | **ABSTRACT** | 理解 overlap 怎么定义、跨方法等价类 |
| → 6 | [MIB](https://proceedings.mlr.press/v267/mueller25a.html)；[SAEBench](https://proceedings.mlr.press/v267/karvonen25a.html) | ICML 2025 | **ABSTRACT / repo index** | 先核两个 evaluation protocol 和简单 baseline |
| → 7 | [Sheng & Fu, Circuit Claims Depend on What Is Extracted and How It Is Compared](https://arxiv.org/abs/2607.18921) | 2026 preprint | **ABSTRACT** | 三种抽取对象与比较粒度；注意非 peer-reviewed claim |
| → 8 | [ViSAE / Inside the Visual Mind](https://proceedings.mlr.press/v306/li26s.html) | ICML 2026 main | **ABSTRACT** | ViT 的 vocabulary coverage / spurious cue 检验 |
| → 9 | [Causal Abstraction](https://www.jmlr.org/papers/v26/23-0058.html) | JMLR 2025 | **ABSTRACT / repo index** | 中介因果与干预预测的界限 |

**高优先级补查方式：** 在 NeurIPS 2026 完整名录中按 *interpretability / concept / causal / circuit / representation* 重新筛，而非只围绕 “xeno” 术语；核对主会、workshop、position、公开 code 与实际假设。最新 arXiv 仅用于补充和避免 claim 撞车。

**下一篇精读的准入：** 必须读原文关键图表/实验，不只写“做了什么”；写 parent、压力、发明该实验的 **RECONSTRUCTED** 路径、相对 3–5 最近邻的证据差异，并指出哪条我们的竞争解释受到影响。
