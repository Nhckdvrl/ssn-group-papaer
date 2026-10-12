# LEDOM: Reverse Language Model（作者最新v4，July2026，接收未核）

`[证据级别：主文精读＋指定方法附录]` [原文](https://arxiv.org/abs/2507.01335v4)。PKU/UCSB/Arizona/NUS；21页，SHA71cd07bb9919b30da338eadd5b4487b0e44836ca932d8275a9c35405b82e8fdf。仅下载论文，未访问直连HF/下载权重；代码/接收未核。

1. **形态/问题：** reverse-trained open LM＋其行为/评测＋逆向候选反馈；从左到右语言建模的普遍约定换方向，研究未来条件下推过去的能力，再找互补用途。不是首创inverse scoring。
2. **idea来源（RECONSTRUCTED）：** reversal curse、abduction与已有TRLM/双向NMT→同架构/数据/分词的纯reverse模型→以query reconstruction作math重排。一般逆向feedback已在TRLM，本文明确承接；主要资源增量是开放2/7B、435B token、matched forward预训练及step-level应用。
3. **方法：** reverse-order conditional P(x|y)，与forward P(y|x)几何加权；理想共享joint下等于forward likelihood−λlog response marginal＋常数。实际两模型不自动共享校准joint，Bayes等式不能直接认证训练后估计一致；也不推出词面重建等于最终意义正确。
4. **理论须判别：** Proposition1先假设wrong inverse-score更低与forward约相等，再证明重排优势；它没有证明hallucination必降低inverse分。若仅约相等，∀λ>0须比较forward/inverse margin，不能当无条件严格保证。条件熵差等式正确，但较低熵不自动保证truth区分；§2.5同joint全序列下“平均left entropy<right”与两chain-rule总熵相等不一致，有限模型近似误差可不同，不用该段给我们的prefix效应归因。
5. **规模：** 64A100/8强互联节点，7B每模型约628h、2B307h；math reverse SFT 100k OpenMathInstruct2、2epoch/4GPU/1024context/lr1e-5/seed0。反向模型做generation的弱处与反馈的应用分开；病例不认证系统解决reversal curse。
6. **评测/结果：** matched模型2B部分语义bench接近，7B大多低于forward（BoolQ37.77 vs65.69、GSM8K1.74 vs16.83）。Math3专用forward族、4bench；QwenMath AIME16.7→23.3为约2道题提升，无完整CI/多seed。OpenMath2 AMC40→40非严格提升，AIME beam6.7低于greedy10；不复制“全部一致优于greedy”的措辞。
7. **复现边界：** 主表64候选、附录D2.3写4，需代码核；main beam宽4与case2不一致。baseline为greedy/random，缺forward self-likelihood/训练verifier匹配预算比较。Fig3正文称monotonic，但图有下降（blue logN3→4/red5→6），不能当搜索单调规律。Table7只有案例文本，未给全部candidate分数，不是posterior degradation全量验证。
8. **阅读范围：** main1–8/limitations/ethics pp1–9全部；AppA2/3 p13 text全部（p14 hyperparameter表未全核）、D1–4 pp18–21全部；main table4/fig3 p8视觉。其他corpus/benchmark/cases附录未全读；未运行代码。
9. **对I07：** 最近邻已把inverse更偏正确当关键可测假设；我们可以在“同一需要改读的观察”上检验它是否违反，以及哪一段credit造成违反。E107严格/宽松依赖与同Source所有候选的条件比较比泛泛inverse unreliable更具体；仍不是reverse-trained LEDOM方法的反证，也不因同主题自动关线。该题值得追的是语义修订与原观察重建目标的冲突，不是另一个一般重排器。
