# E96：共同标准的推断范围与功能传递（2026-10-11）

- **状态：** DONE-PILOT；256 direct与48 thinking完整，0未解析，28初始截断全部续完。
- **类型：** PILOT；围绕一个标准信息接口，不扫层/head/rank。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** 标准能被模型推断后，怎样成为当前来源新判断的约束，而不搬入他人的私人函数？
- **决策表（跑之前写）：** 下表为345d5cbf冻结的不同结果分支，不把文字接口等同原生算法。

## 已知什么，为什么现在做

E95固定2ctx thinking的共同标准16/16，A mixed19/32；B执行与标准推断、私人判断并非同一功能。不能据此说A预测中已形成同一个标准状态，因为Goal和计算不同。E96先检验一个最小功能接口，再决定是否值得做内部运输。

正文对照已在E95完成：Cho的构造性过滤→原生验证；MT-Bayes的prior与pooling竞争；Tang的task-conditioned共同空间；JIT的可解码/可迁移与Goal/时序范围。新核对Kim schema/binding §3–4.2：输出类别概率和具体top1不能直接当相同读数。这里标准问题统一food/service答案空间，功能传递另报yes/no完整profile。CrossICL已有分解/转换接口；本实验不是新方法贡献，也不把text mediation当原生电路。

## 两个有限的反事实

**范围。** 原Prompt明确三人同标准，所以“所有人关注哪个aspect”“A关注哪个aspect”“B关注哪个aspect”具有相同答案。后两问都无未来Review，使用完全相同的证据与food/service答案。再给A问题一句“所有人相同，可以借助任何人的充分例子推断A标准”的恢复指令。比较Source范围，不把A预测里输入后的问题混入这个测量。

**内容。** 从E95自己的完整thinking criterion回答取c_hat，不提供gold criterion或私人偏好、不筛primitive正确项。接收者预测四个新review：

- Full+self：原三人全证据，在demos之后、测试review之前加入c_hat标准句，偏好仍从自己的例子推断。
- Own+none：物理删除B/C，只保留A原始8例，无cue；criterion不可识别，mixed50%是信息权限上界，不作为失败证据。
- Own+self：A原始8例+c_hat，无B/C文字、缓存、标签或身份；标准问答从未看到未来review。
- Own+inverse：相同A证据，给相反标准；两个标准都与A同向例兼容，各自唯一确定个人函数。测criterion控制和偏好保留，不与完整三人上下文制造矛盾后强求模型服从。

Cue仅说“requested reviewer judges only food spiciness/service pace; infer personal preference from their examples”。没有p_A、p_B、额外训练样本、答案或金标准标签。两个receiver标准世界合法；cue词表达预训练已有的aspect意义，其有用性不等于发现新的语义构件。Cue在demos之后，因果模型中早先示例状态不能被未来cue重写；成功也仍兼容criterion-conditioned retrieval及给定规则执行，不直接宣布输入过滤。

## 冻结配置、读数与对照

- **设置：** E95原先固定的前2context（不是挑选成功context），完整p_A±×p_B±×c0/1世界；这是同材料机制探索，不是独立确认。原criterion16行全部使用，若未解析用unknown并保留行，不用gold代填。
- Qwen3.5-27B本地已核revision，openslime/vendor tf5.12.1、bf16/SDPA。Receiver direct256行；范围thinking48行，原medium greedy1024+所有初始截断续2048。两个阶段单卡独立执行，可分GPU，不展开依赖结果的新分支。
- **主读数：** Full+self相对E95同2ctx native的配对改善；Own+self的四格准确率、Own+inverse对cue定义函数的四格准确率；两者concordant私人偏好正确、mixed双向改变。Scope三个Goal统一标准准确率、p_B翻转不变性，与原all Scope16行一起报告。
- **次读数：** argmax/候选二选一/合法率，paired logit/答案改变，不除弱baseline gap；context bootstrap95% CI，n2局限明确。所有完整预测profile、未知/截断均保留。
- **阳性对照：** E95共同criterion16/16、B执行98.4%、完整规则oracle100%；本实验Own+self检验**仅标准**是否够，不冒用旧oracle证明这一点。
- **一句指令恢复：** Scope A恢复句；E95私人判断恢复句已跑且没有恢复，不新增多种prompt搜索。
- **噪声地板 + MIE：** first-batch无操作误差≤.001nats；Source物理缺席、A原始行一致、未来review未进入标准提取、全行唯一键。完整结构profile而非微小logit变化决定下一投资，无自动阈值判死。
- **混杂审计：** 报告Goal不同与额外推理计算；文本cue不证明默认latent部署；Own/Full不作只改变一个变量的归因，Own*self/inverse才是同证据下的标准内容对照。Source B/C地址及其当前query答案在Own接收者不存在；metric读取A例子仍是强替代。

