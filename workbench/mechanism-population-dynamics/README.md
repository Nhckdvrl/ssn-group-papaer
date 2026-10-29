# Mechanism Population Dynamics

当前研究是**MoE的计算组织与功能分工**：从导师关于自发分工跨训练重复的建议，推进到性质载体、响应接口和协作使用关系的干预研究。E144–E166已完成，当前无GPU任务，总并发上限4卡。MoE由用户授权独立推进；正式登记保持PROPOSED，头线保持CLOSED。

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
