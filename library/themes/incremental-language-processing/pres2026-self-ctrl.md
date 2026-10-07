# Self-CTRL：独立行为与说明之间的一致性训练（arXiv2026，MIT CSAIL） `[证据级别：主文精读，范围如下]`

- 阅读时间：2026-10-08T06:36:08.611429+08:00
- 原文：[pres2026-self-ctrl](https://arxiv.org/abs/2606.18327v1)；本地/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07/pres2026-self-ctrl.pdf，SHA 476a0272d1be3789f30f7552735bb215fe91d0ffb0ae7f4eb6db94ec92b095b1。
- 范围：Author v1 main1-6 pp1-13 all, AppB-F pp20-25 all, G/H pp25-29 text, I/J pp29-33 all; figs pp9/31 visual. AppA full examples/K full table not read; code unverified.

1. **形态/压力：** 明确训练接口+功能泛化。标准每prompt好答案不保证模型描述的rule能预测另prompt下实际行为。
2. **idea来源（RECONSTRUCTED）：** simulatability解释评价→把独立的meta/object输出成对打分→分别更新说明或行为；相对RLAIF单独奖励answer，改变关系对象而非更换RL优化器。
3. **方法：** GRPO风格同侧K候选对另一侧highest-prob reference；lambda控制两边更新。coin rule程序定义Bernoulli，jury自然语言用八伦理框架/反框架提示，但共享base backbone而非八独立模型；lexical生成概率信号太弱转compliance SoftYN，作者明确承认。
4. **规模：** 100coin，50双监督/40RL/10held-out，29000 SFT例每epoch；SpecEval756训练/84验证、两类/两原则holdout、400borderline新prompt；Llama8B+Qwen8B LoRA。coin约10H100h、每constitutional run24H100h，seed42、按val consistency选ckpt。
5. **最近邻距离：** Consistency Position给总框架，Hase/Potts解释评价，self-knowledge/OOC推断，RLAIF/ConstitutionalAI单输出；新在明确双向meta–behavior训练后果，不声称一致性发明。
6. **结果/短板：** coin10held-out R²约.64，Llama说明NSG高而behavior安全高；NSG受行为变易预测影响，J已解释。Qwen初始几乎都compliance，jury高分却refusal边界没被识别；I是完整负/异质case，不隐藏。wildchat behavior non-refusal99→90%，不能笼统叫完全无代价。有限类/一个seed不是一般完美可解释。
7. **可迁移动作：** 从双向训练分开能发现机制压力，而非只记平均gain；先问数据是否同时探到边界两侧，保留强近邻自己的失败分析。
8. **对我们：** 一般解释≠行为、consistency会有fixed point均已有owner。E98 Min No98/100也要看正例而非87.5%高总分。当前I07若有增量在具体歧义信息何时失去选择credit，不能把这篇的jury替换当新idea。