## 决策表（跑之前写）

| 结果 | 实际更新 |
|---|---|
| all/B标准好，A标准弱，一句恢复改变 | 标准推断受Source范围/提示策略影响；进一步解释哪个证据被用于推断，不说默认已有标准而不部署 |
| 三个标准Goal都好，私人判断弱 | Source范围本身不足以解释差别；差别位于Goal/新输入/功能组合，尚不能分摊三者 |
| Own+self与inverse有正确完整profile，Full+self恢复 | 有一个仅传标准、保持私人偏好的功能接口；teacher无地址/无已解答案；再研究其内部信息形式 |
| Full+self好、Own+self弱 | 标准词不足以独立支持当前接收接口，不能说已经得到可复用独立程序；保留其它证据/执行解释 |
| Criterion内容对照都弱 | 不再猜新字段/alpha，回到规则信息的构造方式与任务执行；保留这项negative |

- **算力预算：** 两个独立单卡阶段，总≤.8 GPU·时，实际据实记录。
- **资产：** `scripts/e96_criterion_mediation.py`；`results/e96/qwen35_{direct,scopes}`。raw不进git，小audit/run/analysis与卡上传main。

## 结果（以后追加）

完整304行/unique键，自查全记录保留，.213 GPU·时，两个阶段exit0，无训练。正式主张/状态不变，未宣称顶会级贡献。

| 接收条件 | Mixed准确率 / cue函数正确率 | Concordant私人偏好 |
|---|---|---|
| 原E95 matched full native | 53.1% | 100% |
| Full+self criterion | 93.75%[87.5,100] | 100% |
| Own+none（criterion不可识别） | 50% | 100% |
| Own+self criterion | 87.5% | 100% |
| Own+inverse criterion | 按新cue函数87.5%；按旧世界12.5% | 100% |

Full+self的mixed配对改善40.6[31.3,50.0]个百分点。Own+self/inverse两种新输入的答案改变率75%，内容有向response2.96nats；每个条件整体cue函数正确60/64=93.75%，不宣称全部profile完美。没有提供p_A，也没有给Own接收者B/C的数据或身份；标准提取时未来review未出现。标准信息可以治理新的私人判断，而非只能借用teacher答案/地址。此处运输的是文本意义，不证明默认Actor Goal已有可部署的同一latent，也兼容标准条件化的A-example检索。

**范围解释被削弱：** A标准、B标准都16/16，与原all标准16/16相同；因此只用Source范围说明原Goal差别不足。A一句恢复反而13/16，三条错误完整保留，不能用提醒指令成功包装。标准问题没有测试review，私人判断有review且请求不同答案：仍需区分Goal语义、test review与答案格式，不直接归因单一stage。

下一步优先在相同数据上让**测试review对标准问题保持逻辑无关**，并比较命名标准与普通yes/no标准问题，提供已给定标准的yes/no阳性。结果将决定是否是Input干扰、答案代码/组合，或判断Goal调用了不同过程；结束Scope提醒与文字cue矩阵，不继续改十种提示。已有Source形成/读取因果事实不撤回，C16/C20仍L1。

结果`results/e96/qwen35_{direct,scopes}/{analysis,run,design_audit}.json`与`results/e96/completeness_audit.json`；原始输出/token IDs本地。n2、同材料探索、执行者自查的局限保留。
