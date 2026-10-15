# 实验遗产全景：按认知问题检索，而非按 E 编号复制

**整理日期：2026-10-15。全部链接指向原始实验卡；此处只是研究导览，不覆盖原始记录。** “完成”是原卡历史记录，不等于本次重新运行或第三方复现。历史卡的 RUNNING 不代表现在有训练任务。

## 1. 最先阅读的十条证据链

| 链 | 涵盖实验 | 经历了怎样的判断变化 | 当前正确入口 |
|---|---|---|---|
| 复制机制的真实复现 | [E01](../../experiments/E01-induction-baseline-repro.md) → [E02](../../experiments/E02-induction-circuit-population.md) | parent 的消融实现和随机对照问题被发现，改用明确消融后建立小模型局部证据 | [复现陷阱](FAILURE_MODES.md) |
| 伪新颖的随机序列门控 | [E03](../../experiments/E03-antagonist-mediated-regression.md) → [E04](../../experiments/E04-context-naturalness-gating.md) → [E05](../../experiments/E05-gating-across-scale.md) → [E11](../../experiments/E11-functional-consequence.md) | 一度获得强局部干预，但自然任务未受损、规模效应消失；不能作为广泛问题 | 证据账本 C02 |
| 仲裁是否是模型“特质” | [E13](../../experiments/E13-arbitration-across-runs.md) → [E16](../../experiments/E16-arbitration-default-offset.md) → [E18](../../experiments/E18-context-reliance-trait.md) → [E20](../../experiments/E20-recipe-vs-seed-arbitration.md) | 多项看似“统一解释”被条件异质性否定 | 概念：条件化而非全局先验 |
| 数据配方能否产生机制中介 | [E23](../../experiments/E23-corpus-structure-to-copy-prior.md) → [E24](../../experiments/E24-induction-mediation.md) | 主假设失败，事后跨语料相关经家族校正压缩 | 不把跨配方相关当中介 |
| 种子与角色统计 | [E35](../../experiments/E35-init-by-data-mechanism-census.md) → [E45](../../experiments/E45-scale-series-4m-to-1b.md) → [E59](../../experiments/E59-more-head-roles.md) | 统计对应存在，但规模、语料与身份口径必须限缩，1B 有错误标签 | G1 角色图 |
| 训练早期路径依赖 | [E37](../../experiments/E37-identity-lock-in-timing.md) → [E46](../../experiments/E46-controlled-training-basin-and-critical-period.md) → [E66](../../experiments/E66-early-window-warmup-and-optimizer.md) | “关键期百分比锁定”改为学习早期、受训练动力学影响的约束形成 | [训练动力学](../syntheses/TRAINING_DYNAMICS.md) |
| 初始标量为何预测不了 | [E39](../../experiments/E39-init-weight-predictors-of-roles.md) → [E41](../../experiments/E41-initial-gradient-predictors.md) | 范数/梯度范数均无层内预测力，但不能因此宣称证明集体竞争 | 未测试几何/交互来源 |
| 对齐后的含义 | [E70](../../experiments/E70-seed-matched-attribution.md) → [E72](../../experiments/E72-head-alignment-gauge.md) → [E75](../../experiments/E75-ioi-transfer-gap-decomposition.md) | 通用统计对齐能恢复留出角色，却不稳定指认任务因果承担者；目标 DLA 重定位不算零样本迁移 | [对齐与对称](../syntheses/SYMMETRY_ALIGNMENT.md) |
| 任务 carrier 的条件性 | [E42](../../experiments/E42-causal-role-maps-and-transfer.md) → [E73](../../experiments/E73-ioi-component-transfer.md) → [E74](../../experiments/E74-ioi-across-corpora.md) → [E81](../../experiments/E81-carrier-inheritance.md) | attention 角色相似不等于 IOI 因果承担；祖先延续与独立分支不可混同；E81 transfer 的代码指标与文章定义不一致 | [度量审计](MEASUREMENT_AUDIT.md) |
| “形成即锁定”与“删数据致换人” | [E82](../../experiments/E82-when-carriers-are-fixed.md) → [E83](../../experiments/E83-carrier-chosen-at-emergence.md) → [E85/E86](../../experiments/E85-candidate-gap-and-swaps.md) | 3/12 支持锁定，其余不支持；原样重跑也常发生 argmax 易主；训练到 10k 的验证 E87 未完成 | 避免 argmax 概念偷换 |

## 2. 按主题找到所有历史实验

### A. Induction、复制与最初的失败探索

