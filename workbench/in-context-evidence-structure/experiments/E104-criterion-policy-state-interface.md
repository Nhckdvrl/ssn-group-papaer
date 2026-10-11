# E104：标准信息能否作为控制状态，与新的私人证据组合？（2026-10-11）

- **状态：** PLANNED；只启动显式控制的内部接口阳性，不预先运行标准推断矩阵。
- **类型：** PILOT，criterion-only functional transport。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** E103示例私人函数主要经KV使用；一个输入前标准指令的recurrent状态，能否只控制criterion，同时让新接收者从自己的KV证据决定私人映射？

## 主问题与为什么现在做

这一步不是继续给两种memory命名。下一轮真正想检验的是：从多来源推断出来的共同标准，是否能成为与新的私人证据组合的可用状态，而不只是能被说出的答案。E99文字链已确认，E101/E102的局部接口没有运输这种功能。先验证一个能携带相同功能信息的内部控制接口，再比较推断前/后，避免无阳性地解释阴性。

直接近邻：Afendulev等state-swap拥有fact/control方法；JIT拥有功能性任务状态，Hong拥有type-corrected interchange，Lepori拥有可表示/可使用区分；这些宽认识不重命名为ICES novelty。潜在增量仍在来源推断的criterion如何与另一人的私人mapping结合，当前未证实。

## 本卡实际运行的阶段A

4新context，E93生成器seed104001。只保留8个Source A同向例(+,+)/(−,−)，不含B、未含future review。Owner个人p_R±；Owner改名Dana，sender改名Alice，姓名不与Owner混同（phantom B未出现）。两人的review数据相同、私人labels可相反；两者4yes/4no始终平衡。

sender在例子后加入全局指令：For all upcoming review judgments, use only {food spiciness / service pace} as the evaluation aspect. Infer each reviewer's personal preference from that reviewer's own examples.

recipient没有criterion指令，只保留Dana自己的原生KV。分别把**全部48linear层的recurrent与conv状态**换成sender的状态；16attention层KV全部留recipient。sender私人p_T与recipient p_R全交叉。未来Source Dana字段和review整段才输入，使发送者Alice的来源地址不充当当前查询身份。不把Sender RawFacts在RNN的存在隐瞒为teacher完全缺席；只明确teacher attention KV未复制。

未来private query仍沿原E93 schema，数据定义同一reviewer按一个方面和私人偏好判断，不额外给c或p；没有把Teacher的最终答案或当前Input放进sender。prefix切在同user turn内、未来Reviewer字段之前；未来query使用原E93 private Goal，不增加含c的接收者指令；只render一次，token boundary严格对齐。RNN来自不同长度prefix，recipient KV长度决定未来position；该joint state是构造性干预，不保证自然分布。

条件/完整分母：Own baseline32；full-cue sender64；full-cue Owner64；Owner自己cued RNN→uncued Owner64（同名字功能参照）；sender Alice cued RNN→uncued Owner128（p_T×p_R×c×四输入）。总352记录。未来quad完整报告；某些同名/同p对照有重复，报告真实唯一state-query fingerprint，不把352都称独立样本。

## 预测与阳性

主目标p_R*x[c_T]；强替代p_T*x[c_T]（整sender函数）、Own baseline实际profile、常数yes/no或无效输出。sender从未看futureInput，不能用上一步属性/答案复制解释四输入正确函数；Teacher/std输出本阶段不是来自主动推断，不称native已学会可迁移criterion。

- **读数：** unconstrained argmax、yes/no margin、valid；same/opp private p的criterion match与完整quartet、sender-function match，跨c两world对相反mixed inputs的双向作用；Own c不可识别，baseline50%由平衡设计决定，不作能力缺失。
- **阳性对照：** 完整cued Sender/Owner函数应≥90%；同名字cued-RNN对uncued Owner检验整个接口；跨名字/相反私人p的主criterion-only transport至少约85%且四query结构一致才足以继续learned标准运输。阈值是资源判断heuristic，不自动科学判死。
- **噪声地板 + MIE：** self-copy cache路径logits≤.001，未交换KV精确不变、source cache指纹不变；48linear实际消费initial_state。给定cued prefix split与full第一context全16 parent/query对比，argmax须一致、label margin max≤.01；词表差完整报。绝不删除Actor不匹配/失败world。
- **混杂：** 功能criterion可改变检索metric而不是存完整abstract规则；不能凭这个构造接口宣布原生default已经形成criterion控制。不同Actor名字与长度是运输限制，不能事后挑同名或同p成功项。私人p从每Source原labels推断，任何复制sender偏好都必须作为反例报告。
- **决策表（跑之前写）：**

| 结果 | 更新 |
|---|---|
| 跨Actor且opposite p仍遵循recipient p×sender c | 已有可与私人证据组合的控制接口；另冻协议测试来源标准推断前/后，不把constructor当native机制发现 |
| 只有same p/actor有效，或跟sender整函数 | 该接口带Source-bound程序/依赖身份兼容，不能用来证明标准独立运输；不立刻跑learned标准全矩阵 |
| full cue阳性、RNN-only无criterion功能 | 标准指令在此任务仍需KV/其他路径；结束这个memory控制接口，不扫layer/alpha或放宽成功定义 |
| 数值/carry不通过 | 保留并修同样执行，不能当科学阴性 |

## 条件性下一步（未启动）

只有接口成立，才比较多Source真实标准推断前/后RNN对Own新Actor/private p的功能作用。先用E95匿名c-independent数据让Source grouping必要；p_T独立、Teacher no Input、Owner无teacher KV，目标仍p_R×c_T。报告Goal与commit-to-use Goal的c答案都应正确，但其功能状态是否不同不预设。不把任何结果都叫compile；必须另卡冻结Goal/样本/读数，再运行。

- **算力：** 原27B/openslime+vendor、float32/eager单节点两卡，≤2GPU·时；未训练，未扩模型。
- **资产：** `results/e104/qwen35_positive/`；raw/cache本地，小design/analysis/run入git。
- **状态边界：** I04/ACTIVE不改，C16/C20不升级。

### GPU前静态核对

352记录、4新context、所有prefix token与future suffix一致性通过。每次未来Source Dana字段在swap之后才出现，不继承sender当前查询身份。统计唯一输入分别用真实KV tensor与Rec/conv tensor的SHA加实际future token IDs，不用原cache全hash伪增加unique。主阳性含p_T相反于p_R，不挑same p成功项；推断前/后阶段尚未启动。
