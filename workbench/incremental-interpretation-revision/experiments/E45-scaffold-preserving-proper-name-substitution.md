# E45：固定报告框架，仅将描述NP换成名字（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E43–44不支持普通场景的普遍角色反转。
- **问题（一句话）：** E40明确account/identity/report框架完全保留时，固定proper names是否仍产生old正/newother反向与谓词差？
- **设置：** E40全部24来源/12family、两order、两个role worlds及全部old/new readout原文；仅候选描述NP与target phrase替换为E43冻结名字。原source_anchor、actor、activity名词、progressive谓词、identity_intro结构、unused report、event bridge及target其余words原样。Luna作者24条逐一核对并独立whole-rendered审核2016packet（1920raw+96QAcontexts）；current question保留原文，192 native base/scope。去掉描述属性、名字可能改变语义可适配性，故不叫单词级语义等价消融。E40原描述版本与E44普通场景冻结作paired transport comparisons。
- **读数：** M、activity D、neutral D、J=activity D−neutral D全部；主otherActor/sameV两order absolute D及J；old control；different−same；与E40同条件J/D差、E44 no_protocol对应orders J/D差。12family先两source平均，paired bootstrap10000 seed20261005，all/eligible/grammar共同与E31固定cohorts同步。不得由J负单独宣称角色反转，尤其old J须报告。
- **阳性对照：** old activity D正及具名old role QA可用，R8一条scope指令全报。全部候选target pair causal tokens一致、原suffix只target被替换、names两world词袋相同。
- **噪声地板 + MIE：** 固定FP32 seed0 batch4/8；derived1920不是独立n。E40newother同V J−9.921/−7.238，E44普通场景J+6.243/−.999(last CI跨0)，差异不能归到已消除的only/否定。不设通过gate、不挑名字或order。
- **混杂审计：** proper names去掉kinship/社会身份/物种属性；their nephew/brother原读数可能在新actor下发生possessive rebinding，不能把原NP文字相同当entity identity相同。E45名字保留two-world候选身份，E40actor groups可能成员重叠，不证明绝对disjoint。本文无probe/SAE/训练，不把predictability当世界概率。
- **决策表（跑之前写）：** names在E40frame仍稳定反向→描述/possessive不是必要条件，下一匹配frame结构区分roster/episode/report；names改正且old控制有效→角色描述与referential realization是关键边界，下一alias-grounded名称/描述区分语义属性与指称绑定；只一order/少数family→focus/适配竞争，保留全体与不确定；只有J负但activity D正→追neutral validity，不能卖inversion；old控制失效→诊断语言/测量，不扩大模型。
- **算力预算：** 现有venv/local frozen Qwen3-8B，独立GPU0 raw、GPU2 native，预计≤.10GPU·h；**实际：** 待填。
- **命令：** scaffold_name_roles.py build/adopt → event_identity_infer.py --experiment E45 / time_indexed_role.py --experiment E45 → analyze_role_controls.py。所有构造/输入审计须在推断前完成，输出再独立盲审。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
