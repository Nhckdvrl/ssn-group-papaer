# E33：单项利益编辑是否保留可执行控制（2026-10-14）

- **状态：** DONE
- **类型：** PILOT；已有policy的组合控制诊断，不训练。
- **对应：** I02／P06；E26/E32正向证据后的竞争解释。
- **问题（一句话）：** Full的改写稳健性是否保留单项作者利益取向的改变，还是只稳定识别整套人物原型？
- **竞争解释：** H1可编辑语义：只改C时策略按作者完整收益发生有用变化；H2原型／训练相关性：整体人物可区分，新组合不能按新利益行动；H3表述不够明确，普通显式C说明可恢复；H4短训练与单seed不稳定。失败不能独自区分H2/H4。
- **设置：** 原PCSP pin5420f7b，E25正确编码seed42/30iter的Full/No。固定原held五原型各首个人物401/421/441/461/481（同occupation，按ID选）。仅将原作者模板中的C描述改成high或low，其余BF/年龄/职业不变；AST只提取纯_BF_DESC，不导入Anthropic生成模块，原文重建逐字相同。预备明确句 `In this game, the character's Conscientiousness (C) is high/low.`，不指定唯一动作。
- **利益／身体界定：** 原PersonaConfig允许独立设置BF、decay、preferred_actions；只改focal BF_C，保留原decay/prefs。伙伴固定原人物402/409/416/422/429/436/442/449/456/462/469/476/482/489/496。不是原benchmark分布复现，是身体固定的属性干预；原C_high相关work decay=1.3、C_low=.7。原物理、动作、收益、每步顺序不改，收益包括style和social。
- **编码：** 现有Qwen3-Embedding-.6B revision97b0c6，fp16/max256、最后真实token、归一化；5条canonical对E26正确数组cos≥.9999。文本全部保存，无API。
- **读数：** 同一动作轨迹同时在原C_high/C_low环境执行，逐cycle检查物理／观测byte同一，获得完整J_H/J_L，不手改奖励。两输入的利益选择性 `[J_H(pi_H)-J_H(pi_L)]-[J_L(pi_H)-J_L(pi_L)]`，报告全部四格、每个base/seed、需求及动作分布。它不等同全局最优或现实人格。主要报告五base各三world seeds33011/12/13与均值；只有一个训练seed，不伪装更多独立样本、不作训练总体CI。
- **阳性对照：** 先CPU固定动作带验证high/low只改收益不改物理；source完整reward差与style+social精确分解一致，20合法动作收益contrast非零。编码原文数值控制、同输入policy重复完全一致。原生200cycle episode先单个成本gate；待测动作全部policy选择，不脚本替代。E32跨原型控制只作资格。
- **噪声地板 + MIE：** 固定动作／byte控制为零地板；同seed共用独立CPU generator采样流。pilot参考为至少4/5base同向、选择性交互均值>0且非浮点误差，不自动当科学裁决。所有seed保留。
- **混杂审计：** 记录长度／原始及projection距离；非C属性逐项断言。身体相关性故意破开，可能合法OOD，不能径归因语义压缩。伙伴输入/body固定，伙伴可响应focal动作，属原生后果；不同route伙伴政策不同，主要route内比较。单occupation/五profile/单短训练seed未控制。source奖励直接定义部分行为，不称独立人格效度。
- **决策表（跑之前写）：** 资格控制失败→先修工具；plain两route均至少4/5base正且均值>0→支持组合控制，停止失败假说；否则全部五base、两route、三seed运行明确句，不只重测失败者；若恢复→接受普通描述解释；否则保留原型／身体相关性／短训练竞争解释，有新区分证据再考虑确认或方法。PERSONA/PCSP/DAIL/GSR的已有ownership不变。
- **算力预算：** CPU gate≤30秒；编码单空闲GPU≤5分钟（先核设备，白天总≤8）；原生cost gate一episode≤120秒，plain60episodes预计CPU≤5分钟，必要时明确句再60。超gate不自动扩大。0训练/API，现有fgvd/deps，raw `/tmp/npc_e33_*`。

## 结果（跑完后填写；不改上面的内容）
CPU奖励gate .173秒，五base物理／观测byte同一，完整奖励差分解最大误差2.78e−17；20动作contrast范围最小.529。25文本编码64.78秒（单GPU、含载入），五canonical真cos最小.9999965；首版误将fp16近单位向量点积称cos，在读policy结果前补分母并重算，原数保留。首完整episode1.726秒，随后全60episodes CPU55.836秒，0训练/API，GPU已释放。

预定相对利益选择性No均值2.2565、Full2.4703，两者均5/5base均值为正，30个route×base×world对比中26正4负。所有seed保留。按原决策表，不追加明确句60episodes，不扩大训练。该读数不支持“只能识别整套原型、完全不能响应单项C语义”的强失败故事。

**四格构念校对（原卡已要求报告四格，不改primary）：** 五base均值的10个route×base单元中，9个由low输入在两种原生目标下同时取得更高总收益，1个由high输入同时更高，0个呈期望偏好交叉。故正的差中差只证明相对取向，不能提升为“编辑改善对应目标总效用”。先前口头强解释已收窄；单训练seed／三world seed、身体相关性、style与非style权衡仍是竞争解释。没有新机制claim。

轨迹抽查（POST-HOC描述，不重新选样）：Full441/33013高输入104次socialize_initiate、25次focused_work，低输入129/17；高目标收益104.10/147.69，高输入并未更优。Full401/33013差中差−.597、No461/33011差中差−1.495均保留。物理需求与原动作完整保存，不从C标签判唯一正确动作。

[全部数字／四格](../results/E33_single_interest_control.json)。原始约4.93MB持久化到既有cache/runs/e33_{reward_gate,codes,native_cost,plain}，/tmp原路径保留映射；60完整轨迹含obs/actions/needs/positions/rewards。C01仍L1，I02仍SEED，尚无已验证新科学增量。

用户执行准则更新（2026-10-14，原读数不改）：取消以预设MIE／比例／若干base过线作为科学价值裁决或舍弃线索的规则；原卡决策条款仅保留历史。结果按现象、竞争解释及顶会近邻实际证据解释，自由探索。资源预算与实现正确性核对照常记录，不等同科研淘汰bar。
