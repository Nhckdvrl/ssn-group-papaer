# ARR Responsible NLP Research checklist — 作答草稿（提交时填在 OpenReview 表单）

题目来源：https://aclrollingreview.org/responsibleNLPresearch/ （2026-10-04 核对）。“需要人决定”的条目已标出。

| 条目 | 回答 | 位置 / 说明 |
|---|---|---|
| A1 局限性 | Yes | `Limitations`（正文后、参考文献前） |
| A2 潜在风险 | Yes | `Ethics Statement`：只用公开模型与数据；报告公开检查点的初始化与标签不符，用于正确使用公开资源 |
| B1 引用所用资源的作者 | Yes | §2、§4.1、附录 G：DataDecide、Pythia、PolyPythias、OLMo 2、Dolma、Flan、ParaConflict、PopQA、NQ-Swap |
| B2 许可证 | Yes | 附录 G：DataDecide 模型 Apache 2.0、数据配方 ODC-BY；Pythia / PolyPythias / OLMo 2 Apache 2.0；ParaConflict Apache 2.0；NQ-Swap MIT；PopQA 按作者发布条款（HF 页面未标许可证，**需人核对**） |
| B3 使用是否符合预期用途 | Yes | 附录 G：均用于研究 |
| B4 个人信息 / 冒犯内容 | N/A | 不新收集或发布数据；只用公开基准的反事实提示（实体为国家、公司、作者等公开事实） |
| B5 资源文档（领域、语言） | Yes | §2、附录 G：英文网页语料、代码、论文、书籍 |
| B6 统计量（样本数等） | Yes | §2、§4.1、附录：模型数（75 / 69 / 800+）、条目数（ParaConflict 共同已知 1680 条、PopQA 1299 条、NQ-Swap 3533 / 3750 条） |
| C1 参数量、算力、硬件 | Yes | §2（模型尺寸 4M–12B）、附录 D（受控模型结构）、附录 G（A100 80GB，约 200 GPU 时） |
| C2 实验设置与超参 | Yes | 附录 D、附录 E（受控预训练与 SGD 温度） |
| C3 描述统计（均值 / 误差 / 次数） | Yes | 全文报告均值 ± SE、bootstrap 区间、置换 / Mantel 检验；附录 H |
| C4 所用软件包与设置 | Yes | 附录 G：PyTorch、Transformers、SciPy；bf16、eager attention |
| D1–D5 人类受试者 | N/A | 无人工标注或受试者 |
| E1 AI 助手 | **需人决定**：如实填写（例如“用于代码编写、文献检索与语言润色，所有内容经作者核对”），录用后在 Acknowledgements 写明范围 | ARR CFP 要求 |
