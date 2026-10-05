# E34：被撤回的角色解释，还是仅被提到的关系？（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；用户明确要求持续验证直到找到合适idea，不停在候选汇报，不进入论文组织。
- **问题（一句话）：** 最终角色事实和历史关系词句相同时，初始描述是否曾被当作事实，会不会改变被撤回关系对新事件的影响？
- **设置：** 同24published source/12family、named role facts。初始描述内容交叉NP-only/ref-only；来源交叉presented as factual account vs hypothetical example；共同superseded transition之后给完全相同的verified final named事实（NP-only/ref-only）。初始/最终role两个因素完全交叉，各角色句都同时提到源NP/reference，使对象词频/词袋在相反role间匹配。late report只约束同一旧活动；新用途固定began a separate same activity、otherActor，配套old activity与noticed neutral。新post-update raw1536、pre-update384（只在两来源×两prior role下、无final事实，核对原描述是否影响预测），NLI post768：old-source E/C、old-reference C/E、new-other U、unrelated U。NLI base3cyclic mappings2304+一句既有scope恢复map0 768，raw与native分卡。没有SAE/probe/训练、模型/seed/prompt sweep。全材料先两Luna独立逐条预审，原/衍生全文留cache。
- **读数：** raw M=bits(other NP)−bits(source NP)。每source固定status/final/branch/frame测 prior effect H=M_priorNP−M_priorRef；固定status/prior测 final effect D=M_finalNP−M_finalRef，分别全条件与另一role因子的平衡平均。J为activity−neutral。主对比是最终ref-only（源NP被排除）时new-other的 H_J_factual−H_J_hypothetical；另报final NP-only、平均、prior×final交互、old/new transfer、pre-update H/J、new final D/J及全部M/cell。NLI报告old final correctness/probability、与prior一致的分类方向、new U及signed initial/final carryover、choice mass/greedy valid，三map均报；一句恢复只与base map0配对。12family各2source先平均，paired bootstrap10000/seed20261005/95%CI；all、审计eligible/faithful整套共同family、原anchor-clear11/acceptable9与parent-faithful9层预先冻结。不根据分数删源/换status句/改primary。
- **阳性对照：** pre-update role对old活动预测应可读，报告两status的效应，不预设hypothetical必为0；post old final role D与旧event NLI E/C检验final事实用途，无关U检验unknown label可用。若old final出问题，追why，不以new效应当成功纠正；若来源操纵没有区分，不从null证明没有记忆。两个目标pre-token identity与HF/manual target-loss核验。原E29/E31 source-free固定分数供无history参照，不将差异自动归因provenance。
- **噪声地板 + MIE：** 固定FP32误差远低于统计CI，来源/替换语义与n12才是重点；pre-update两个不同status不保证initial belief已经形成。CI/逐family说明不确定，不设停步阈值，不以几千derived rows当独立n。teacher独立标旧描述证据状态、替换优先级、最终事实scope及gold，不由执行者自行检查语义。
- **混杂审计：** factual/hypothetical标签本身可改变注意/语用，来源依赖不是latent belief证明；superseded与verified是明确的优先级线索，不能宣称所有自然纠正。初始引用内容不直接标物理世界真值，只有after supersession最终verified事实建立post gold。consistent也被同句supersede，转接词完全相同；与prior conflict条件不能不同说“错误”。只测同V/换actor最强结构，未扩semantic/verb grid，目标source NP vs另作者NP非完整患者分布。native提问可引起重分析，与question-free预测不强合隐状态。R8仍保留一句instruction控制。
- **决策表（跑之前写）：** old final可访问、new prior作用随factual/hypo与冲突变化 → 来源/撤回history对未来关系使用有信息，下一区分撤回具体事件 vs新事件替换及自然功能后果；history两status近同但初始内容仍影响 → ordinary relation priming/contrast更充分，收窄revision叙事并依结果追context作用，不强命名新机制；new主要由final事实而非prior/source决定 → 当前C05是最后fact的aftereffect，不能叫撤回旧解释残留，下一选备选生成/事件对比的具体预测；old final错误与prior同时迁移 → 更新失败竞争增强，先校对NLI/一句恢复与报告来源，不能叫成功修订后的双系统；pre role无效/审核不清 → 优先来源/材料why，不盲目扩大sweep。以上均继续同I01探索，不自动关线或进论文。
- **算力预算：** 已有venv/pinned Qwen3-8B FP32/SDPA/TF32=false/seed0，raw batch4/native8；GPU0/1/2独立，预计≤.18 GPU·h。**实际：** 待填。
- **命令：** `scripts/retracted_role_history.py build/adopt/analyze`；`event_identity_infer.py --experiment E34`，`event_constraint_state.py run --experiment E34 --mode base/repair`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
