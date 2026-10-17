# E26：人物描述与原生控制的语义资格（2026-10-14）

- **状态：** DONE
- **类型：** measurement / 强基线；不以文本扰动本身宣称创新。
- **对应：** I02 / P06 / P09 / C01；E23–E25。
- **问题（一句话）：** 排除padding后，原人物的描述顺序/非机械背景变化，是否改变原生角色utility；普通具体行为提示是否已解释这种变化？
- **设置：** PCSP pin5420f7b v3-large、原test100/16NPC/200cycles、三世界seed26011/12/13。canonical（E23正确pool）、canonical_repeat（同模型原文重算数值地板）、reverse_clauses（年龄职业header不动，逗号分隔描述逆序，词和事实保留）、traits_only（去年龄职业header，所有特质保留；信息删除不称完整等义）、action_cue（原文+一句作者preferred_actions具体动作名；信息量/长度增加，为R8普通强提示）。Qwen3-Embedding-0.6B同revision/fp16/正确last-nonpad/max256不截断，核tokenlength≤256；canon与E23同文parity须cos≥.9999。先生成文本并hash固定，再看行为。
- **读数：** 同native状态action JSD只诊断；primary原累计return差、preferred_action_rate、critical needs，persona簇paired bootstrap95%。先原public Full/NoCons42/43/44全部（correct输入与原cache差由E24列），再E25正确编码30iter两不同政策Full/NoCons；readout_only byte同一共享exact rollout。原body/reward/初始世界不变，所有16code同时变含peer dynamics，不叫单focal效应。行为不同但utility保持允许为正结果，不给唯一动作gold。
- **阳性对照：** canon_repeat与E23高余弦；逆序前后clause multiset完全一致；原完整episode byte replay；trained weights strict-load、初始世界同一。cue仅作者preferred原动作，不另定义greedy/忠诚gold；cue恢复仍是已有动作锚/grounding解释。
- **噪声地板 + MIE：** canonical_repeat为fp16微扰地板；return≥5%且超地板才深入形成路径，阈值仅pilot判断。三public seed全保留；correct30iter没学好游戏不能否定机制。
- **混杂审计：** clause顺序可受已知叙事prior影响；traits_only删除背景，非完整等义；cue增加语言/长度/action anchors，非净语义干预。作者preference/style reward只验证游戏控制，不是人类人格gold。PCSP已有English50角色/两韩语同义/PHASE5几何，不冒领。
- **决策表（跑之前写）：** utility在地板内→persona可有效且控制稳健，I02失稳线索弱；普通cue恢复→承认已有解释；可预测Full/NoCons差→结合E25路由再定位，不据单次顺序敏感称好idea；正控制失败→先修恢复。
- **算力预算：** encoder1GPU≤10分钟，其余单CPU≤30分钟；与E25合计最多4GPU<白天8；fgvd+deps，0API、原资产不覆写。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
原public与正确训练短pilot分支均完成；分支结果如下。

原100文本复算cos均值.9999975/最小.9999918；逆序.950099，traits_only.772916，action_cue.931475。原六公开policy分支完成，210秒单CPU；reverse_clauses累计reward差Full42/43/44=−29.93/−31.99/−18.05，NoCons=−26.78/−34.88/−27.84，显著超重复微扰（约0至−.51）。不是Full特有现象。critical needs变化方向随seed不同，不能把总reward下降同义为身体更差。action_cue目前附在canonical而非reverse上，**不能据它宣称恢复或未恢复reverse异常**；需单独卡注册reverse+cue控制。

Full删除biography三seed差+1.16/+2.58/+4.00，NoCons−14.55/−.37/+4.38，没有一致NoCons失稳结论；不筛seed。LIBERO-Para/GSR已有同义指令行动退化与重绑定强近邻，普通顺序敏感不是新科学增量。[public原生结果](../results/E26_public_semantic_utility.json)、[编码资格](../results/E26_semantic_encoding_gate.json)。E25正确训练分支待检查，0API。

E25正确训练30iter分支DONE（64秒单CPU）：canonical NoCons84.997、Full83.850；reverse损失−11.344[−14.342,−8.400]、−8.447[−10.278,−6.701]；traits_only两者+4.179/+4.218。Full不显示独有顺序失稳，弱化I02该解释。两者reverse身体critical fraction也降低，但这是作者reward/健康指标不同，不能换primary给更好/更坏单一结论。[正确短pilot结果](../results/E26_corrected_pilot_semantic_utility.json)。新科学增量0。

## POST-HOC：梯度路由与改写损失的交互（2026-10-14）
已有正确编码seed42结果，配对Full−No的reward-change差：reverse +2.8976、persona簇95%[.4871,5.3894]；repeat+.1386[−.0330,.3427]；traits-only+.0390[−1.7543,1.7531]；action-cue+1.8282[−.1660,3.9416]。全部四项保留，不当预注册primary，也不把held-persona CI当训练seed方差。原总reward含作者style项：reverse时两policy critical-need fraction都下降，所以收益变化不是单纯生理损害。[事后结果](../results/E26_POST_HOC_route_interaction.json)。该正向线索引出E32的新预注册静态区分，不据此直接扩训练。
