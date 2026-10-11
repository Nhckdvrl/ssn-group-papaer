# E112：来源条件化时序不同，证据形成机制是否相同？（2026-10-11）

- **状态：** DONE-CONFIRMATION
- **类型：** REPRO / 机制解释的跨架构竞争
- **对应：** I04、P17、E109形成路径（拟C21）。
- **问题（一句话）：** E64中Qwen与Mistral在query来源处理时序不同，E109的namespace→历史答案K→本来源label形成解释能否跨二者成立？
- **设置：** fvcrc20本地Mistral-7B-v0.3 checkpoint（32层，架构config已核对；不称Instruct，revision尚未核对，运行保存asset SHA）；同E109 MHS、safe/toxic vspass/flag、16新context seed112001，FP32/eager。source edge方法仅移植架构接口，全部层、全部A label receiver、全部B答案/完整prelabel定义不变；没有先搜索Mistral的最佳头/层。
- **读数：** 与E109相同signed/absolute B-rule影响，source消息族与K/V对照全部保留；冻结系数1 namespace/raw和rule双差分重建，全5预测器；native/instruction同时报。每context 24条件×8query，3072评分。
- **阳性对照：** full-A cache重建far gate；同架构native edge self≤.001；token namespace单词长度与位置完全对齐，源cache指纹、32层真实消费计数；完整label界面阳性。
- **噪声地板 + MIE：** 全float32 matched GEMM；若原有历史效应/label接口弱，不把K/V阴性叫算法差异。若形成机制与query时序形成分离，明确其发生阶段；pilot清楚时再独立确认，不扫新model。
- **混杂审计：** 型号是已缓存本地base资产，按真实metadata标注；不把base/instruction差异归因模型大小。MHS是受控私人规则的输入池，不是真人标注。Source全query禁读B只隔离读取，不抹掉历史形成。参数、读取粒度、词表几何等架构差异保留，效应大小不直接比较比例。
- **决策表（跑之前写）：**

| 结果 | 更新 |
|---|---|
| label与B答案K形成路径保持，query时序仍不同 | 形成时的来源依赖与query来源处理时序可分；核心机制得到跨架构支持 |
| label强但K/答案路径不同 | 阶段结构可能共享，具体算法不同；保留差异，不找一组头强行同化 |
| 历史效应/label接口弱 | 当前材料无机制杠杆，不作Mistral缺陷或完美来源独立结论 |
| 数值/词表几何不通过 | 只修执行/保存失败，不改科学变量 |

- **算力预算：** ≤.5 GPU·时，远程独立单卡。**实际：** .076695 discovery＋.140210 confirmation＝.216906 GPU·时，fvcrc20 GPU0，未训练。

## 结果（运行后追加）

结果路径：`results/e112/mistral_{discovery,confirmation}/`。小型analysis/run/reconstruction/completeness审计入git；原始JSONL及checkpoint留共享资产，不入git。

### 资产与实际启动核对

确认base `mistralai/Mistral-7B-v0.3` revision `caa1feb0e54d415e2df31207e5f4e273e33509b1`：远程本地3权重SHA256逐个与shared HF snapshot的content-address blob相同，7份metadata也相同，见model_identity_audit.json；不是Instruct。前两次SSH被继承的identity agent阻塞，远端0GPU科学记录；用直接内网连接/IdentityAgent=none后实际启动。不得把连接等待算成GPU预算或丢失seed。preflight几何通过，现模型已加载、首样本self/数值通过。

### Discovery结果与确认冻结

16contexts/3072评分：Mistral的A-only B-rule幅度.0905[.0648,.1176]，far label .0230；完整label减弱.0675[.0409,.0944]，B答案形成边K-only .0650[.0397,.0929]，KV .0582[.0304,.0860]；B prelabel KV −.00029[−.00183,.00130]。绝对规模较Qwen小，但同一预定形成路径有杠杆，不搜索Mistral head/层。self0、numeric1.91e−6、.0767 GPU·时。

32新contexts seed112101同脚本/条件确认；实际revision由额外asset SHA审计明确，run原字段unverified保留并链接审计。E64的query时序区别是其原任务结论，不能说本项已重测当前任务的query时序。

### Confirmation结果：形成路径在第二个模型家族成立

32/32 contexts、6144/6144评分完整保留。shared gate的B-rule幅度.105218，far label .043337；完整label接口减弱.061882[.033341,.094670]nats，历史答案K形成边.061117[.028437,.098590]、KV .058232[.029138,.090046]，完整B prelabel消息仅.000154[−.001259,.001612]。

按E109已冻结的系数1模型，逐query rule双差分重建：K r=.966321[.934481,.981498]、RMSE.264881[.211449,.314552]；KV r=.976745[.952333,.988507]、RMSE.225425[.174651,.274406]；零预测RMSE.864965。V r=.508、prelabel r=−.301，全部5种预测器保存于reconstruction_audit，不择优删报。这个结果支持相同的历史答案形成路径，无须重新选头/层；未证明其它路径不存在，也未重测E64时序。

完整A缓存重建阳性、self edge、源缓存完整性全部通过；numeric max1.91e−6、32层实际消费计数完整。作者bootstrap10000次seed109910；独立会话另用20000次seed20261011从原始记录复算，点估计一致，区间微差来自重采样。详见`results/e109/independent_review_2026-10-11.md`。

### §4混杂审计

| 项 | 核对 |
|---|---|
| 1 噪声 | FP32 matched-shape；self0，numeric1.91e−6，主要效应与重建误差均报告 |
| 2 工具 | full-A→far gate精确重建，32层干预真正消费，source fingerprint不变 |
| 3 采样 | 固定seed112001/112101；不按模型输出挑context，全部分母保留 |
| 4 读数 | 相同signed z及context-bootstrap；namespace raw与rule双差分都保存 |
| 5 指令 | native/instruction条件完整保留；不是能力缺失或无法恢复的主张 |
| 6 输入 | 与E109相同任务/条件定义；Mistral自身token几何预检通过，不强求跨架构字节级表示相同 |
| 7 种子 | discovery/confirmation无删种子；SSH失败在科学运行前、无GPU评分 |
| 8 算力 | 无训练/调参；固定全部层全部头；检验因果重建，不作等算力性能方法主张 |
| 9 重叠 | 新context而非MHS原始评论完全disjoint；可能预训练暴露不排除，规则是受控私有约定 |
| 10 多重比较 | 全5预测器、原定读数保留，未在Mistral找最佳层/头/alpha |
| 11 地板 | 效应比Qwen小，但主要区间大于0；argmax/准确率不代替logit效应 |
| 12 范围 | base Mistral-7B-v0.3，revision由真实SHA核对；只支持形成子图跨家族，不把E111关联V或query时序一起泛化 |
