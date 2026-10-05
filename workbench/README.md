# Workbench — 驻留与建设

**版本：v4.1（2026-10-01）。** 诊断见 [`../search/PROCESS_DIAGNOSIS_2026-09-30.md`](../search/PROCESS_DIAGNOSIS_2026-09-30.md)。v2 全文在 git 历史中；其中“强基线优先”“成功案例也是证据”“失败梯度”“论文身份允许变化”继续有效，已并入下文。

本目录的三份文件：
- **本文件**：驻留怎样开始、容量与节奏、何时关闭或升级、当前登记表；
- [`IDEA_EXPLORATION.md`](IDEA_EXPLORATION.md)：驻留中 idea 从哪里来、怎样用决定性 pilot 筛、怎样排序（不判死）；
- [`EXECUTION.md`](EXECUTION.md)：执行协议——三本账（痛点 / 实验卡 / 主张账本）、证据等级 L0–L5、混杂审计、校对、算力排程、截稿日的用法、漂移检测、人审触发条件。

新建 workbench：`python3 tools/process/new.py workbench <名字>`（生成 README、CLAIMS、PAIN_LOG、experiments/、ideas/、logs/）；检查：`python3 tools/process/check.py`；人审骨架：`python3 tools/process/review.py <名字> --write`。

**不排日程。** agent 执行很快，流程按状态和证据推进：交付物齐了就进入下一步，决策点到了就人审。

---

## 0. 一句话

> **workbench 的任务不是“找到一个意外现象”，而是：在一个领域里把强开源系统跑通、建出可复用资产、在建设过程中系统地测量——让论文从真实痛点、系统测量和强基线上的失败里长出来。**

v2 的问题（诊断 §3）：入场禁止方法、门槛在没有证据时执行、并行 14 条线。结果是 7/14 的 workbench 一个脚本都没跑就被降级，剩下的多数在拿到像样的证据前就冻结。唯一存活的线恰好是唯一写了论文形态卡、绑定了会议截稿日的线。

---

## 1. 容量与决策点

- **同时最多 1 条主线 + 1 条探索线。** 开新线必须先关闭或暂停一条（由人决定）。
- **人审在决策点触发，不按周**（触发条件见 `EXECUTION.md` §9：D1–D6 交付、pilot 要选分支、主张升降级、漂移信号、开关线 / 转向 / 进候选 / 投稿之前）：看论文形态卡（§4）、主张账本与痛点日志；人负责注入品味、可疑的对比、替代解释、缺失的基线，并做决定。agent 负责执行，不自行开新 workbench。
- **每条主线登记一个目标会议**。截稿日是外部约束，不是计划：到截稿时主张够投就投，不够就投下一个会（`EXECUTION.md` §7）。参考（以官方公告为准）：CVPR 2027 = 2026-11-16；ICML 2027 ≈ 2027-01 下旬；ACL 2027（ARR）≈ 2027-02；NeurIPS 2027 ≈ 2027-05；EMNLP 2027（ARR）≈ 2027-05/06；ICLR 2028 ≈ 2027-09 下旬。
- 被拒后重投是常态（ICLR 2026 拒稿中约 840 篇被 ICML 2026 接收）。按“投—改—再投”规划，不要在想法阶段追求一次命中。

---

## 2. 驻留 = 建设（以交付物为准，不以时间为准）

D1–D6 交付齐全之前，不允许以“没意思 / 被拥有 / 天花板不够”为由关闭；交付齐全即进入驻留人审，不需要等满任何时长。

