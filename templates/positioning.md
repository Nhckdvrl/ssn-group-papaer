# 定位表（D5；主旨改变、主张升到 L2、进候选前、投稿前更新）

来源：`python3 tools/venue_corpus/query.py nearest "<当前一句话主旨>" -k 15` 的接收论文与 near-miss 拒稿 + 最新 arXiv（awesome 列表 / daily 镜像）。

| 近邻 | 会议 / arXiv | 它的 claim | 设定 | 方法 | 证据类型与规模 | 我们的增量（一句话） |
|---|---|---|---|---|---|---|

- **精确撞车**：claim、证据类型、设定高度重合且写不出实质增量。
- **Compression risk**：即使三项不全同，只要 reviewer 可能压缩成“同 claim，只换模型/数据/场景/规模”，就单独标出来，并解释该差异为什么 load-bearing。
- 强预印本与已接收未出版工作也会占具体 claim；它们不自动杀 territory，但不能忽略 ownership。
- 撞车/压缩风险出现时先调整增量（设定差异必须有科学含义；也可换证据类型 / 加方法 / 加理论 / 新 consequence），调整不了再在人审中讨论。
