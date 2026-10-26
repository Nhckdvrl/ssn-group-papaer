# 主题 1：最初的研究——头的分工从哪里来、能否跨训练对应（E01–E88）

**状态：** 2026-10-11 人决定结项（TERMINATED），不再新增实验或论文工作。卡片上残留的 RUNNING / REGISTERED 是结项时未更新的状态。完整来龙去脉见 [../HISTORY.md](../HISTORY.md) §0–§4、§7。

## 问题
同一架构独立训练多次，注意力头之间的分工（谁做 induction、谁做检索……）从哪里来？哪些陈述能跨训练迁移？

## 站得住的（都限定在所测模型与任务上）
1. **层内哪个头担任角色跟随初始化，不跟随语料。** DataDecide 3 初始化 × 25 语料：同初始化层内一致 0.31–0.42，不同初始化 ≈ 0；9 种角色、14 个尺寸、两个模型家族成立。“在哪一层”对所有模型基本相同（C05，L2）。
2. **分配在训练早期一小段内形成。** 1% 时扰动会重排；2.5% 起同量级噪声仍回到原分配（0.79–0.98）；换语料在 2.5% / 10% 后仍改写 40% / 29%。保留多少随语料实词相似度变化（ρ −0.56 至 −0.80）。
3. **能力、强度、出现时间、基准表现跟随语料；不存在“幸运种子”。**
4. **复制机制群体（E01–E24）：** induction 在 10 个种子里都是“previous-token 瓶颈头 + induction 头”，头身份不重现、相对层序重现（C01）；31M–70M 的晚期“随机序列复制门控”（C02）；仲裁的几种统一解释都被否定。

## 为什么结项
- 对象“头的编号”是坐标：置换对称性下独立初始化之间没有天然对应的编号；同初始化跨语料能保持多少，没能连到更抽象的计算机制，so what 回答不了。
- 四版论文（v0–v3）都在给同一个对象换包装；DLA 排名信度约 0.40；原样重跑就有 9 / 15 次易主（v3）；近邻 Tigges 2024、Bali 2026 已解释大半。

## 论文
[papers/](papers/)：v0 *Born to Copy, Taught to Trust*（10-04）→ v1 *Which Head Takes Which Role?*（10-06）→ v2 *When Do Mechanisms Correspond Across Pretraining Runs?*（10-08）→ v3 *Which Head Does the Work?*（10-10/11）。各版问题见 HISTORY §4。

## 实验卡
**阶段一：复制机制群体、门控与上下文—记忆仲裁（09-30 – 10-03）**

| 卡 | 问题 |
|---|---|
| [E01](experiments/E01-induction-baseline-repro.md) | Pythia-70M induction baseline reproduction |
| [E02](experiments/E02-induction-circuit-population.md) | Induction circuit across 10 independent Pythia-70M runs |
| [E03](experiments/E03-antagonist-mediated-regression.md) | Is late copy regression mediated by acquired antagonist heads? |
| [E04](experiments/E04-context-naturalness-gating.md) | Does a layer-0 "context naturalness" offset gate in-context copying? |
| [E05](experiments/E05-gating-across-scale.md) | Is gated in-context copying a general late-training phenomenon? |
| [E06](experiments/E06-what-keys-the-gate.md) | What property of the context keys the copy gate? |
| [E07](experiments/E07-gate-vs-degeneration.md) | Context-level gate or token-level degeneration? |
| [E08](experiments/E08-is-the-gate-rational.md) | Is copying actually less reliable in rare-dense contexts of the training data? |
| [E08b](experiments/E08b-gate-regime-data-support.md) | Data support and copy reliability of the gate's regime, on a large Pile sample |
| [E09](experiments/E09-gate-at-160m.md) | Does the rarity-keyed context gate, and its data-sparse seed spread, exist at 160M? |
| [E10](experiments/E10-gate-vs-capacity.md) | How do the copy gate and its between-run spread depend on capacity? |
| [E11](experiments/E11-functional-consequence.md) | Which realistic in-context tasks does the late gate impair? |
| [E13](experiments/E13-arbitration-across-runs.md) | Is context-vs-memory arbitration reproducible across independent runs? |
| [E14](experiments/E14-ioi-portability.md) | Claim portability for the IOI circuit across independent runs |
| [E15](experiments/E15-claim-portability.md) | Claim portability across independent runs |
| [E16](experiments/E16-arbitration-default-offset.md) | Is run-level arbitration divergence a low-dimensional default offset on a shared knob? |
| [E17](experiments/E17-arbitration-vs-knowledge.md) | Is run-level arbitration divergence just knowledge-strength divergence? |
| [E18](experiments/E18-context-reliance-trait.md) | Is context reliance a stable run-level trait? |
| [E19](experiments/E19-late-snapshot-stability.md) | Is the run-level context/memory difference a property of the run or of the snapshot? |
| [E20](experiments/E20-recipe-vs-seed-arbitration.md) | Does the data recipe or the seed set context/memory arbitration at 1B? |
| [E21](experiments/E21-rare-fact-divergence.md) | Do same-recipe runs disagree mostly on rare facts? |
| [E22](experiments/E22-global-context-prior.md) | Is there a corpus-level "context-trust prior" beyond item frequency? |
| [E23](experiments/E23-corpus-structure-to-copy-prior.md) | Does corpus repetition structure predict a recipe's copy-vs-recall prior? |
| [E24](experiments/E24-induction-mediation.md) | Is the recipe's copy-vs-recall prior carried by induction (copy) strength? |

