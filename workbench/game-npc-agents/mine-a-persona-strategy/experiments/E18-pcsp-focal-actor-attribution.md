# E18：PCSP 原轨迹单位与焦点NPC因果归因（2026-10-14）

- **状态：** DONE
- **类型：** REPRO / measurement因果校准（P06；代码事实不是自动科学创新）
- **对应：** C01 / E08 / E17。
- **问题（一句话）：** 作者检索protocol读取的是个体NPC还是同人物群体的前200帧；修正actor单位后，在异质伙伴中能否正确识别焦点NPC且保留其真实persona控制？
- **设置：** PCSP@5420f7b…，公开v3-large full_seed42/full/policy.pt与traj_encoder.pt、原500 embedding/test100。source consistency._rollout_persona复制同persona至32角色，顺序拼所有actor帧；_encode_trajectories截前200（约6.25 world cycles）。本实验先逐byte复现该all-A helper正控制，再同一原native世界生成all-A/all-B/focalA+31B/focalB+31A。A固定test100源顺序首条；B固定φ距A最大但不同BigFive联合原型的test人物，不依据behavior选。world seeds17301/17302/17303；每200cycles，原AEC依次observe/get_action/step，所有参数冻结。先一完整episode核成本；有信息再另2worldseed/其他policyseed，不挑最好结果。
- **读数：** 两个既定单位：作者joint-first200及focal0自己的200时间步，统一100候选persona projection余弦top1/3。focal真ID、peer真ID及pred与概率完整记录，不能将population label冒称focal label。focal原action分布/needs/reward/位置及同state A/B logits KL（作者已有KL，作为控制阳性）；θ/φ/η均不更新。完整actor_id序列+obs+actions+source hash缓存。
- **阳性对照：** all-A自写native循环与原helper在同Torch/world seed下joint obs/action逐byte相同；strict加载checkpoint；counterfactual仅换原作者persona configs/embedding分配，world规则/reward公式原样，非改reward制造异常。原all-A/full应超过chance；若资产不一致先报不复现。
- **噪声地板 + MIE：** 3worldseed全保留，1个预选角色对只作测量资格。joint与focal单位同时改变时间跨度/actor混合，不能把数值差都归某个因素。焦点固定A更换peers时focal trace仅改真实交互context，若decoderpred改为peer而同state自身persona KL仍明显，则另做世界/身体/decoder解释最小控制，不能立刻判人格漂移。
- **混杂审计：** joint population分类有其合法解释范围，作者也已验证MeltingPot/UE5，不能据一个函数关掉其贡献。个体策略应随伙伴和利益环境变化；错误解码不等于个体政策丧失角色。该实验是native benchmark，不是LLM自述人格，trait奖励已被直接定义，不当独立personality gold。修改观测单位是新诊断条件，作者原结果完整保留。
- **决策表（跑之前写）：** own-unit稳健→承认角色控制并限制原metric单位；两单位均偏peer→先定位utility/context/训练分布，至少两竞争解释；仅joint偏peer→归actor聚合解释，非新机制；原all-A控制失败→优先asset/protocol，不筛人/seed替换。
- **算力预算：** CPU≤15分钟，GPU0，现有fgvd+overlay，0API；模型与raw不进git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

首个native成本gate核验修正：当前v3-large源码N_AGENTS实际为16，非预估32；原helper200-cycle产生3200帧，截前200约12.5 cycles。上面的32数字是运行前估计，实际manifest/所有物理执行以未改源码16为准。E18 all-A与原helper全部obs/action逐byte一致；首个A=f401的own200正确识别401，joint前200识别同原型另一职业412。固定f401/peer427后，own识别同原型409，joint识别488。此时不支持“角色控制丧失”；单位/职业粒度/群体内容必须分开解释，尚无新科学claim。

seed42/A401-B427/3world seeds四条件全保留。all-A原helper obs/action逐byte一致；当前source16NPC×200cycle=3200帧，joint前200近12.5cycle，own200为200cycle。两种input unit不同，但各自有明确范围；原η在mixed peers时joint cosine偏向majority，own cosine仍偏自身，原A的主要动作rest_with_others、B为rest_alone。这个结果支持个体输入的真实控制而非角色漂移；不能将joint分类直接报成focal行为/Persona gap。世界/utility/social compatibility会随作者persona配置变化，这是原规则，不是强行改reward。数据见E18_focal_attribution_summary.json；只一预选pair，未升L2。
