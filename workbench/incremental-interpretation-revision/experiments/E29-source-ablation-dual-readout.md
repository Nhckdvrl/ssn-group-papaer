# E29：移除完整源句，区分source记忆与纠正句自身迁移（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01/C04/P11；E25 likelihood跨actor更强、E28正负分类迁移同actor更强，不能硬拼机制。
- **问题（一句话）：** 新活动中的关系痕迹和旧事实过推广，需要最初完整源句，还是仅明确局部only事实就足以产生？
- **设置：** 原24source/12verb-family，删除完整S1，替换actor took part in an act of V-ing（原actor/activity fields），only句/活动桥/续写目标及NLI proposition逐字不改。GP/cue消融后相同，去重一次，不把两份副本当配对效应。概率1152=原活动384+同actor新活动384+另一actor新活动384，各2role×2style×activity/neutral×own/otherNP；分类480=E28 GP原480消融后，5state×2role×2style。两独立Luna各816全量检查语法、锚、旧事实作用范围、患者角色与NLI三类语义；未审/uncertain不强标。原source gold不改。已完成E24/E25/E28冻结reuse，不重跑。
- **读数：** raw M=bits(other NP)−bits(own NP)；每三scope：K=(M_named−M_generic)_activity−(M_named−M_generic)_neutral，两个role方向分别报告；J=(M_initialOnly−M_referenceOnly)_activity−同neutral，两个style分别报告。比较anchor−GP、anchor−cue，不能将二者平均叫GP消除。NLI全部base三cyclic mapping，5state accuracy/p_correct/3class/mass；signed-role-carryover同E28定义，两新branch与其anchor−GP、anchor−cue，allmaps主且每map保留。没有新增prompt/repair/模型，E28现有repair结果保留，R8已有同source对照不重新挑指令。
- **阳性对照：** anchor原活动only的角色双向预测J、NLI old E/old C与无关U控制；失败则不能声称仅更新来源被消融。neutral读数控制实体可及性，但anchor同时删除源patient提及，控制不能保证完全消除其交互。
- **噪声地板 + MIE：** family数量12，不把1632派生行当独立样本；paired bootstrap10000/seed20261005/95%CI。main全量与eligible/prior-faithful∩ablation-faithful共同完整source/family层，全配置保留，不筛种子/赢家。无自动阈值或停线gate。
- **混杂审计：** 这不是只去逗号或只去旧parse：同时移除源patient提及、matrix proposition、词数和话语结构。只检验full-S1 necessity/old-role correction sufficiency，不能从消融差归因单一机制。明确episode anchor避免悬空that；其角色未知，外审不能把源S1原关系补回。classification末尾可重分析，不证明预问内部状态；base映射大漂移必须全报。raw J/K与分类carryover单位不同，不强行数值相关/同机制。anchor输出patient可新引入，不假设所有候选已被提及。
- **决策表（跑之前写）：** 新活动NLI正负carryover仅anchor也在而原controls好 → GP/source不是必要条件，重心解释一般局部纠正的默认迁移，与GP历史specific likelihood分开；likelihood K/J anchor足以重现cue而GP仍不同 → source history调节但不能卖源句完全必要；两读数都在anchor显著减弱 → full-S1或实体/话语输入成分必要，后续要分离这些成分；两个用途消融响应不同 → 以对象/依赖差异提出更具体预测，不用generic QA/prob gap当novelty；若anchor或control不清楚 → 先why，不增加sweep。优先回答一个因果来源问题，再判断是否值得论文候选。
- **算力预算：** 现成venv/pinned Qwen3-8B frozen FP32/SDPA/TF32false/seed0；GPU0 raw1152 batch4（与冻结E24/E25原配置一致），GPU1 native1440 batch8，独立两卡预计总≤.15 GPU·h。**实际：** raw46.774s + native120.893s，总0.04657427 GPU·h。
- **命令：** source_ablation.py build/adopt；event_identity_infer.py --experiment E29 --data probability-audited-v2.jsonl --batch-size 4；event_constraint_state.py run --experiment E29 --mode base --data nli-audited-v2.jsonl；事前analyze_source_ablation.py输出配对统计。所有raw及标注在cache，git只code/hash/stat。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

