# Data-Centric RSI

## 状态
**状态：** PROPOSED（2026-10-04 起停步；2026-11-27 准备重拾，方向待重新讨论）
**目标会议：** ICML / ICLR / NeurIPS；偏 NLP 数据学习则 ACL / EMNLP 主会。届次未定。
**上次人审：** 无。

**一句话：** 研究“改进器为学生制造/挑选训练数据，并且自己也越来越会做这件事”的数据闭环。2026-10 的第一轮（E00–E14）没有做出可用的结果，重拾时**不沿用旧思路**（旧 I01–I03、旧主张 C01–C04 均停用），需要结合 2026-10 之后的新工作重新找问题。

**第一轮做了什么、为什么没成：** 见 [RETROSPECTIVE_2026-11-27.md](RETROSPECTIVE_2026-11-27.md)。要点：
- 唯一可靠的结果是“用真实标注数据训练比不训练高”。各种数据选法之间的差别大多在噪声内。
- “改进器变强”一次都没测过，研究对象一步步被换成了静态选数据方法的比较。
- 只跑单种子，而换种子造成的差（LLaVA 八项均值 0.52、单项最多 3.7）就比方法之间的差还大。
- 本地教师出不了合格的题，生成数据从未接上训练。
- 问的是程度问题，近邻已占据大部分宽泛说法。

## 文件
| 文件 | 内容 | 还有用的地方 |
|---|---|---|
| [RETROSPECTIVE_2026-11-27.md](RETROSPECTIVE_2026-11-27.md) | 第一轮回顾、失败原因、教训 | 重拾前必读 |
| [RSI_AUDIT_AND_EXPERIMENTS_2026-10-04.md](RSI_AUDIT_AND_EXPERIMENTS_2026-10-04.md) | 10-04 外部审计：Gödel Forest、EEM、AutoLLMResearch、ReasoningBank 等近邻的生长逻辑，以及“实验经验迁移”转向提案 | 近邻分析、一个候选方向 |
| [FIELD_MAP.md](FIELD_MAP.md) | 领域谱系（自生成监督、课程/选样、可验证自博弈、数据研究 agent、自博弈预训练）和问题地图 | 领域入口（截至 2026-10-02） |
| [POSITIONING.md](POSITIONING.md) | 约 60 篇近邻各自已经拥有的主张 | 查撞车（截至 2026-10-03） |
| [READING_LIST.md](READING_LIST.md) | 文献编号与阅读深度 | 文献账本；论文卡在 [RSI_PAPER_CARDS.md](../../library/themes/training-post-training/RSI_PAPER_CARDS.md) |
| [CLAIMS.md](CLAIMS.md) | 主张账本（目前为空，旧主张已停用） | — |
| [results/LLAVA_SCORES.csv](results/LLAVA_SCORES.csv) | E12–E14 全部 14 个 LLaVA 运行的八项分数 | 噪声/效应量参考 |
| `scripts/`、`compat/` | Curation-Bench 本地 LLaVA-1.5-7B 10K SFT → 八项评测的最小脚本 | 若再用这个底座 |
| `logs/` | 会话日志 | — |

痛点记录：第一轮的痛点（评测提示敏感、vLLM 贪心解码不确定、本地教师质量、ICONS/ARDS 公开代码索引错位、单种子噪声）已并入回顾第 3–4 节；新一轮的痛点重新记。

## 资产
- **已删除**：节点 fvcrc10/12/13/20 的 `/var/tmp/xiang-data-rsi/`，包括 LLaVA Arrow（93GB）、论文起点模型、所有 checkpoint。重用底座需要重新下载（`scripts/e12_fetch.py`、`e12_fetch_evals.py`）。
- **仍在本地**：`~/.cache/research/data-centric-rsi/`（Curation-Bench、DataEnvGym、AZR、LESS、SQLM、Cure-SFT 等代码仓，1.6G）和 `~/.venvs/data-centric-rsi`。
- **完整历史**：所有实验卡（E00–E14）、idea 卡、痛点日志、一次性脚本和 200 多个中间结果文件，都在 2026-11-27 瘦身时删除。需要时用 `git checkout 6ac6dda5 -- workbench/data-centric-rsi/<路径>` 恢复。

## 决策记录
- **2026-10-02**：用户授权调研并注册 PROPOSED。
- **2026-10-04**：E13/E14 收尾后停步交人审，没有形成成形的 idea。
- **2026-11-27**：用户决定重拾这个方向，但大概率不沿用旧思路；先回顾，再给工作台瘦身。
