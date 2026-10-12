**当前末版精度修正（首有效评分前）：** dispatcher SHA `5abd14f91ac0cd56f40e714413d83d066ff4173af5a24e0de1cd4788a5f0beb9`；protocol `550890014e6553290695f7fb6f35823a4b25ef06acca551649934a69d30b643f`、三engine/18CPU材料不变。仅TF32 True→False，恢复原full-FP32 GEMM；0科学row失败与原f704…seal均保留于failed_tf32。以下原CPU检查仍适用，文中的TF32方案为被撤回的数值实现候选，不是当前设置。

# E131首评分前独立校对

18批实际CPU全部通过；未发现科学干预、真值或observer blocker。可冻结最终protocol/dispatch/三engine，启动Q32与两8B新配对；L70待各实际节点完整权重校验后按同固定协议运行。当前0科学评分，runtime多卡图/缓存/数值尚未验证。本次围绕大小模型的同一Source证据形成解释，不因E129/E130有限Cue接口给旧机制附资格，也不改变三项核心认识/等级/研究状态。

最后protocol SHA `550890014e6553290695f7fb6f35823a4b25ef06acca551649934a69d30b643f`；dispatch SHA `2e6d2d2ab1f38937408c0a60ce09c141f4ddb6abd303857311a263c1638508bd`。[完整JSON](independent_pre_score_review_2026-10-12.json)保存全部engine/父源/依赖/18材料哈希、逐context移边和CPUtoy结果；无GPU/原科学源或文稿修改/commit。

| stage | 冻结父实验 | conditions/ctx | contexts合计 | 预定scores |
|---|---|---:|---:|---:|
| mechanism | E121 | 43 | 160 | 55040 |
| native | E120 | 64 | 160 | 81920 |
| function | E123 | 85 | 160 | 108800 |

合计18run/480contexts/245760预定科学评分；实际CPU核5440 prefix streams、12160 mask集合、30720整个query批图、268800demo/query gold槽。重复校验不是新增样本；两个大模型三stage各16→32，两个8B锚点三stage各32。Source角色、两private方向、shared/far、within secondary、single与pure instruction均完整。

AST逐项证明：移除唯一新增dispatch import，并恢复model loader、model revision、gpu_hours倍率以及两处跨设备torch.equal校验的tensor复制后，三engine**整棵AST完全等于冻结父源**，不是只比compile/analyze；三个analyze AST也逐字相同。故材料、目标、mask移边/恢复、KV/K/V交互位置、gold、归一化、原指标和CI没有改。主科学指标仍是三环节原生形成/固定系数1重建、无donor原生操作、真实SST Source功能政策。

literal函数仅将CUDA常量替CPU并截在model forward前执行，再与独立numpy因果图逐元素比。Native cross/within阻断严格过去答案块→真实A首label-word，self保留；answer_only_restore是在全部B→A形成阻断后仅开放B答案词/分隔符→A-label，非完整label donor恒等恢复。Function双向answer_cross_off、all_cross_off对称按各Source真实label/answer位置；所有namespace/world移边和length相同。query全token读取/gate/padding/globalposition正确，pure instruction仍native形成。

实际数据：自然stage的官方SST5 train/validation/test arrow SHA/gold均从本地原始Dataset独立核。训练demo按冻结text hash parity分池，discovery query为官方validation、confirmation为test，去train/validation重叠且不重写原文；没有能力/输出筛材料。B input保持多重集/labelstream/Source/位置，cross改变private规则、within只改关联控制，A固定。Synthetic native按原生成器词库单独核gold。两家族×三stage的大小新32材料全部逐字相同，新固定seed文件不同于旧小模型确认；“fresh”是新采样context，不称整个官方语料未出现过。

真正tokenizer：Q32读取9216… official snapshot；L70只读拷贝fvcrc11的config/tokenizer四小文件，实际重构而非直接用L8代替。确认Q8/32为36/64层、L8/70为32/80层；Q8审计helper曾误假设32并及时assert停止，修helper后18批全过，科学协议从未硬编码32层。Q32根据记录的17shard size/SHA逐项与pin plan比对；70官方/mirror30shard计划SHA一致，实际各节点复制完成仍由protocol identity gate保证。这不是独立重新hash全部大权重。

