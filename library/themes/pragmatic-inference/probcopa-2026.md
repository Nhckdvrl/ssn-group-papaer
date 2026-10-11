# Humans and LLMs Diverge on Probabilistic Inferences (TACL2026)

来源：[primary](https://aclanthology.org/2026.tacl-1.93/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 正文1–9页methods/results/主要related已读；后段related与B/C附录未全读。public probabilistic-reasoning repo b983b12dd3b5b0efd01ee7f990ea5c5791a6d4d1。
2. **背景与压力：** 离散causal gold无法表示人类有限信息下的合理分歧。
3. **改变前提 / idea来源：** 判断对象改为human概率分布。DOCUMENTED：COPA原因→结果，不混反向解释；词汇差异holdout验证。
4. **方法 / 数据 / 证据：** 210项105pairs，328人，每题25–30判断，8reasoning模型×30采样。口头0–100概率而非raw probability；human间差异更大，models回避中间概率；temp/persona不足以消除。
5. **短板与校对：** 多次model采样与多个人不是同样uncertainty；unimodality检验未拒绝不等于证明单峰。人类偏差分布不自动是规范gold。
6. **最近邻与claim ownership：** 完整human分布与温度不能修复的gap已有ownership。E17只检验受限likelihood与实际生成支持是否一致；必须对齐mean MAE与sample MAE。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
