# E25：纠正影响原事件、同人物新事件，还是另一人物的新事件？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01/C04/P10；E24跨source结构存在，但不同event/actor/predicate解释仍竞争。
- **问题（一句话）：** 更新一个活动的参与者约束后，后续关系偏好的改变是否局限于那个活动，还是泛化到人物或整个谓词？
- **设置：** E24原24source/12verb-family、原S1/原actor原event的only角色事实逐字保留。新增同actor/同verb另一published actor两支，actor continued a separate activity（continued aspect固定），随后In that new activity, actor was/were V-ing own/other NP for a moment或neutral noticed。24×2GP/cue×2role事实×2named/generic×2actor×2readout frames×2NP targets=1536新输入，原event reuse E24 own/other768冻结分数。只用已有source actor/coreNP字段，换actor数一致性用独立注释donor was/were，不猜性别/造actor。两独立Luna768条逐variant审核S1/事实/old scope/new scope/actor identity/grammaticality，before inference。
- **读数：** M=bits(other NP)−bits(own NP)。I=[named−generic GP−cue]_activity−同值_neutral；各role evidence、actor/new事件、GP/cue/frame cell全部报告。主reference-only event_transfer=I_sameActorNew−I_originalEvent，actor_transfer=I_otherActorNew−I_sameActorNew，full_transfer辅助。每verb两个source先平均，再12family paired bootstrap10000/seed20261005/95%CI。all/eligible/acceptable/prior-role-clear∩new scope/actor/readout-clear，共同cohort要求原+两新branch完整，不能按model score删家族。
- **阳性对照：** E24原event I_all−.795 [−1.210,−.394]bits、strict9−.766 [−1.168,−.363]及双向role facts响应明确；原event scores immutable reuse。新活动没有显式only约束own/other，**不以患者选择当logical correctness gold**。独立审核应能确认原only只指old actor/old event，而新的活动桥/actor明确；pre-token identity/HF loss同reader校验。
- **噪声地板 + MIE：** FP32约1e−5bits、12family source variation主导。差为零的CI不能证明相等，报告paired差/每family；不用效果门槛决定科学好坏。
- **混杂审计：** 原/新event桥 that particular→a separate、readout same→new，aspect与时态固定，但event presupposition/长度改变；严格event causal mechanism仍未隔离。两新branch只换合法published actor/aux，首次引入actor是角色变化的一部分；matched neutral控制普通entity accessibility。data reviewer处理scope accommodation不确定，不根据结果改材料。新对象及old事实可语义相关，概率迁移不是逻辑scope violation；需要未来真正use任务才讨论失败。源GP难读保留marginal而非过滤条件。
- **决策表（跑之前写）：** 原I负、新event两actor都明显弱 → event-dependent修订解释增强（仍有event语言差别）；sameActor新event保留而otherActor弱 → actor-conditioned关联增强；两新event两actor均保留 → predicate/global关联更可解释，不能叫精准旧event binding；neutral也平行变化 → 一般entity salience竞争；方向变化/CI宽 → 报具体cell和family，不扫prompt/models/synonyms。只在功能证据存在时才提出scope错误；E23未通过的读数不追认。
- **算力预算：** 两空闲H20独立actor分片，各768，预计总≤.08 GPU·h，frozen同pinned Qwen3-8B FP32/SDPA/batch4/seed0/TF32false，raw无chat/question/instruction。分片immutable config/scores各自hash，合并核对全1536 ID/相同code/model；GPU·h取两片实际和。**实际：** 两独立actor768分片，各约35.5s，合计.01978564 GPU·h；合并1536 ID/hash/config全部核对。
- **命令：** correction_scope.py build/adopt/split；两张卡分别event_identity_infer.py --experiment E25 --data audited-same_actor-v1.jsonl / audited-other_actor-v1.jsonl；correction_scope.py merge/analyze。所有cache raw不进git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

1536新输入全部eligible、704acceptable、1424prior+new-scope-faithful；原+两新branch共同完整all12family、strict9family。原S1/旧事实保持，独立审核均将old only作用范围定为old actor/old activity。

主reference-only I_all12：原event−.795 [−1.210,−.394]bits；同actor新event−1.249 [−1.757,−.762]；另一actor新event−2.070 [−3.099,−1.200]。event_transfer−.454 [−1.114,.220]不确定；actor_transfer−.820 [−1.460,−.322]，换人物没有消失而更强。strict9：−.766/−1.041/−1.600，actor_transfer−.559 [−.885,−.169]。均为source-family paired CI，未把variant当N。

[统计](../results/E25-summary.json)、[每family](../results/E25-per-family.csv)、[合并配置与immutable分片hash](../results/E25-config.json)、[材料audit](../results/D0-E25-material-audit.json)。按决策表限制解释：event-specific/actor-specific的完整绑定修订解释不足；谓词/模板相关的可迁移关联更可解释。新活动患者没有gold，**不能称这些分数变化为scope违反或新事件事实错误**。下一直接测事件范围判断与源句final interpretation controls，区分scope知识可访问而prediction有portable trace、以及scope本身没处理好。C04仍L1测量，I01 PILOT，尚不讲hidden state或一般能力。
