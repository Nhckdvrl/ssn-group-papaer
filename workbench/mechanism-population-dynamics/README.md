# Mechanism Population Dynamics

**状态（2026-10-23）：** 已结项（10-11 论文线终止；10-17 修复线按收尾规则停止）。目前只做导师 10-22 新意见的分析，不跑实验。

## 从这里读
| 想知道 | 读 |
|---|---|
| 我们做过什么、发现了什么、为什么停 | **[RESEARCH_HISTORY.md](RESEARCH_HISTORY.md)**（唯一的总文档） |
| 导师 10-22 的 MoE / 头方向怎么看 | [knowledge/research/ADVISOR_2026-10-23_MOE.md](knowledge/research/ADVISOR_2026-10-23_MOE.md) |
| 每条主张的证据等级与作废记录 | [CLAIMS.md](CLAIMS.md) |
| 踩过的坑（代码、统计、公开模型数据完整性） | [PAIN_LOG.md](PAIN_LOG.md)、[knowledge/heritage/FAILURE_MODES.md](knowledge/heritage/FAILURE_MODES.md) |
| 读过的论文 | [knowledge/PAPER_CATALOG.md](knowledge/PAPER_CATALOG.md) |

## 目录
- `experiments/`：实验卡 E01–E119、混杂审计 A01（原始记录，不改动）。
- `results/`：全部结果（大文件只在本机）。
- `scripts/`：全部代码。主要入口：
  - `e46_train.py`：受控预训练；
  - `e59_roles.py`：头角色图；
  - `e89_labor.py`：多任务因果分工；
  - `e93_lesion.py`：损伤 + 继续训练；
  - `e105_unlearn.py`：参数子集遗忘。
- `paper-acl-v0`–`v3/`：四版论文（PDF + LaTeX），均已被取代，v3 为最后一版。
- `logs/`：每日记录。
- `knowledge/`：论文卡、方法教训、概念工具、当前分析。

## 资产提醒
- 本地缓存 `~/mechpop_cache`（Pythia 检查点、Pile 分词数据）在 10-23 已不存在，再做实验需要重新准备。
- 旧的独立复现包与过程文档已于 10-23 删除，可从 Git 历史恢复（见 [RESEARCH_HISTORY.md §11](RESEARCH_HISTORY.md)）。
