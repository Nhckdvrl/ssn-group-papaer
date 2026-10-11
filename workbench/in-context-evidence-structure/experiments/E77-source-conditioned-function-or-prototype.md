# E77：来源响应正确，是否就学会了来源条件化函数？（2026-10-10）

- **状态：** DONE（direct控制有效；单来源identity也弱，不称独有Source组合缺陷）
- **类型：** PILOT，修正E76中点/加性任务的替代解释；非Source能力判决。
- **对应：** I04/C09/C15/P18；不能从Source反事实响应直接推出完整Input×Source计算。
- **为什么现在：** E76新名字/数字确认准确率仅.6875/.7344、未过.80，虽然Source方向响应稳定。其未见Input总是demo中点，Source label平均值可答；且x+b是加性主效应，不足以检验Source对Input规则的真正选择。因此暂不铺foreign-word机制，先使mean/prototype与function预测分离。
- **设置：** Qwen3-8B float32/eager、GPU0、conda；32contexts seed77001，SourceA规则identity/9-minus-input均衡，B为另一规则，C/D独立identity/complement，8个A×C×D组合各4contexts，Alex/Sam/Chris/Dana。每Source Input2/7各2records，Label为x或9−x，16混排。
  - 每source的Input/Label边缘频率都完全相同（2/7各2）；均值恒4.5，不携带operator identity。所有query x=0..9，A/B共20queries，同一context跨query改变Input。2/7为seen正控，3/4/5/6为插值novel，0/1/8/9为外推novel，后两组所有gold不在demo标签集；identity的Word在query Input中、complement多需计算，分开报告，不能只看identity。
  - identity vs9−x的Source差为2x−9，随Input反转，不能用Source常量偏置解释全域正确。模型已知两种熟悉候选算法，只需从source的Input→Label关系识别选择；不是arbitrary-function learning。
  - 五接口：mixed inference、mixed+一句Source scope、single inference、single+Source scope（每query只给所问Source4records）、mixed direct-rule table（header明确每Source是哪种operator，检验已知Source绑定＋算术执行，非学习证据）。规则table随counterfactual真值一起更新，不喂错规则。
  - base、owned_a、owned_b、foreign_swap；只交换对应Source内2/7的Input→Label关系，使该Source operator翻转，global及per-source Word频率/输入/位置不变。Foreign只翻C/D、A/B不变。Single irrelevant修改不影响其prefix；所有conditions全保存，不挑答案/Source。
- **读数：** 精确0..9十数字continuation概率（共同space＋一digit），严格margin>0 accuracy、margin、demo-output {2,7}选择率；seen/interpolation/extrapolation分开，identity/complement分开。参数Source效应按theta_A[LD_A(base)−LD_A(owned_a)]、theta_B相应，其中LD_s(x)=lp_s(x)−lp_s(9−x)；Source排名只辅助，不拿其正号当完整函数。4000context bootstrap seed770。
  - 模型比较是同一上下文paired Single−Mixed、Source指令−Mixed、Direct−Mixed。均值/nearest-demo作为明确的受限解释，不把“函数之外全部是mean”二分。
- **阳性对照：** exact十digit oracle与8格平衡、theta关系翻转及每Source label-count不变；full seen≥.90；Direct-rule identity/complement novel各≥.90才讨论inference；重复cache no-op≤.10nats。无missing权重；所有32×5×4×20评分，Source-specific single分别prefill，不能把A的single-cache用于B。
- **噪声地板 + MIE：** no-op≤.10；要称有效未知Source函数执行，interpolation/extrapolation的identity/complement各≥.80。Single−Mixed或Direct−Mixed novel差≥.10、CI不跨0为重要程序边界。Source响应≥1CI不跨0仅是有界source使用，不单独触发完整机制主张。若控制无效/未过门槛，不做强机制判决。
- **混杂审计：** 熟悉operator选择不是新算法学习；single长度/干扰不同，不从其差单独定位Source计算环节；direct额外提供规则信息，仅阳性。Teacher-forced numeric choices非自由生成，marker/原生聊天边界另测。任何未见数字失败不能自动称组合缺陷；mean只是E76新增替代，不是强文献空白。
- **决策表（跑之前写）：**
  - seen/中间支持好但novel只产2/7或常量 → 以原型/实例检索解释优先，Source响应不证明function已学会。
  - direct与single novel有效、mixed差 → 才有Source-conditioned inference的组合线索；仍需指令与机制控制，不自动说功能不存在。
  - single novel也差、direct好 → 一般从demo推断/部署operator的问题，不归Source特有组合。
  - mixed两operator的插值/外推都可靠 → 才有Input×Source函数执行的阳性；原E76平均解释被新任务排除，之后考虑word/rule拆解。
  - direct也差 → 即时接口/已知算术执行无效，不归function inference或binding；换观测/原生接口。
