# E32：反向患者预测跟随角色事实，还是跟随否定对象的位置？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C05 / I01 / P11；不改研究对象、不做模型或prompt sweep。
- **问题（一句话）：** 在旧角色真值和词袋完全相同的情况下，把允许对象放在动词旁、被排除对象放在句末，E31的同/不同谓词方向结构是否保留？
- **设置：** 固定24原source/12verb-family，只测具名role事实。`V not X but only Y` → `V only Y but not X`，原source anchor、role NP、bridge、target和后文不变；保留only和but且词袋相同。复用E29具名原event192与E31具名两predicate×两actor768，共960原输入的冻结分数；960新输入包括old event与new same/different began ×same/other actor，每branch两role事实×activity/neutral×两个相同目标NP。无新增患者gold、无问答；不把新event患者偏好当事实错误。两Luna各480对完整rendered文本和旧版逐条独立审事实、role scope、目标角色、grammar，先审后跑。
- **读数：** M=bits(other author NP)−bits(own author NP)；D=M_initial_patient_only−M_reference_only；J=D_activity−D_neutral。主要两个新event actor层分别报告同/不同V的D/J、within-new-order differentV−sameV，以及new−old order的predicate差之差。配套各cell/order change、old-event D/J、neutral、actor contrast，全部明确事前读数。12family先各2source平均、paired bootstrap10000、seed20261005、95%CI。原有all/eligible、anchor-clear11/acceptable9、prior-and-ablation-faithful9层加新order independently-faithful完整共同family；不依据分数选句。
- **阳性对照：** 旧event具名角色事实应仍正向影响activity；若该用途已变化，先追truth/scope/focus或格式，不从newevent消失推出词序解释。原E31同V/D及不同V/D冻结完整复用，所有上下文的两个target pre-token identity及HF/manual loss核验。
- **噪声地板 + MIE：** 旧FP32 indexing误差约1e−6，主要不确定性为12family与旧锚语法边缘项；报告各family和CI，不添加通过门槛。完整所有数据都评分，清晰层样本少也如实报告。不能用order差CI跨0证明等价或稳定性。
- **混杂审计：** 虽词袋/旧角色真值不变，线性位置、but对比方向和焦点组织一同变化，不是纯position因果手术。strictly same event旧only scope须独立审核，目标NP及另一作者NP与旧事实对象保持原状。反向跨order可限制“被排除对象必须紧邻V”解释，不排除两种顺序都激活focus alternatives。新旧predicate不同仍有活动意义差；新readout活动名词不构造。raw likelihood只测预测，不证明内部belief或能力。
- **决策表（跑之前写）：** 新order旧event仍正、同V新event仍负而不同V较正且J差保留 → 单纯negated-NP近V位置不足，下一same-action释义更有信息；新order旧event有效、同V反向消失/翻正并且predicate差改变 → 词序/焦点构成候选的核心条件，先拆scope/focus而不硬讲semantic relational memory；全部包括old event都改向/变弱 → 追role语义或不同focus，不叫恢复或普通echo胜出；结果CI宽/clear层少 → 承认有限、不换模板挑winner。保留C05的历史协议事实，只调整account/适用条件。
- **算力预算：** 现成venv，本地pinned Qwen3-8B FP32/SDPA/TF32=false/seed0/batch4，960新输入独立单H20，预计≤.04 GPU·h；旧分数只复用不重跑。**实际：** .01101391 GPU·h / 39.650s，960输入全部评分。
- **命令：** `scripts/role_fact_transfer_order.py build/adopt/analyze`；冻结推理`event_identity_infer.py --experiment E32`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

## 跑前审计与输入核对

960独立逐条audit，ID/hash全覆盖；grammar acceptable600/marginal360（首审360/120、次审240/240，次审另将embrace/hug/kiss锚搭配标边缘，分歧保留），所有facts/scope/target角色clear。parent flags全部保留；新order字段独立。词袋相同、因果目标token一致、24source各40variant核验。旧锚的bath/shaving/cuddle边缘意见如实保留；尚无新order模型分数。

跑前计数勘误：上次卡文字误将首审比例套到全量；实际采用adopt报告600/360，立即纠正，所有audit/input/hash不变，未开始模型推理。


## 实测结果

- 新order旧event D_activity +1.072 [.132,2.018]bits，D_neutral −2.291 [−2.717,−1.909]、J+3.363 [2.383,4.452]。允许对象不是紧邻动词就能保证新event也更被预测。
- 同V新event D_activity：sameActor −3.213 [−4.596,−1.810]、otherActor −4.483 [−5.769,−3.195]。反向保留且更强，单纯“被排除对象必须在动词附近”解释不足。
- 但是neutral自身也强反向（sameActor −2.364、otherActor −1.176），matched-neutral后的sameActor J−.849 [−2.161,.443]不确定，otherActor −3.307 [−4.769,−1.875]；不能把绝对反向全部归关系特异记忆。
- 不同V D_activity：sameActor −.978 [−2.167,.249]、otherActor −2.183 [−2.958,−1.348]，故E31“不同V变正”不是跨事实词序不变量。不同V−同V的J仍正：sameActor +1.937 [1.043,2.841]、otherActor +2.359 [1.444,3.359]，strict9为+2.245 [1.129,3.307]/+2.620 [1.407,3.877]。
- predicate J差的order change分别−.567 [−1.232,.010]/−.533 [−1.509,.399]；CI跨0不证明两order相同。actor对比及所有branch/neutral/family保留，无prompt/model sweep。
- 按跑前决策：近V位置不足，但focus/order明显改变实体可及性与绝对方向；候选应围绕事件/谓词条件的相对预测结构，不能硬讲“换词完全修复”。C05历史protocol measurement保留L1，限定泛化；I01仍PILOT。
- [统计](../results/E32-summary.json)、[每family](../results/E32-per-family.csv)、[配置](../results/E32-probability-config.json)、[audit](../results/D0-E32-order-audit.json)。实际运行git `187a5d94a0669db3c552ae0b637094835f1c6a16`。
- 分析实现校对：首次汇总named-only会把旧all-style-defined prior-faithful9扩大为12，未用该扩大层更新主张；修为固定E31跑前共同cohort后重新汇总。all12及主contrast不变，strict9按原固定family，完整summary含parent-cohort hash，不改读数/筛family。
