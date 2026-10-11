# E103：从示例推断的规则，经哪种原生记忆约束新输入？（2026-10-11）

- **状态：** DONE-PILOT；256记录/128 unique、0未解析，函数主要跟KV；未发现C/P分属两记忆。
- **类型：** PILOT，内部memory counterfactual；不扫层、head、alpha，不训练修复。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** 来源地址有效之后，选择输入方面的criterion c与私人输出映射p，是由同一历史记忆提供，还是有可区分的功能依赖？

## 为什么现在做、最强近邻

E102 Source-field B→A主要指向recipient B，不能称携带donor规则；E91历史已改变自身证据的K/V。应该研究规则内容的形成/调用，而非加字段控制。当前强Qwen3.5-27B有16full-attention层KV与48linear层recurrent/conv状态，可以让同一个未来query面对两套不同函数的记忆。

直接借用Afendulev等《What Attention Recalls and Recurrence Controls》(arXiv2609.04434)的state-swap；正文§3/附录B/C/E已核对，它拥有方法和retrieval/control分离，且已测Qwen3.5-27B。**我们不声称首次混合两记忆。** 该文以显式dictionary与language/persona指令区分事实/响应模式。本pilot的c、p全由同一格式的私人demo推断，答案恒yes/no，未给c或p指令；“私人偏好”等于响应模式、“criterion”等于事实，这两种自然类比都未被证明。若结果仅整个函数依赖KV，它符合现有框架，增量有限，不继续architecture扫描。

## 冻结数据与内部操作

E93生成器，4未用于E94/E102的context，seed103001；两来源，同一criterion，不同偏好。Source A的8同向例，B的8四格例；只测试**完全可识别的B函数**，避免A原子/组合能力尚不稳定决定机制结果。此阶段是规则记忆的功能定位，不凭B结果宣称完成A对共同标准的组合机制。

四parent world：c_R∈{food,service}，B私人p_R±、A为−p_R。donor为c_D=1−c_R、p_D=−p_R；姓名、所有review、频率、格式与输出词表相同，仅demo labels变。完整world频率每Source4yes/4no；未来review措辞没在demos出现。

在未来Input出现前、同user turn的末尾Reviewer:B字段后切token；chat只render一次，prefix IDs必须是完整prompt的严格前缀，不分别render/重编码。prefix单batch/no padding计算完整cache；所有48recurrent与conv一并保存，不能只换attention KV便称donor历史不存在。随后输入recipient的原样后缀、新review、direct Answer:。

四条件：native R(K_R,R_R)、all-donor(K_D,R_D)、KV-donor(K_D,R_R)、Rec-donor(K_R,R_D)。全channel成组替换，不selected层。层类型/状态shape/metadata/seq length相同，clone pristine cache；每次新query前重新clone，不让上一个query进入历史。all-donor应数值复现相同未来input的native D，是完整函数运输/实现阳性。

每context4world×4query×4condition=64记录，共256。**实际只有128 unique (KV-world,Rec-world,query)状态输入**：all-donor与native有重复，两个cross条件在相反receiver world也有重复。重复是对照，不扩分母。context bootstrap10000、seed103001，n4仅探索；paired quartet比单query高匹配更重要。

## 功能预测，不预设两记忆分工

四输入使f_R=p_R x[c_R]、f_D=p_D x[c_D]、仅criterion变p_R x[c_D]、仅p变p_D x[c_R]互异。

| 候选依赖 | KV-donor预测 | Rec-donor预测 |
|---|---|---|
| 全函数主要由KV提供 | f_D | f_R |
| 全函数主要由Rec提供 | f_R | f_D |
| criterion取KV，private p取Rec | p_R x[c_D] | p_D x[c_R] |
| private p取KV，criterion取Rec | p_D x[c_R] | p_R x[c_D] |

还保留actual native R/D零效应或整函数参照、常数yes/no/解析失败和混合结果。C/P功能分工不自动等于存储独立abstract变量，cache也可存示例关系或retrieval policy；对整通道off-distribution组合的解释限定在这些因果依赖。

