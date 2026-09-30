# SSN Group Paper — Research Repository

**流程版本：v4（2026-09-30）。** 目标：ICML / ICLR / NeurIPS / CVPR / ICCV / ACL / EMNLP / NAACL 主会（不投 Findings，不参考 EACL）。
为什么改：[`search/PROCESS_DIAGNOSIS_2026-09-30.md`](search/PROCESS_DIAGNOSIS_2026-09-30.md)（25 天、1,420 次提交、约 255 个被杀题目、14 个 workbench、0 个 candidate 的原因分析与顶会校准数据）。
**AI agent 先读 [`AGENTS.md`](AGENTS.md)。**

## 全流程

```
找题 SEARCH ──► 驻留 WORKBENCH ──────────────────────────► 候选 CANDIDATE ──► 投稿 PAPER
选领域          建设 + 系统测量                               模拟审稿 + 写作       投—改—再投
(≤1 周)         ┌──── 探索 idea（每周）────┐                  (T−8 周起)
                │ 痛点 / 测量异常 → 研究动作 │
                │ → idea 卡 → 决定性 pilot   │
                └────────────┬──────────────┘
                             ▼
                ┌──── 执行（每天）──────────┐
                │ 实验卡 → 运行 → 主张账本   │
                │ L0 → L5，混杂审计，校对    │
                └───────────────────────────┘
```

| 阶段 | 输入 → 输出 | 关口（人签字） | 文档 |
|---|---|---|---|
| **找题** | 组内偏好 + 题材库 + 顶会语料 + 最新 arXiv → territory 卡（热度 / 谱系 / 形态 / 立足点 / 压力清单） | 选 1 主线 + 最多 1 探索线；放弃领域只有三种理由 | [`search/README.md`](search/README.md) |
| **驻留** | territory 卡 → 2–3 周内 D1–D6：强基线复现、资产、痛点日志、系统测量、定位表、形态卡 + idea 组合 | 第 3 周：继续 / 同领域转向 / 暂停 | [`workbench/README.md`](workbench/README.md) |
| **探索 idea** | 痛点、测量异常、强基线的成功、近邻分歧 → idea 卡 → 决定性 pilot → 排序（不判死） | 每周人审选前 1–2 个 | [`workbench/IDEA_EXPLORATION.md`](workbench/IDEA_EXPLORATION.md) |
| **执行** | 实验卡（跑前写决策表）→ 结果 → 主张账本（证据等级 L0–L5） | 主张升 L3 前独立校对 | [`workbench/EXECUTION.md`](workbench/EXECUTION.md) |
| **候选** | 主旨 ≥ L3、贡献各 ≥ L2、机制 ≥ L4 → 候选包、校准过的模拟审稿、写作倒排 | 进入候选；投稿 | [`candidates/README.md`](candidates/README.md) |
| **投稿** | 投稿 → rebuttal → 结果 → 按转投路线再投 | 转投选择 | [`candidates/README.md`](candidates/README.md) §5 |

## 五条核心原则
1. **选题选的是要住进去建设的领域，不是要去验证的现象。** 旧的“猜现象 → 赌博 → 实验”已被证伪。
2. **新颖性 = 可陈述的增量，不是无人触碰的空白。** 近邻是常态；撞车 = 同一 claim + 同一证据类型 + 同一设定，而且先改增量。用真实的顶会接收 / 拒稿数据校准（`tools/venue_corpus/`）。
3. **论文从建设中长出来。** idea 来自痛点和测量，用研究动作推出来、用决定性 pilot 筛；方法从驻留第一周起允许，只要针对真实出现的痛点。
4. **每次运行都推动一条主张。** 先写实验卡和决策表；主张按证据等级爬升；每周只问“哪条主张升了级、为什么”。
5. **没被证据否定的东西只搁置、不杀死。** 关闭只由人决定，且只能基于实验证据或可行性。

## 节奏与分工

| 频率 | 做什么 | agent | 人 |
|---|---|---|---|
| 每次会话 | 实验卡 → 运行 → 更新账本 → `logs/` 一条 | 执行 | — |
| 每周（约 30 分钟） | 人审：倒计时、主张变化、idea 排序、漂移信号、形态卡（`tools/process/weekly.py` 生成骨架） | 准备骨架与数字 | 注入品味、做决定 |
| 每两周 | 新近邻扫描，更新定位表 | 执行 | 看增量是否要调整 |
| 每月 | territory 健康检查 | 起草 | 确认 |
| 截稿倒排 | T−12 … T 的里程碑（`workbench/EXECUTION.md` §7） | 执行 | 决定主投 / 改投 |

## 目录

| 路径 | 作用 |
|---|---|
| `AGENTS.md` | AI agent 的工作规则（硬规则、会话开始流程、汇报格式） |
| `search/` | 找题：流程、诊断、两个品味通道（`our-taste/`、`sasano-taste/`）、territory 扫描 |
| `workbench/` | 驻留、idea 探索、执行；登记表（README §9）；同时最多 1 主线 + 1 探索线 |
| `candidates/` | 已成形的论文候选与投稿流程；当前 **0** |
| `templates/` | 全流程卡片模板（territory、论文卡、idea、实验、主张账本、定位表、周审、形态卡、关闭记录、候选、模拟审稿） |
| `tools/` | `venue_corpus/`（顶会接收 + 拒稿语料：热度 / 形态 / 近邻）；`process/`（生成卡片、检查流程、每周人审骨架） |
| `library/` | 按**题材**组织的知识库：谱系、论文卡、开源资产、awesome 列表、热度数据 |
| `failed/` | 跨项目的失败记录；桌面新颖性 kill 在 v3 起可带增量重开 |
| `archive/` | 只读历史 |

## 当前状态（2026-09-30）
- **主线**：`workbench/video-world-model-temporal-interfaces/`（CVPR 2027，11-16 截稿）。
- **提议的探索线**：`workbench/multi-llm-collaboration/`（训练出来的开源异构 LLM 团队；待人确认）。
- 完整登记表：[`workbench/README.md`](workbench/README.md) §9；检查：`python3 tools/process/check.py`。

## 仓库规则
- 顶层目录代表阶段 / 功能，不代表题目；不建 `search_rounds/` 之类的过程堆积目录；不在 `search/` 下放实验。
- 候选编号只在 candidate 阶段出现；观察结果留在产生它的 workbench。
- 当前状态以本 README、`workbench/README.md` §9 登记表与各阶段 README 为准。