- **算力：** GPU0空卡，E75在GPU1仍回答任意函数空间问题。NVMe8B，预计3–8分钟，不训练；只这组辨别pilot，不并行下游patch。
- **产物：** scripts/e77_function.py、scripts/analyze_e77.py；小run/analysis入git，raw JSONL本地。
- **定位：** Cho task recognition/learning、Kossen label relations、ICL Ciphers、Few-Shot Examples Add Up与activation patching方法已拥有很多成分。本卡是对我们自身因果Source→能力桥的校对和更好任务，不因新实验名称宣称novelty。

## 启动控制校正（未读取科学结果）
首轮在direct-rule的长度/位置断言失败，0条完整科学context，保留`qwen3_function_invalid_direct_layout`与日志。Direct-rule翻转会改变header中“copies…”/“subtracts…”长度，本来是额外给规则的能力阳性，不能当inferred条件的token-matched关系交换；原卡已明确direct额外信息与table更新。修正断言只用于四个inferred模式，且把所有contexts/variants的布局预检移到权重加载前；direct的Source响应仅辅助、不能作纯关系位置因果证据。数据/seed/规则/读数/MIE均未变，原进程终止后再改，E75依赖保持。

## 结果
32context、五模式×四真反事实×20query×10候选完整，no-op0、179.393s；`results/e77/qwen3_function/{analysis,run}.json`。

| 模式 | seen | 插值identity / complement | 外推identity / complement |
|---|---|---|---|
| mixed | .9453 | .4219 / .8438 | .4141 / .6563 |
| mixed+Source指令 | .9609 | .1875 / .9844 | .3438 / .7109 |
| single | .9844 | .5625 / 1.00 | .6719 / .8828 |
| single+Source指令 | .9922 | .3828 / 1.00 | .5625 / .8828 |
| direct source-rule table | 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |

Single−Mixed 插值+.1484[.0195,.2695]，外推+.2422[.1719,.3125]，确有mixed代价；但identity单来源亦低于.80，所以**不判多来源特有的功能组合缺陷**。Direct所有query全对说明指定接口可绑定已给规则并执行，不能据此说已从demo推断正确。简单Source指令增强complement而进一步损害identity，不是普遍恢复。
平均标签/prototype已不够解释全部结果：single complement在新输入上插值1.00、外推.8828，全部这些gold未在demo标签集{2,7}出现；同一context改变Input且function差随Input反转。另一方面，不能把该部分成功推广到两种operator或所有Source：identity多数失败，完整未知函数执行gate未过，不直接进入word-provenance。

### POST-HOC错误签名（不改主读数）
每operator256个novel query全保留：mixed identity错149，其中130输出另一合法operator结果、19其它值；single identity错98，全部输出complement结果。加Source指令后mixed identity188错，其中180另一operator。single complement241/256正确。提示更值得追的是**function-level偏好/参数推断与应用的区分**，不是Source均值或仅Label词出现次数。先检验operator-ID判断、函数描述顺序与Source-before-Input，再判断是否真“知道函数却不用”；当前没有该内部证据。
只有发现材料，未做独立确认/正式科研校对；Source direction辅助见analysis，不以方向取代函数执行。没有C##升级。
