# Workbench — 驻留与建设

**版本：v4（2026-09-30）。** 诊断见 [`../search/PROCESS_DIAGNOSIS_2026-09-30.md`](../search/PROCESS_DIAGNOSIS_2026-09-30.md)。v2 全文在 git 历史中；其中“强基线优先”“成功案例也是证据”“失败梯度”“论文身份允许变化”继续有效，已并入下文。

本目录的三份文件：
- **本文件**：驻留怎样开始、容量与节奏、何时关闭或升级、当前登记表；
- [`IDEA_EXPLORATION.md`](IDEA_EXPLORATION.md)：驻留中 idea 从哪里来、怎样用决定性 pilot 筛、怎样排序（不判死）；
- [`EXECUTION.md`](EXECUTION.md)：执行协议——三本账（痛点 / 实验卡 / 主张账本）、证据等级 L0–L5、混杂审计、校对、算力排程、截稿倒排、漂移检测。

新建 workbench：`python3 tools/process/new.py workbench <名字>`（生成 README、CLAIMS、PAIN_LOG、experiments/、ideas/、logs/）；检查：`python3 tools/process/check.py`；每周人审骨架：`python3 tools/process/weekly.py <名字> --write`。

---

## 0. 一句话

> **workbench 的任务不是“找到一个意外现象”，而是：在一个领域里把强开源系统跑通、建出可复用资产、在建设过程中系统地测量——让论文从真实痛点、系统测量和强基线上的失败里长出来。**

v2 的问题（诊断 §3）：入场禁止方法、门槛在没有证据时执行、寿命以小时计、并行 14 条线。结果是 7/14 的 workbench 一个脚本都没跑就被降级，剩下的多数在一天内冻结。唯一存活的线恰好是唯一写了论文形态卡、绑定了会议截稿日的线。

---

## 1. 容量与节奏

- **同时最多 1 条主线 + 1 条探索线。** 开新线必须先关闭或暂停一条（由人决定）。
- **每周一次人审（约 30 分钟）**：看论文形态卡（§4）和痛点日志（§2 D3）；人负责注入品味、可疑的对比、替代解释、缺失的基线。agent 负责执行，不自行开新 workbench。
- **每条主线绑定一个目标会议与截稿日**，倒排里程碑。参考（以官方公告为准）：CVPR 2027 = 2026-11-16；ICML 2027 ≈ 2027-01 下旬；ACL 2027（ARR）≈ 2027-02；NeurIPS 2027 ≈ 2027-05；EMNLP 2027（ARR）≈ 2027-05/06；ICLR 2028 ≈ 2027-09 下旬。
- 被拒后重投是常态（ICLR 2026 拒稿中约 840 篇被 ICML 2026 接收）。按“投—改—再投”规划，不要在想法阶段追求一次命中。

---

## 2. 第 1–3 周：驻留 = 建设（交付物）

驻留期**至少 2 周、通常 3 周**。交付物齐全之前，不允许以“没意思 / 被拥有 / 天花板不够”为由关闭。

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

- **Build**：针对痛点日志里**真实出现**的问题，做最小的修复 / 方法 / 训练改动 / 评测协议——**从第一周起就允许**。在强基线上发现问题并修好，是顶会最常见的论文来源（诊断 §4.2–4.3：ICLR 多智能体接收论文 90% 是方法/框架型）。
- **Understand**：诊断、消融、表征分析、机制解释——回答“为什么坏、为什么修得好”。
- 两条轨道互相喂：方法没效果 → 诊断为什么；诊断揭示瓶颈 → 设计最小干预。
- **Failure → Bottleneck → Action → Outcome** 仍然是论文的叙事标准，每一环都要有证据；但它是**写论文的标准，不是开始动手的许可**。
- 成功案例也是证据：强基线为什么在旧系统失败的地方成功？哪个旧瓶颈消失了？哪个设计变得不必要？
- 论文身份允许变化：RQ 可以变，方法可以变得不必要，意外的失败可以成为中心结果。但每次变化都要**让故事更简单**，而不是加更多条件。

---

## 4. 论文形态卡（每周更新，人审时看这一页）

参考范例：[`video-world-model-temporal-interfaces/CVPR_ASSESSMENT.md`](video-world-model-temporal-interfaces/CVPR_ASSESSMENT.md)。

