# Multi-LLM Collaboration — 开源 LLM 协同训练与 collaborative structure

## 状态（中文进度页）

**ACTIVE-EXPLORE（2026-10-01，人已确认开线）。**  
主线仍是 `video-world-model-temporal-interfaces`（CVPR 2027）；本线占用唯一 ACTIVE-EXPLORE 名额。

- territory 卡：[`../../search/our-taste/TERRITORY_SCAN_2026-09-30.md`](../../search/our-taste/TERRITORY_SCAN_2026-09-30.md) §2
- 题材页：[`../../library/themes/multi-agent-collaboration/`](../../library/themes/multi-agent-collaboration/README.md)
- 目标会议：ICML 2027；证据不够则顺延 ACL 2027 / NeurIPS 2027，不因错过一个 deadline 关线
- **实验硬约束：核心训练与评测必须能用公开权重、本地部署完成；闭源 API 论文只作为 prior，不作为不可替代实验依赖。**

### Territory object（不是已注册的最终 RQ）

> **当多个 open-weight LLM agents 被共同训练后，究竟学到了什么 collaborative structure；其中哪些部分能跨伙伴、角色、模型和预算泛化，哪些只是共同训练产生的相互适配？**

这不是“RL 会不会让换伙伴性能下降”的单一假设，也不是“再做一个多智能体框架”。论文主旨必须从 strong-baseline residency、系统测量和真实 pain 中长出来。

---

## 为什么值得驻留

这个 territory 同时具备：

1. **强开源 substrate**：Dr. MAS / CoMLRL-MAGRPO / MARTI / AT-GRPO 等可训练团队；Qwen / Llama 可本地运行并访问内部状态。
2. **真实 lineage tension**：
   - 传统 ZSC / ad-hoc teamwork：共同训练容易学到 partner-specific convention；
   - prompted LLM collaboration：对陌生伙伴常显示出一定鲁棒性；
   - SRPO 已经明确表明“collaborative policies 对 unseen partners 脆弱”并在一个 LLM collaboration task 上做了初步验证；
   - equal-cost work 与 SAT 又分别质疑“团队收益只是更多算力”和“固定组织方式”的默认前提。
3. **论文形态不单一**：失败模式+修复、成熟构念+测量、评测/会计协议、机制分析都存在已接收先例。
4. **资源匹配**：1.5B–4B 团队可在单节点 4×80–96GB 上做主实验；7B 只作为关键对照。

### 已被占有的宽故事（禁止当作我们的 novelty）

- “协同训练的 agent 换 unseen partner 会脆弱”——SRPO 已直接覆盖。
- “多智能体在等推理成本下未必胜单智能体”——equal-inference-cost lineage 已覆盖。
- “团队不会自然利用最强专家 / 会出现 lazy agent”——Teams Hold Experts Back / Lazy Agents 已覆盖。
- “优化多 Agent 的 role / topology / routing”——已有大量方法。
- “不同模型有 complementarity”——已有 heterogeneous / weak–strong / cross-teaching 工作。

这些不是 kill signal；它们定义我们必须比什么更深。

---

## 四个 pressure families

不是把 P1–P6 当六条独立逃生路线，而是四组：

### V · Value under fair resources
团队在公平训练与推理预算下究竟贡献了什么？  
I02 是全线基础设施，不默认单独成文。

### G · Partner generalization / co-adaptation
共同训练后，协作结构对新伙伴、尺寸、家族、checkpoint 是否可迁移？  
I01 是**第一把测量尺**。消息、内部表征、私有 convention（原 P4/P5）只有在行为结果出现后才作为 mechanism branches。

### R · Heterogeneous roles / contribution
大+小、强+弱成员共同训练后，贡献如何分布；global model strength 是否等于 collaborative role utility？  
I03 只有在异构 baseline 真跑通后才启动，不能预设“小模型会懒惰”。

### T · Task structure
数学 Solver→Verifier 这种固定语义接口，可能天然压低 private-convention 风险。最终结论至少需要一个真正要求 coordination、存在多个可行 convention / distributed information 的任务。合作游戏/NPC 可以作为自然实验环境，而不是为了迎合题材硬塞应用。

---

## 当前 idea 组合与优先级

