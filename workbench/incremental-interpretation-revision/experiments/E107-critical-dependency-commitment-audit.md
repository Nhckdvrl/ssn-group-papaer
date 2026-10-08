# E107：角色正确是明确修订了依赖，还是留下了未绑定内容？

- **状态：** RUNNING；自动E431在新HTTP/统计前更名E107。
- **对应：** I07/P20与I06谓词框架；E103完整Min效果后固定顺序读全部4个positive案例引发的POST-HOC指标质量追问，不覆盖旧T4。
- **问题：** suffix所选“correct roles”可能来自删除实体object而只说understood/noticed/discovered something；原T4不分明确clausal content argument与语篇隐式联系。区分旧误关系撤销、新依赖明确绑定、语境可恢复、未承诺；不能把语法object形式直接当语义错。
- **数据：** E103固定全50GP Source/三族/全部1200候选assignment和所有exact Source/P packet，只审新增生成文本所承诺的关键依赖，不改/重审现成Source/Gold，不挑收益Source。cap/unfinished全部保留UNKNOWN。
- **新读数而非替换标签：** EXPLICIT_FINAL（完整关键依赖有明确内容/角色或唯一this/that等referent）、IMPLICIT_FINAL（自然连贯语篇可支持该关系但无明确link）、GENERIC_UNBOUND（不明确指向Source所需内容，仅vague object/bare predicate/分离事实）、INITIAL_MISREADING（实际词义明确赋予Source须撤回的初始角色）、OTHER。若两解析并存，initial优先；不因NP object/active voice形式单独判initial错；inchoative patient改写可正确。允许自然ellipsis/anaphora，不强迫正式图/字面复制。
- **主读数：** WHOLE、原T2 suffix、GREEDY、UNIFORM、E106唯一positivegain的EXPLICIT/IMPLICIT/UNBOUND/INITIAL比例；严格explicit与宽松explicit+implicit两种支持范围、unknown/cap上下界、同池explicit/宽松oracle可获得率；各族全50/三ct，Source→原48clusters10000bootstrap seed107。严格与宽松之差是承诺方式差，不冒称全部implicit都错误。
- **标注：** 独立匿名Source/P新protocol新ID，不提供旧T4/分数/Model/Seed/政策/Gold。Step Plan step-5-preview only，high effort、批≤5、共享全局8槽，两打乱遍+分歧第三遍；新五类别以compat option_labels编码，grammar/T2等固定不是新Source标记。
- **阳性对照：** Source/P SHA对应全1200冻结生成/评分cfg，旧T4/map不覆盖。示例原则：repeated the proposition claim-is-false vs repeated the claim需分清内容；noticed something+report overdue不预定为错，允许implicit；明说noticed that report overdue是explicit。MVRR/NPZ按Source特定参与者依赖，不强把something在任何句子都判unbound。
- **噪声地板：** 语言允许语篇推理，这块不能用“没有字面that”断言没有理解；教师agreement/uncertain与所有类别全报。该审计来自看到完整单族效果，明确POST-HOC，不把新strict metric冒称原主指标。
- **决策表（跑之前写）：** suffix明确新绑定也提高→实质内容选择证据更强；仅implicit/unbound增加→把“faithful修复”收紧为撤回/少说，不能升级完整重新解释；original whole看似initial但实际仅implicit→原T4把语法frame当语义shortcut，另版传播定位后再解释；混合→如实保留，不调判据救正结果。
- **算力：** CPU/API only，0GPU/新P/模型下载；复用exact packets减少调用不删Source，完成后原GPU已可清理权重，不占09:00后卡。

2026-10-08T07:57:25.298407+08:00 全1200 assignment/243 distinct Source-P packet冻结，high-effort Step Plan新维度双遍共享8在途，0Source重审/0新P/0GPU。旧T4 ActorAgent/Patient规则不覆盖，仅新增content dependency明确程度，不以lack-that/NP-object形式判断错误，不强把自然implicit读法判坏。

2026-10-08 08:25 封版前补充**次要内容credit读数**，不改变上面all-Source主指标/判据/标签/selection policy：在全三族同Source池所有known stopped候选中，分别比较EXPLICIT_FINAL vs INITIAL_MISREADING、EXPLICIT+IMPLICIT vs INITIAL，以及EXPLICIT vs GENERIC_UNBOUND。全候选对等权、再按Source→原cluster汇总；显式和unbound的比较只测承诺度偏好，不把implicit当错误。报告每格有两类别的Source覆盖/NA/unknown、whole/before/suffix的平均差和正确rank率、whole负而suffix正的比例。conditional pair分析不冒称全Source平均能力。另在all50上报是否出现至少一对完整修订被prefix抵消，未有eligible pair的Source只对这个存在事件记0，不当0能力。先核whole=before+suffix且all8同target，原unknown/cap候选不补标签。代码`analyze_dependency_credit_pairs.py`只等原E107 complete-map标记后读全图，无新GPU/API/位置规则；结果若只遗漏/隐式间重排，收紧内容修订叙事，不继续奖励网格。
