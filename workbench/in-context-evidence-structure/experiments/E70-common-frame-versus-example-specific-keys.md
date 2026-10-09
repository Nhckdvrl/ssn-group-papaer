# E70：历史访问必要，是样例地址改变，还是共同状态偏移？（2026-10-10）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C15/C16/P12/I04；E69 label-blind prefix K保留、isolated K受损。
- **问题：** label-free历史上下文化对prefix K的因果作用，是否主要来自所有demo共享的mean offset，而非各demo特定的地址变化？
- **为什么现在：** E68隔离history损害不能证明形成了task judgement；E69 blind key有效也不能自动证明特殊schema。混合cache可能引入公共context frame失配，必须与example-specific binding解释竞争。目标是校准“历史访问/上下文化干预说明了什么”的桥梁，非提出新修分方法。
- **设置：** frozen Qwen3-8B bf16/eager；32 fresh contexts seed70001 animals/fruits yes/no；if MIE≥threshold与controls有效，则64 fresh contexts seed170001 occupations/vehicles toxic/safe确认。沿E67同信息/最终标签的source-code prefix布局，D1Q1为原生recipient。
  - 以E69全4Dlabel-blind与demo-isolated masks生成donor；所有query看到的nativelabel缓存保持，V不变；只干预demo prefix K。blind非label对label-flip逐位相同、禁读质量0、full 4D=no-op。
  - 每层每head令Δ_i=K_blind,i−K_isolated,i，Δbar=16个demo均值。**common-only：** K_isolated,i+Δbar；**centered-only：** K_isolated,i+Δ_i−Δbar；**both：** K_blind,i。native K、isolated K作为两参照。
  - **标度/方向对照：** isolated K逐token缩放到blind K的norm；common negative（−Δbar）。源词/code/class均无分组估计，不用gold/query/seed挑选，mean只从未读label的cached states计算。
  - 写入bf16后的norm/分解误差记录；直接both donor KV K交换必须与标准blind K逐位一致、其output重复误差≤0.10nats。common/centered均计算float32再cast，不将舍入当机制；数学mean相对key RMS记录。
  - 观察native probabilities：query各位置对prefix组的total attention mass和组内requested-source比例；各层完整保存与全层汇总，只作诊断。由于每层所有demo prefix加入同一个key vector，**固定Q条件下组内相对QK logits不变**（cast的误差另核对）；可改变相对其它token组的mass及后续query状态，不能直接等同来源选择的充分解释。
  - headspace的mean是跨demo索引的rank1，不是全模型一维向量；逐层逐head的高容量状态，不宣称无代价的小开关。
  - 本卡加full four native D×Q用于编码边界；single/instruction与前卡同设置/新seed，默认反事实主要读数不改。
- **读数：** correct margin、accuracy、同input source排序；blind−isolated full效应，common/centered/norm/negative相对isolated的转移比例（full gap>0.2nats才比）、相对native差；prefix组mass/within-source比例。context bootstrap4000。
- **阳性对照：** labelblind非label flip差0、forbidden质量0、fullmask=no-op、both=blind缓存/outputs；source-code/token多重集与rule方向平衡；common固定Q相对logits数学invariance及bf16写回误差验证；所有层/head，不挑最有用部分。
- **噪声地板 + MIE：** no-op≤0.10nats；common或centered转移≥0.50full effect且CI不跨0.25，并恢复≥0.05source排序或accuracy且CI不跨0，才进入确认。两个都有效则有冗余/非线性，不能二选一强保；norm-only类似common效果→标度/激活失配解释；都无效而blind有效→耦合/非加性，不能硬称新地址机制。
- **混杂审计：** query/input/label缓存/V完全相同；mean label-blind、不用gold/query，all sample保留；common仅跨demo索引共享但可含context整体关系；多层干预能经反馈改变后续Q，fixed-Q invariance不代表完整程序不变。mean写回舍入与非自然hybrid cache，损害并不证明天然算法缺少frame；仅这个接口。
- **决策表（跑之前写）：**
  - common恢复、centered弱 → 当前历史necessity主要不需example-specific K变化；撤回从history干预推特殊地址形成的当前版本，追group visibility/状态兼容性。
  - centered恢复、common弱 → 个体K关系有因果线索；仍须把source/code结构与position、语义内容分开，不称binding ID已证实。
  - norm-only恢复 → norm/competition解释优先，不包装关系结构。
  - both有作用但拆开均失败 → state部件协作、单一分解不足；保留negative。
  - 部分mean效应只有margin、无accuracy/ranking → 不升级来源选择，只报告logit动态。
  - 控制失败 → VOID、修harness；不修改threshold。
- **算力预算：** pilot≤0.3GPU·时、确认≤0.5；实际待填。关键实验串行、单卡conda。

## 结果
待运行。

### 写回精度检查（编码前，2026-10-10）
捕获native每层/query/head的post-RoPE Q，计算common实际bf16写回后相对isolated的scaled QK-logit改变量在prefix组内的spread；最大≤0.02nats才支持近似fixed-Q分布不变解释。此阈值在任何E70读数前定义；失败保留VOID并用更高精度核对，不放宽阈值。

### 校对失败后的重跑协议（2026-10-10，重跑前）
bf16首轮32contexts完整完成，但common实际写回fixed-Q组内scaled logit spread max0.06986>预定0.02；输出no-op/max误差仅4.77e-7不足以挽救这个更严格的几何对照。VOID保留`qwen3_discovery_invalid_bf16_frame/control_failure.json`，未读取科学条件结果。改全float32同seed/n重跑、阈值不变；both直接写blind donor（理论上等于i+Δ）确保逐位相同，而非float32减加引入微小非零。有效范围将明确是float32，不能等同bf16默认程序。
