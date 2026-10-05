# E35：当前事实优先级的一句恢复（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；追E34的冲突历史旧event问答失败why，不扩大prompt sweep。
- **问题（一句话）：** E34旧角色判读错误是无法访问final事实，还是将被引用/撤回的初始描述也当作当前世界事实的任务解读？
- **设置：** 原E34独立审计nli-audited-v3.jsonl768句/24source/12family完全原字节和gold，不重新构造。仅BASE定义增加一句 `Use only the final verified account to decide what actually happened; the superseded initial description is not an additional fact about that event.` 三cyclic mapping全部paired E34 base；2304tasks。原R8 generic event-scope repair没有说初始引用优先级，不足以区分这个why。复用frozen Qwen3-8B FP32 batch8 seed0/SDPA，不改任何旧score。
- **读数：** 先两source/family平均，paired bootstrap10000/seed20261005/95CI；all及E34冻结敏感cohorts。correct/p_correct/p_relation/choice_mass/greedy_valid，分别factual/hypothetical×consistent/conflicting×旧source/旧reference/newother/unrelated×全map及每map；恢复−base配对。另按fixed final role拆old-source E/C，检查平均50是否单极性拒绝。主读数factual conflicting旧source correct恢复−base全map；必须同时报告hypothetical及每map。新event U和无关U不混成旧事实能力。
- **阳性对照：** consistent旧source和旧reference、unrelated U；未加instruction的旧分数是冻结paired baseline。高choice_mass仅证明类别输出有效，不证明语义能力。
- **噪声地板 + MIE：** 固定FP32数值小于family CI；n12和mapping不是独立n。恢复幅度支持任务解释竞争，不设达到多少便宣布通过的gate；若mapping间不同完整报告。
- **混杂审计：** R8明确提示final优先级可能诱发新重分析，恢复不等于未提问时已正确表示。数据/模板/gold复用已审材料；只system instruction改变，不需要伪造新增标签。原BASE contradiction定义可能使模型将quoted superseded句也解释为当前事实；恢复是否有效是当前待测解释。
- **决策表（跑之前写）：** 多map旧冲突大幅恢复、consistent/U不降 → 不能把E34原问答54%归为不可更新，收窄为未指定current-world任务解读；仍不能证明raw隐状态已改。无恢复/单map → 优先拆final E/C和history读法，不宣布修订成功。恢复后new U仍正确 → 后续预测反向不是必然的错误事实外推；继续role实现方式的核心科学区分。所有分支继续I01，不改线状态/不进入论文。
- **算力预算：** 单GPU0独立已有venv，≤.10 GPU·h；**实际：** 待填。
- **命令：** `event_constraint_state.py run --experiment E35 --mode current_world --data CACHE/E34-material-preparation-v1/nli-audited-v3.jsonl --out CACHE/runs/E35-current-world`；`analyze_current_world.py`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
