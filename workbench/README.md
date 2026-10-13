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

参考范例：[`in-context-evidence-structure/PAPER_SHAPE.md`](in-context-evidence-structure/PAPER_SHAPE.md)（文件含历史形态卡，使用时请查看最新状态）。

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

## 当前决定与整理（截至 2026-10-12）

- **用户明确要求直接删除** `real-time-causalization-capability-preservation`、`scoped-context-state`、`cross-lingual-acquisition-regimes`、`multi-llm-collaboration`、`video-world-model-temporal-interfaces` 这五个 workbench 的当前 Git 树文件。历史 Git 提交仍可追溯，不另建 archive 副本，不擅自触及外部服务器缓存。
- **`mechanism-population-dynamics`：CLOSED / TERMINATED / 已收尾。** 用户认为该项目投入大量研究工作后，进一步的科学价值、意义有限，决定终止。论文 v0–v3、结果、代码、实验与日志全部保留在原目录，不启动新的实验或论文工作。10 月 9 日“继续”的历史决定已由 10 月 11 日决定覆盖。
- **没有 ACTIVE-MAIN。** `in-context-evidence-structure` 保持唯一 ACTIVE-EXPLORE；其它剩余工作台状态不变。
- 2026-10-11 **后续人类决定**：再从 HEAD 删除 `npc-persona-behavior-grounding` 和 `npc-deception-investigability`，仍保留知识库中的 NPC 文献；**10 月 11 日清理后剩余 5 个 workbench**。2026-10-12 新建 `xeno-interpretability` 后，**截至 2026-10-12 共 6 个**；2026-10-13 新建 `game-npc-agents` 后共 7 个。详见 [清理记录](WORKBENCH_CLEANUP_2026-10-11.md)。
- [2026-10-09 审计](WORKBENCH_AUDIT_2026-10-09.md)只是历史快照；相关领域的 `library/` 文献继续保留。

## 9. 登记表（2026-10-13；`tools/process/check.py` 读取本表）

状态只能是 `ACTIVE-MAIN` / `ACTIVE-EXPLORE` / `PROPOSED` / `PAUSED` / `CLOSED`；ACTIVE-MAIN 与 ACTIVE-EXPLORE 各最多 1 条。改状态由人决定并写进对应 README 的决策记录。“截稿”只填官方公告的日期（YYYY-MM-DD），未公告写“—”。

| workbench | 状态 | 目标会议 | 截稿 | 主张账本 | 上次人审 | 备注 |
|---|---|---|---|---|---|---|
| `mechanism-population-dynamics` | CLOSED | — | — | `CLAIMS.md` | 2026-10-11 | **终止并完成结项整理**：[科学总结](mechanism-population-dynamics/CLOSEOUT.md)、[v3 最终工作稿](mechanism-population-dynamics/paper-acl-v3/)、[科研资产索引](mechanism-population-dynamics/ASSET_INDEX.md)。所有旧论文、科研结果与独立复现包保留；清除 13 个再生缓存，不继续实验。 |
| `latent-world-model-planning` | PROPOSED | ICML / ICLR / NeurIPS；届次待定 | — | `CLAIMS.md` | — | **已有原生GPU测量与训练**：R1–R5持续开放；固定数据充分训练seed0/1/2为38/19/36（各48）；当前方法入口按RESEARCH_PLAN与I14/E20执行，尚无已成立科学主张；不改变ACTIVE分配 |
| `data-centric-rsi` | PROPOSED | ICML / ICLR / NeurIPS；届次待定 | — | `CLAIMS.md` | — | **已有真实GPU底座**：E12四静态策略完整八任务评分；E13/E14八支训练与全部原定终点评分完成，当前停步交人审；I01/I02/I03仍为候选，主张均L0；实时数字见workbench状态页，不改变ACTIVE调度 |
| `in-context-evidence-structure` | ACTIVE-EXPLORE | ICML / ICLR；ACL / EMNLP 叙事并行 | — | `CLAIMS.md` | 2026-10-08 | 继续保持正式探索线；截至 2026-10-11 已完成 E103，E104 的运行前设计已建立，尚未形成新机制主张；本次清理不改变其研究状态。 |
| `incremental-interpretation-revision` | PROPOSED | ACL / EMNLP / NAACL | — | `CLAIMS.md` | 2026-10-06 | **人已授权 residency；2026-10-08要求整理并上传main**：103张卡的方向/结果与整体总结见该workbench，尚无合格idea；09:00前已释放GPU和权重，当前无实验队列。需标注只用Step Plan step-5-preview，禁止现金接口；未改变当前ACTIVE分配或线状态 |
| `xeno-interpretability` | PROPOSED | —（探索阶段） | — | `CLAIMS.md` | — | **用户 2026-10-12 指定新建 workbench，专属知识库在 [`knowledge/`](xeno-interpretability/knowledge/) 内；初始文献核查与实验设计仍未构成实证发现；不调整 ACTIVE 分配。** |
| `game-npc-agents` | PROPOSED | ICML / ICLR / NeurIPS；ACL / EMNLP / NAACL（取决于论文形态） | — | `CLAIMS.md` | — | **2026-10-13 用户明确授权新建游戏 NPC Agent 独立 workbench**；专属 [knowledge/](game-npc-agents/knowledge/README.md)，2026-10-14 用户重新开放领域范围（行为学习、互动、人格漂移、NPC安全、游戏内多Agent经济/攻击等并列），详见 [领域地图](game-npc-agents/knowledge/DOMAIN_ATLAS.md)；无锁定具体idea、无新GPU实验、不占 ACTIVE。 |
