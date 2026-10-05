# E30：新事件的患者反向预测来自边界身份，还是separate的对比意味？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01/C04/P11；E29 source-free具名role activity方向旧+2.65、新same−1.86/other−2.90bits，neutral近0；native却正向旧role carryover。
- **问题（一句话）：** 保持“另一事件”不变，去掉separate的显式对比词，患者反向预测还会出现吗？
- **设置：** E29 anchor-only新事件分支，在唯一bridge将continued a separate→continued a second，仅一个word变化；仍有旧活动+明确第二活动，actor、only事实、后续In that new…/noticed、own/other targets、native proposition全部不改。768raw/192新NLI输入、2独立Luna各480实际逐条检查，previous_text用于确认only lexical intervention；second指另一次事件而非同一次第二阶段需独立审。原E29 separate768raw/576base新event任务冻结复用；原活动384raw与E/C/无关U controls冻结复用。新native second base三映射576、second与separate repair各192（已有E28一句scope指令，不引入新prompt），共960native新任务；R8以各marker map0 paired分析。
- **读数：** raw D=M_initialOnly−M_referenceOnly，M=bits(other NP)−bits(own NP)，具名和泛指各自activity/neutral；J=D_activity−D_neutral，主named D_activity/J在second仍否及second−separate，actor两项、所有style同报。原event D/J在相同共同source层辅助，避免忽略baseline。NLI两new kind正确U、p_E/p_C/p_U、choice mass/greedyvalid、signed old-role carryover，base三cyclic平均主/每mapping分项；second−separate与repair−base-map0各marker，12verb-family先两source平均再paired bootstrap10000/seed20261005/95%CI。all/eligible/prior-and-ablation-faithful以及第三anchor-clear/acceptable共同完整层，全变体评分，不挑种子/配置。
- **阳性对照：** E29同材料原event具名D/J正、NLI old E类100%、old C80.21%、unrelatedU100%，不是完美gate；保留全mapping/old controls。新second不应改变only事实的旧活动指向，外审关系与旧事件身份若变则主对比只能在clear层解读。
- **噪声地板 + MIE：** family n12，原phrase anchors bath/shaving/cuddle marginal flags原样保留；新second的独立语法/episode指称不确定可新增flag但不覆盖旧审。数值FP32小漂移比family CI小，不自动判零/等价或只用“显著”。
- **混杂审计：** second也可能诱导新颖性/对比，不是pure absent-contrast条件，所以保留反向effect只排除单一separate lexical trigger，不能证明event graph。second是有序序列词，separate是distinctness词，固定事件数量/clear scope不保证所有pragmatics一致。raw两个role事实顺序与句法不同但在marker干预中不变；generic entity提及差异原样报告。native分类可能逻辑任务偏向，不能由与likelihood相反方向宣称两隐状态；需要边界干预的预测结构。无新模型/训练/SAE/probe。
- **决策表（跑之前写）：** second下具名反向患者预测消失而原facts/范围外审仍清楚 → separate-specific对比/词触发增强；second仍反向且neutral近0 → exact separate触发不足，事件区分/关系抑制仍竞争，下一需predicate-match或自然用途；classification carryover减弱而prediction不变 → 边界可访问性与预测策略不同，不能用泛泛gap充novelty；repair恢复分类而prediction仍反向 → default scope policy可恢复，不叫能力欠缺；两用途同变 → 共同边界cue解释增强而非强造双机制。先看具体为何，下一只做能改变至少两解释预测的动作。
- **算力预算：** 现成venv/pinned frozen Qwen3-8B FP32/SDPA/TF32false/seed0，GPU0 raw768 batch4、GPU1 base576 batch8、GPU2两个repair各192顺序batch8，总预计≤.08 GPU·h。**实际：** 768raw/960native全部完成，总.03805593 GPU·h。
- **命令：** event_boundary.py生成；source_ablation.py adopt应用独立审（不重置prior anchor flags）；event_identity_infer.py --experiment E30；event_constraint_state.py run --experiment E30 --mode base/repair；analyze_event_boundary.py事前冻结。原raw/QA/audit text仍cache-only。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

所有新材料通过单词改动/跨hash校验，192语义均U，全部评分，预设12/11/9/9家族敏感层全报。

**反向患者预测不需要separate字面词。** second的具名activity角色方向D，同actor−1.641 [−2.635,−.805]bits、另一actor−2.109 [−2.905,−1.278]；neutral−.039 [−.422,.321]、+.171 [−.287,.550]。扣neutral的J−1.603 [−2.395,−.865]、−2.280 [−3.106,−1.480]。原event D+2.646 [1.584,3.650]，第三审自然9的second D−1.999/−2.116，prior-faithful9−2.061/−2.198。generic分项也全部保存，不能把具名D符号扩给所有表述。

second−separate同actorJ−.016 [−.687,.620]，换actor+.780 [.170,1.312]（自然9+.605 [−.156,1.293]，仍不确定）。词确有幅度贡献，但不是全部反向效应；不宣称separate/second等价，也不能把second当无任何contrast的语用中性词。

**native仍按旧role方向泛化，R8不稳定修复。** base三map mean second新sameActor U31.25 [21.87,41.32]% /otherActor63.89 [52.78,74.31]%，signed carryover68.00 [58.50,76.65]pp/24.52 [14.36,35.41]，separate61.25/10.97。repair-map0 sameActor25.0%/otherActor65.63%，必须与各自base-map0配对，不与三mapmean比；所有mapping及paired变化都在统计。不能升级一般无scope能力或隐双机制。

**解释与下一动作：** 能区分更具体的两个account：旧关系的predicate-linked抑制/复用，或新事件的一般discourse参与者对比。E31在began新活动的同aspect对照里替换为另一个已审上游谓词（不乱生成同义词），旧fact/actor/target不动；若跨谓词仍反向，则exact relation/predicate memory不足；若消失而neutral不变，则一般新事件对比不足。仍只推进I01、同一territory，不新开线。

[完整统计](../results/E30-summary.json)、[raw config](../results/E30-probability-config.json)、[native base](../results/E30-nli-base-config.json)、[second repair](../results/E30-nli-second-repair-config.json)、[separate repair](../results/E30-nli-separate-repair-config.json)。E29 POST-HOC拆分不追注册为旧假设；E30是事前预测检验，C04 L1/I01 PILOT。

**跑前外审完成：** 960改动逐条确认仅separate→second；概率768全部eligible/faithful（608acceptable/160marginal），192NLI全部clear/undetermined/faithful（152acceptable/40marginal）。独立审核仍标原有anchor搭配边缘，不因新marker筛掉难例；预设anchor第三审清楚/自然层原样保留。模型评分全部，所有raw及audit hash见D0-E30-probability/nli-audit.json。
