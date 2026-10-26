# MoE：任务、学习历史与专家职责的可组合性

**状态（2026-10-26，用户决定）：** 方向已确认，文档与首轮实验设计已整理；模型执行仍为 PAUSED，本轮没有新模型运行。E120–E142 是已有实验，E143 保留备选，E144/E145 为首批核心设计，E146 为条件后续。头线继续 CLOSED。

## 1. 当前问题与阅读入口

> 给定真实语言模型接口及其要求的条件计算，任务约束了哪些专家职责和配合关系，学习历史选择了哪些实现；这些差异何时改变组件重新组合后的预测行为？

完整论证、数学边界、已有证据和一手文献定位统一维护在 **[RESEARCH_DIRECTION.md](RESEARCH_DIRECTION.md)**。先读该文，再读下面的实验卡；旧交接和暂停判断是历史材料，不再作为当前方向说明。

导师提出的“独立训练能否自发形成相同分工”仍是长期动机。当前用固定原生 OLMoE 输入表示、目标函数及下游的重复学习窗口，拆开总体计算、专家分解与训练历史。它不等同于多个完整模型独立预训练；价值要由责任差异的预测后果和可解释关系来建立，不能只凭匹配分数低或编号可置换。

## 2. 现有证据怎样支持这个问题

| 已有分支 | 尝试与现有认识 | 当前使用方式 |
|---|---|---|
| E120–E122：测量、原生路由与功能桥接 | 已知答案校准；原生路由有超出词身份的组织；路由/指纹相似不直接决定替换后果 | 保留工具审计与真实语言计算锚点 |
| E123–E131：dense 骨干插层、恢复、重复训练与历史 | 不同初始化的指定作用指纹对应弱；同父等曝光短暂次序处理留下终点差异；E130 order1 另有曝光混杂 | 保留限定事实，不直接解释为原生模型任务重要分工不重现 |
| E132–E134：整 bank 移植、输出对齐、c/r 必要性 | dense-CE 的 c-only ΔNLL 小，但 calibration r 平方能量仍约占输出能量的 41%–43%；原生 teacher 的 c/r 干预后果不同 | 小 NLL 变化不表示残差为空；接口来源、监督和读出敏感性需要区分 |
| E135–E138：原生函数重复实现、固定 gate | 原生接口内重新学习后，特异残差仍有预测作用；固定 gate 下组件差异部分抵消；共同 teacher 偏差仍大 | 作为真实接口下的受控窗口；不要求先完美恢复 teacher 才能提问 |
| E139–E142：自由 gate、教师暖启动、支持分账、共享随机起点 | 组件变异 R/S/T/F 约为 .07247/.04326/.03282/.03121，总输出变异约 .0156–.0179 | 追问共享历史稳定了什么，以及配套差异是否被下游预测读取 |

来源、单位和范围见 [方向文档](RESEARCH_DIRECTION.md) 与 [完整逐项索引](experiments/INDEX.md)。上述方差是三个模型的有限 cohort 统计；R/S 共享同一完整 seed1，输入 bootstrap 不是训练种子总体区间。

**2026-10-26 解释修订：** 旧页“冻结骨干不会长出分工”“蒸馏线偏离原问题”的表述过宽。E130 只支持其 dense 接口＋CE 设置的限定判断；E135/E136 已反驳一般性的冻结骨干不可能论。约 74.5% 是特定评测混合的干预损失比，不能称不变量或可加功能份额。共同偏差、逐点零空间、跨 seed 负协方差也没有单独证明长尾记忆、全局等函数流形或性能与模块化必然冲突。

## 3. 首轮初步实验

