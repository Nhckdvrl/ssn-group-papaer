# Zhao, Qin, Alvarez-Melis, Kakade, Saphra — Random Scaling of Emergent Capabilities（arXiv 2502.17356 v5；早期版本名 Distributional Scaling Laws for Emergent Capabilities）

**原文**：[arXiv v5 HTML](https://arxiv.org/html/2502.17356v5)。**阅读范围**：正文主体。会议信息来自第三方聚合页，未核实。

## 结论
能力在种子间双峰（要么学会、要么完全不会），成功概率随规模平滑上升；“突然涌现”是单 run 曲线落在众数上的假象；连续损失指标下双峰仍在；深度主要影响成功概率、宽度影响成功后的水平。

## 设置
合成任务（计数 250 种子、加法 200 种子，长度泛化）；语法泛化（3–6 层，80 种子）；Qwen2.5-0.5B / 1.5B 重初始化最后注意力层与输出头后继续训练（MMLU 混合比例，每比例 80 / 20 种子）。

## 没做的
无机制分析；不使用真实多种子预训练检查点（Pythia / PolyPythias）；不检验能否从早期检查点预测成败；作者写到外推需要预测成功涌现的概率。

## 与 E92 的对照
E92（PolyPythias 14M–410M × 10 种子，42 个任务）的终点：**正常 run 的种子差异是逐任务、彼此近乎独立的小幅连续波动，不是双峰**；失败尾部是 run 级事件（410M seed3 / 4 的 spike；31M seed8 的格式偏好）。真实预训练（≤410M、这批任务）中，“能力抽签”式双峰并不常见。
