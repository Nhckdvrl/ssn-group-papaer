# Readers make targeted regressions to plausible errors in reanalysis of “noisy-channel garden-path” sentences（CoNLL2026，Outstanding Paper）

证据：正式主文§1–5与Limitations完整阅读，附录A与B例子阅读；C–E未深读。[官方论文](https://aclanthology.org/2026.conll-main.25/)。PDF17页/67192字符，外置reassessment-2026-10-07/clark2026-targeted-noisy-channel.pdf，SHA a812872f27c045b3182c10e8f11153ffa17f646a0060087bea971e6f2b29eae2。

1. **论文形态：** 构念扩大＋能区分解释的材料＋算法模型的质性预测，不是新LLM能力benchmark。
2. **压力：** 常见重读既可能reactivate已支持依赖，也可能reanalyse错误；自然语料中dependency与PMI共变，单个surprisal只预测何时惊讶，不预测回看哪里。传统合法GP只允许更换结构，忽略读者还可怀疑源词出错。
3. **改变的前提：** 把latent object从给定字符串的parse扩到可能的intended string/error actions，回溯的目标也应受后文与可修复错误的联合证据支配。
4. **idea来源（RECONSTRUCTED）：** Levy2008噪声通道→Gibson2013语义先验＋错误率→Clark2025增量SMC与rejuvenation→Wilcox2024高PMI回视/Christianson2024非选择重读的不同解释→设计同prefix、后文决定哪个早词可能错的实验。关键动作是使旧代理无法区别两个条件、新对象可以；不是给surprisal另起名字。
5. **近邻距离：** Levy2008粒子模型固定真实字符串、此处推断源词错误；Clark2025模型已有，新增人类回视的定位证据；Wilcox2024自然语料关联PMI，此处保持句法依赖而交叉语义配对；Christianson2024合法NPZ与本研究真实/可能词错误不是同一个对象，因此不同结果不直接互相否定。Li/Ettinger2023处理异常与ERP，该文增加回视目标的行为证据。
6. **材料与方法：** 36items×5conditions×2counterbalanced variants=360句，每句20人；200 Prolific英文母语者＋36填充。MoTR鼠标spotlight是眼动代理，并非真实眼动追踪。匹配prefix的kicked/licked与ball/lollipop交换suffix；其他条件Typo、Unrelated-GP、Late-Error。GPT2 noisy-channel SMC输出当前surprisal与全句后验错误概率；Bayesian hurdle-lognormal重读时长/logistic回视，词频/长度/位置/POS/当前surprisal协变量。重读时长是登记后追加读数，作者明示。排除低覆盖trial、异常gaze、填充错误判断>20%的participant；主文未报告最终全部排除计数，未核对附录。
7. **结果/强度：** Neighbor-GP×CriticalWord回视β .369 CrI[.242,.499]，Unrelated .279[.156,.406]；重读时长Neighbor .215[.125,.310]、Unrelated .101[.007,.196]。二者不同点估计不自动证明彼此差异CI分开；模型只作condition-level质性对应，未有模型之间out-of-sample预测优劣。晚异常回视不能证明读者最终纠正成特定句子；最终任务仅“有错/无错/不确定”。
8. **可借动作：** 重新确定修订对象；用同前缀后文分歧使纯incremental解释预测相同，实际候选修订解释预测不同；区分从哪里找证据与是否真的修复。
9. **对我们：** 合法GP自由表达错读未必只是在结构候选间错误选择，也可能隐式补词/生产错误推断。E68答案路由本身不决定这两种对象。优先先在原发表语义×结构材料测剩余失败（E69），再由完整自由输出看错误内容，不能直接用“错误越合理”宣布噪声通道机制。论文主旨是人类行为，未完整覆盖LLM源支持修订的因果关系；不据相近部分关线。
