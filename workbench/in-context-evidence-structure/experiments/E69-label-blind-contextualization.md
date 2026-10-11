# E69：依赖历史上下文化，是否等于前缀已学会标签规则？（2026-10-10）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C15/C16、I04/P12；E68分歧：isolated prefix损害判断，但prefix的label-flip donor响应仅约2.4%。
- **问题：** 保留历史input/source/code与所有token位置，但令所有非label状态均无法读取任何最终label，该前缀状态能否仍支持native来源条件化？
- **为什么现在：** E68依赖history的结果不能自动解释成先前demo的“答案/规则计算”。label donor响应小；历史可能在构造表示/地址空间，或isolation只是分布移位。label-blind full history与no-history直接竞争；不拿necessity代替state内容。
- **近邻：** Cho shortcut（前demo可当query）、Few-Shot Examples Add Up（contextualization的QK贡献）、Bai模板汇聚、Li inert/transferrable状态；本实验只检验这个推理桥梁，不宣称历史上下文化或无标签表示学习从未被研究。
- **设置：** Qwen3-8B frozen bf16/eager，沿E67信息配对布局。32 contexts seed69001 animals/fruits yes/no；若主要比较≥MIE且控制有效，再64独立contexts seed169001 occupations/vehicles toxic/safe确认。原生D0Q0、D1Q1及一句指令、single参照。
  - **label-blind donor：** 全prefix 4D causal mask；所有receiver不能访问任何final-label列，唯一例外是label自身的self-loop（防止非法空行；不会被别的token读取）。因此其它非labeltoken的全层状态不可能通过早先meta token间接得到label信息；不只屏蔽label→prefix直接边。
  - **isolated donor：** 同E68，各demo仅header+本demo，保留原pos/RoPE。普通完整4Dmask=no-op。
  - D1原生recipient只替换demo prefix K/V/KV；加入source、Tag KV与source+Tag+prefix KV，native label-anchor KV与其它状态保持。对label-blind和isolated同site做配对。不删除原始label证据或给query正确答案。
  - **无label泄漏控制：** flip所有demo最终labels后重算label-blind donor，所有非label positions K/V逐位不变；hook检查所有被禁止label列attention质量0。first-prefix、full/native、fullswap与no-op再核对。
- **读数：** 各原生/干预的correct margin、accuracy、同input source排序；label-blind−native、isolated−native、label-blind−isolated配对差；rule-label盲化的残余量相对isolated损失（绝对分母>0.2nats才比例），所有raw CI同时报。context bootstrap4000。
- **阳性对照：** 全4Dmask/no-op≤0.10nats（预期0）；labelblind非label特征对flip最大绝对差0、禁读attention质量0；isolated精确禁止跨demo；native source规则有信号、single可识别、一句指令。bf16处理范围与此前float32缓存试验不混用。
- **噪声地板 + MIE：** matched-cache控制0；label-blind在prefix干预上相对native的margin损失≤isolated损失的20%且CI不跨50%，且accuracy/ranking损失95%CI不超过0.05，为“历史作用不需标签内容”的线索；label-blind−isolated≥0.2nats并且accuracy或ranking≥0.05、CI不跨0；否则只报告不充分。强负结果label-blind与isolated同幅受损，转向task-dependenthistory/关系不可部署。
- **混杂审计：** token/位置/当前raw输入/来源/code/标签证据匹配；全label列禁读避免contextual relay漏标签；允许其它native缓存在query被读，所以成功仅说明被换的指定状态不需label history，不能说整个分类无标签学习；mask改变正常context统计/归一化，label-blind保留非label结构能部分约束，不完全消除。多层高容量KV、非自然hybrids，失效不证明信息绝不存在。accuracy与排序必须随margin报。
- **决策表（跑之前写）：**
  - label-blind prefix保留、isolated损害 → 历史用于label-independent上下文化的具体线索；不能称已有正确task判决，下一步测试source-code关系与位置/归一化哪项决定作用。
  - label-blind与isolated均损害 → 不支持label-independent前缀；label-flip弱可能干预不充分，保留耦合/替代路径。
  - prefix单独保留但joint carriers失败 → 不推整体source路由不需label；检验分布式协作与其它位置。
  - 所有状态在新seed均不重要、或只margin变化 → E68有边界/精度/混合cache效应，不延伸新机制。
  - leakage/no-op失败 → VOID并修harness，不以科学结果解释。
- **算力预算：** pilot≤0.3GPU·时，confirmation≤0.5；实际待填。E68确认与本独立pilot分别单卡，不预铺后续。

## 结果
待运行。

### 编码前补充的联合接口（2026-10-10，未运行本卡）
另保留`all_nonlabel` KV移植：所有非final-label缓存来自blind/isolated donor，仅实际label-anchor KV保持native，检验是否只有prefix单点可保留，还是联合非label接口也可部署。仍不意味着整个分类不用label history（native标签状态可含历史），决策表相同。该组在任何本卡输出产生前定义。

### 结果（2026-10-10）
- 发现32/独立确认64完成；blind所有非label KV对规则label-flip**逐位相同**，禁读label列/isolated跨demo质量0；fullmask/self误差0，排除了token relay偷读labels。
- **确认prefix K：** blind−native margin+0.111[0.059,0.165]、accuracy+0.012[-0.008,0.031]、source排序+0.016[-0.016,0.047]，按预定5点界限保留读数；isolated−native source排序−0.086[-0.156,-0.016]。blind−isolated margin+0.395[0.305,0.489]、source排序+0.102[0.031,0.172]，符合主要MIE。
- **prefix KV范围更弱：** blind−native accuracy+0.012[-0.016,0.039]、source排序−0.008[-0.055,0.039]，排序CI轻微超5点等效界，不能正式称完全等价；blind−isolated source排序+0.148[0.070,0.227]。V-only排序−0.055[-0.117,0]，不笼统宣布所有state均不需labels。
- **all_nonlabel KV：** 保留native label-anchor KV，blind−native accuracy+0.086[0.039,0.129]，但source排序−0.047[-0.102,0.008]；blind−isolated source排序+0.383[0.320,0.445]。不能把accuracy涨分称来源binding变好，更不能声称整个模型无标签学习。
- **决策：** 具体prefix K的history作用不需要label内容；不支持先前标签判断复用是唯一原因。原生其它cached states/label仍可含历史，指定接口而非全模型结论。E70区别公共offset与逐样例地址变化，C18新增L1、完整理论未建立。
- 资产`results/e69/qwen3_{discovery,confirmation}/{run,analysis}.json`；实际122.55秒=0.034GPU·时。