| # | 交付物 | 标准 |
|---|---|---|
| D1 | **强基线跑通并复现** | 代码/权重版本固定；复现到官方数字的误差范围写清；至少 2–3 个种子的方差；评测 harness 可一键重跑 |
| D2 | **可复用资产进仓库** | `experiments/`（代码）、`env.sh`/环境说明、数据准备脚本；大文件不进 git，写清下载方式 |
| D3 | **痛点日志**（`PAIN_LOG.md`） | 跑的过程中遇到的：坏掉的、不稳定的、慢的、指标之间不一致的、意外地好的。每条带复现条件和粗略量级 |
| D4 | **领域标准的系统测量**（实验卡 + `CLAIMS.md`） | 每个领域不同（例：多智能体 → 交叉配对矩阵、算力匹配曲线；可解释性 → 基线探针/干预强度与噪声地板；推理 → 按难度/位置的失败分布；世界模型 → 按块内位置的控制响应）。**测量先于解释**；每次运行先写实验卡（`EXECUTION.md` §2） |
| D5 | **定位表初稿** | 对最近 10 篇接收论文 + 5–10 篇最新 arXiv 写增量（`../templates/positioning.md`） |
| D6 | **论文形态卡初稿 + idea 组合** | §4；3–6 个有来源的 idea 卡（`IDEA_EXPLORATION.md`），每个预期贡献至少一条 L1 主张或明确标 ❌ |

---

## 3. 两条轨道并行：建设（build）与理解（understand）

- **Build**：针对痛点日志里**真实出现**的问题，做最小的修复 / 方法 / 训练改动 / 评测协议——**从驻留一开始就允许**。在强基线上发现问题并修好，是顶会最常见的论文来源（诊断 §4.2–4.3：ICLR 多智能体接收论文 90% 是方法/框架型）。
- **Understand**：诊断、消融、表征分析、机制解释——回答“为什么坏、为什么修得好”。
- 两条轨道互相喂：方法没效果 → 诊断为什么；诊断揭示瓶颈 → 设计最小干预。
- **Failure → Bottleneck → Action → Outcome** 仍然是论文的叙事标准，每一环都要有证据；但它是**写论文的标准，不是开始动手的许可**。
- 成功案例也是证据：强基线为什么在旧系统失败的地方成功？哪个旧瓶颈消失了？哪个设计变得不必要？
- 论文身份允许变化：RQ 可以变，方法可以变得不必要，意外的失败可以成为中心结果。但每次变化都要**让故事更简单**，而不是加更多条件。

---

## 4. 论文形态卡（每次人审更新，模板 `templates/paper_shape.md`）

参考范例：[`video-world-model-temporal-interfaces/CVPR_ASSESSMENT.md`](video-world-model-temporal-interfaces/CVPR_ASSESSMENT.md)。

```markdown
## 论文形态卡 — <workbench> — <日期>
- 一句话主旨（当前版本）：
- 论文形态：失败模式+修复 / 构念引入+测量 / 理论+受控实验 / benchmark / 系统
- manuscript-critical contributions（数量由故事决定；状态：✅/⚠️/❌；各对应 C#）：
- 摘要主张（数量由故事决定；各自证据等级）：
- 主图/表（数量由证据链决定；每张对应 E#/C#）：
- 基线列表（含最强开源基线、算力匹配方式）：
- 证据标准：模型/家族数、benchmark 数、种子数、置信区间
- 定位表摘要（最近 5 个近邻 + 各自增量）：
- 风险登记（可能性 / 影响 / 对策）：
- 目标会议（截稿时够投就投，否则下一个会）：
- 本次决定：继续 / 转向（同一领域内）/ 暂停
```

---

## 5. 实验卫生（这是我们的比较优势）

完整的 12 项混杂审计清单、证据等级与独立校对见 [`EXECUTION.md`](EXECUTION.md) §3–§5。最常用的七条：噪声地板（L19）、一阶工具有效性（L29）、算力匹配、≥3 个种子且不筛幸存种子（L45）、输入指纹（S03）、“一句指令能否恢复”（实时线）、选窗 / 读数与被测变量解耦（视频线 E29）。

---

## 6. 何时关闭、暂停或转向

