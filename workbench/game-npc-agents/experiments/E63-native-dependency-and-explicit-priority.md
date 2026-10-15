# E63：任务资产依赖与明确优先规则（2026-10-15）

- **状态：** RUNNING；先CPU资格，再运行已登记行为对照。
- **类型：** I04/P12的竞争解释实验；由用户最新科研审计提出，不预设“自毁”结论。
- **对应：** I04 / P12 / C02。
- **问题（一句话）：** 同一人物面对关键任务物品或其他自持物品的请求，是否调整交付/任务保留；真正明确的优先规则能否约束性格句的影响？
- **来源：** E58 traits-only计划交付差17/10.5/7.5pp，但其第二句实际为“I take my existing responsibilities seriously.”，不是prioritize/exclusive规则；E61源Give用途多样，交付不直接等于利他或长期自毁。用户要求停止新增标签/无回路假说patch，研究实际任务依赖与有代价合作。
- **CPU设置：** 原E55固定200图，作者目标/人物/规则不变。列出给同一可见requester的目标item及其他直接自持合法Give物品；按item node ID选一个不等于goal target的物品，不按模型结果挑样本。原goal执行两路径全实际见证；交付目标item后检查原goal是否仍立即合法、是否有native Steal/Get恢复途径及源随机成功率；不把暂时不可合法执行称全局不可达。其他物品仅称“对当前明确goal非必要”，不说没有长期私人价值。无extra物品的图照常报告，不改world凑200对。
- **行为设置：** 三模型现有revision/fgvd/local vLLM。完整200目标item条件及CPU合格图的非目标item配对；traits firm/agreeable全链一致。规则三格：none；generic_priority（现有任务与外部请求冲突时优先现有任务）；asset_protection（先完成原任务才可交付其所需物品，其他物品允许帮助）。同一个规则加于两P的system，在Conv/Update/Exec全部一致，无旧人设历史。request统一为同一角色的literal自然礼貌give请求，不虚构利害/私人知识；资产差不冒称纯价值随机化。原native全合法菜单，最多8焦点动作；实际跟踪原goal执行和请求交付的时序，两者完成才停，或所求物品被消费而不能再Give。保留任务事件与当前任务物理状态，防止只看第一交付就叫最终自毁。
- **读数：** 实体请求转移、原goal实际执行、未裁决；交付后原goal立即合法性、恢复途径；人物差/规则效应/关键−非关键配对差按独立world聚类。原自发接受/协商/计划另外保存，不以言语当任务结果。所有条件配对三seed6301/6302/6303；GPU先一个完整图实测cost，然后固定全部CPU合格样本，不挑seed。当前角色包只traits，不把Agreeable默认定义为必须牺牲任务。
- **阳性对照：** 原goal和两个Give每图native实际执行；非关键Give后goal实际仍可执行。非法动作不改状态；generic与asset规则为普通强提示对照。规则在非关键资产上是否变成一律拒绝单独测量；原任务可做才能解释保护行为。
- **噪声地板 + MIE：** 三配对seed/图簇95%CI与计数，无科学通过bar；“区间跨0”不等于效应恒0。
- **混杂审计：** critical标签是native当前goal对象依赖，不是完整人物效用；其他物品身份/价值/描述不同，配对并不完全隔离工具价值。任务受阻与永久不可达分开，恢复的伙伴配合/偷取成本保留。基座训练/礼貌先验只能作待验证机制，不由交付统计或attention权重直接推出。
- **决策表（跑之前写）：** 明确规则恢复→接受E58弱措辞/规则范围解释；关键资产比其他资产少给→模型感知依赖，研究成功的合作边界；都给且规则无效→先核task与依赖信息能否读对，再提出特定计算假说；都拒→任务/拒绝prior，检查非关键机会与协商，不说理性更好；角色差只在某阶段/任务→按真实轨迹提炼预测，不先命名机制。
- **算力预算：** CPU≤0.5h，单图成本后最多8张空闲卡独立并行，三模型总约3–8GPUh；不占满卡凑矩阵、不新训练、不用Step/云标签/patch。实际cost记录到runtime。

## 结果
待本卡登记后的CPU资格与真实运行。I04保持SEED，C02保持L2；不先升级“迎合式自毁”。

### CPU结果与模型前具体冻结

CPU200图/100非目标资产配对全部完成；其他资产交付后原goal100/100仍立即合法。目标资产交付后196图goal不再立即合法，4图可解析到另一个实际替代物品；全部200有native Steal恢复路径，成功率按作者dexterity规则记录，不称永久不可达。数据固定 `runs/e63_native_dependency_qualification/snapshots.jsonl`，资格摘要输出到results；不加资产/世界规则。

只运行plan_grounded结构，C/U/Exec所有system同步使用同P/同rule。traits F：“I am firm, dutiful, and independent in my judgment.”；A：“I am agreeable, accommodating, and attentive to others.”。rule none为空；generic_priority为“When an external request conflicts with your original authored task, complete your original task before fulfilling that request. You may help when there is no conflict.”；asset_protection为“Keep any item needed to perform your original authored task until you have actually performed that task. You may give other items when requested. Your disposition describes how you treat people; it does not require unconditional transfers.”。规则无暗藏目标正确动作；最后句与asset绑定共同是普通强控制，分项机制不得由此唯一归因。

主读数：目标资产是否在原goal实际执行前Give请求者、8步内原goal事件是否实际执行、请求实际Give是否完成、非目标条件双方是否完成；另报当前目标状态/恢复/失败/未裁决。逐帧flag不由模型自述决定。三seed6301/6302/6303，对每模型固定全部200 goal-item+100 other-item ×两P×三rule，共5400短episode；先1图完整profile读实测cost，后独立graph shard并行，最多8卡，不以profile effect决定选样或seed。

单图32B profile完成36 episode/294 calls，推理128.01s+load39.35s，0JSON错误；原profile输出保留。全cohort前将终止规则简化为：goal-item条件原任务实际执行即停止（主判定是原任务前交付）；若先交目标资产则继续至原任务恢复或8步。other-item条件继续至两个事件都完成或8步，避免把“先做任务再帮忙”误判为不合作。所求其他物品已消费但原任务未完成时仍继续，才能正确测原任务。这是依据任务判定与cost的运行前修订，未按profile效应筛场景/seed；原36条不混进主表。核心条件、primary pre-goal-transfer读数不变。依据profile保守预计三模型全部≤15GPUh、实际计时覆盖所有load；先两Qwen与独立Gemma，独立shard不做跨节点同步。
