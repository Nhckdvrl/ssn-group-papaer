# Workbench 清理与终止决定（2026-10-11）

**人类明确授权的最终决定。** 本记录不是 archive，也不是新研究工作台。

## 直接从当前 Git HEAD 删除（五项，合计 323 个已跟踪文件）

- `workbench/real-time-causalization-capability-preservation/`
- `workbench/scoped-context-state/`
- `workbench/cross-lingual-acquisition-regimes/`
- `workbench/multi-llm-collaboration/`
- `workbench/video-world-model-temporal-interfaces/`

不另建 archive 副本；不修改这些项目的旧 Git 提交，也不自动清理任何外部服务器上的本地模型、数据或 checkpoint。删除工作台不删除 `library/` 中本来就存在的可复用文献知识。

## Mechanism Population Dynamics：终止、已收尾，但保留全部资产

- `workbench/mechanism-population-dynamics/` 变更为 **CLOSED / TERMINATED**。
- 用户判断：已投入大量实验、分析和论文修改，继续做的科学价值和意义有限，正式结束研究，不再继续运行实验或自动修订论文。
- **保留** 原目录内所有论文版本（v0–v3）、代码、结果、日志、数据与图表（实际存在于 Git HEAD 的资产保持原样）；不重写历史、不将研究负结果改成阳性主张。
- 2026-10-09 “继续”的历史决定以本次 2026-10-11 的决定为准。

## 剩余七个 workbench

- `in-context-evidence-structure`：ACTIVE-EXPLORE。
- `latent-world-model-planning`、`data-centric-rsi`、`incremental-interpretation-revision`：PROPOSED。
- `npc-persona-behavior-grounding`、`npc-deception-investigability`：PAUSED。
- `mechanism-population-dynamics`：CLOSED。
- **ACTIVE-MAIN 目前空缺**；不在本次清理中自行选择替代主线。

## 追溯

删除前主分支提交 [`b7be63751eac0342679819cc1fac0da264e39c89`](https://github.com/Nhckdvrl/ssn-group-papaer/tree/b7be63751eac0342679819cc1fac0da264e39c89/workbench)；需要查看或恢复旧目录时可使用该历史版本。删除只影响新 Git 树，不清除 Git 历史、外部主机文件或独立设备缓存。

所有当前状态以 [workbench 登记表](README.md) 为准；[2026-10-09 审计](WORKBENCH_AUDIT_2026-10-09.md) 仅是历史快照。

## 2026-10-11 后续人类决定：NPC 两项目一并删除

- 已直接从当前 HEAD 删除 `workbench/npc-persona-behavior-grounding/` 与 `workbench/npc-deception-investigability/`。这两个目录原先各只有一个 README，均无已提交的实验结果；不另建 archive 副本。
- `library/themes/game-npc-social/` 是通用文献知识库，保留；删除 workbench 不代表从 Git 历史抹除旧方案。
- 当前由 7 个缩至 **5 个 workbench**，`mechanism-population-dynamics` 保持 CLOSED，不恢复研究。
- 同一决定还要求整理 mechpop：以最终论文 / 结项索引为先，剔除明确缓存文件；实验测量与历史复现包保留。
