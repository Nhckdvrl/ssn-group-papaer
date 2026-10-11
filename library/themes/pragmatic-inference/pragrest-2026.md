# PragReST: Self-Reinforcing Counterfactual Reasoning (arXiv2026)

来源：[primary](https://arxiv.org/abs/2606.18624)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 正文及关键A/B/D已读；其余附录与原code运行未完成。
2. **背景与压力：** 推断隐含意图不只需logic，缺替代说法与speaker counterfactual。
3. **改变前提 / idea来源：** 自生成counterfactual推理后SFT/GRPO，来源DOCUMENTED：alternative-based pragmatic explanation。
4. **方法 / 数据 / 证据：** 多pragmatic benchmarks；human judge校准100条precision .780，错误tag κ .628；含unsupported/overextension，非仅hit-side gain。
5. **短板与校对：** 训练与judge/data质量可能混杂；counterfactual解释提高不能证明自然语境license全面改善。资产未复现的数字按原论文标而非自己结果。
6. **最近邻与claim ownership：** counterfactual训练、过强推断错误都已有ownership。本轮先frozen测真实边界，不为讲新method重复训练pipeline。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
