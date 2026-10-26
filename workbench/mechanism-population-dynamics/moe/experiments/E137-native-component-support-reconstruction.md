# E137：固定坐标的专家内容在native支持内外恢复了什么（2026-10-26）

- **状态：** DONE（实现/测量前）
- **类型：** MEASUREMENT；E136后提出的新前瞻测量，原U/A/预测读数和所有结论保留，不改主指标。
- **对应：** P24：给定teacher分配后A对应提高，但标量目标词效应/共享支持/总Y拟合不足以判断逐expert向量内容是否恢复；承接P23。
- **问题（一句话）：** 在已施加的同一expert坐标下，重学是否恢复了实际调用区域内的f_e(h)，而全输入差异主要在未调用区域；还是仍有较大的component误差在加权sum中抵消？

## 固定对象与两个输入群体
- **四条件：** 原生public teacher、其BF16原值精确复制到FP32存储的copy、E136 oracle_initial、oracle_final。全部eval/无梯度/只读，不新增训练、映射、gain、noise或共享中心化条件。
- Teacher/copy及两个oracle的gate在实际BF16 forward下相同；identity是预先给定的接口，不是本测量发现的语义对应。权重/源/teacher/cache哈希沿E135/136冻结资产，旧artifact不改。
- **主解释群体：** 恰好E124 plan held512 POS目标位置，与E136 U/A使用完全相同的IDs/mask/last/next_id/顺序。必要时仅重放teacher原生prefix取得完整序列L9 H；target H须与已存teacher Htarget精确核对。测native component时仍用完整原B16 padded-sequence程序的selected expert子batch，再只统计真实target rows，不能将短target-only GEMM叫bit-exact原native component。
- **函数目标群体：** E135固定Dolma held H/Y cache32×16×512=262144位置，沿原B16×512实际程序；不采新样本。两个群体分开报告，不将Dolma内容误差代替POS行为人口。
- 对每个h，以**当前teacher native top8**定义on/off；是当前路由支持内外，不声称off点在整个teacher预训练历史中从未用过，也不是模型输入文本OOD。

## 向量读数与真实算子
- **内容误差：** teacher与各条件expert f_e(h)的原输出向量误差，物理L9输出基底共享且prefix/downstream冻结；不拟合旋转/尺度。各expert/on/off保留count、teacher energy、误差SSE与每坐标MSE；除各自teacher energy的相对误差只作单位化，不能叫知识比例。
- on内容与**gated component**沿HF真实selected子batch/相同token-row顺序计算，actual weights先cast到hidden dtype、按native BF16乘积，不能用全H计算的f代称bit-exact selected component。可用forward hooks观察，不修改输出/参数。
- off内容在相同固定Htarget（POS与原U查询batch一致）或held H（Dolma）上显式查询，再按teacher mask取off点；记录同一条件全query-on与native-selected-on的GEMM形状误差floor。copy给相同函数的数值参照，不能把归约差偷偷算作内容差异。
- 对实际gated component差δ_e（以真实BF16乘积转换到FP32），记录每位置 `sum_e ||δ_e||²`、FP32参考 `||sum_e δ_e||²` 与二者差cross-term；同时累加同一δ_e的FP64 sum，只用于审计FP32归约误差并给FP64-reference cross-term，不改变模型前向；再**单独**记录实际native BF16 aggregate差及其与FP32 sum-delta参考的残差、teacher/component-sum→native floor。代数reference和native程序误差不混合，不把负cross-term自动称专家语义协作。
- 按on/off各自count归一化，不因off约7倍而直接比较总SSE。zero-count/zero-energy明确未定义，不丢expert、不用0填。所有64个expert均报告；全局聚合用明确的slot/位置权重。
- POS按word cluster、Dolma按file cluster的1000次seed137 paired bootstrap给全局指标评测区间（point为固定群体 pooled error/energy，不是seed CI）；逐expert给point/count/energy，不新增筛选。保留原始逐序列/逐expert充分统计，不存TB级向量。

## 阳性对照、预算与结果分支
- tiny已知答案：复制函数零差；两selected专家等门值的相反误差可有component SSE>0而sum误差0/cross-term负，验证权重/row index/归约；真实copy与native/reference floor完整报告，无科学分数准入线。
- **预算≤15 GPU分钟**：fvcrc21空闲单卡，独立E137 ledger，数据/模型在NVMe，stream perbatch；不改E135/136 source、cache、预算或权重。若资源耗尽明确incomplete，不挑已完成的有利条件；不加新训练/匹配/gain网格。
- on恢复而off差异保留→全输入潜在指纹的弱对应可能包含支持外成分；不证明所有自然职责相同。
- actual component差仍大、sum差相对较小→存在本固定输入/坐标下的误差抵消，单看A或总Y不能认定完整component内容恢复；保留剩余aggregate差，不宣称严格同函数自由度。
- on与aggregate差均保留→仍主要受未拟合/有限训练约束，不能从中作普遍不可识别性判断。向量接近也不等于独有语义知识或预测必要性。
- 所有分支都不自动升级/关闭方向；这是在共同坐标下区分恢复对象的一次内容测量，不是又一种挑高correlation的匹配。

## 结果（运行后追加）
- 四条件/两群体完整，独立预算47.84/900 GPU秒。`results/e137/components.json` complete/errors空；统计独立复算`independent_audit.json`全部点/CI/64expert表吻合；归档清单`archive_manifest.json`，durable `~/mechpop_cache/e137_support_components`，20文件不复制模型/cache。
- final Dolma on/off内容SSE/各自teacher能量=.726999618/1.101923986；actual component error=.259113863，native aggregate error=.162669766。相应POS=.704388365/1.077066740/.631683265/.384696922。两个on/off比率分母不同，不称知识比例。
- 同vector²单位Dolma每位置Σ分量误差=.272994770、FP64 sum误差=.185075344、cross=−.087919427 [−.093523,−.083495]；POS=.314921763/.229474425/−.085447339。copy误差0，F32/F64统计sum差约1e−19/native归约floor另列，不称语义协作。
- POS42/51/52 target-on=0，raw A恒0；row-center继承共同均值不算独立承担证据。旧全部分数/列保留。图`results/e137/figures/support_components.png`。
- 支持内内容也未完整恢复，支持外差异不足以解释全部内容差；负cross可能是不同学生共有的teacher偏差，故按原主问题继续E138跨学生有限cohort分解，不再盯单学生恢复。C07/C08等级不变。
