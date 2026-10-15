# 种子间能力差异、发育与失稳：近邻地图（2026-10-15）

为 E90–E92 找参照系而读。阅读深度：标注“摘要”者只读了摘要/页面；其余读了正文主体（HTML），未读附录全部，未复现代码。

| 工作 | 已经回答了什么 | 没有回答的（与我们相关） |
|---|---|---|
| Wang, Hoogland, van Wingerden, Furman, Murfet, *Differentiation and Specialization of Attention Heads via the Refined LLC*（ICLR 2025） | 2 层纯注意力模型中，各头的 refined LLC 曲线先相似后分化，按曲线聚类可还原 previous-token / induction / multigram 等类型；multigram 回路与 induction 竞争，部分 multigram 在 8.5k–50k 步从第 0 层迁到第 1 层 | 只在 2 层小模型；不讨论哪个头成为哪类、跨种子的差异（附录 G 有种子比较，未读到） |
| Singh, Moskovitz, Dragutinovic, Hill, Chan, Saxe, *Strategy Coopetition Explains the Emergence and Transience of ICL*（arXiv 2503.05631，摘要） | 玩具设置中 ICL 与“受上下文约束的权重内学习”共享子电路、先合作后竞争，ICL 是暂时的 | 自然语言预训练中的对应 |
| Zhao, Qin, Alvarez-Melis, Kakade, Saphra, *Random Scaling of Emergent Capabilities*（arXiv 2502.17356 v5） | 合成任务（200–250 种子）、语法泛化（80 种子）、Qwen2.5 重初始化后继续训练：能力在种子间双峰，成功概率随规模平滑上升；深度影响成功概率、宽度影响成功后的水平 | **无机制分析；未用真实多种子预训练检查点；未检验早期可预测性**；作者写到外推需要预测成功概率 |
| Baherwani, Chen, Qiu, Wilson, Izmailov, *Emergent Capabilities Arise Randomly from Learning Sparse Attention Patterns*（arXiv 2606.25010） | Pythia 14M–410M 各 10 个种子：重复、模式补全、IOI 在随机时间点突然出现，大模型平均更早；把出现归因于任务相关注意力模式的突然学会（把出现后的注意力分数修补进出现前模型可恢复差距）；合成任务中稀疏 / 长上下文模式更难学 | **只研究初级能力；不分析失败种子为何失败；假设学会后不回退**；更复杂、依赖上下文的模式“可能性质不同” |
| Şahin, Feucht, Belfki, Wendler, Bau, Brinkmann, Mueller, *In-Context Learning Without Copying*（arXiv 2511.05743 v2） | 1B、40B token：把可由 induction 预测的位置从损失中去掉，induction 头更少更弱，抽取式 ICL 变差，抽象 ICL 多数持平或更好 | 已基本回答“抽象 ICL 是否必需 induction”，我们不再追此题 |
| PolyPythias（van der Wal et al., ICLR 2025） | 50 个 run 聚合指标稳定；只有 410M seed3、seed4 异常并伴 loss spike（附录 A 图 5，未给步数），HMM 训练图有分叉 | 异常的内部后果；逐任务的种子分布 |
| Kimi K2（2025）；Wortsman et al. 2023；Zhai et al. 2023；arXiv 2505.15548 | 注意力 logit 增长 / 熵塌缩导致失稳；K2：只有少数头 logit 爆炸，逐头 QK-Clip；2505.15548：短程依赖使 logit 快速增长 | 真实发生的 spike 中是哪种功能的头（E91 只作便宜的排除项） |
| *Transport Instability Coordinates*（ICML 2026，摘要） | loss spike 预警；附带审计 PolyPythias-410M 异常窗口 | 机制层面 |

## 对我们的意义
- “能力在种子间双峰”本身已被提出（Zhao/Saphra），“初级能力在随机时间出现、与注意力模式突变相连”也已被展示（Baherwani）。
- 留下的空白是**解释性的**：真实预训练里更复杂能力的种子差异从哪里来——学习过程本身的分岔，还是优化事故后的不可恢复？失败是“从未学会”还是“学会后丢失”？能否早期预测？E90 已给出 2 个“事故 + 重学按发育顺序、后期能力不回来”的样本，E92 用 50 个 run 的整体测量检验它是不是普遍来源。
- 若 E92 显示复杂能力普遍双峰且多由事故造成，这与 Zhao/Saphra 的“学习竞争”解释形成对照，是需要正面回答的分歧；若多为学习分岔，则回到机制（E89 探针）找分岔前后的差异。
