# I05：history / partial observability 会怎样改变 action-aware planning objectives？（2026-10-02）

- **状态：** PARKED
- **来源：** SMWM/AC-MTM 的 inverse-dynamics assumptions、Causal-JEPA、JEPA-WMs context sweep、What Must… 的 sufficiency hierarchy共同指向 observability；但当前首轮 LeWM tasks 未必提供干净的 POMDP identification。
- **研究动作：** 改变 regime + 可识别性分析。
- **如果为真，潜在主张：** action-recoverability / reachability / geometry regularizers 的有效性依赖 observation history 是否足以 disambiguate latent state；在 aliasing 下同一“action-aware” objective 可能施加错误压力。
- **不同结果各带来什么 information gain：** 只有在 I01/I03 暴露 history-dependent failure 或找到可控 POMDP substrate 后再展开。
- **最近 3 个近邻与增量：** SMWM/AC-MTM（inverse action assumptions）、Causal-JEPA（structured partial observability）、JEPA-WMs（context length）。当前 exact delta 尚不够清楚。
- **最便宜的决定性 pilot：** 暂无；不为凑 idea 卡强跑。
- **预期论文形态：** 理论+受控实验。
- **排序打分（1–3）：** 证据 1 · 增量清楚度 1 · 形态匹配 2 · 成本 1 · 可完成性 1 · 不同结果的信息增益 2
- **PARKED / REFUTED 时：** **重开条件：** E03–E07 出现无法由 full-observation controls解释的 history effect，或找到一个能在现有 compact WM stack 上精确控制 aliasing 的环境。