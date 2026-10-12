# How can embedding models bind concepts?（ICML2026正式）`[证据级别：主文全文]`

[正式页](https://proceedings.mlr.press/v306/uselis26b.html)；Tübingen/KAIST Uselis、Koishigarina、Oh。正式28页PDF SHA17b88854068e0f50c97ce343592a4299003dcf327c6a52c1c322eadee017191b。Main1–6及limitations pp1–9全部读；AppB pp14–16、C1–4 pp17–20、D6–7 pp25–26已读，Figs4/6–9与Tables2–5视觉核对。D1–5/E完整与代码未读。首个无代理raw请求超时，普通论文连接成功；不是HF下载，原PDF外置。

**Source-grounded record.** The paper separates concept recognition from object recognition and explains why CLIP’s within-modality binding can coexist with cross-modal failure. Scene embeddings support additive object replacement, but concept-to-object mappings generalize poorly under MLP, random-forest and XGBoost approximators. CLIP text object-based reconstruction reaches R² .92; concept-based reconstruction reaches .84. Removing concepts leaves object decoding largely intact. Controlled dual encoders, approximately 20M parameters each, learn systematic binding with sufficient object coverage. Multiplicative approximators outperform additive ones on held-out objects. The experiments use synthetic structured scenes; complexity is relative to the approximator family. The appendix selects approximator configurations by test object accuracy, so reported best performance is an upper envelope. Main text describes two concepts in the multiplicative setup while plots include three-concept cases; the pixel appendix’s two concepts with 50 values conflicts with its stated 6.5 million object combinations. These discrepancies remain unverified against code.

**idea来源（我的重构）：** 起点是两个已存在的观察互相不对齐，而不是空白题：行为像bag-of-concepts，probe却能恢复object。先证明object确实可作功能单元，再改变问题尺度，从“有没有binding”到“绑定函数是否能被两种用途共同泛化”。最后构造存在性对照说明旧模型失败不是embedding架构的定理。这是一条解释而非只刷点的叙事；简单函数的拟合成功还不是模型内部实际乘法算法的因果认证。

**与近邻的距离：** Feng的token绑定ID和CLIP单模态probe都提供起点；本文换成单向量场景的函数复杂度/跨模态对齐。我们的旧源库干预只是功能迁移，还没有解释修订前后的关系如何对齐；一般“内部有而答案未用”不能独占。不能照搬小MLP失败就宣称语言角色函数高复杂度。

**对我们：** 有价值的研究动作是把熟悉的矛盾改写为一个能预测新情形的对象，并用另一种实现证明不是必然限制。E82仍有完整关系错误，E85正在复用自然词义材料定位可修订功能的范围；两者任务不同，不能像两个相同encoder一样直接认定共同几何。下一因果实验应使关系重绑与输入拒绝产生不同可观察后果，而不是多做一个可读probe或平均attention图。
