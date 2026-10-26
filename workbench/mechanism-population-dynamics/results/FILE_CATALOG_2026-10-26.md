# 工作台文件目录元数据快照（2026-10-26）

扫描时间：2026-10-26T05:43:39+00:00 至 2026-10-26T05:43:51+00:00。工作台内共有 **20,221** 个文件/软链条目，表观字节合计 **3.41 GiB**，其中软链 **0** 个。完整逐路径元数据见 [file_catalog_2026-10-26.json](file_catalog_2026-10-26.json)。

本快照遍历工作台实际目录，包括被git忽略的raw/cache；不进入`.git`，不跟随软链，不读取内容或计算哈希。`bytes`为`lstat`表观大小，软链计的是目标文字长度；汇总会重复计算硬链接，**不代表增量或实际已分配磁盘占用**。遍历并非原子操作，mtime只反映当时观测。清单自身的JSON和本页不列入快照。

## 顶层目录

| 顶层 | 文件/软链 | 软链 | 表观大小 |
|---|---:|---:|---:|
| `results` | 19,496 | 0 | 3.40 GiB |
| `scripts` | 367 | 0 | 4.04 MiB |
| `paper-acl-v2` | 40 | 0 | 1.73 MiB |
| `paper-acl-v1` | 36 | 0 | 1.56 MiB |
| `paper-acl-v0` | 31 | 0 | 1.36 MiB |
| `paper-acl-v3` | 32 | 0 | 1.11 MiB |
| `experiments` | 123 | 0 | 699.25 KiB |
| `knowledge` | 73 | 0 | 340.19 KiB |
| `logs` | 14 | 0 | 147.01 KiB |
| `(root)` | 8 | 0 | 144.03 KiB |
| `.claude` | 1 | 0 | 118 B |

## 文档入口

- 当前MoE整理：[研究总览](../MOE_RESEARCH_SUMMARY_2026-10-26.md)、[状态页](../README.md)、[论文形态卡](../PAPER_SHAPE_MOE.md)、[主张账本](../CLAIMS.md)、[痛点日志](../PAIN_LOG.md)、[交接记录](../HANDOFF_MOE_2026-10-25.md)。
- 实验/结果导航：[MoE E120–E142索引](../experiments/INDEX_MOE_2026-10-26.md)、[实验卡与小结果机器索引](research_inventory_2026-10-26.json)；原卡在[`experiments/`](../experiments/)，原证据在[`results/`](../results/)，代码在[`scripts/`](../scripts/)。
- 历史闭线：[研究总档](../RESEARCH_HISTORY.md)、[论文v0](../paper-acl-v0/README.md)、[v1](../paper-acl-v1/README.md)、[v2](../paper-acl-v2/README.md)、[v3](../paper-acl-v3/README.md)；过程记录在[`logs/`](../logs/)，论文阅读与审计在[`knowledge/`](../knowledge/)。

历史论文稿件和头线均已结项；旧卡、旧handoff或旧稿中的“下一步”不是当前实验队列。用户要求暂停新增实验，待人消化后再决定方向。本清单只说明文件在哪里、当时大小和mtime，**不提出删除或保留决策**。

## 完整清单的保存

展开JSON保留在本地`results/file_catalog_2026-10-26.json`，约6.47MB；Git保存无损压缩的[同一清单](file_catalog_2026-10-26.json.gz)，可用`gzip -dc results/file_catalog_2026-10-26.json.gz > results/file_catalog_2026-10-26.json`恢复。压缩内容已与展开JSON逐字节核对。清单是生成时的非原子元数据快照；自身文件及其派生压缩导出不作为被盘点的原始科学资产。
