# Mechanism Population Dynamics

**2026-11-23 起的当前工作：** [hybrid/](hybrid/README.md)，问混合架构（循环层 + 少量全注意力层）里被切开的词在哪一层拼回整词。试测卡 E194 已写好，等人签字后才跑。

此前的工作是**分别训练的 MoE 是否自发形成同一套专家分工**（[division/](division/README.md)，2026-10-31 起）。11-22 起不再作为主问题：头线已答过同类问题，结项原因是答不出"所以呢"。经过见 [PROGRESS_REVIEW](division/PROGRESS_REVIEW_2026-11-22.md)。此前的 MoE 计算组织线（E144–E166）已由人决定摒弃，结果存档于 [moe/](moe/README.md)，理由见[复盘](moe/notes/RETROSPECTIVE_2026-10-31.md)。头线保持 CLOSED。

## 从这里开始

| 想了解什么 | 入口 |
|---|---|
| 当前结论、五幅关键图、下一决定 | [moe/README.md](moe/README.md) |
| 导师最初建议的原文 | [10-22日语会议录](moe/notes/MEETING_10-22_JA.md) |
| 如何从原始问题推进到当前题目 | [研究主线与演进](moe/RESEARCH_DIRECTION.md) |
| 论文论证与领域位置 | [PAPER_SHAPE](moe/PAPER_SHAPE.md)、[英文论文](moe/paper/main.pdf) |
| 主张、等级、校正与失败 | [CLAIMS](CLAIMS.md)、[PAIN_LOG](PAIN_LOG.md) |
| 模型、checkpoint、raw及恢复 | [ASSETS](moe/ASSETS.md) |
| 实验协议与全部结果 | [实验索引](moe/experiments/INDEX.md)、[结果导航](moe/results/README.md) |
| 当前代码与CPU复算 | [scripts](moe/scripts/README.md) |
| 执行约定与过程 | [AGENTS](AGENTS.md)、[logs](logs/) |

## 已结项的历史与共有资料

| 区域 | 内容与状态 |
|---|---|
| [heads](heads/README.md) | E01–E88及四版论文、E89–E119；均已结项，不自动恢复。结论/撤回见[HISTORY](heads/HISTORY.md) |
| [suite-audits](suite-audits/README.md) | 公开模型套件完整性报告、核查证据与已提交链接 |
| [knowledge](knowledge/PAPER_CATALOG.md) | 按主题组织的论文卡与可复用研究教训 |

历史执行脚本退出日常目录，固定Git快照及逐文件SHA由统一入口按需恢复；原数值程序、原卡、结果和失败记录保留。结项头线的未跟踪本地资产和已结束实验console迁入耐久归档，位置与核验见ASSETS。没有清理公共HF缓存、唯一checkpoint或其他workbench。