```markdown
## 论文形态卡 — <workbench> — <日期>
- 一句话主旨（当前版本）：
- 论文形态：失败模式+修复 / 构念引入+测量 / 理论+受控实验 / benchmark / 系统
- 3 个贡献（状态：✅/⚠️/❌）：
- 4 条摘要主张（状态）：
- 5 张主图/表（状态）：
- 基线列表（含最强开源基线、算力匹配方式）：
- 证据标准：模型/家族数、benchmark 数、种子数、置信区间
- 定位表摘要（最近 5 个近邻 + 各自增量）：
- 风险登记（可能性 / 影响 / 对策）：
- 目标会议与倒排里程碑：
- 本周决定：继续 / 转向（同一领域内）/ 暂停
```

---

## 5. 实验卫生（这是我们的比较优势）

完整的 12 项混杂审计清单、证据等级与独立校对见 [`EXECUTION.md`](EXECUTION.md) §3–§5。最常用的七条：噪声地板（L19）、一阶工具有效性（L29）、算力匹配、≥3 个种子且不筛幸存种子（L45）、输入指纹（S03）、“一句指令能否恢复”（实时线）、选窗 / 读数与被测变量解耦（视频线 E29）。

---

## 6. 何时关闭、暂停或转向

**关闭**（在 D1–D6 交付之后，满足其一，并写明证据）：
- (a) 强基线无法复现，且原因不可修复；
- (b) 主要效应在可承受算力下低于噪声地板；
- (c) 定位表显示**精确撞车**（同一 claim + 同一证据类型 + 同一设定），且无法调整增量；
- (d) 在目标会议前达不到证据标准，且没有合适的后续会议（否则改期，不关闭）。

**不构成关闭理由**：有人做过相关工作；已经成了一个 program；一个解释被证伪（null 结果杀的是解释，不是领域）；第一个 lead 不成立。

**两次连续降级重置**（保留）：连续两个 lead 被平凡对照或近邻吸收后，停止在同一叙事上加实验——回到**同一领域**的痛点日志、形态卡和其他压力，而不是开新 workbench。

关闭或暂停**只由人决定**；agent 可以用 [`../templates/close_record.md`](../templates/close_record.md) 提议（写明证据类别 A 实验 / C 可行性；B 桌面判断不能作为关闭理由）。记录写在本 workbench README 末尾；只有跨项目有用的才复制到 `failed/`（ID 从 K254 起）。

---

## 7. 何时升为 candidate

门槛与候选包见 [`../candidates/README.md`](../candidates/README.md) §1：主旨主张 ≥ L3、3 个贡献各 ≥ L2、机制主张 ≥ L4、全部校对；定位表完成；一句话主旨连续 2 周未变；距截稿 ≥ 8 周（否则改投下一会）；人签字。

---

## 8. README 模板（≤ 200 行）

[`../templates/workbench_readme.md`](../templates/workbench_readme.md)：状态页 / 论文形态卡 / idea 组合 / 主张摘要 / 痛点摘要 / 决策记录 / 资产位置。详细过程写进 `logs/`、实验卡或 `results/`，不写合同式长文。

---

## 9. 登记表（2026-09-30；`tools/process/check.py` 读取本表）

状态只能是 `ACTIVE-MAIN` / `ACTIVE-EXPLORE` / `PROPOSED` / `PAUSED` / `CLOSED`；ACTIVE-MAIN 与 ACTIVE-EXPLORE 各最多 1 条。改状态由人决定并写进对应 README 的决策记录。“截稿”只填官方公告的日期（YYYY-MM-DD），未公告写“—”。

| workbench | 状态 | 目标会议 | 截稿 | 主张账本 | 上次人审 | 备注 |
|---|---|---|---|---|---|---|
| `video-world-model-temporal-interfaces` | ACTIVE-MAIN | CVPR 2027 | 2026-11-16 | `CLAIMS.md` | 2026-09-29 | 块首“接缝失聪”，3 个独立系统复现；关口与第二阶段计划见 `CVPR_ASSESSMENT.md`；`CLAIMS.md` / `PAIN_LOG.md` 于 9/30 按 v4 格式整理，待负责人确认 |
| `multi-llm-collaboration` | PROPOSED | ICML 2027（约 1 月下旬） | — | `CLAIMS.md` | — | 训练出来的开源异构 LLM 团队；territory 卡 `../search/our-taste/TERRITORY_SCAN_2026-09-30.md`；待人确认后改为 ACTIVE-EXPLORE |
| `cross-lingual-acquisition-regimes` | PAUSED | — | — | — | — | 9/30 按 v2 开启，尚未运行；恢复前补 territory 卡的热度 / 立足点 |
| `scoped-context-state` | PAUSED | — | — | — | — | 已生成数据，未完成 P1；恢复前补形态卡 |
| `mechanism-population-dynamics` | PAUSED | — | — | — | — | 未开始；可解释性方向的候选资产 |
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