- [E01](../../experiments/E01-induction-baseline-repro.md)：基础复现和 parent 代码测量偏差；重要的是复现代码审计，不是“另一个复制分数”。
- [E02](../../experiments/E02-induction-circuit-population.md)：多个 Pythia-70M seed 的前一 token→induction 组成，受限于合成随机序列。
- [E03](../../experiments/E03-antagonist-mediated-regression.md)：单头拮抗解释被撤回；必须保存干预方式不一致的反证。
- [E04](../../experiments/E04-context-naturalness-gating.md)：分布均值平移对 synthetic 复制的局部挽救。
- [E05](../../experiments/E05-gating-across-scale.md)：规模条件，后期门控不是大型模型的普遍现象。
- [E06](../../experiments/E06-what-keys-the-gate.md)：门控信号的输入形态诊断。
- [E07](../../experiments/E07-gate-vs-degeneration.md)：区分原始退化指标和真正计算能力。
- [E08](../../experiments/E08-is-the-gate-rational.md)、[E08b](../../experiments/E08b-gate-regime-data-support.md)：早期“合理数据校准”结论被更完整数据推翻。
- [E09](../../experiments/E09-gate-at-160m.md)、[E10](../../experiments/E10-gate-vs-capacity.md)：跨规模和容量控制。
- [E11](../../experiments/E11-functional-consequence.md)：自然上下文任务不受显著损害，给出清晰止损证据。
- [E14](../../experiments/E14-ioi-portability.md)、[E15](../../experiments/E15-claim-portability.md)：机制结论沿独立训练迁移的陈述层级；注意读数的任务和阈值依赖。
- [E19](../../experiments/E19-late-snapshot-stability.md)：单次训练晚期快照的角色/行为稳定性。
- [E55](../../experiments/E55-algorithm-level-universality.md)：75/75 权重组合满足随机对照阈值，但单头因果证据 12/18；“完全算法普适”证据不足。

### B. Context vs memory：原研究分叉

- [E13](../../experiments/E13-arbitration-across-runs.md)：10 个 410M seed 中仲裁角色可见、层/成分不固定；原第二机制猜想部分失败。
- [E16](../../experiments/E16-arbitration-default-offset.md)：统一一维旋钮不足。
- [E17](../../experiments/E17-arbitration-vs-knowledge.md)：知识强度不能单独解释条件间差异。
- [E18](../../experiments/E18-context-reliance-trait.md)：不是稳定的跨条件“个人性格”。
- [E20](../../experiments/E20-recipe-vs-seed-arbitration.md)：配方作用存在，但没有跨条件统一的“可信度先验”。
- [E21](../../experiments/E21-rare-fact-divergence.md)、[E22](../../experiments/E22-global-context-prior.md)：稀有事实与全局偏好等假说的检验；注意原主张降级。
- [E23](../../experiments/E23-corpus-structure-to-copy-prior.md)、[E24](../../experiments/E24-induction-mediation.md)：数据统计与复制读数不足以形成因果中介链。
- [E38](../../experiments/E38-c05-at-300m.md)：后来归入初始化交叉验证，不能被读作仲裁的结果。
- [E77](../../experiments/E77-arbitration-atlas.md)、[E79](../../experiments/E79-memory-route-under-conflict.md)：2026-10-10 晚期探索中，E77 仅部分检查点数据且主要先验不通过；E79 是单个 Pythia 模型原型，不能当通用发现。

**历史清理说明：** Flan/Question 格式线的 E25–E34、E47–E49、E50、E53、E65、E76、E80 等卡原本就已从当前树移出；不要创建伪链接、不要从旧稿复活已停止的主张。可用 Git 历史研究来龙去脉，但不把已删文件当作当前文件。

### C. 初始化 × 语料、角色分配与表示

