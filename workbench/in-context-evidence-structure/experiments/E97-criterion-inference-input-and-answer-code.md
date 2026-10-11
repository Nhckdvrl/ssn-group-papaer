# E97：判断Goal与标准Goal的差别来自测试输入还是答案形式？（2026-10-11）

- **状态：** DONE-PILOT；160行完整，无筛选/未解析；运行前提交 `9c99f582`。
- **类型：** PILOT；一次最小Goal比较，不启动新层/头矩阵。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** 同一来源的标准能被推断并用于新判断，为何直接私人判断仍弱？
- **决策表（跑之前写）：** 下表冻结；任何结果都不能自动证明默认过程已有标准而不用。

E95/E96已建立：A/B/all标准各16/16；自推断criterion使Full mixed53.1→93.75%，Own+self/inverse按cue87.5%且私人偏好保留。但标准询问没有test review、使用food/service；私人判断有review、使用yes/no。不能把这两个同时变化的因素跳过便宣布不同内部模块。

## 文献与可区分预测

JIT已有Goal/位置与task-state范围；Cho区分语义/任务verbalization、用unseen-label检验补充计算；TTR拥有predicate与token-bound routing分离。此次不抢这些宽主张。新定位是从多Source私人例子推断共同标准后，对相同标准的查询是否受逻辑无关的test input、或episode中私人判断标签的答案形式影响。若都不影响，Source范围/输入/输出代码不足以解释判断Goal差别，才有更明确的算法比较对象。

| 候选解释 | 关键不同预测 |
|---|---|
| test review诱导了错误标准 | 同一个标准命名问题，review加入后性能下降；标准本来与review无关 |
| yes/no答案形式或额外predicate/route组合影响 | 命名标准保持好，普通yes/no标准问题下降；给定标准的yes/no阳性可区分基本问答执行 |
| 私人判断Goal调用不同过程 | 有review与yes/no的标准问题仍好，但同材料私人判断仍弱；这是功能证据，下一步才做原生因果比较 |

Bool下降不自动归因output indexing：Goal形式、predicate计算、答案路由都可能。Bool/命名都好会削弱简单“输出词空间解释”，不能无论结果如何仍说支持旧I04。

## 设置与读数

- **设置：** 原固定2ctx、全p_A/p_B/c世界，未按成功项筛选；同材料探索，不升级独立确认。Qwen3.5-27B既有revision，openslime/vendor tf5.12.1、bf16/SDPA、medium greedy1024+初始截断全部续2048。
- 4组共160请求：name_with_review32（两个mixed review，仍只问A标准）；bool_no_review32（food与service两种predicate）；bool_with_review64；bool_given_criterion32（无review，加入模型在E95自身得到的criterion，不提供p_A）。E96 name_no_review16作为已有冻结参照，不重跑。不问review label，bool只是“是否按该aspect判断”，普通语言题。
- **读数：** 标准正确率/解析率；food与service predicate、两个review均齐报；p_A/p_B翻转对criterion回答的非应有影响；c翻转响应；context bootstrap95% CI，n2区间只作探索。
- **阳性对照：** 已有name_no_review16/16；bool_given_criterion验证给定标准后的predicate/yes-no执行。E95同材料私人判断19/32 mixed作为功能对照，不混为相同Goal的干预结果。
- **噪声地板 + MIE：** 同一数据与Goal gold静态核对；全部prompt/唯一键/原batch覆盖；teacher criterion来源完整记录；未知/3072截断保留。结构性模式决定下一投资，不以任一微小差异命名新机制。
- **一句指令恢复：** E96 A标准恢复句13/16已齐报；本次bool_given提供信息权限阳性，不能当相同信息的恢复指令。标准Goal能力阳性和完整私人函数oracle已有，不据单行为探针宣布能力缺失。
- **混杂审计：** 标准在两world唯一、review不提供新监督且与标准逻辑无关；两predicate真/假平衡；私人偏好双向；bool与命名是同一标准信息但操作不完全相同，给定阳性不排除所有组合瓶颈。文本/Goal差异是研究变量，尚非已定位的内部route。

## 决策表（跑之前写）

| 结果 | 更新 |
|---|---|
| name_with_review明显下降 | query本身改变标准推断；不把问题先锁成部署失败 |
| name稳定、bool弱、given-bool好 | narrowing为标准推断与predicate/code的组合；回读TTR并设计正交语义/答案反事实，不宣称token identity唯一原因 |
| given-bool也弱 | Bool接口不能作机制判据；保留执行问题，不追加复杂latent控制 |
| 所有标准Goal都好 | Source范围、review出现、yes/no答案空间均非充分解释；把重要对象定位到私人判断Goal的计算过程，停止这些格式控制 |

- **算力预算：** 三个单卡分片独立，完整原8行batch按索引分配，总≤1 GPU·时；不训练，全部结果保留。
- **资产：** `scripts/e97_goal_comparison.py`；`results/e97/qwen35_part{0,1,2}`，raw本地，小run/audit/analysis入git。

## 结果与决策

`results/e97/{analysis,completeness_audit}.json`：160/160正确，32 name+review、32 bool无review、64 bool+review、32 given-bool各全对。p_A/p_B翻转影响均0；c翻转与双世界都正确均100%。121初始截断全部续完，0仍截断/未知；总.778 GPU·时。n=2的context bootstrap为退化[100,100]，仅描述这批探索材料，不是总体能力置信界。

按冻结决策走最后一行：停止Source范围、review出现与yes/no形式控制。现在应解释私人判断怎样调用标准推断，而非继续要求旧模型失败。与E95私人mixed19/32形成有界功能差别；E97的`Unlabelled new review:`与E95的`Review:`并非逐token相同，不能声称整个query prefix已固定。共同header+demos在Goal前相同，不同Goal不会逆向改变这些已形成状态。

独立agent检查发现analyzer报告变量被子循环覆盖、JSON list与内存tuple比较报错；合并前修正这两项序列化/报告问题，科学引擎与读数未变。160唯一键、20原batch、gold/predicate/自推criterion均核对。主张仍L1；下一步只做一个无teacher缓存的内部功能运输接口。
