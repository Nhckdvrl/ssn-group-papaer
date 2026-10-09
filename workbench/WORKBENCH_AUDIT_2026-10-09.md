# Workbench 整理审计 — 2026-10-09

## 原则

这次只按**仓库里有没有真实执行资产、用户是否明确保留、历史证据是否值得追溯**分类，不根据旧的 `PAUSED`/`CLOSED` 标签机械删除。尤其：**`mechanism-population-dynamics` 仍在继续**（2026-10-09 用户最新明确指示）；2026-10-08 的停止投入说明已不是当前决定。

清理前 `workbench/` 有 21 个研究目录；本次只把 **5 个没有实验代码/结果的桌面方向归档**，整理后保留 **16 个**。归档是 Git tree 搬移，保留原文件全部内容，Git 历史可恢复；未碰实验代码、结果、论文草稿、模型权重、资源排程。

## 保留在 workbench 的项目（16）

| 项目 | 为什么保留 | 当前科学/排程边界 |
|---|---|---|
| `mechanism-population-dynamics` | ACL 论文 v0/v1/v2、数千实验/脚本/结果，**用户最新明确继续** | **ONGOING**；正式排程暂用 PROPOSED，不得按 10/08 旧停止说明归档 |
| `in-context-evidence-structure` | E01–E48，真实标注者实验及 ICL 机制 | 正式 ACTIVE-EXPLORE |
| `real-time-causalization-capability-preservation` | 人指定的主线与阶段测量计划，虽尚无实证脚本 | 正式 ACTIVE-MAIN；不能以“仅有文档”清理 |
| `latent-world-model-planning` | I16 / E21–E23、真实训练及评测结果 | 2026-10-07 人要求暂停实验，**不是删除研究成果** |
| `data-centric-rsi` | E00–E14，真实 SFT/评分/对照和代码 | 原定终点已完成，待审；不能当空壳 |
| `incremental-interpretation-revision` | 103 张实验卡、实际实验、失败审计及总结 | 已释放 GPU，保留复现与探索记录 |
| `cross-lingual-acquisition-regimes` | 52 次已完成运行、训练和跨语言数据 | PAUSED 排程；真实证据及资产完整保留 |
| `video-world-model-temporal-interfaces` | 真实时序诊断、评测 harness 和结果，新主线可复用 | 旧独立题暂停；**资产在用** |
| `scoped-context-state` | 已有脚本、数据集和模型 smoke/verify 结果 | 仍有实证资产，不视作零工作 |
| `multi-llm-collaboration` | 虽未正式跑 GPU，但有人审可行性结论、明确研究卡及复开条件 | PAUSED；保留，避免误删有意搁置的协作方向 |
| `moe-route-preference` | 历史 CT03 实验结果与 MoE 路由反例的索引 | CLOSED；有实证来源，不是纯空白构想 |
| `omni-recon` | 实际全双工系统评测脚本和结果 | CLOSED；历史可复用 |
| `pragmatic-inference-calibration` | E65–E68 完成实验与用户要求的关闭记录 | CLOSED；保留末次核验结果 |
| `realtime-agent-capability-transition` | τ-bench 分析、实际运行数据、代码 | CLOSED；研究结论保留 |
| `realtime-computation-boundaries` | 多个实时语音模型的实验与评分文件 | CLOSED；评测工具保留 |
| `shape-olmo` | 混合架构系统探针、结果和负结论 | CLOSED；真实实验保留 |

## 移出 workbench，原样归档（5）

| 原路径 | 去向 | 判断依据 |
|---|---|---|
| `ai4quant/` | `../archive/workbenches/ai4quant/` | 只有选题卡、失败/可行性笔记，没有实验 runner 和数据 |
| `hybrid-adaptation/` | `../archive/workbenches/hybrid-adaptation/` | 单个概念 README，没有执行资产 |
| `model-diffing-measurement/` | `../archive/workbenches/model-diffing-measurement/` | 一份很完整的 desk/literature 分析，但尚无实验资产 |
| `npc-deception-investigability/` | `../archive/workbenches/npc-deception-investigability/` | 文献与拟定实验，没有实际研究运行 |
| `npc-persona-behavior-grounding/` | `../archive/workbenches/npc-persona-behavior-grounding/` | desk feasibility 研究，没启动实证项目 |

## 不改动的东西

- 所有保留项目的 **实验代码、数据、结果、论文、日志**，以及本地环境、权重和训练任务。
- `AGENTS.md`、`tools/process/check.py` 的工作流程与「正式 ACTIVE-MAIN / ACTIVE-EXPLORE 各最多 1」规则。
- 不把某个具体解释被否定，当成整个 workbench 被否定。

本次变更只清理确认为 desk-only 的目录、维护索引，并按最新人类指令纠正明显过时的状态文字。
