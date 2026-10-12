# 阅读审计 · 2026-10-12

这是**完成/未完成记录**，不是备忘录堆叠。详细实验和 idea 来源见 [CORE_READS.md](papers/CORE_READS.md)。

## 论证与主要实验已完成核查
- **FULL**：[Xeno](papers/PIERUCCI_2026_XENO.md) v2 全 45 页；[Geiger JMLR2025 Causal Abstraction](https://www.jmlr.org/papers/volume26/23-0058/23-0058.pdf)；[Sutter NeurIPS2025 Non-Linear Dilemma](https://pdfs.assets.alphaxiv.org/2507.08802v2.pdf)；[Paulo/Belrose ICLR2026](https://pdfs.assets.alphaxiv.org/2501.16615v2.pdf)；[Goyal et al. NeurIPS2025 Spotlight](https://proceedings.neurips.cc/paper_files/paper/2025/file/5faf0f518f39e4d6b2b595e3ca2fe0c4-Paper-Conference.pdf)；[Sheng/Fu 2026 preprint](https://pdfs.assets.alphaxiv.org/2607.18921v1.pdf)；[Williams et al. 2025 position](https://arxiv.org/pdf/2506.18852)。
- **MAIN+METHODS**：[Feldhus/Kopf 2025 survey](https://aclanthology.org/2025.blackboxnlp-1.8.pdf)；[Ma NeurIPS2025](https://papers.neurips.cc/paper_files/paper/2025/file/5b6ce2529a79862a2d8ac57ac0e01d90-Paper-Conference.pdf)；[Ma ICML2026](https://arxiv.org/pdf/2601.05679) v7；[Torop NeurIPS2026](https://arxiv.org/pdf/2608.02957)；[Parisini 2026](https://arxiv.org/pdf/2603.29654)；[MIB ICML2025](https://pdfs.assets.alphaxiv.org/2504.13151v2.pdf)；[SAEBench ICML2025](https://pdfs.assets.alphaxiv.org/2503.09532v4.pdf)；[Gurnee et al. 2026 J-space](https://www.transformer-circuits.pub/2026/workspace/index.html)；[Li et al. ViSAE ICML2026](https://pdfs.assets.alphaxiv.org/2606.06664v1.pdf)（19页原文主要方法/表4–8已核）。
- **PARTIAL**：[Wang et al. IJCAI2026 CBM Survey](https://www.ijcai.org/proceedings/2026/0892.pdf)；[Song et al. ACL2026 SAE consistency](https://aclanthology.org/2026.acl-long.99/)（正式版摘要、早期原文部分）。
- **ABSTRACT**：[ViSAE ICML2026](https://proceedings.mlr.press/v306/li26s.html)（正式 PMLR 摘要＋仓库）；[NeuroFaith](https://openreview.net/pdf?id=s61y3S7GiT)（学术 PDF 原文受访问挑战，不升级）；[Flow-NLA](https://arxiv.org/abs/2609.33702)（最新 arXiv，尚未完整评审）；[NLA reconstruction faithfulness audit](https://arxiv.org/abs/2607.20379)（最新 arXiv）。

## 无法凭空“完成”的三份直接邻域论文
| 论文 | 已确认 | 仍缺 |
|---|---|---|
| [Tang et al. Concept-Based MI Needs a Concrete Evaluation Paradigm](https://zenodo.org/records/20444131) | Zenodo 元数据及 NeurIPS2026 **Position Paper Track** 信息、作者研究简介 | 官网 PDF 下载连接超时，多入口无法提取完整方法/实验。**未精读，不得写结果** |
| [Delisle & Tan, Bypassing PC1 Makes SAEs More Reproducible](https://chenhaot.com/papers/) | 作者主页列 NeurIPS2026 | 未找到可访问全文，**TITLE ONLY** |
| [Conclusions from Circuit Extraction Depend on the Level of Description: A Controlled Comparison](https://neurips.cc/Downloads/2026) | NeurIPS2026 官方题名目录 | 作者/论文原文及具体 conference track 未核，**TITLE ONLY**。近邻 [Sheng/Fu 2026 preprint](https://arxiv.org/abs/2607.18921) 已独立读完，**不声称两者为同篇** |

**审计标准：** 若官方目录将主会、position、workshop 混在一起，不得仅依目录断言接受轨道；摘要、标题、博客都不能替代方法与主表。2026 新论文出现或 PDF 可获取时回到本表补齐。不为临时不可访问材料造“已知结论”。

**本轮并未运行任何复现实验。** 下一步如需实验，先由 user 确认 ACTIVE 状态与具体经文献审查的研究问题，再创建标准 E## 卡。
