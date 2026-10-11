# I16 文献与科学复核知识库

> 更新：2026-10-11。存放位置遵照研究者要求：**workbench 内，不写入仓库根目录 `library/`**。
> 本目录是一次研究审计及以后重开 I16 的科学参考，**不是**实验恢复、状态升级或论文主张确认。

## 读取顺序

1. [I16_SCIENTIFIC_AUDIT_2026-10-11.md](I16_SCIENTIFIC_AUDIT_2026-10-11.md)：区分现象、可支持主张、统计/代码/理论缺陷，逐项列出需要什么证据才能宣称因果。
2. [PAPER_NOTES_2026-10-11.md](PAPER_NOTES_2026-10-11.md)：关键相邻论文与研究谱系；每篇明确问题、方法、证据、与 I16 的实质重叠及未覆盖区域；按核对深度分级。
3. [NEXT_DECISIONS_2026-10-11.md](NEXT_DECISIONS_2026-10-11.md)：可复用的决定性实验设计，不默认恢复实验；每项说明预期怎样改变对科学问题的判断。

## 证据来源

本次只读复核实际看过以下原始仓库内容：
- [原 idea I16](../ideas/I16-latent-bandwidth.md)、[E21](../experiments/E21-scaling-planning.md)、[E22](../experiments/E22-latent-bandwidth-law.md)、[E23](../experiments/E23-paper-grid.md)、[E24](../experiments/E24-vicreg-generality.md)。
- [原汇总数据](../results/E21_scaling_table.json)、[E23 主表](../results/E23_table.json)、[E23 D_eff](../results/E23_deff_collapse.json)、[官方 224px 锚点](../results/E23_released_anchor.json)。
- [模型结构](../scaling/wm.py)、[训练实现](../scaling/train.py)、[评测/度量视野/SFA](../scaling/eval_plan.py)、[规模统计](../scaling/e23_report.py)、[核恒等式检查](../scaling/kernel_bound.py)、[D_eff 回归](../scaling/deff_collapse.py)。
- 对照论文官方 arXiv/PMLR 页面及可获取正文；具体来源链接和核对层级见论文笔记。

## 纪律

- **[OBS]** 实际实验报告读数；本轮没有重新跑模型，不能称为独立复算。
- **[CODE]** 从已检查的源码可直接确定的实现事实。
- **[PAPER]** 其他作者在论文中报告的结论；未经本机复现，不是我们的实验。
- **[INF]** 本轮推断或重建；需提出竞争解释。
- **[OPEN]** 尚待核实或实验决定的主张。
- 所有“首次／无人研究／已解决”的判断须回论文版本、强最近邻和代码重新核对；不得把预印本当作已录用顶会。
- **不自动恢复已暂停的 E24、E23、训练或跨节点队列**；仅人可决定是否重新开跑、改变工作台状态。
- 早期 `literature/CORE_READINGS.md` 和根目录 `library/themes/latent-world-models` 仍是历史资料，**本轮新增审计以本目录为入口**，不再在其间多处同步相同结论。
