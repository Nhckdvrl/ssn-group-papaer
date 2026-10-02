# E32：同源训练阶段的原alternative-expectation读数

- **状态：** DONE
- **对应：** C02/P02；S1动作种子，不创建待保的paper hypothesis
- **问题（一句话）：** stage与size对问答入口的变化之外，原人类scalar材料上的未说出备选表达expectedness怎样变化？
- **设置：** E18同原300SyntaxGym模板、四human datasets、strong-region5完整logprob、裸语言continuation/无chat无指令/不应用generation处理；固定源码与原target/EOS规则。8端点Qwen2.5-3B Base/Instruct、OLMoE Base/SFT/DPO、Qwen3-4B/8B/14B。已完成Q25Instruct/Q3-4B E18原run依config/input/code hash验证后复用，不为凑8重复；另6作业按独立GPU锁，原model SHA。
- **读数：** 原string predictor surprisal与各dataset human SI rates的Pearson/Spearman、scale cluster CI；同family paired raw surprisal Δ与corr Δ，所有template合并规则固定。不把correlation当criterion，不把该材料与ImplicatureX另一材料配对作mediation。
- **阳性对照：** E18原GPT2 294项published parity既已通过；完整原300源hash；同族未加special文本token IDs逐项核对。固定首末batch1/8总target logprob差<.001；失败隔离。读取公开human均值，不增加label。
- **噪声地板 + MIE：** 原300是templates非300独立scales，VT16同scale三template平均；paired CI按scale，seed0/2000；无training replicate、不以显著性选择dataset、no预设effect门槛。
- **混杂审计：** 此测量是语言备选expectedness，不是隐含意义被许可与否，不能证实knowledge/representation未变或推断policy因果改变。stage训练会影响语法/词汇/长度；group内target tokens保持并报告不加length-normalization主读数。大小跨training/data不是纯scale。E29极性错误不能自动归该predictor。
- **决策表（跑之前写）：** A stage源语言continuation也系统改变→削弱“仅问答入口漂移”的极端解释，仍需同材料证据作用比较；B原expectedness稳定而问答改变→保留elicitation/决策解释，不能直接证明latent知识不变；C各dataset方向不同→scalar类别边界，拒绝统一能力scalar；Dgate/hash失败→技术隔离。不会单凭任何结果形成paper claim，结果若只大模型更好则留baseline。
- **算力预算：** 6新单卡作业×300targets，≤1GPU时，复用已下载models；GPU0/1先跑OL Base/SFT，2/3 DPO/Q25Base等待E28，4/5新8B/14B等待E28/E31锁，无API/training/子agent。

## 结果
先卡后run；继承原E18完整source与已核验parser，新增stage矩阵外置runs/E32-*；不覆盖旧run。


## 完成与证据限度

6 fresh+2 hash校对复用均完成，原300target源码一致、同family完整input IDs/target长度一致。OL SFT−Base pvt21 surprisal+.36134[.12838,.58692]、DPO−SFT vt16+.12268[.04137,.20303]；Q25 Instruct−Base rx22 human correlation Δ−.06642[−.12322,−.01410]。其余均值/相关变化有多项CI含零；无跨材料统一方向，不跨数据作knowledge mediation。原string predictor仅备选文本预期，不是推断概率。结果：results/E32-stage-expectation-summary.json，数值/input parity文件同目录。

C01/C02仍L0；技术与原任务描述不升级为论文贡献。
