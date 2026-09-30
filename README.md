# SSN Group Paper — Research Repository

**流程版本：v3（2026-09-30）。** 目标：ICML / ICLR / NeurIPS / CVPR / ICCV / ACL / EMNLP / NAACL 主会。
为什么从 v2 改到 v3：见 [`search/PROCESS_DIAGNOSIS_2026-09-30.md`](search/PROCESS_DIAGNOSIS_2026-09-30.md)（25 天、1,420 次提交、约 255 个被杀题目、14 个 workbench、0 个 candidate 的原因分析与顶会校准数据）。

## 主流程

> **SEARCH（选领域）→ WORKBENCH（驻留 = 建设 + 系统测量）→ CANDIDATE → PAPER（投—改—再投）**

三条核心原则：

1. **选题选的是要住进去建设的领域，不是要去验证的现象。** 旧的“猜现象 → 赌博 → 实验”已被证伪。
2. **新颖性 = 可陈述的增量，不是无人触碰的空白。** 顶会每个周期都在同一个 parent 下接收大量论文；“有人做过 / 已成 program”不是放弃理由。用真实的顶会接收/拒稿数据（`tools/venue_corpus/`）校准，而不是让 agent 在全 arXiv 上找“有没有人碰过”。
3. **论文从建设中长出来。** 在强开源系统上跑通、建资产、记录痛点、系统测量；从第一周起允许针对真实痛点做方法。Failure → Bottleneck → Action → Outcome 是论文的叙事标准，不是动手的许可。

## 目录结构（按阶段/功能，不按题目）

| 路径 | 作用 |
|---|---|
| `search/` | 选领域：流程（`README.md`）、诊断、两个品味通道（`our-taste/`、`sasano-taste/`）、territory 扫描 |
| `workbench/` | 驻留与建设：强基线、资产、痛点日志、系统测量、论文形态卡；同时最多 1 主线 + 1 探索线 |
| `candidates/` | 已经在 workbench 中成形的论文候选；当前 **0** |
| `library/` | 按**题材**组织的知识库：谱系、关键论文卡、开源资产、awesome 列表、热度数据 |
| `tools/` | 可复用工具；`venue_corpus/` = 顶会接收+拒稿语料库（热度 / 论文形态 / 近邻定位） |
| `failed/` | 跨项目的 kill 记录；2026-09-30 再审见 `failed/REAUDIT_2026-09-30.md`（桌面新颖性 kill 改为可带增量重开） |
| `archive/` | 只读历史：旧候选、旧“good”包、旧搜索系统 |

## 1. Search（选领域）
流程与模板：[`search/README.md`](search/README.md)。输出是一张 territory 卡：热度卡、谱系卡、形态卡、立足点卡、压力清单。

## 2. Workbench（驻留 = 建设）
流程与模板：[`workbench/README.md`](workbench/README.md)。第 1–3 周交付 D1–D6（强基线复现、可复用资产、痛点日志、领域标准测量、定位表、论文形态卡）；之前不许以“没意思 / 被拥有”为由关闭。

## 3. Candidates
主结果在强基线、公平算力、多种子下成立；定位表完成；论文形态卡稳定；目标会议明确。当前 **0**。

## 4. Library
先查 `library/README.md`（题材索引）→ 对应题材页 → `tools/venue_corpus` → 最新 arXiv。

## 5. Failed / Archive
`failed/` 记录**有证据的**失败与其教训；桌面新颖性 kill 在 v3 下可带新增量重开。`archive/` 只读，旧状态标签不构成任何授权。

## 仓库规则
- 顶层目录代表阶段/功能，不代表题目；
- 不建 `search_rounds/` 之类的过程堆积目录；不在 `search/` 下放实验；
- 候选编号只在 candidate 阶段出现；
- 观察结果留在产生它的 workbench；
- 当前状态以本 README 与各阶段 README 为准。
