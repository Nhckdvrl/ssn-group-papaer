# E31：谓词关联，还是新事件的一般参与者对比？（2026-10-05）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01/C04/P11；E29/E30 source-free具名患者预测随event身份翻转，exact separate词不足；native却沿用旧关系方向。
- **问题（一句话）：** 参与者反向预测是否需要新事件使用旧谓词，还是新事件本身就足够？
- **设置：** 同24source/12verb-family的E29 anchor-only新事件。新bridge两个条件均began a separate activity：同谓词或另一个上游已审谓词；新activity noun/主谓progressive/body/hyp同步匹配，旧source anchor/局部only事实/actor/患者targets原样。不同谓词固定按alphabetical12家族+5循环，跑前mapping/hash，不按可显著/顺耳选pair；同谓词began阳性匹配控制避免直接比较continued旧谓词 vs新谓词导致aspect/继续预设混杂。新raw1536、NLI384输入×base3mapping/repair-map0共1536native任务。两Luna各960逐条审新搭配、事件指称、selectional plausibility和三类关系。没有自行造新verb/释义。E29 continued与原activity raw冻结复用；E29 continued base/E30 separate-repair冻结复用。
- **读数：** D_activity/D_neutral=两role事实的患者M方向差，M=bits(other NP)−bits(own NP)，J=D_activity−D_neutral，named/generic、sameActor/otherActor分别报告。主different_began−same_began的D/J及各cell是否仍反向；same_began−continued_separate作为aspect sensitivity，不能只挑different vs旧control。NLI两新branch U accuracy/p_E/p_C/p_U、choice_mass/greedyvalid、signed-role carryover、different−same同aspect对比，三map平均主及全部mapping；repair only paired map0。12verb-family（2源先平均）paired bootstrap10000/seed20261005/95%CI。全部/eligible/prior-and-ablation-faithful、预设anchor第三审clear11/acceptable9层共同完整源。新选择合理性flag保留，不从概率倒填语义gold。
- **阳性对照：** 同谓词began应先核对反向预测是否仍在，old fact原event具名D正、known E/C与无关U原阳性读数保留；fresh native不同V仍不应该由old only决定患者。阳性不是停步gate，若同Vbegan变化须解释aspect再讨论differentV。
- **噪声地板 + MIE：** family n12/9，来源角色语义与anchor不自然标志原保留；新谓词成分可能有selectional odd、相关语义，teacher如实标，全部model评分。CI显示不确定不等于零，严禁以更好新verb子集改主结果。
- **混杂审计：** 不同verb也改变活动语义、适配度与source词重叠，不是纯lemma手术；其作用仅能限制exact predicate-memory vs一般跨活动对比，不能直接证明内部回路。循环是bijective，每new family恰好由一个old family对应，family重采样仍不覆盖所有verb交叉组合，不作全空间推广。began两条件相同，但与旧continued的次要比较有aspect变化。raw probability与native判读并不测同一潜状态，model只有固定8B，不宣称所有LLM。negative native use已有原一句恢复，现在同指令继续测两谓词模式，避免把default policy当无能力。
- **决策表（跑之前写）：** differentV的具名D/J反向消失而sameVbegan保留、neutral近0 → predicate-linked关联/抑制更强，generic new-event novelty不足；differentV仍反向且neutral近0 → exact relation/predicate echo不足，更一般叙事/角色对比竞争加强；NLI不同V恢复unknown而同V越界 → 模型对predicate identity比事件boundary更敏感，下一自然相同事件释义/不同事件同V的身份交叉才能支持lexical shortcut；两用途不同V均恢复 → 共享predicate依赖增强，不硬讲双机制；sameVbegan已不反向 → 优先aspect/预设why，不能把differentV故事卖novelty。结果只收敛同一个I01，是否paper-like要根据具体结构而非强写叙事。
- **算力预算：** 现成venv/pinned Qwen3-8B frozen FP32/SDPA/TF32false/seed0；GPU0 raw1536 batch4，GPU1 base1152 batch8，GPU2 repair384 batch8独立并行，预计总≤.12 GPU·h。**实际：** 外审中，未运行。
- **命令：** predicate_scope.py生成；source_ablation.py adopt独立标注；event_identity_infer.py --experiment E31；event_constraint_state.py --experiment E31 base/repair；analyze_event_boundary.py --experiment E31 --repair-new E31-repair --repair-separate E30-nli-separate-repair。所有raw/audit仍cache-only。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待外审。I01 PILOT/C04 L1，候选主旨来自E29/E30数据，而非提前选择结果。

**跑前独立外审与诊断补充：** 两审1920材料完整，NLI384全clear/undetermined，全部eligible/faithful。第二审发现12新搭配odd（8raw/4NLI，babies healing），第一审未标odd，分歧保留不覆盖；全部model评分，跑前增加selection-no-odd共同family敏感层，不因部分新V效果筛样本。neutral行选择关联未指定标uncertain是合理字段语义，不当成无效刺激。E30另外做POST-HOC native wording分层：named也同向迁移（sameActor separate63.40/second71.99pp），因此不是将raw named与native pooled混比制造相反方向；该分层全部结果/脚本保留，E31将named/generic native分层事前列为诊断读数。所有label maps依旧全报。