- **读数：** 全词表argmax、margin、valid；每种cross对四函数的匹配/完整quartet；两方向合在一起对四依赖模型的预测准确率（同时报唯一状态分母）；原生B/实际donor profile；全条件全context，不筛错误。
- **阳性对照：** 原生B应在全部新材料≥90%，不筛弱context；all-donor的logits须复现native D≤.001nats。self-all-copy及复制前后pristine cache指纹一致，来源字段名字/未来input不换。未过阳性只报接口结果，不能否定功能变量存在。
- **噪声地板 + MIE：** 同parent cache self-copy/all-donor≤.001nats；未交换通道精确不变。split与unsplit原生推理对第一context全部16parent/query比较全词表、label margin、argmax，完整报告；若argmax不一致或label margin误差>.01nats，停止主cross并检查cache执行路径，不升科学主张。这个跨算法数值界是预设harness诊断，不是自动科学收益判决。
- **carry校验：** 按近邻附录B，future multi-token处理时每个linear mixer必须实际收到非空initial_state，记录48层覆盖；vendor已支持cached chunk，将实际调用包装只做assert/计数、不改变返回。conv与recurrent一起换。
- **混杂：** 不把cache内部若有某信息称native单独variable；不把all-donor可执行当abstract rule独立存储；当前是B完整函数，不预先推广A共享标准。名字/label counts/任务提示不变，criterion与p同时相反用完整四profile区分，两个单query同答案不够。
- **决策表（跑之前写）：** 见下表。

| 结果 | 更新与后续 |
|---|---|
| 两cross出现互补C/P完整profile，远超actual-R/D/常数解释 | 找到私人规则的可区分功能内容；冻结operator到独立材料，随后检验A的共享criterion/私有映射，不先命名新模块 |
| 两cross主要跟同一个channel的完整函数 | 当前rule计算主要依赖此channel；符合已知memory框架的部分保留，解释A历史内容形成，不再补architecture/层矩阵 |
| 两方向均主要失效/混合 | 通道cooperation或joint-state兼容性未被四个分工模型解释；保留失败与joint positive，先看样例/读文献，不包成factorization |
| cache阳性/数值/carry失败 | 这是实现或功能接口瓶颈；保留记录、先修相同执行，不读为科学阴性 |

- **算力：** 原27B revision/openslime+vendor、float32/eager单节点两GPU，≤2 GPU·时。独立确认/SourceA thinking只在结果后另冻协议，不先启动。
- **资产：** `results/e103/qwen35_discovery/`；raw token/prompt/cache仅本地；小preflight/analysis/run/数值审计、源代码入git。
- **正式状态：** 无开关线、I04/ACTIVE不改，C16/C20仍L1。

### GPU前实现校验

新seed103001四context，strict prefix/suffix token边界与world间future后缀相同全部通过；实际16KV/48linear。合成C/P双通道模型能被analyzer正确识别，256记录/128唯一状态输入的分母一致；这是读数校验，不是模型证据。实际缓存必须同时验证conv/recurrent、pristine不变、48层future chunk消费非空initial_state，以及all-donor复现native D。代码/卡提交后才启动模型。

## 结果与科学更新

全部256记录、128 unique memory-query输入、0未解析，.12035 GPU·时；64 cross unique，重复对照不算额外独立样本。4个新context全部保留。Native B63/64＝98.44%[95.31,100]，阳性成立。all-donor全词表精确复现native D、self-copy与重复输入最大误差0，原cache指纹不变、未换通道精确保留，48linear层各260次实际消费恢复的initial_state。

第一context全部16query的split/unsplit原生输出argmax相同；全词表max差.01332nats、yes/no margin max差.00111，小于预设.01 margin界。报告不同执行路径的roundoff，不把全词表差默写为0。真正的state-swap/self-copy路径比较均0。

KV-donor61/64符合donor整函数、14/16完整quartet；Rec-donor61/64符合recipient整函数、14/16完整quartet。两方向合读的“整函数取KV”模型95.31%[90.63,100]（128记录/64 cross unique），Rec整函数51.56%，KV-c/Rec-p4.69%，KV-p/Rec-c48.44%。两种C/P分工模型没有任何完整四输入profile；个别cross仍有不同于KV native的答案，不声称Rec严格无作用。

**更新：** 这里从examples推断的私人分类函数，其criterion与输出极性没有显出对两种memory的互补依赖；主要功能内容经KV被使用。这个结果符合已知attention retrieval框架，不强行包装为新memory分工，也不能证明KV存完整abstract程序而不是示例关系。我们不追加cache层扫描。B完全可识别是定位材料，尚未证明A共享criterion的机制。

下一步回到核心：**模型在推断共同标准后，得到的只是可报告的知识，还是能与新的私人证据组合的内部状态？** 前者与后者在文本行为上都可由E99达到，内部功能尚未成立。借用已验证的state-swap，先验证显式criterion控制可经内部状态运输，再比较标准推断前/后的真实历史状态；不同结果必须分别支持“已有可用信息”“推断改变功能形态”或“未得到该接口”，不将每个结果写成compile理论。主张仍L1，正式状态不变。

结果：`results/e103/qwen35_discovery/{analysis,run,numeric_audit,carry_audit,completeness_audit}.json`；原始token/cache/behavior不进git。root完成逐行代数/分母/hash审计，不冒称独立L3校对。