| 优先级 | 卡片 | 直接问题 | 当前状态 |
|---|---|---|---|
| 核心 1 | [E144：固定 gate 重组](experiments/E144-fixed-gate-recombination.md) | 保持共同 teacher gate，比较三学生整套来源与逐专家独立来源；层误差是否传到真实 KL/NLL？ | PLANNED；30 变体，复用终点，无训练 |
| 核心 2 | [E145：gate × bank 交叉](experiments/E145-history-gate-bank-cross.md) | 用 R/S 共同 seed1 作接收者，四 donor 的 gate/bank 四格，区分当前路由与专家兼容性 | PLANNED；13 变体，含 teacher 至多 14，无训练 |
| 条件后续 | [E146：分组重组](experiments/E146-grouped-recombination.md) | 保留组内共同来源是否比同大小随机组更能保持预测？ | PLANNED；8×8 粒度、4 分区、48 新 bank；依 E144 读数判断必要性 |
| 暂存备选 | [E143：跨公开模型路由分工](experiments/E143-cross-model-routing-division.md) | 不同完整模型的组织是否对应 | 原协议保留；不进入本批 |

三卡共用旧 Dolma held 中按 SHA 预定的 64 条完整序列（32768 位置），冻结成四个新 B16 batch；同子集重测原生基线、C/V 和数值地板。旧 held 已用于探索，不称新独立确认。E144 的来源 MC、E145 的两对 donor 和 E146 的四个来源基础向量各自保留正确统计单位。

当前只完成设计，新 GPU driver、selected/source maps 和 E144–E146 结果均未生成。直接测完整下游 KL/NLL 优先于完整 Fisher 计算；新训练、时间轨迹、接收者旋转和更多模型仅在具体未决问题需要时讨论。资源上限与实现正确性检查不代替科学效果判断。

## 4. 主张与痛点

- [CLAIMS](../CLAIMS.md)：C06=L1；C07=L2（原固定设置的重复测量）；C08=L1（单父历史 pilot）；C09=L1（有限 cohort 的协议差异）。本轮设计和摘要重算不升级任何等级。
- [PAIN_LOG](../PAIN_LOG.md)：P22/P26–P29 延续；P30 加有日期的范围修订；P31 记录实际组件抵消的预测后果与重组粒度仍不清楚。
- [2026-10-26 日志](../logs/2026-10-26.md)：保留旧暂停决定，追加用户确认方向、设计与上传记录；其他 workbench 的 ACTIVE 分配不变。

## 5. 可复核数字与历史材料

- **本轮 POST-HOC 摘要重算：** [脚本](scripts/recompute_discussion_20261026.py) 与 [JSON](results/discussion_2026-10-26/reanalysis.json)。只读五个已提交摘要，核验原 Git blob，重算初态 Q、终态 C−V、c/r 能量与干预比；没有模型调用。从仓库根运行：

  ```bash
  python3 workbench/mechanism-population-dynamics/moe/scripts/recompute_discussion_20261026.py --check
  ```

- [导师原话与最初调研](notes/ADVISOR_2026-10-23.md)；[10-23 讨论](notes/DISCUSSION_2026-10-23.md)。
- [旧交接](notes/HANDOFF_2026-10-25.md)、[E120–E142 阶段快照](notes/GPT_PHASE_SUMMARY_E120-E142.md)、[旧定位表](notes/POSITIONING_2026-10-26.md)、[可识别性范围笔记](notes/IDENTIFIABILITY_SCOPE_2026-10-26.md)均保留历史含义；当前方向以本页及主文档为准。
- 既有论文卡在 [knowledge/papers](../knowledge/papers/)，既有测量审计在 [notes/audits](notes/audits/)。

## 6. 代码与资产

历史代码在 [scripts](scripts/)，历史摘要在 [results](results/)；不修改旧脚本与实验结果以迎合新解释。已有 initial/final 权重和中间 loss 标量不等于中间参数轨迹。

原机器上的大权重、token 与数组依 [ASSETS.md](ASSETS.md) 和各 manifest 核验；当前文档环境不证明它们已挂载。首轮推理只依赖所需终点、原 token 与元数据，不因旧训练 preflight 而自动重建约 71.7GB H/Y cache。大文件不进入 Git。