全1152 raw +1440 native完成，12family及预设9/10/11-family敏感层保留。native1440/1440greedy合法，min label mass .805919，未隐去off-label质量。所有模型/环境/每用途batch一致核验；label token集合一致（B数组顺序不同，集合相同，修正分析比较方式，不重新评分）。

**源句不是三类判断中scope迁移的必要条件。** 仅活动锚+局部only事实：old E100%、old C80.21 [74.31,86.46]%、无关U100%；同actor新活动U31.60 [22.57,40.63]%、另一actor66.32 [59.03,73.61]%。同actor正负carryover61.25 [52.07,70.07]pp，换actor10.97 [4.81,18.79]；anchor−GP同actor+2.65 [−3.78,8.17]、换actor−1.37 [−5.35,3.09]。不是证明精确等价，而是强效应在无S1仍存在。strict9/第三审可接受9均保留同形。

**两个用途没有同一方向迁移。** 注册J（role事实方向对activity相对neutral的影响）具名条件anchor旧event+2.88 [1.81,3.83]bits，同actor新event−1.59 [−2.45,−.71]、另一actor−3.06 [−4.12,−2.04]；strict9 +3.36/−1.94/−3.34，第三审自然9 +2.60/−1.78/−3.04。GP/cue具名新event也多为负，native却在新event按旧role方向偏E/C；不能讲统一旧绑定机制。

**POST-HOC追why，保留主指标：** 负J可能只是neutral提高，故完整拆分所有role/style/origin/cohort。具名anchor实际activity的old患者方向效应旧event+2.646 [1.584,3.650]、新同actor−1.864 [−2.858,−.917]、新另一actor−2.898 [−4.037,−1.801]bits；neutral分别−.238 [−.743,.247]、−.278 [−.734,.117]、+.161 [−.289,.569]，不只由neutral增加制造。generic不同：删除源NP提及后ordinary salience主导（未修饰activity方向仍正），不得把具名结果扩成所有fact风格。

这使“不同事件的关系预测可能含对比/避免重复，而逻辑类判断泛化人物关系”成为更具体竞争解释。现在不是发现新机制或一般能力；边界桥separate本身可能诱导对比，下一E30仅separate→second仍保持两事件不同，独立审核后区分词触发的contrast与事件边界使用。不扩模型/问答措辞。I01 PILOT、C04 L1。

[主统计](../results/E29-summary.json)、[POST-HOC完整拆分](../results/E29-posthoc-role-decomposition.json)、[raw config](../results/E29-probability-config.json)、[native config](../results/E29-nli-config.json)、[第三锚审计](../results/D0-E29-anchor-cross-audit.json)。


## 推理前材料校对（2026-10-05）

v1有14种anchor错误使用an+辅音（952全量行）；独立review发现并修为a/an后全部重审为v2，v1未推理/不覆盖。另review1初版将192新活动患者误套旧活动模板，理由还虚构same/actor词；保留初版，要求完整重审，v2末句关系全覆盖且与预设分支机械对齐（192旧/384新/576neutral）。外审自身也须校对，不把teacher视为真理。

v2 probability1152 eligible/faithful、1056acceptable/96marginal；NLI480 clear/faithful、440acceptable/40marginal。bath/shaving锚搭配边缘与另一外审无此flag的分歧保留，全部评分；**跑前补充sensitivity** anchor-acceptable-common层排除任一anchor不acceptable的source-family，同时原GP/cue输入仍可marginal，不用此层选择主结果。两审完整hash和材料hash见D0-E29-probability/nli-audit.json。24source锚额外独立校对待回收，若发现语义问题先处理而非直接推理。

**推理前配置核对：** E24/E25原raw batch4、E28 native batch8；E29分别沿用4/8，分析在各自用途内比较batch，不要求两个用途同batch。此修订在模型推理前登记。

**第三独立锚校对已收齐（仍为跑前）：** 24source/96关系与逐条审核一致；18anchor acceptable/6marginal（cuddle/bath/shaving），22语义清楚/2shaving源不够清楚。原row标注不覆盖、不丢model行；加入第三审anchor-cross-acceptable-common及anchor-cross-clear-common敏感层。新audited-v2只是附加这些预先外审flags，文本和gold未改变；三层结果全报。
