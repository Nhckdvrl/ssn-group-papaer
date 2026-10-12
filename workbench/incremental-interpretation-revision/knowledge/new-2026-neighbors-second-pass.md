# 2026-10-12 第二轮检索新增近邻（ABSTRACT_ONLY，三篇；均为 2026 年）

## Baitalik & Datta 2026 — Garden Path Recovery in Causal and Masked Language Models（ACL 2026 SRW, pp.383–392）
- 已知：100 对 GP/对照（NP/Z、NP/S、MV/RR）；因果模型用 surprisal、掩码模型用伪 surprisal；消歧词之后的累计超额 surprisal、AUC 恢复摘要、逐层隐状态与对照的散度。发现：因果模型消歧效应更大（NP/Z 最明显）；双向编码器因右上下文"被缓冲"。主张"GP 评估应强调恢复动态而非终态"。
- 距离：它是 H-C（架构固定）的直接相关工作，但只测在线动态，不测最终解释。我们的 X1 架构对比条件可引用它；他们没有替代依赖读数。SRW 非主会。

## Barenholtz 2026 — Trajectory Dynamics in LM Hidden States Predict Human Processing Costs Beyond Surprisal（arXiv 2606.05346）
- 已知：轨迹外推误差（对前序隐状态拟合直线，看下一状态偏离）与 surprisal 几乎不相关（r=.044），独立预测自定步速阅读时间，GP 句最强；GPT-2 S/M/L、Pythia。
- 距离：又一个"困难"指标；可作 X3 的协变量候选，不是我们的对象。

## Yoshida, Isono, Someya, Oseki, Kuribayashi 2026 — An Existence Proof for Neural LMs That Can Explain Garden-Path Effects via Surprisal（ACL 2026）
- 已知：在 GP 句上微调 LM 使 surprisal 逼近人类 RT，留出项仍成立且自然语料更好；结论：此前负结果是预测分布错配而非 surprisal 理论失败。
- 距离：它说明"LLM 预测分布可以被调到像人"，但没有碰最终解释。对我们的意义：若有人把这类微调模型给出的替代依赖断言率作为对照，可区分"预测像人"与"重建像人"是否同一回事——这是一个可写进 06 §7 的未来反证来源。

## 本轮未能升级为主文的债务
- Hanna & Mueller 2025 正式 PDF、Emura & Sugawara 2026 PDF、Oh & Demberg 2026 PDF 均已下载到本机工具缓存，但环境无 PDF 文本提取库（无 pdftotext/pypdf/fitz）；需在有依赖的环境提取后补卡。Huang & Ferreira 2021 作者稿 403。
