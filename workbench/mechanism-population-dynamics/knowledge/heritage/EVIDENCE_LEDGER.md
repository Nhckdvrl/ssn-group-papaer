# 证据账本：稳定观察、解释假说、撤回结果必须分开

**2026-10-15 整理。历史等级来自根目录 [CLAIMS.md](../../CLAIMS.md)，不是本知识库独立验证的新等级。**

## 1. 推荐的五态

- **OBSERVED**：指定模型/任务/指标下有已保存的实验报告或代码。
- **SUPPORTED-LIMITED**：有多组或有限干预的支持，但可外推范围窄，不能泛化。
- **HYPOTHESIS**：与结果一致的解释之一；尚无区分性因果实验。
- **REJECTED/REVISED**：曾明确提出并经登记反证或严格审计后撤回。
- **UNKNOWN/BLOCKED**：关键结果未运行、原始对象缺失、存在代码合同错误或已知数据异常。

上述状态不能改写原始 L1/L2；需要解释的是“能知道什么”。

## 2. 历史 C01/C02/C03/C05

| 主张 | 可安全复述的事实 | 不可复述的强化版本 | 证据 |
|---|---|---|---|
| C01：induction 机制可复现 | 10 个 Pythia-70M seed 里找到了 previous-token 与 induction 的计算组合和部分因果依赖，限其合成测量 | 各模型全部 ICL / few-shot 算法都一样 | [E02](../../experiments/E02-induction-circuit-population.md)、[E55](../../experiments/E55-algorithm-level-universality.md) |
| C02：后期随机复制门控 | Pythia-70M 特定随机 token 条件有分布平移式干预线索 | 是自然任务的真实通用瓶颈；大模型普遍存在 | [E04](../../experiments/E04-context-naturalness-gating.md)、[E11](../../experiments/E11-functional-consequence.md) |
| C03：机制陈述跨训练可迁移性分层 | 角色/算法宽泛描述比单头编号更易跨一些任务和 seed 保持；阈值与能力条件重要 | 已建立跨模型定量统一可迁移性定律 | [E15](../../experiments/E15-claim-portability.md)、[CLAIMS](../../CLAIMS.md) |
| C05：初始化 × 数据与角色图 | 已审计69个1B模型，同初始化跨语料有一定层内角色图对应，异初始化原编号接近零 | 初始化决定具体头命运；数据绝不能影响 head；有直接行为因果后果 | [E35](../../experiments/E35-init-by-data-mechanism-census.md)、[E59](../../experiments/E59-more-head-roles.md)、[E42](../../experiments/E42-causal-role-maps-and-transfer.md) |

## 2b. 2026-10-15/16 重启后的新证据（E89–E92；原始记录见各实验卡）

| 观察 | 状态 | 范围与读法 | 证据 |
|---|---|---|---|
| 跨独立种子重现的是任务深度顺序与“哪些任务共用关键头”（greater-than~后继 10/10、induction~反义词 ICL 9/10；S 跨模型 0.57 / 满分 0.95 / 打乱 0.38），不重现的是头编号与层号 | SUPPORTED-LIMITED | Pythia-410M 10 种子、160M 15 模型、DataDecide-1B 12 模型；9 个任务；共用关系由 top-3 重合与 S 刻画，未做“共用头”的因果检验；两组共用可由已有认识预言（Olsson、Gould） | [E89](../../experiments/E89-division-of-labour-atlas.md) |
| 编号对应只在共享初始化时出现（同一 run 0.97、重跑 0.74、换顺序 0.72、换去重语料 0.52、换种子 0.00） | OBSERVED | 160M weight-seed 实为原版重跑（P09 复核） | E89 结果二 |
| 正常 410M 种子在 1k 步定下 induction 的单点瓶颈 previous-token 头，此后 14 万步不换；两个异常种子各在一次单步 loss spike（74k→76k、122k→124k）当步换头并全面崩溃，之后按原发育顺序重学，示例格式 ICL 在剩余训练内不恢复 | OBSERVED（n=2 事件） | “深度预算”解释被 seed4 否定；剩余解释接近“后期能力重学慢 + 学习率已低” | [E90](../../experiments/E90-outlier-trajectories.md) |
| seed4 的 spike 前 ≥7k 步，第 21 层非 previous-token 头 21.14 的行内 logit 尖锐度陡增；seed3 无头级前兆 | OBSERVED，停止 | 与 Kimi K2“少数头 logit 爆炸”一致，作排除项 | [E91](../../experiments/E91-spike-origin-heads.md) |
| 真实预训练（PolyPythias ≤410M，42 任务）中正常 run 的能力种子差异是逐任务独立的小幅连续波动，不是双峰；失败尾部是 run 级事件 | SUPPORTED-LIMITED | 31M seed8 的 few-shot 全零主要是“A: 后接换行”格式偏好；410M seed8 的“反义词失败”是 E89 自制测法的假象 | [E92](../../experiments/E92-capability-atlas-seeds.md) |
| 31M 正常种子中出现“学会后丢失”（后继 4 种子 0.30–0.40 → 0.05–0.17 等）而损失持续下降 | HYPOTHESIS（线索） | 只在 31M、未做机制分析；IOI 的低于随机下探已由 Dahiya 2026 解释 | E92 结果二 |

