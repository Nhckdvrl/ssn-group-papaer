# E19：EPITOME原材料上的知识判断与语用使用（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 same-substrate stage + elicitation measurement
- **对应：** C02、P02；明确候选命题而非全局有无言外之意。
- **问题（一句话）：** 同一材料中，正确识别说话者是否知情，是否伴随正确的条件推断；这种关系在公开阶段与读数之间怎样改变？
- **设置：** OSF sn7gj（TACL2024 EPITOME）原SI已发布360行prompt（40items×3 some条件+6数字条件），原prior/speach/knowledge字符串逐字复用并与raw40模板及官方生成src校对；原IR64行16items×aware/unaware×explicit/implicit。SI760 unique prompts（重复prior只算一次）、IR64，合824prompt/condition。5个现有causal checkpoints GPT2、Qwen2.5-3B/Qwen3-4B/Qwen1.5-14B、FlanXL，加OLMoE Base/SFT/DPO，8models独立单卡。裸任务原restricted next-token；额外一条仅格式指令+official chat（Flan仅格式前缀），OLMoE统一SFT template，token输入哈希保留；thinking关，FP32/TF32off，无训练/闭源API。
- **读数：** 原选项raw条件概率；SI prior/posterior/knowledge，Δp2/Δp3按access×n、原publication百分比rounding下accuracy（不更改parent规则）；IR Yes-No logodds、同item aware/unaware差分，按cue分开；同item raw/format paired差，item-cluster2000 bootstrap seed0。knowledge正确≠语用用得正确；原some歧义单列，不把some条件当强gold。human原分布后续独立校对，不能直接当No/Yes规范标签。
- **阳性对照：** 原prompt与published359/360?行覆盖严格对齐为360（输入断言40×9）；原src的bet3_diff=post−prior，与论文Table2不一致，按src复现并记录。连续Δ与rounding都保留，不按漂亮结果选其一。固定每task每choice type首末batch1/8概率差<1e-3，token均单token并核对prefix+candidate token边界，失败隔离。8个model所有824原裸字串同一SHA；stage lexical tokenizer相同才比较。
- **噪声地板 + MIE：** 原规则依赖rounding/零边界，parent score只是复现；持续保留连续Δ，不把tiny sign shift当scientific finding。CI按40SI/16IR原item，条件/模型不是独立训练seed；不预设方向或升级阈值。
- **混杂审计：** 原知识check human删410trials而model不删，完整coverage审计后报告raw/parent-filter双scope；SI1 observed-vs-total some歧义已由作者指出；SI2 a2,n1虽然部分知情仍允许排除3，因此不全局赋ignorance=unlicensed。IR correct源码按critical_a、不是方法段typo。本轮不是SDT、不证明representation、不是首次knowledge-use separation；clean stage checkpoint有训练数据/算法共同差异。
- **决策表（跑之前写）：** A知识check与conditional infer同改善→支持该设定整合提升，仍非generic competence；B知识check正常但条件contrast异常→优先审概率/rounding/wording与readout，再跨SI/IR边界；C格式恢复→只能elicitation变化；Dsame family stage不单调或phenomenon反向→记录完整边界，不用平均分救criterion；E数值/输入失败→技术隔离。
- **算力预算：** GPU0–4已有5模型在E18/E15完成后；GPU5–7 stage下载+E12/E16完后自动续跑。fcntl单卡资源锁、无抢占/通信，总≤2GPU·时。下载完成/输入先核对，不因要占卡放低设计标准。

## 结果
跑前冻结。被prior拥有的“模型知道却用不上”不是新claim；只有现代/阶段条件结构改变已有结论才考虑升级。具体候选科学对象见FIELD_SYNTHESIS。

### GPU读数之前的canonical资产审计
所有初启动在输入准备阶段退出，未加载模型、无预测，不属观察后的筛题。公开IR raw虽64行/16items，但item7–16整套40条件缺critical_utterance；原src明确dropna后仅24行/6items。复用原eligibility，**当前unique读数=760SI+24IR=784/condition**。不自行补写缺失40条，不冒称16item完整复现；human比较仅匹配6个完整item。此问题影响跨现象结论的外推，不能靠缩小claim救故事。Released SI使用q_posterior而src引用q_prior，逐项确认两模板之一与release匹配后以发布prompt为准，审计保留版本数。
原echo协议对完整prompt+candidate分词；GPT2结尾双换行可由单token628重切为198/198。按每candidate完整字串取得prefix，断言所有candidate共享同一prefix且decode原字节完全一致；不把standalone prefix分词代替原echo。所有目标仍须一token，记录边界重切数及actual token-ID hash。

### 数值 / readout协议门槛（非scientific结果）
FlanXL的原答案0不是单token；原定atomic-choice readout不能覆盖它，E19该branch在binding gate退出，保留失败，不能据此排名能力。暂不为凑8个model更换该模型读数。GPT2 left-padding需要显式累积position_ids，首次batch1/8门槛失败、未产生主预测；修复绝对位置后另存-r3，不使用失败门槛的结果。Qwen三模型同一门槛均通过，无需重跑。这是输入/数值工程错误审计，不以某一模型结果修改评价对象。