**关闭 / 暂停**（原则上在 D1–D6 交付之后，满足其一，并写明证据）：
- (a) 强基线无法复现，且原因不可修复；
- (b) 主要现象在当前测量分辨率与可承受算力下无法区分出对决策有意义的效应（不是机械 `2×noise`）；
- (c) 定位表显示精确撞车或极高 compression risk，且无法形成实质 delta；
- (d) 在可承受算力下达不到任何目标会议需要的证据（达不到当前会议只是改投，不关闭）；
- (e) **H 类：Human scientific-yield judgment**——baseline 已跑通、已有系统 measurement、positioning 和论文形态卡之后，人判断即使结果成立也不值得继续投入。H 只能由人签字，agent 不得在桌面阶段使用。

**不构成关闭理由**：有人做过相关工作；已经成了一个 program；一个解释被证伪（null 结果杀的是解释，不是领域）；第一个 lead 不成立。

**两次连续降级重置**（保留）：连续两个 lead 被平凡对照或近邻吸收后，停止在同一叙事上加实验——回到**同一领域**的痛点日志、形态卡和其他压力，而不是开新 workbench。

关闭或暂停**只由人决定**；agent 可以用 [`../templates/close_record.md`](../templates/close_record.md) 提议（证据类别 A 实验 / C 可行性 / H 人类 scientific-yield；B 桌面判断不能作为关闭理由，H 也必须满足上面的 residency 前置条件）。记录写在本 workbench README 末尾；只有跨项目有用的才复制到 `failed/`（ID 从 K254 起）。

---

## 7. 何时升为 candidate

门槛与候选包见 [`../candidates/README.md`](../candidates/README.md) §1：主旨主张通常 ≥ L3；所有 manuscript-critical contributions 有与措辞匹配的证据（通常 ≥ L2）；机制/因果主张通常 ≥ L4；全部校对；定位表完成；一句话主旨在一次新近邻扫描与一次人审之后没有改变；人签字。不要为了固定“3 个贡献 / 5 张图”而 padding。

---

## 8. README 模板（≤ 200 行）

[`../templates/workbench_readme.md`](../templates/workbench_readme.md)：状态页 / 论文形态卡 / idea 组合 / 主张摘要 / 痛点摘要 / 决策记录 / 资产位置。详细过程写进 `logs/`、实验卡或 `results/`，不写合同式长文。

---

## 9. 登记表（2026-10-02；`tools/process/check.py` 读取本表）

状态只能是 `ACTIVE-MAIN` / `ACTIVE-EXPLORE` / `PROPOSED` / `PAUSED` / `CLOSED`；ACTIVE-MAIN 与 ACTIVE-EXPLORE 各最多 1 条。改状态由人决定并写进对应 README 的决策记录。“截稿”只填官方公告的日期（YYYY-MM-DD），未公告写“—”。