实际DynamicCache CPUtoy执行literal patch的48 scope/kind组合，全部层K/V、clone ptr、只改指定A/B/label区域、source保持、batch8/seq均正确；执行literal edge_eager跨36/64/32/80层共848 K/KV/V/self交互，全原GEMM几何，只替指定sender K/V并替receiver输出行；attention同词/严格过去可用计数一致。toy非模型forward/科学成绩。

多卡：balanced装载强制实际1/2/4个GPU、全部param FP32 CUDA frozen，device_map禁止cpu/disk；缓存patch/edge按layer_idx对应层且使用Python索引，未见CUDA0布尔索引跨设备错误。检查本地Transformers模型skip全局迁移past_key_values，DynamicCache按各层设备repeat，eager把实际mask加到score后FP32 softmax。device-local比较仅复制校验tensor到收到mask的设备。未独立跑多卡模型，实际cache各层设备、nooffload、mask收到正确设备及.001 cached/full/self需runtime记录验证；不把CPU检查称runtime通过。

protocol每stage终于恢复原eager，成功/异常都恢复；同process只复用冻结weights，重新生成每stage/phase历史cache，分析定义不变。最后驻留计时补丁记录首次模型装载到完成或失败stage的连续device-hours，包含权重驻留期间CPU材料/analysis/interstage/floor等待；保留各stage wall×真正卡数与独立等待字段，加载/floor失败不记科学阴性。累计resident字段不可逐stage再相加，只取最终每worker总计；最多12张卡须按实际launcher/同时活动worker核，CPU本身未证明资源并发。

TF32是授权的数值实现变化，权重/cache仍FP32。图和函数相同不等于逐值数学实现完全相同；继承.001 cached/full/self未放宽，但它比较同TF32实现内部等效，不证明与旧non-TF32输出完全一致。新配对大小锚点同设置，flag、大小模型primitive/正反方向、负/零和近满分性能都需如实保留。理论不以同层编号、同效应量或持续错误定义成功。

范围：C21–23的Source关系形成/内容/使用三环节与实际Source功能跨尺度得到同协议检验；参数量与训练配方一起变化，不是纯scaling-law因果实验。本项没有新Food/Service双criterion交叉，不能因此自动外推原C24全部任务。原attention mass是head求和，不能不校正头数拿绝对mass大小作跨模型机制强弱证据。保留强近邻CTA/Cho/AddUp/Sun已有计算所有权，是否新增知识要看同关系操作与后继Source使用的实际预测，而非只比错误比例。无需增head/layer/alpha/格式门槛。

阅读范围：完整E131卡、protocol/dispatch/三engine与冻结父源及依赖，18CPU、真正tokenizer/config、官方SST arrow、installed eager/DynamicCache、字面CPU cache/edge。外部理论论文依既有定位和root读文记录，本次未独立复现外部机制；无科学raw或author summary存在。CPU helper正常exit0后ResourceTracker destructor有stderr噪声，未影响实际assert/结果，不作科学失败。

精度补核：独立AST证明确实仅一处allow_tf32常量True→False（注释不执行），所有其它dispatch/protocol/三engine源码、18CPU input SHA均不变，无需重跑CPU。Q8/L8/Q32 cached/full最大误差分别.039123535/.005498886/.003240585，均>.001且behavior.jsonl空；三失败worker驻留计时独立重算合计.075811325GPU·时，不能算科学阴性或用于种子筛选。原f704…JSON/MD及三个失败目录/日志完整保留，原地板/读数/同材料种子不改。当前full-FP32可冻结同18协议重启，真实多卡runtime仍需通过既有floor/mask/cache检查；不收缩C21–23/核心三认识，不新增模型/控制/层头格式矩阵。详见[精度补核JSON](independent_precision_fix_review_2026-10-12.json)。
