# E70：历史访问必要，是样例地址改变，还是共同状态偏移？（2026-10-10）

- **状态：** DONE
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

### pilot有效后的可迁移性检验（2026-10-10，确认运行前）
float32 pilot common转移0.890[0.678,1.100]的blind−isolated效应，centered仅−0.073，norm−0.050；fixed-Q spread2.86e-6。先从**同发现32contexts**重新提取blind−isolated的逐层/head均值（只提states、不再打分），再对contexts取均值，冻结为一个所有recipient共享的frame。该frame不使用query、正确性、target confirmation数据或labels内容。确认新增`shared_frame`：isolated-prefix K＋冻结frame，与own-context common及centered/full/norm/negative同时对比。若own有效但shared失败→不支持通用公共frame；若shared也有效→指定prefix-key历史依赖不必携带recipient-specific信息。仍保留其它native缓存，不能推广整个ICL无需context。frame无训练，但多层/head高容量；不是全模型一维向量。至少≥0.50effect fraction且≥0.05source排序/accuracy并CI不跨0，才考虑可迁移公共偏移线索。

### 有效发现、冻结frame与独立确认（2026-10-10）
- float32发现32/确认64完成；fullmask/self/both-cache与blind输出误差0，blind非label对flip差0，禁读attention0；fixed-Q common组内logit spread最大发现2.86e-6、确认3.81e-6，小于预定0.02，common确实近似不直接改变组内相对匹配。bf16首轮VOID不参与科学分析；有效结论明确限float32。
- **发现：** blind−isolated margin0.333[0.264,0.410]；common转移0.890[0.678,1.100]，accuracy+0.078[0.008,0.148]、source排序+0.125[0.047,0.203]；centered fraction−0.073，norm−0.050，negative common损害，触发预定确认。
- **确认own common：** blind−isolated0.514[0.426,0.601]nats；common fraction0.622[0.428,0.808]，accuracy+0.047[0.016,0.082]、source排序+0.031[-0.031,0.102]，单独未达到预定5点行为MIE。centered fraction0.078[-0.041,0.179]，norm−0.094[-0.196,-0.001]，negative−0.660[-0.856,-0.499]；不能说所有历史效应只来自公共frame。
- **冻结shared frame（跑前追加）：** 从发现32仅提unlabeled states的均值，shape36×1×8×1×128，无query/gold/confirmation样本；对所有新context/demos用同一个偏移，且跨词库与标签词。文件sha256 `bcec93a6282d781665716699083885caad6c636414beb65ec5da7b19f8b0f3d9`。shared fraction0.527[0.274,0.760]、accuracy+0.059[0.023,0.094]符合预定条件。
- **恢复的边界：** isolated accuracy0.543，shared0.602，native0.605；Source排序isolated0.789，shared0.828，native0.938。shared−native排序−0.109[-0.164,-0.055]，绝非完整binding恢复；blind完整K排序0.938。common/centered可对accuracy与排序有不同作用。其它native状态/label KV依然提供task信息，不能称frame本身编码完整函数。
- **决策：** 公共、label-free的偏移能介导相当部分预测效应，example-specific K变化不是此接口全部损失的唯一原因；恢复原生Source排序仍需完整状态，拒绝“generic frame解释全部Source条件化”。固定Q下common偏移等价于prefix token组的logit prior，但完整程序会改变后续Q/其它组，不把数学invariance扩成全路径不变。
- 资产`results/e70/qwen3_{discovery,confirmation}/{run,analysis}.json`、`frozen_frame/frame_metadata.json`；frame.npy与逐条JSONL只在NFS，按`--extract-frame-only`重建。原始主版本在git8c24fbe8；frame扩展源码hash见metadata/run。
- 有效主运行268.66秒、无打分frame提取21.46秒，合计0.081GPU·时；bf16 VOID39.21秒单报。C19新增L1，不升L2/完整理论。