| ID | 角色 | 状态 | 说明 |
|---|---|---|---|
| [I01](ideas/I01-cross-play-matrix.md) | 第一把行为测量尺 | SEED | 测 cross-play landscape；**不以“发现 partner brittleness”为 novelty** |
| [I02](ideas/I02-compute-matched-gain.md) | 公平比较基础设施 | SEED | 建 performance–compute Pareto accounting，不只做一个 matched point |
| [I03](ideas/I03-big-small-roles.md) | R-family 分支 | PARKED（有触发条件） | 异构 team 跑通且出现 contribution anomaly 后启动 |
| [I04](ideas/I04-message-portability.md) | G-family mechanism 分支 | PARKED（有触发条件） | I01 出现 cross-play signal 或 message-level pain 后启动；functional usability 优先于“读得懂” |

账本：[`CLAIMS.md`](CLAIMS.md) 当前为空；[`PAIN_LOG.md`](PAIN_LOG.md) 从实际运行开始追加。

---

## Residency 顺序（按证据推进，不按周排期）

### D1/D2 · strong baseline + 可复用资产

1. **E01 Dr. MAS math reproduction**：Solver + Verifier，open-weight 小模型起步；复现官方趋势、训练稳定性与 agent-wise gradient 诊断。
2. 从 E01 保存完整 checkpoint / rollout / message / compute log；两个独立训练 seed 直接提供 I01 的 2×2 cross-play smoke test。
3. **统一 compute accounting** 从第一天启用：
   - LM calls / sample；
   - generated + context tokens；
   - active-parameter-token / 近似 FLOPs（能算则算）；
   - GPU·s / GPU·h；
   - wall latency。
4. **E02 CoMLRL code reproduction**：作为第二 substrate；若 math 的固定 Solver–Verifier 接口没有 cross-play signal，不把 null 当作 G-family 的否定。
5. 若需要真正 coordination substrate，优先进入公开、可本地跑的 distributed-information / cooperation game，而不是继续在数学接口上堆控制。

D1/D2 的 reproduction、harness 和标准 measurement 属于 residency 本身，不计入 EXPLORE quota。

### 第一把尺：I01 cross-play smoke test

- 先只回答：不同独立训练 team 的成员互换后，行为矩阵是什么样？
- 若出现大而稳定的 off-diagonal degradation：加第 3 seed + checkpoint trajectory + 受控 partner shift，先确认 effect 和边界；**不立即宣布 novelty**。
- 若 Dr. MAS math 近零：转到更需要 coordination 的任务；不能据此声称“LLM 团队天然 ZSC”。
- 只有 stable behavior 出现后，才决定是否进入 message / role / white-box mechanism。

### I02 作为全线 accounting

最终比较目标是 performance–compute Pareto curve，而不是“token 数完全相等”的单点：
- inference calls/tokens；
- approximate FLOPs；
- GPU time；
- wall latency；
- training compute。

---

## White-box 触发规则

**默认不做“训练前后哪里变了”的 activation fishing。**

只有行为层先出现稳定主张（例如某类 partner shift 明显造成 cross-play degradation，或异构 role contribution 出现稳定反转）后，才启动白盒轨道。白盒实验必须区分至少两个明确 behavioral outcomes，并服务于可证伪 mechanism hypothesis。

---

## 论文形态卡（当前只登记约束，不预写故事）

- 当前一句话主旨：**未定**。
- 当前已成立 contribution：**0**。
- 当前 claims：**0**。
- 必须出现的公平性资产：strong open baseline、compute accounting、多种子、不筛种子、至少一个真正 coordination task。
- positioning ownership：SRPO / equal-inference-cost / Teams Hold Experts Back / SAT / Lazy Agents / Dr. MAS / TeamTR 等持续跟踪；强 arXiv 也视为 claim ownership。
- 不要求“任意结果都能成论文”；只有当 evidence 汇聚成一个清楚 claim + consequence +（需要时）最小 repair，才进入 candidate。

---

## 决策记录

- 2026-09-30：territory scan 推荐本方向；状态 PROPOSED。
- **2026-10-01：人确认正式开线 → ACTIVE-EXPLORE。** 同时采纳 v4.1 校正：
  - I01 是测量尺，不预注册 partner brittleness 为 novelty；
  - I02 是 accounting infrastructure；
  - I03/I04 设 behavior-triggered gate；
  - P4 white-box 延后到稳定行为现象之后；
  - Dr. MAS math 只作为 smoke-test substrate，null 不外推到一般协作；
  - paper shape / 贡献数量不预注册。

## 资产位置

- 实验卡：`experiments/`
- idea 卡：`ideas/`
- 运行日志：`logs/`
- 结果与小型统计：`results/`
- checkpoint / rollout 大文件：节点本地，不进 git；首次运行后在此补精确路径与模型 revision
