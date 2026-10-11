# E62：相同三元组的字段位置是否改变证据载体（2026-10-10）

- **状态：** DONE（2026-10-10；发现、预定独立确认及有界复现完成）
- **类型：** PILOT（E59/E61后，实验B的信息等价变体）
- **对应：** I04、C12/C13；E59位置分离；E61纯payload解释不足。
- **问题（一句话）：** 保持所有(x,source,label)信息与输出候选等同，把来源移到输出标签之后，会不会让映射证据从label anchor移到source token，并改变来源条件化行为？
- **为什么现在做：** 若“output是唯一可靠证据索引”是结构性原则，其解释应能面对信息完整但最后字段变化的情况。若有效carrier取决于三元组被完成的位置，则来源在标签之前/之后的相同信息排列会给出不同因果中介预测；不能只比较得分。
- **设置：** Qwen3-8B，frozen/bf16，无训练。两demo格式：before=`Item/Comment: x\nSource/Annotator: name\nLabel: y`，after=`Item/Comment: x\nLabel: y\nSource/Annotator: name`。所有label/source均single token；每字段token数量共享，总prefix长度逐位assert（位置本来是操纵变量）。同一context各格式使用相同输入/名字/标签/次序/query；两来源仍共用标签词yes/no或toxic/safe，答案空间恒为2。
  - discovery：64 synthetic animals/fruits seed62001 +48 E56真实train-pool seed62002。
  - confirmation：64 synthetic occupations/vehicles seed162001 +48真实test-pool seed162002。
  - 每批两个全局词表交叉，排除E58任务与词表同时改变。
  - Query恒用内容→来源→Label:；另报告来源→内容→Label:的query-order control，以及一句指令，防止因query模板匹配直接作能力判决。after中候选答案不得附带来源身份。
  - 每format词表下source-swap、label-flip作为完整反事实；交换source_name K（source donor）、label_anchor KV（source donor）、source_name KV（label donor）、label_anchor KV（label donor）；全部层移植，query不变。现场构建格式对应位置，不跨格式移植。
- **读数：** accuracy、margin与paired bootstrapCI；after−before accuracy；各位置的source/label反事实fraction（完整效应≤0.2nats不归一化），同一批context估计carrier fraction的after−before差。query-order/instruction作为解释限制，全报告。
- **阳性对照：** 完整source/label donor改变答案；no-op=base；全KV重建source donor≤0.10nats；独立确认词库/真实评论；token数匹配；来源与标签频率完整2×2。
- **噪声地板 + MIE：** repeat/no-op预期0；carrier转移fraction≥0.30且CI不跨0才作为有信息量的结构改变；accuracy≥0.05且CI不跨0才叫明显行为差。相同三元组信息等价不代表prompt pragmatics严格等价，需报告其限制。
- **混杂审计：** 任务/源信息/标签集合/候选数/长度/数据/种子配对控制；移动字段不增加训练信息；query布局、指令control；不挑层；未控制：字段最后位置与因果掩码、模板匹配共同变化，这是操纵变量但不能拆开解释；after样例中label不在最后，预训练格式熟悉度不同；cache干预可能hybrid失配。
- **决策表（跑之前写）：**
  - mapping中介从labelKV移到sourceKV且确认复现 → evidence carrier随信息完成位置变化；收窄output-only叙事，下一步寻找可预测的机制选择原则。
  - carrier不变、performance变化 → 优先格式/输出校准，不将涨分当新机制。
  - 两格式都labelKV主导且after退化 → 目前仍支持输出anchor路径，但负结果受query/template影响，不能主张一般不可能。
  - sourceKV与labelKV共同参与 → 多carrier/协作模型，不强行唯一锚点。
  - discovery与confirmation/两个词表不一致 → 明确结构边界，不扩大模型扫点。
- **算力预算：** ≤1GPU·时；**实际：** 0.219 GPU·时（单卡进程墙时折算，含加载，非积分利用率）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 字段后移没有提高预测。synthetic yes/no独立确认准确率after−before=−0.230[−0.285,−0.176]；query-source-first仍−0.086[−0.129,−0.043]。real确认变化较小，见完整表。
- synthetic确认的mapping-effect在source-KV上的比例提高：yes/no+0.242[0.193,0.294]、toxic/safe+0.270[0.210,0.338]；label-KV比例分别降0.446/0.435。真实文本的转移更弱，不支持普遍“最后字段成为唯一证据载体”。
- 结果：`results/e62/*/analysis.json`。按表报告多个carrier参与及格式边界，拒绝“同信息换位置即可修复”与唯一terminal-carrier理论；不将准确率差自动解释为新机制。