| workbench | 状态 | 目标会议 | 截稿 | 主张账本 | 上次人审 | 备注 |
|---|---|---|---|---|---|---|
| `video-world-model-temporal-interfaces` | PAUSED | — | — | `CLAIMS.md` | 2026-10-02 | **H 类 scientific-yield 暂停**：接缝失聪现象成立，但当前 story 过窄、下游后果有限，且 ActionSplice 已占据 chunk/action responsiveness 的宽叙事；资产转为新主线的 diagnostic，不再执行旧 CVPR 扩系统/修 seam 计划 |
| `real-time-causalization-capability-preservation` | ACTIVE-MAIN | CVPR 2027 / ICML 2027 | 2026-11-16 | `CLAIMS.md` | 2026-10-02 | **人已确认换轨**：研究 bidirectional/foundation → causal AR → few-step/distilled real-time 转换中 world-model capability 的选择性损失/保留；入口只做公开 stage checkpoints 的 matched measurement，不从零训 foundation model；ForgeWM stage-wise ablation 是近邻而非 novelty |
| `multi-llm-collaboration` | PAUSED | ICML 2027（约 1 月下旬） | — | `CLAIMS.md` | 2026-10-01 | **可行性暂停（C）**：第一轮有解释力的 cross-play 需要至少两个充分训练 team；原始强 baseline 的完整 RL 成本过高，不适合作为当前探索线。保留全部 territory / cards，未来有廉价充分训练 substrate 时可重开 |
| `cross-lingual-acquisition-regimes` | PAUSED | — | — | `CLAIMS.md` | 2026-10-02 | 已有八轮 52 次完成运行；人审撤回 acquisition 领先叙事，停止局部冻结探针，明确授权有界 MONOWEB 英语学习→德语迁移 baseline 修复；持续 ACTIVE 调度归属待人统一确认，不自行改其他线 |
| `scoped-context-state` | PAUSED | — | — | — | — | 已生成数据，未完成 P1；恢复前补形态卡 |
| `mechanism-population-dynamics` | ACTIVE-EXPLORE | ICML 2027 / NeurIPS 2027 | — | `CLAIMS.md` | 2026-10-01 | **人已确认开线**：利用公开 multi-seed × multi-checkpoint 模型群体研究 mechanistic claim 在什么抽象层次上可复现；第一轮不训练模型，先做已知 mechanism 的 causal baseline + population measurement |
| `latent-world-model-planning` | PROPOSED | ICML / ICLR / NeurIPS；届次待定 | — | `CLAIMS.md` | — | **已有原生GPU测量与训练**：R1–R5持续开放；固定数据充分训练seed0/1/2为38/19/36（各48）；当前方法入口按RESEARCH_PLAN与I14/E20执行，尚无已成立科学主张；不改变ACTIVE分配 |
| `data-centric-rsi` | PROPOSED | ICML / ICLR / NeurIPS；届次待定 | — | `CLAIMS.md` | — | **已有真实GPU底座**：E12四静态策略完整八任务评分；E13/E14八支训练与全部原定终点评分完成，当前停步交人审；I01/I02/I03仍为候选，主张均L0；实时数字见workbench状态页，不改变ACTIVE调度 |
| `incremental-interpretation-revision` | PROPOSED | ACL / EMNLP / NAACL | — | `CLAIMS.md` | 2026-10-05 | **人已授权 baseline residency**：增量语言理解/解释修订；GP 仅作 calibration，禁止以 generic garden-path recovery 为 novelty；training-free 起步，不改变当前 ACTIVE 分配 |
| `pragmatic-inference-calibration` | CLOSED | — | — | `CLAIMS.md` | 2026-10-03 | **人明确决定终止本题**：有限核心检验已收尾，实验raw/data/旧runner与本地模型已清理；保留最终证据和环境，不再自动探索 |
| `npc-persona-behavior-grounding` | PAUSED | — | — | — | — | v2 桌面降级（零脚本），可重开（先填 territory 卡） |
| `npc-deception-investigability` | PAUSED | — | — | — | — | 同上 |
| `model-diffing-measurement` | PAUSED | — | — | — | — | 同上；工具链可用于多智能体线的白盒分析（P4） |
| `hybrid-adaptation` | PAUSED | — | — | — | — | v2 桌面降级，可重开 |
| `ai4quant` | PAUSED | — | — | — | — | v2 桌面降级，可重开 |
| `realtime-agent-capability-transition` | CLOSED | — | — | — | — | 证据关闭：E04 严格对照下口语化不造成可测损失；资产：τ-Voice 20GB 轨迹 + 脚本 |
| `realtime-computation-boundaries` | CLOSED | — | — | — | — | 证据关闭：失败落在前台模型默认策略（一句指令可恢复）；资产：多个全双工模型的评测脚本 |
| `omni-recon` | CLOSED | — | — | — | — | 侦察记录；B1 null 等事实可复用 |
| `shape-olmo` | CLOSED | — | — | — | — | hybrid 相关假设在对照下不成立；OLMo T/H 对照资产 |
| `moe-route-preference` | CLOSED | — | — | — | — | 观察有效，但更广的结论已被反事实路由工作覆盖 |