## 3. 重要的可观测数值与正确读法

| 观察（历史实验读数） | 情境/单位 | 现阶段如何理解 |
|---|---|---|
| E59 9 类角色层内相关 SI 0.18–0.43 / SD ~0 | DataDecide-1B 已核查模型对 | 指标为 attention/OV score 的平均秩相关，不是“九种因果职业” |
| E72 留出角色异初始化对齐后 induction .68 / previous .74 | 多维通用角色 Hungarian 对齐 | 对齐后的功能统计相似，有效维度小，可能多个角色相关，非 IOI transfer |
| E42 头级消融相对迁移约 20% | 18模型、特定头/任务、单头读数 | 强相关主张未过预登记门槛 |
| E73 IOI top3 迁移 .85 (160M) 与 .05 (410M) | Pythia std→dedup、DLA top3 | 任务因果承担很依赖训练结果，不能单个尺寸外推 |
| E75 410M .06→.85，异初始化 0→.94 | 原编号 joint vs 使用目标 DLA 匹配再在留出提示评测 | 可目标辅助重定位，不是 source-only zero shot |
| E81 ablation map 跨兄弟 .02，注意 .24–.34 | 三语料×三初始化，部分是同 seed 独立训练 | 注意统计同因果承担不是同一对象；原统计量信度需区别 |
| E81 DLA rank SB .40，value Pearson .98 | Pythia410M, IOI N=200，split-half | 大量近零头的秩不稳，不等于重要效应读数不稳 |
| E83 主力头行为首次出现后仍延续 3/12 | DataDecide1B 12 run 轨迹 | 明确否定发育即锁定的一般律 |
| E86 3000步不变 rerun argmax易主9/15，随机屏蔽14/30 | 控制预训练12层模型 | 换第一名并不证明整套因果角色换人；mask并非特异原因 |
| E68 weight baseline seed识别98–100% | 4M–1B 多尺寸 | provenance 不是头布局的独特应用 |
| P12 75个中6个初始化错误标注 | 训练起点直接核对 | 1B比较必须使用有效69个模型 |

## 4. 需要“禁止重新宣传”的结论

**REJECTED：**
- “所有的初始化在尚未见到数据时预先给每个 head 分配功能。”
- “模型权重忘记 seed，头却能识别它，因此有独特 provenance 应用。”——已有 raw weight 更强基线。
- “原编号电路在共享初始化模型能稳定迁移。”——跨语料及部分 Pythia 尺寸不成立。
- “任务能力首次出现就锁定承担者。”——E83 留出验证失败。
- “随机屏蔽少量训练数据会独特地导致最强 induction head 易主。”——完全一样 rerun 也常发生。
- “完整 IOI 计算算法在所有模型已被证明相同。”——现有只是部分功能类/路径/权重组合。
- “Flan 含少量问答语料就普遍教会一套上下文可信度总开关。”——根项目已明确撤回。

**UNKNOWN，不能以口头叙述补齐：**
- E81 在 v3 中选头与联合消融的一致定义（已有代码不一致）。
- E87 10k步的完整 rerun 实验（用户已叫停，没有结果）。
- E88 bootstrap bug 部分未修。
- v3 某些图依赖 Git 未跟踪的 NPZ 原始数组，clone 后不保证能复算。
- “函数相同”究竟是在类别、局部中介还是完整路径层面。

## 5. 独立复现与结果出处

审计时分别记：
- **预登记预测/阈值**：在看结果前写下的；
- **实际结果**：来自 JSON / ndarray / model forward；
- **事后分析**：发现异常后设计，不应和预登记并为一份主证据；
- **进一步解释**：一种可能解释，可与竞争解释并列；
- **独立证据**：其他 model family / corpus / train lineage / dataset 的证据，不能靠重复一个统计推断扩充数量。

原始事实索引见 [EXPERIMENT_ATLAS](EXPERIMENT_ATLAS.md)。若新的知识卡与原始实验卡冲突，检查时间戳和修订记录，再更新本文件，保留冲突原因。
