# E32：区分语义选择性与整体角色控制减弱（2026-10-14）

- **状态：** DONE
- **类型：** PILOT / 已有检查点的CPU因果诊断；不训练、不生成新游戏世界。
- **对应：** I02 / P06；E25、E26。
- **问题（一句话）：** E26正确编码短pilot中Full的改写损失较小，是保留了更有意义的角色控制，还是对所有角色输入都更不敏感？
- **来源：** 2026-10-14对E26已有结果的POST-HOC交互核验：reverse相对canonical的Full−No变化+2.8976，persona簇95%[.4871,5.3894]；canonical-repeat+.1386[−.0330,.3427]。这是单训练seed事后线索，不是独立确认，四种变体均归档，不能只挑这个正结果。
- **竞争解释：** H1共享投影学习了语义选择性（等义改写稳定，但真实不同角色仍可区分）；H2Full整体弱化角色输入/动作响应，因此改写也不敏感；H3原收益差主要来自不同世界访问或伙伴变化，静态policy响应不呈H1模式。
- **设置：** E25正确编码Full/NoCons、同初始化seed42/30iter原检查点，η-only policy已与NoCons逐byte同一，不浪费重复。固定E25 no_mixed原100角色×3世界seed的观测，预定cycle[0,20,100,199]共1200focal states，两policy看到相同obs。输入为E26 canonical/canonical_repeat/reverse_clauses；对照为原held100中同occupation、不同BigFive的全部4个角色编码，不按输出选donor。只替换policy输入e，body/原世界/reward不改，模型eval/无梯度。原生rollout不再运行。
- **读数：** 固定state的动作分布JSD（nats）、argmax改变率、原始及projection cosine距离；不同角色JSD取4donor均值。primary选择性为log((JS_reverse+1e−8)/(JS_other_role+1e−8))的Full−No，按persona平均再bootstrap，固定seed32658/20000。另报告两种JS的绝对水平和repeat数值地板；不是越少角色差异越好，不把distribution可分性直接称语义正确/utility改善。
- **阳性对照：** 同输入同state重复logits完全相同；No与η-only全参数byte一致；不同角色的原BigFive/occupation从source元数据核验；所有input shape及数组ID明确，obs为原source69维，不混版本。source/weights/input sha随结果保存；原repeat encoding作为近零控制。
- **噪声地板 + MIE：** CPU确定性zero repeat及canonical_repeat为数值层；JS_other必须高于repeat100倍且均值≥1e−5才讨论比例。选择性差−.25 log单位为pilot参考、同时Full不同角色JS保留No的≥80%才叫“选择性且保留控制”的候选；这些是预定启发式，不是科学自动裁决。CI只涵盖held persona差异，不涵盖训练seed。
- **混杂审计：** 真实不同角色文本改动幅度/年龄也会不同，全部原始/投影距离报告，不强称词级完美匹配；other-role不是唯一期望动作gold。固定No的状态分布可能偏向No，按early/late分层但不事后改primary。正结果也可能是已知线性压缩/对比语言绑定（PCSP、DAIL、GSR等已有owner），先更新定位再决定是否值得确认。
- **决策表（跑之前写）：** H1候选模式→补强近邻定位并考虑单个独立训练seed确认，不直接宣称新机制或新训练法；整体弱化/比例无区别→将Full收益线索保留但不沿“语义修复”扩训练；静态无模式→考虑状态/伙伴混杂而非硬解释；地板/对照不过→只修诊断、不立claim。
- **算力预算：** 既有fgvd/deps，CPU≤5分钟，0GPU/API，raw在/tmp或cache、Git仅结果摘要；不启动新模型服务/环境。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
CPU0.462秒、0GPU/API，无新rollout。1200相同原生states，Full等义改写JS .041712、No .075181；真实不同角色JS .221613/.244304，Full保留90.71%，不同角色argmax改变率反而.6875/.57646。预定log选择性Full−No=−.47931，persona簇95%[−.63850,−.31580]，四时段方向相同；repeat约4.94e−7/8.99e−7，两个语义contrast均远高于地板。

这满足预定“选择性且保留控制”的候选模式，**整体角色控制变弱不足以解释本次Full的较小改写损失**。这不是证明语义正确，更不是跨训练seed确认。全角色改动距离更大、不同角色同时改BigFive/年龄；单state policy response未排除原收益中population效应。不能反过来强讲一致性训练只有proxy收益。

[完整结果](../results/E32_semantic_selectivity.json)，raw /tmp/npc_e32_semantic_selectivity/per_state.npz。下一关键区分是：有用的语言—目标语义保持，还是对既有整套角色原型的稳定识别；后者同样可以通过本次两个contrast。须先核PCSP/DAIL/GSR等已有ownership，再决定是否需要单目标改动的原生utility实验，不直接扩大训练或宣布新方法。C01仍L1。
