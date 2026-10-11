# E102：来源字段交换是在重定位证据，还是携带学到的规则？（2026-10-11）

- **状态：** PLANNED；在GPU科学行产生前冻结设计与源码。
- **类型：** PILOT；已有功能接口的机制分叉，不继续扩大行为任务。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** 输入前的来源条件信号使模型改用B函数时，函数来自被移植状态，还是recipient中B的示例？

## 为什么现在做

E101首次局部断言交换能改下一词，却未改变后续功能profile；不继续猜CoT事件。E94在1-based16层替换整个输入前Reviewer字段，B私人函数匹配28.1%→98.4%。但recipient仍有同一个B，地址与程序都解释这个阳性。现在让同名B在donor和recipient拥有不同规则，直接检验这座推理桥：整体交换成功≠规则内容运输。

Mixing Mechanisms §3.4通过让donor答案在recipient中缺席区分pointer与answer；这里不是重复实体回忆，而是让两边从不同demo标签推断的完整函数竞争。DAS §5.3说明因果“关系”甚至可分解为词身份数据结构，故不先用训练目标宣称criterion。来源绑定/任务向量/地址检索的宽认识由近邻占有，本pilot不把它们改名为新机制。

## 冻结设置

沿用E94全部4context、seed94001、原受控review/顺序/姓名与Qwen3.5-27B revision；不选材料。与E94完全相同的direct系统、chat模板、Answer:、float32/eager双GPU、batch4、use_cache=False。仅固定1-based16层，整个Reviewer字段3token，alpha1，未训练。输入前donor截断prefix包含完整示例与Reviewer字段，**不含未来review和任何query答案**。实际前缀token逐一对齐，不能从输入后状态叫query-agnostic。

recipient：A私人偏好p_A，B偏好−p_A，共同criterion c_R；A的8同向例只确定私人偏好，B四格例确定criterion。分别取得recipient A、B的原生四输入函数。

donor：名字、所有review、A labels、位置均与recipient相同；仅改变B demo labels得到四种(c_D,p_D)。提取donor请求B的字段输出，替换recipient请求A的同字段。跨来源交换与全量标签差异完整交叉：c_D∈{c_R,1−c_R}，p_D∈{−p_A,+p_A}；共每context64次交换、48native，4context448科学行。self-copy只作数值校验，不充当程序运输阳性。

主分叉是c_D=1−c_R且p_D=−p_A。对每组完整四输入x，四种预测互不相同：

| 解释 | 预测函数 |
|---|---|
| recipient A原任务 | p_A x[c_R] |
| 来源地址，读recipient B | −p_A x[c_R] |
| donor criterion与recipient私人映射组合 | p_A x[c_D] |
| donor B整套私人函数 | −p_A x[c_D] |

额外保留actual native A与B的profile，避免把模型原生错误当规范函数。“程序”可能改变后续检索，不自动意味着独立完整算法；当前实验只区分上述函数依赖。

## 读数与对照

- **读数：** 全词表argmax、yes/no logit margin与解析率；四预测逐query匹配和完整quartet匹配；对相同receiver改变donor c/p的答案变化、margin有向变化；recipient-native B/实际donor-native B预测的相似度；不以某个原匹配很高当运输。主分叉64行/16quartet。所有448行、未解析、所有context完整报告。context聚类bootstrap10000、seed102001，n4探索，不由小CI宣称普遍性。
- **阳性对照：** 同世界B→A字段交换应重现E94的B函数切换；recipient-native B与所有donor B函数预测（均在native B行覆盖）检验内容可执行。cross-world结果若仍有强B函数响应且不跟donor，是有效的地址型功能结果；若连同世界阳性消失，只报接口未复现，不宣布内容不存在。
- **噪声地板 + MIE：** self-copy全词表logit差≤.001nats、非字段差精确0，donor/receiver字段与完整prefix token一致；重复E94同世界地址条件的旧logits差报告，不靠bf16微扰作结论。主要比较完整函数，不把很小差异包装为criterion运输。
- **混杂：** recipient全历史保留；没有移植donor KV或hybrid recurrent缓存。位置、词、A示例不变，B labels是唯一world差别。四个donor世界在一些输入上答案相同，因此完整四输入profile是必要读数。Source-field可能含多个分量；地址占优不证明全模型没有criterion，也不排除轻微程序分量。此结果仅定位input前固定接口，与E91历史证据内容形成的结果相连，不等于整个ICL算法。
- **决策表（跑之前写）：** 见下表。

| 结果 | 实际认识更新与后续 |
|---|---|
| 阳性成立，主分叉接近recipient B，不随donor规则变化 | 这个已验证接口主要重定位recipient证据；不再把字段全复制当程序运输。回到已有E91内容载体解释选择后读取的函数，不加层/alpha矩阵。 |
| 主分叉随donor完整私人函数 | 来源状态含可跨证据world执行的函数信息候选；冻结到新context确认，再对donor c与p分量作因果对齐，检验是否仅criterion或signed program。 |
| 主分叉随donor criterion×recipient p_A | 找到可与recipient私人信息组合的功能状态；独立确认并追形成/调用，避免重做文字标准方法。 |
| donor/recipient预测混合或阳性不足 | 定量报告混合/接口范围，核对最强已有解释；不选成功样本、不自动添实验。 |

- **算力：** 单节点两卡、≤2 GPU·时。其它卡不为填满而启动依赖分支。
- **资产：** `results/e102/qwen35_discovery/`，原始prompt/activation/behavior本地；小design/preflight/analysis/run与源码入git。
- **状态边界：** I04和正式ACTIVE不改；无主张升级。

## 定位（先于运行）

最直接近邻：Cho 2025普通检索电路、Mixing 2026 pointer vs answer、JIT功能性任务状态、Hong类型校正运输、DAS关系vs词身份。它们拥有一般方法/概念；本实验增量是**已从示例推断的来源函数与接收者可检索示例分离**，是机制辨别证据而非已完成新理论。venue corpus nearest查询已执行，返回多为领域词命中，未找到精确题目；不能以此宣称无近邻，人工正文核对继续。

**运行前最近邻补核：** Steele等《One mechanism for many mental spaces》(arXiv2607.10248)正文§4.2/4.6/4.7已读：shared router/value slot、报告与规则使用可分离由其直接研究；与E101词/判断区别近，不能叫首次发现。其颜色属性由文本断言、sorting rule明确给出；本实验固定的是从多来源示例推断的函数。这个设置差异不是自动novelty，结果若仅确认地址，价值在为后续规则内容形成解释提供可用的机制约束，不独立宣称新理论。

**GPU前分母校正：** 为覆盖全部donor私人偏好世界，native B从16扩为32，加native A16，每context48 native+64interchange=112；总448。主分叉仍64行/16quartet。此纠正在任何科学结果之前，不删重复/困难world。CPU合成地址模型验证analyzer四profile判别通过。
