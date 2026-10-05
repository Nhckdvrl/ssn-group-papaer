# E39：两个具名患者，移除self/reciprocal结构混杂（2026-10-06）

- **状态：** COMPLETED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；role evidence还是reflexive/non-reflexive construction及一般action association。
- **问题（一句话）：** 当两个role世界都为非自向的具名患者、词袋对称时，旧/新event的预测方向翻转还存在吗？
- **设置：** 用同24source/12family、sourceNP=A/donorNP=B的真实原NP（E38已提取），Luna独立构造旧activity only A vs only B、三个fact实现（not-contrast/affirm mention-first/last），每world A/B各一次、同实现两world同token multiset。identity_intro明确两个不同entities，允许puppy不误说人，不添实际活动参与。原E29 old与E31同/不同predicate×两actor后文/target完全原字节，raw2880；old-role direct query144contexts×base/一句scope recovery=288 responses作阳性控制。全部全文独立审计。原reflexive两world parent分数冻结作定位，不能称纯single-token消融。
- **读数：** M=bits(B)−bits(A)，D=old onlyA−onlyB，J=D_activity−D_neutral。主读数非自向contrast实现otherActor/sameV J，另报三个form old/sameV/differentV×same/otherActor全部cell，different−same J及与original-reflexive实现差。句式/identity intro和B mentions改变，跨old/new within-E39结构比差值更有信息。native oldA/B direct retrieval、R8 paired；n12family先两source平均bootstrap10000/seed20261005/95CI，all/eligible/grammar共同、E31 frozen clear11/acceptable9/parent9，不按scores筛源。
- **阳性对照：** old D/J正向、direct role retrieval A/B两方向皆能回答；causal-token target pairs/词袋/hash及suffix原样复核。已知parent旧positive/新反向，原neutral一并保留。
- **噪声地板 + MIE：** 固定FP32/seed0，n12及语境构造局限重于数值误差；CIs不作为停步/科学门槛，uncertain分项同报。
- **混杂审计：** B现在在旧fact中出现并可能为patient，改变event情境，不是纯reflexive字面移除；两个具名对象才允许更直接区分relational exclusion与self/other construction。explicit distinct intro解决源noun可共指，不当作自然发布故事原句；动作availability/结果状态仍竞争，不用坚持反向就声称semantic memory机制。only/focus仍在，三个form完整报告。native不再给new who能力标签（E37自然默认风险），只检查明确old query事实可访问。
- **决策表（跑之前写）：** old控制有效、三form新sameV反向及predicate差保持 → 当前role-transfer不限self/reciprocal construction，进一步追availability/状态后果与role-level contrast的具体区分。仅contrast反向 → focus/discourse realization核心边界；只原REF有效 → 警惕construction priming或self vsobject改变驱动，收窄C05，不包装一般role-memory。old失效/alias不清 → 先why材料，保留独立audit切片，不换模型扫参。所有分支同I01继续，不切新workbench/论文阶段。
- **算力预算：** rawGPU3/nativeGPU6独立，已有venv/frozen Qwen3-8B FP32 batch4/8 seed0，≤.10GPU·h；**实际：** 0.054098 GPU·h。
- **命令：** `named_patient_roles.py build/adopt` + `event_identity_infer.py --experiment E39` + frozen direct role generation，R8只用一条scope句。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

[完整统计](../results/E39-summary.json)，[独立材料审计](../results/D0-E39-named-role-audit.json)：2880 raw与144question contexts全文独立审核、288mode任务gold一致，所有entity distinct/scope clear；语法2268 acceptable/756 marginal（3024packets）。实际run 47fc1fc6。

主contrast非自向otherActor/sameV J−6.127 [−8.048,−4.302]bits，old J+8.599 [6.886,10.315]；affirmative-first/last otherActor同V J−7.568 [−9.126,−5.977]/−6.251 [−7.749,−4.649]，三个表述均反向。different−same J otherActor分别+4.662/+4.277/+4.152，各paired CI正；但differentV otherActor绝对J仍负，不泛化“换谓词变正”。contrast sameActor/sameV J+.231 [−1.003,1.540]，sameActor全部order并不普遍反向。所有all/grammar9/原parent切片全报。

独立逐条输出盲审288/288correct，source/other各144、clear288；base与一句scope两mode均100%，family finite CI[100,100]不等于普遍能力已证。reflexive/non-reflexive不是反向结构必要条件，不能用构造数据叫自然语言普遍机制；only/focus仍竞争。C05 L1保留、I01 PILOT；下一E40去only普通肯定角色事实，区分排他焦点与一般role关系，不扩模型。