**阶段二：Flan“Question:”模板习惯（C04）**——人 10-10 决定不作研究对象，卡片与结果已删除（Git 历史保留）。E26 / E28 两个脚本因被后续代码导入而保留在 `../scripts/`。

**阶段三：初始化 × 语料与头的角色（10-03 – 10-11，论文线）**

| 卡 | 问题 |
|---|---|
| [A01](experiments/A01-confound-audit-C04-C05.md) | 混杂审计（EXECUTION.md §4）：C04 与 C05 |
| [E35](experiments/E35-init-by-data-mechanism-census.md) | Is mechanistic component identity set by initialization or by training data? A crossed 3-init × 25-data census |
| [E36](experiments/E36-init-effects-on-behaviour.md) | Does the initialization carry behavioural offsets across 25 training corpora? |
| [E37](experiments/E37-identity-lock-in-timing.md) | When during pretraining is the initialization-set component layout locked in? |
| [E38](experiments/E38-c05-at-300m.md) | Does the init-sets-layout / data-sets-strength dissociation (C05) hold at 300M? |
| [E39](experiments/E39-init-weight-predictors-of-roles.md) | What in the random initialization predicts which heads take which roles? |
| [E40](experiments/E40-lock-in-curves-pythia.md) | Lock-in curves of role layout within single runs (Pythia, dense early checkpoints; CPU) |
| [E41](experiments/E41-initial-gradient-predictors.md) | Does the initial gradient (growth rate at step 0) predict which heads take which roles? |
| [E42](experiments/E42-causal-role-maps-and-transfer.md) | 因果定义的角色图是否也由初始化决定？头级干预能否在模型之间迁移？ |
| [E43](experiments/E43-coordinate-system-vs-content.md) | 初始化固定的是“坐标系”，数据决定的是“内容”？——按索引对齐 vs 置换 / 旋转不变的交叉分离 |
| [E44](experiments/E44-pythia-natural-experiments.md) | 第二个模型家族的天然实验——Pythia 标准 / 去重共用初始化；PolyPythias 拆开初始化与数据顺序 |
| [E45](experiments/E45-scale-series-4m-to-1b.md) | 尺寸曲线——“位置由初始化决定”在 DataDecide 的 14 个尺寸（4M–1B）上是否成立、如何随尺寸变化？ |
| [E46](experiments/E46-controlled-training-basin-and-critical-period.md) | 受控预训练——数据能否挪动成分位置？初始化扰动的吸引域多大？位置何时锁定（关键期）？ |
| [E46b](experiments/E46b-controlled-training-larger-model.md) | 受控训练中的规模效应——更大的模型里，位置由初始化还是早期数据决定？ |
| [E46c](experiments/E46c-what-sets-inheritance-init-scale-and-lr.md) | 继承强度由什么决定？——固定架构下操纵初始化尺度与学习率 |
| [E51](experiments/E51-benchmark-variance-decomposition.md) | 下游基准上的“先天 / 后天”——初始化对 11 个任务有没有主效应？ |
| [E52](experiments/E52-specialized-neurons-inheritance.md) | 头记得 seed、神经元忘了——高度特化的神经元是否例外？ |
| [E54](experiments/E54-when-developmental-timing.md) | “何时”由谁决定？——受控训练中 induction 出现时刻的初始化 / 语料分解 |
| [E55](experiments/E55-algorithm-level-universality.md) | 算法层是否普适？——previous-token → induction 的两步算法在每个模型中都成立吗 |
| [E56](experiments/E56-inheritance-depends-on-corpus-similarity.md) | 继承的边界条件——同初始化的头身份，只在早期统计相似的语料之间被继承？ |
| [E57](experiments/E57-scale-curve-development.md) | 尺寸曲线的发育视角——小模型是从来没有继承，还是继承过又被冲掉？ |
| [E58](experiments/E58-pythia-to-12b.md) | 第二家族扩展到 12B——Pythia 6.9B / 12B 的标准版与去重版 |
| [E59](experiments/E59-more-head-roles.md) | 更多头角色——“初始化选槽位”是否适用于所有类型的头？ |
| [E60](experiments/E60-corpus-distance-predicts-inheritance.md) | 语料越相似，初始化的槽位继承越强？ |
| [E61](experiments/E61-anatomical-seed-identification.md) | 解剖学 seed 识别——只看头的分工布局，能否认出在陌生语料上训练的模型来自哪个 seed？ |
| [E62](experiments/E62-batch-size-sets-inheritance.md) | batch 大小决定继承强度？——为 DataDecide 的规模趋势找机制 |
| [E66](experiments/E66-early-window-warmup-and-optimizer.md) | 早期窗口跟随训练进度，还是跟随学习率 warm-up 与优化器状态？ |
| [E67](experiments/E67-audit-all-sizes.md) | 1B 以下所有尺寸的初始化核查与 checkpoint 记录 |
| [E68](experiments/E68-identification-baselines.md) | 认出初始化——权重 baseline 与 SeedPrints baseline |
| [E69](experiments/E69-strongest-head-and-reviewer-checks.md) | E69（POST-HOC）：最强头的一致、只看承载角色的层、模板特异性的合并检验 |
| [E70](experiments/E70-seed-matched-attribution.md) | 比较不同数据训练的模型时，头层面的差异有多少来自初始化？ |
| [E71](experiments/E71-early-localization.md) | 能否在训练早期定位将来的角色头？ |
| [E72](experiments/E72-head-alignment-gauge.md) | 头的编号是不是纯粹的坐标约定？跨初始化对齐后，被留出的角色能否对上？ |
| [E73](experiments/E73-ioi-component-transfer.md) | 一个已发表 circuit 的头标签，能否带到同初始化、不同数据的模型上？（IOI，2026-10-07） |
| [E74](experiments/E74-ioi-across-corpora.md) | IOI circuit 的头标签在 25 个语料、3 个初始化之间如何推广？（DataDecide 1B，2026-10-07） |
| [E75](experiments/E75-ioi-transfer-gap-decomposition.md) | 410M 同初始化兄弟之间 IOI 迁移只有 0.05——是计算变了、同一计算换了承担者，还是测量造成的？ |
| [E77](experiments/E77-arbitration-atlas.md) | 上下文 / 记忆仲裁的条目级图谱——训练让模型沿着同一条“置信度曲线”移动，还是改变了曲线本身？ |
| [E79](experiments/E79-memory-route-under-conflict.md) | 冲突上下文下，存活的记忆从哪条通路进入？ |
| [E81](experiments/E81-carrier-inheritance.md) | 头角色与因果承担者的继承——信度校正，以及继续训练的后代 |
| [E82](experiments/E82-when-carriers-are-fixed.md) | 因果承担者在训练的什么时候定下来？兄弟模型从哪一步开始分叉？ |
| [E83](experiments/E83-carrier-chosen-at-emergence.md) | 主力承担者是不是在任务行为出现时选定一次、之后保持？兄弟是否共享由那一刻决定？ |
| [E84](experiments/E84-relocation-vs-suppression.md) | 删数据重训后“目标头变弱”，是能力被抑制，还是活换给了别的头？ |
| [E85](experiments/E85-candidate-gap-and-swaps.md) | 两个候选越接近，随机删数据越容易换掉胜者吗？ |
| [E87](experiments/E87-E88-review-checks.md) | 回应 2026-10-11 审稿意见的检验 |

## 代码与结果
共用 [../scripts/](../scripts/) 与 [../results/](../results/)（按 `eNN` 命名）。脚本以 `heads/` 为根（`mp_common.RESULTS = heads/results`）；Pythia / DataDecide 检查点已不在本地，重跑需重新下载。
