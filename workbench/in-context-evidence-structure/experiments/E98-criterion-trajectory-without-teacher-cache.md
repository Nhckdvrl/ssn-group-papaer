# E98：没有teacher证据地址时，内部状态传递标准还是完整私人函数？

- **状态：** DONE-PILOT；112行接口阳性未通过，384行主运输按冻结决策未运行。
- **对应：** I04 / C16 / C20 / P17。
- **研究问题：** 从多人私人示例推断的共同criterion，能否作为内部功能信息与接收者自己的偏好组合？

## 为什么现在做

E95匿名证据相同、Source分组决定共同标准；E96 criterion文字能支持Own-only新组合；E97标准Goal160/160，review和yes/no不是私人Goal差异的充分解释。下一步需要区分内部运输的内容，而不是再找哪个Source字段/层最强。

Hong的type-corrected interchange要求recipient输出关系解释donor内容；Mixing通过删解引用对象区分指针与内容；JIT已有输入前任务状态跨位置运输；Cho先建立构造性接口再研究原生形成。此方法本身不是novelty。具体待测增量是**从私人Source分组形成的信息能否按共同标准而非完整私人函数组合**。RawFull对照与prepared差别含额外推理/Goal/长度，不能单独声称某个专属推理模块。

## 冻结设计与接口

使用E95原前2context，E97全部32个bool_no_review回答（c×asked-aspect×donor p_A×p_B，全保留，未按成功挑选；实际全部正确）。同材料探索，不作新材料确认。未来评论均不进入donor。

接收者仅原A的8个同向示例，B/C姓名、原文、attention KV、linear recurrent/conv状态全部不存在：从Own文本重新forward，`past_key_values=None, use_cache=False`。接收者p_R与donor p_D独立完整交叉，四种新review齐全。

固定载体为输入前共同`Reviewer: A\nReview:`的最后token。对donor只运行到冒号，捕获64个decoder层**输入**的该token residual；receiver在同一token位置逐层替换，未来review/其它token照常重算。无训练、无拟合、无层/alpha筛选。它是单位置的64层外部状态轨迹，不是单一向量或原生瓶颈。

- Explicit donor：Own原文+仅criterion cue，不提供偏好；p_D完整交叉。相同载体。
- Prepared donor：重放E97原prompt与完整已生成token序列（含最终Bool回答），再接一个user turn，仅`Reviewer: A\nReview:`；最终答yes/no由asked-aspect与c交叉，不能等同criterion。
- RawFull donor：原完整三人示例直接接相同载体，无criterion询问/生成。
- Receiver：Own-only one-turn、相同载体后接四种review和私人label请求，direct Answer:读出。与原E96 prompt执行方式一致；prepared与raw多轮结构差异如实保留。

## 阶段、读数、阳性对照

1. **先做112行接口阳性：** Own baseline16，Own+explicit criterion文字32，explicit-donor运输64（2ctx×p_D2×p_R2×c2×query4）。Self-copy数值误差与非载体零修改、精确token前缀一并验证。
2. 若上述运输在p_D≠p_R的mixed上至少12/16正确、concordant至少14/16且self-copy≤1e-3 nats，运行prepared256与RawFull128；否则完整保留结果并结束接口，不扫新层/alpha。此阈值是接口可行性分支，不是科学价值/开关线判决。

**读数冻结：** 全词表argmax与目标域yes/no准确率齐报；margin z=logit(yes)-logit(no)。按context bootstrap报告、n2只探索。分别比较：criterion组合profile p_R*x_c，donor私人函数p_D*x_c，上一Bool常数答；相反私人偏好条件为关键区分。criterion翻转在mixed上的双向响应/两个world均正确；concordant保留recipient偏好；四query全profile正确率；prepared相同c不同asked-aspect的非应有答案变化；不以只有正logit变化称完整criterion执行。

**噪声地板 + MIE：** float32/eager双GPU，固定revision和源码SHA；同样输入self-copy误差≤1e-3，全非载体位置修改0；donor永不见未来review，接收者缓存为空；112/384全唯一键与期望参数枚举审计。接口没有阳性则不下内容不存在结论。已有E95一句分解指令不能恢复direct（51.6%），E96 explicit功能阳性保留，不把该人工状态接口当原生能力缺失。

## 决策表（跑之前写）

| 结果 | 实际更新 |
|---|---|
| explicit文字好，但内部接口阳性失败 | 此单载体轨迹不能可靠传递可组合标准；停止接口，不解释成标准不存在 |
| 只有p_D=p_R有效，相反偏好随donor函数 | 接口运输主要兼容完整私人函数，不能说criterion分解 |
| prepared随Bool答变化，不执行双向query profile | 更接近上一答/Goal状态污染，未建立标准功能运输 |
| prepared执行p_R*x_c，RawFull弱 | 经过标准推断的状态可组合使用；准备过程多个因素共变，下一步才研究原生形成/调用 |
| 两类donor都执行p_R*x_c | RawFull已经具有此接口可用的信息；不能把问题只写成标准推断没发生 |

## 算力与资产

本机两张空闲96GB卡，float32/eager、max_memory每卡64GiB，不跨节点训练；阶段1预计<0.5 GPU·时，全阶段上限估计2 GPU·时。其它空卡保留给独立材料/问题，不在接口阳性返回前铺后续矩阵。原素材JSONL及激活本地，源码/卡/小JSON进git。

- 源码：`scripts/e98_criterion_trajectory.py`（待实现）。
- 资产：`results/e98/qwen35_positive/`、`results/e98/qwen35_transfer/`。

## 完整结果与决定

`results/e98/qwen35_positive/{analysis,run,completeness_audit}.json`：文字criterion mixed14/16（87.5%）、concordant16/16；内部运输mixed16/32（50%），其中p_D≠p_R仅8/16，未达到冻结12/16接口分支，concordant仍16/16。c翻转答案改变0，两个world同时正确0；有向响应.00346[−.01110,.01803]nats，文字对照2.96078。n2仅探索。

112唯一键、float32 self-copy最大误差0、非载体修改0、源码SHA886f61b8…一致；.16550 GPU·时。独立agent逐行核对gold/参数/读数。POST-HOC辅助检查64运输答案均与Own基线相同，但平均绝对logit改变量.15131、最大.70229nats，说明干预影响计算，却没有传递所注册的标准功能；辅助统计不替代预定读数。

**决定：** 不启动prepared/RawFull 384行、不扫层/alpha。这个接口不能把文字标准的作用转移过去；尚未回答prepared信息的内容，也不证明criterion不存在、只存地址或所有内部运输失败。它没有给中心机制带来新的正解释，应诚实视为未建立的测量接口，而不是包装成新机制发现。E99独立确认按原计划继续。