- [E35](../../experiments/E35-init-by-data-mechanism-census.md)：核心交叉设计；使用 [P12 初始化审计](../../PAIN_LOG.md) 后的69个1B模型重算，不引用未筛 75 个总体作主要效应。
- [E36](../../experiments/E36-init-effects-on-behaviour.md)：种子偏向在某些行为层面没有强主效应，不意味着种子对所有行为都无影响。
- [E37](../../experiments/E37-identity-lock-in-timing.md)、[E40](../../experiments/E40-lock-in-curves-pythia.md)：在时间轴观察统计角色图。
- [E39](../../experiments/E39-init-weight-predictors-of-roles.md)、[E41](../../experiments/E41-initial-gradient-predictors.md)：范数级预测失败，不能以此证明不存在初始方向信息。
- [E42](../../experiments/E42-causal-role-maps-and-transfer.md)：G1统计到G2因果跨越不足；约20%的相对迁移未过预设标准。
- [E43](../../experiments/E43-coordinate-system-vs-content.md)：index-aligned vs CKA / permutation invariant 的相似性不同。
- [E44](../../experiments/E44-pythia-natural-experiments.md)：第二模型家族；部分公开检查点的标签错误。
- [E45](../../experiments/E45-scale-series-4m-to-1b.md)：规模趋势有角色依赖；不是4M至1B每个尺寸均成立。
- [E46](../../experiments/E46-controlled-training-basin-and-critical-period.md)、[E46b](../../experiments/E46b-controlled-training-larger-model.md)、[E46c](../../experiments/E46c-what-sets-inheritance-init-scale-and-lr.md)：受控训练、扰动及对地板效应的修正。
- [E51](../../experiments/E51-benchmark-variance-decomposition.md)、[E52](../../experiments/E52-specialized-neurons-inheritance.md)、[E54](../../experiments/E54-when-developmental-timing.md)：行为/神经元/时间维度；勿将跨尺度主效应说成因果解释。
- [E56](../../experiments/E56-inheritance-depends-on-corpus-similarity.md)、[E57](../../experiments/E57-scale-curve-development.md)、[E58](../../experiments/E58-pythia-to-12b.md)、[E59](../../experiments/E59-more-head-roles.md)：继承尺度、角色范围与第二模型家族扩展；Pythia-2.8B 去重版异常不纳入分析。
- [E60](../../experiments/E60-corpus-distance-predicts-inheritance.md)、[E62](../../experiments/E62-batch-size-sets-inheritance.md)、[E66](../../experiments/E66-early-window-warmup-and-optimizer.md)：语料距离和训练动力学；关联不等于统一的一般数学定律。
- [E61](../../experiments/E61-anatomical-seed-identification.md)、[E67](../../experiments/E67-audit-all-sizes.md)、[E68](../../experiments/E68-identification-baselines.md)、[E69](../../experiments/E69-strongest-head-and-reviewer-checks.md)：识别应用被权重更强基线压缩，不能作主要论文贡献。

### D. 对齐、跨 run 电路与 carrier 演化

- [E70](../../experiments/E70-seed-matched-attribution.md)、[E71](../../experiments/E71-early-localization.md)、[E72](../../experiments/E72-head-alignment-gauge.md)：同初始化来源、早期定位、多角色匹配；E72b 指向低有效维度而非丰富类型。
- [E73](../../experiments/E73-ioi-component-transfer.md)：同初始化跨 Pythia 去重版的迁移高度依赖规模与分散程度。
- [E74](../../experiments/E74-ioi-across-corpora.md)：同种子不同语料的 IOI 因果定位弱于注意力图，源端 top3 不是高效 target circuit。
- [E75](../../experiments/E75-ioi-transfer-gap-decomposition.md)：区分原编号、角色匹配与目标辅助 DLA 重定位；已有 target-only 基线缺口。
- [E81](../../experiments/E81-carrier-inheritance.md)：真正同 lineage vs independently trained sibling；信度与定义契约问题。
- [E82](../../experiments/E82-when-carriers-are-fixed.md)、[E83](../../experiments/E83-carrier-chosen-at-emergence.md)：Pythia 的后验轨迹不足，DataDecide 前瞻3/12 否定“出现即锁定”一般律。
- [E84](../../experiments/E84-relocation-vs-suppression.md)、[E85/E86](../../experiments/E85-candidate-gap-and-swaps.md)：随机掩码与完全相同 rerun 对照，argmax 转移不等于因果工作转移。
- [E87/E88](../../experiments/E87-E88-review-checks.md)：10k步验证停止，bootstrap 脚本部分有 bug；禁止在任何综合图中算作完成。

## 3. 工作链的主张版本不是“进度条”

历史论文：
- [v0](../../paper-acl-v0/main.tex) “Born to Copy, Taught to Trust”：先天/后天比喻与独立 Flan 故事混写，已弃。
- [v1](../../paper-acl-v1/main.tex) “Which Head Takes Which Role?”：依赖头地址继承，provenance 被更强权重基线压缩。
- [v2](../../paper-acl-v2/main.tex) “When Do Mechanisms Correspond Across Pretraining Runs?”：本来想跨机制抽象，但 target-aided mapping 混成知识迁移。
- [v3](../../paper-acl-v3/main.tex) “Which Head Does the Work?”：加入训练谱系与因果 carrier，但指标定义不一致，E83 否定发育规律，最近邻意义不足。

**四版都保留作为错误/改善的研究过程材料，不要以 v3 存在推断项目已可投稿。**

## 4. 当前知识复用优先级

**值得继续解读**：E72（通用角色匹配 vs 任务因果匹配）、E75（目标辅助重定位的实证边界）、E81（同训练后代 vs 独立训练分支）、E46/E66（训练期形成约束）、E55未通过因果验证的具体模型。

**优先存入“避免重做”**：旧 Flan 格式效果、Gating generalization、seed provenance、只基于头编号/argmax 的发现、E83 早期锁定。

**需要独立核查才能提升可信度**：关键脚本与 raw arrays 的复现；同一个 head set 的真实联合干预；训练谱系；E87 缺失结果。
