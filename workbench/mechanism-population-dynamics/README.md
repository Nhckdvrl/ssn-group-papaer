# Mechanism Population Dynamics

**状态（2026-10-25）：** 头线已结项（10-11 论文线终止；10-17 修复线停止）。当前方向是 **MoE 专家分工的跨训练可重现性**，处于探索初期（E120、E121 已完成，尚无跨种子数据），准备移交给其他 AI 继续。**接手请先读 [HANDOFF_MOE_2026-10-25.md](HANDOFF_MOE_2026-10-25.md)。**

## 从这里读
| 想知道 | 读 |
|---|---|
| 接手当前方向：研究问题、已知事实、测量合同、下一步实验 | **[HANDOFF_MOE_2026-10-25.md](HANDOFF_MOE_2026-10-25.md)** |
| 我们做过什么、发现了什么、为什么停 | [RESEARCH_HISTORY.md](RESEARCH_HISTORY.md)（历史总档） |
| MoE 方向的讨论过程（已被交接文档吸收） | [ADVISOR_2026-10-23_MOE.md](knowledge/research/ADVISOR_2026-10-23_MOE.md)、[MOE_DISCUSSION_2026-10-23.md](knowledge/research/MOE_DISCUSSION_2026-10-23.md) |
| 每条主张的证据等级与作废记录 | [CLAIMS.md](CLAIMS.md) |
| 踩过的坑（代码、统计、公开模型数据完整性） | [PAIN_LOG.md](PAIN_LOG.md)、[knowledge/heritage/FAILURE_MODES.md](knowledge/heritage/FAILURE_MODES.md) |
| 读过的论文 | [knowledge/PAPER_CATALOG.md](knowledge/PAPER_CATALOG.md) |

## 目录
- `experiments/`：实验卡 E01–E119、混杂审计 A01（原始记录，不改动）；10-23 起 MoE 方向：E120（测量工具合成验证）、E121（OLMoE 路由组织与专家差异）。
- `results/`：全部结果（大文件只在本机）。
- `scripts/`：全部代码。主要入口：
  - `e46_train.py`：受控预训练；
  - `e59_roles.py`：头角色图；
  - `e89_labor.py`：多任务因果分工；
  - `e93_lesion.py`：损伤 + 继续训练；
  - `e105_unlearn.py`：参数子集遗忘；
  - MoE 方向：`moe_measure.py`（测量工具库）、`e120_synth.py`、`e121_data.py`、`e121_olmoe.py`、`e121_analyze.py`。
- `paper-acl-v0`–`v3/`：四版论文（PDF + LaTeX），均已被取代，v3 为最后一版。
- `logs/`：每日记录。
- `knowledge/`：论文卡、方法教训、概念工具、当前分析。

## 资产提醒
- 本地缓存 `~/mechpop_cache`：头线的 Pythia 检查点与 Pile 分词数据已不存在；现有 `hf_olmoe/`（4 个 OLMoE 检查点，约 52 GB）、`e121/`（采集数组，约 21 GB）、`lingdata/`（UD EWT、SemCor）。
- 旧的独立复现包与过程文档已于 10-23 删除，可从 Git 历史恢复（见 [RESEARCH_HISTORY.md §11](RESEARCH_HISTORY.md)）。
