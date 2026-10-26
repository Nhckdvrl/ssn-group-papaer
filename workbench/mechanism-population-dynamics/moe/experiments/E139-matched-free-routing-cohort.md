# E139：自由路由的配对三学生对照（2026-10-26）

- **状态：** DONE；训练、全部读数、三份独立审计完整；原预登记与技术失败记录保持。
- **类型：** PILOT / REPRO；补齐E138缺失条件，不是优化恢复分数。
- **对应：** P26：固定分配组三学生较一致，尚不能将一致性归因于额外路由信息；承接P25/C07的问题，主张等级暂不变。
- **问题（一句话）：** 同样的总函数目标与预算下，提供并冻结teacher分配，是否比自由联合学习更稳定地确定跨初始化的实际计算分解？

## 设置：配对初值与固定预算
- 自由组复用已观察E135 seed1，只新增seed0、seed2；固定组复用E138 seed0/2与E136 seed1。两个组都包含已观察pilot，不称全前瞻样本，不筛选/替换seed。
- 新自由学生沿原TensorMoE构造器/init_std=.02，保留随机gate并训练全部参数。逐seed证明expert初值与固定组完全相同；seed1完整构造器重建须等于原E135初值，不使用训练过的expert。不修改旧源/权重/结果/预算。
- 同E135 cache manifest SHA `2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43`：8,388,608训练H/Y位置、四个固定seed135 epoch排列、4096更新/33,554,432位置曝光，held32×16×512。原生OLMoE L9 prefix/downstream冻结，64×1024/top8/no-renorm。
- 原E135固定train-energy归一MSE+.01LB+.001z，AdamW(.9,.95),eps1e-8,wd.1,clip1,peakLR.0003,10% warmup/cosine。固定4096终点；无中途最佳选择、拟合准入线或LR/gain/aux网格。
- **混杂审计：** 缓存、目标、expert初值、更新/曝光配对；free/fixed改变的是完整协议：teacher路由信息、gate冻结及其aux/全局clip/weight-decay耦合。不能称单独边界机制的因果效应。自由组支持可不同，actual component同时含分配与expert内容，不叫纯内容。

## 读数：先总函数，再分解；不按结果决定资格
- 两组各三个学生，均按1/3有限cohort权重，teacher不作为第4学生。主群体Dolma held262144位置，次要群体原POS held512目标位置，使用既有native selected子batch/完整gate行/actual BF16乘积。
- native输出直接分解 `mean_s||Y_s-Y_T||² = ||mean_sY_s-Y_T||² + mean_s||Y_s-mean_sY_s||²`。总函数分解不依赖任何专家对齐，首先报告；共同偏差不能冒充跨学生变异。
- 自由编号需置换对齐：**唯一预定**在原training-only native Hcal8192上，以actual gated component `c_s,e(h)=w_s,e(h) f_s,e(h)`（当前不被选则0）的未中心化/未缩放平方距离作64×64 cal cost，Hungarian到本组**已观察seed1**。初值/终点各拟合一次，仅用cal；不使用teacher对应、不在多matcher中挑结果。
- 该预定seed1锚定置换不是三模型joint最优方差，不穷尽所有对应；初/终点各拟合不能用于声称坐标随训练保持。
- 固定组使用相同cal规则，并另保留E138已知identity读数。所有映射只是数据轴重标记，不物理重排模型权重/重新路由。cal矩阵、完整映射、支持覆盖/歧义保留；所有64专家保留，零覆盖记未定义/零贡献而不删列。
- held时将各模型实际selected分量按各自mask散射至共同query位置，未选为0；逐expert流式计算cohort component variance，FP64求和reference variance及cross-covariance。不得直接堆叠不同自由gate的on-row数组。native BF16 aggregate与FP32/FP64归约差单列；同vector²单位比较，不将rho/KL相除。
- 两组初值与固定终点都报告，不将对齐后差异声称为数学不可识别性。校准图样可能过拟合，held应用固定映射；区间不包含重新拟合映射的不确定性。
- 自由组三个终点相对teacher及三个学生对的自然Dolma/POS预测KL、NLL、top1全部报告。POS使用真FP32最后head，Dolma沿BF16 logits→FP32 logsoftmax，精度路径分开。固定组预测以SHA绑定复用E138。
- 辅助A只沿原自然drop实际贡献采新增seed0/2；seed1复用E135；如报告自由组A对应，只用上述cal component映射，不再cal-U/route新搜索。POS覆盖限制（teacher/fixed 42/51/52 target-on=0）完整保留，不称64个独立内容证据。
- 两组比较报告同一群体/单位下free−fixed的有限cohort点差，并用相同file/word重采样索引给paired输入区间；不拿两组CI重叠代替差值分析，不将输入区间当处理效应的seed总体不确定性。
- 原始逐序列/逐expert充分统计、输入/源码/权重SHA保存。Dolma file/POS word的1000次seed139 cluster bootstrap只是给定cohort的输入不确定性，不是初始化总体CI；三个重叠seed pair不当独立n。

## 阳性对照、噪声地板 + MIE、决策表（跑之前写）
- CPU已知答案：完全相同学生cohort variance=0；共同偏差不进入variance；相反分量扰动可抵消；纯descriptor已知置换应恢复零cost（重复分量允许多解）；不同support的零散射有手算对照。复制/数值floor沿E137/E138另报。
- 不设任意MIE/teacher恢复/相关阈值。连续报告两组总函数与分解的变异和区间，再判断哪种解释仍成立。
- 若自由组actual分解比固定组更变动，而总Y也更变动：分配/内容与函数共同变化，不能隔离出同函数分解自由度。
- 若两组总Y相近、自由组held分量变异及其抵消更大：支持提供分配信息约束可行近似的有限cohort证据，仍非严格同函数/唯一性或参数机制证明。
- 若两组相似：不将E138一致性归因于固定gate；总Y目标/共同架构可能已足够约束近似。若对齐只在cal有效，保留跨输入不稳定解释，不追加匹配网格。
- 任一结果均不自动开关线/升论文状态；单模型、单层、有限缓存/预算及pilot复用限制保留。
- **算力预算：** 新增总计≤1.5 GPU·时，独立E139 ledger；fvcrc21两新训练单卡并行，读数独立单卡，最多4卡/全探索≤8。复用原cache/Hcal/教师/已有固定组，不重建70GB H/Y。

## 结果（运行后追加；不修改以上预定读数）
- CPU完整/断点续跑已知答案及node21两个真实资产预检通过；seed0/2 expert初值SHA各自与对应E138完全一致，重建seed1完整state与E135原initial一致。训练器`e139_train.py` SHA `c118b4b73ec0d549b40a6a8317b01e44ce4765eb7be5372efbc5bddbacce600d`已冻结。
- 03:22:52 UTC在fvcrc21 GPU0/1实际启动seed0/2，PID875305/875306。原cache/固定组/预算未修改，新ledger `/tmp/xiang-moe-20261025/e139_budget.json`。E135 seed1及固定组是明确引用的旧运行，不算新增训练。

### 技术记录：首次设备初始化失败（未更新）
03:22:52 UTC两臂在`base.restore_rng`缺少CUDA RNG字段处退出，未写initial/checkpoint、未执行任何optimizer update；不是分数失败，不丢弃任何seed。原源c118b4…ce600d及失败proof保存在`~/mechpop_cache/e139_device_setup_failure_032252`，摘要`results/e139/device_setup_failure.json`。两次耗时合计1.008811秒仍计入原E139 ledger，不清零。只修CUDA状态初始化，保持同实验配置/初值，修正后重启原seed，使用新launch文件保留原记录。

- 修复后source SHA `93ac8504e21364ca94d6dd5ca18c22493850c41e74b7f0d1cfe12b398e3bcbac`，CPU mock覆盖CUDA新运行/CPU/resume，完整/断点自检及真实预检通过。03:26:50 UTC同GPU0/1重启PID876325/876326；初值/目标/超参不变，失败预算未清零，初版source保留。

### 完整训练终点与读数冻结（新held component分析前）
- 新自由seed0/2全部4096完整、9个预定MSE事件保留，held固定train-energy MSE=.17027721505543736/.1704162564373377；复用seed1(E135)=.1693501617。无seed筛选或续训。
- 读数源`e139_components.py` SHA `ce8e7029f707b735770a4915bbca4e53406033867bea4d4683a0b0c7fe7342b2`；`e139_readout.py` SHA `6ac6444b6b61dfc7b4380e8d4ad05c81286dbd6bfec9d6bac386060ff2e359e9`冻结，原训练SHA不变。CPU/非自逆置换/不同support零散射/方差双恒等式/paired输入CI/mapped-A已知答案及真实初始资产预检通过；完整终点CPU预检正在执行，随后才GPU读数。
- Hcal沿原8192整体reshape B16×512 native程序，cal cost存原始SSE（除8192即原定义MSE，同一最优置换）；未中心化/缩放。固定与自由A都由各自该cal映射CPU重标，fixed identity另保留。不物理重排权重，避免引入新的BF16平局效应。

### 完整结果与独立审计
- `results/e139/readout.json`全components/predictions/A complete、errors空。实际总预算1901.946335 GPU秒（含1.008811秒两次更新前设备失败；无失败seed筛选），旧ledger不变。
- Dolma teacher误差/共同bias/cohort variance（nativeTeacher能量归一）：free .176401906/.160690527/.015711380；fixed .162563352/.148547890/.014015462。总函数及拟合仍不同，不宣称同函数等价。
- 同vector²/位置单位componentVar free/fixed=.072467196/.031208956；FP64sumVar=.017869477/.015947143；cross=−.054597719/−.015261813。paired free−fixed componentVar=+.041258240 [输入CI .039905247,.043002846]，cross=−.039335906 [−.040786718,−.037973749]，sumVar=+.001922334 [.001551537,.002431933]；nativeVar差+.001929495。不是seed处理效应CI。
- POS同方向：componentVar .074797000/.036913420，sumVar .019476059/.017823811；paired component差+.037883580 [.029155292,.047470226]，sumVar差+.001652248 [.000975050,.002305398]。原群体/单位各自保持，不与Dolma归一量混合。
- 初态componentVar fixed .339771大于free .129446，因此最终关系不是简单较低初始variance floor；不把初终相减改为新主读数。fixed final两张cal map全64identity，initial18/19；free final1/0身份碰巧相同只是编号，不作语义证据。
- 自然Dolma三student pair KL free=.009105268/.009220522/.009063447，fixed原=.008730334/.008823162/.008845247；free teacher→student=.042595403/.042465585/.042789074。POS三pair=.008997134/.007485945/.010062931，完整NLL/top1/反向KL及区间均保留，不按较近者挑seed。
- 同cal-component映射下辅助A free三pair=.178186900/.191692996/.233825446，fixed=.484816185/.526466312/.499266457；full区间在summary。free seed0的expert11/57、seed2的expert6在POS held target-on=0，free seed1无zero-on；fixed seed0/1/2的42/51/52为0。全部64列保留。零覆盖列的原A为0，但row-center可继承组内共同均值；free/fixed A差包含support、门值、mask与映射因素，不能解释为纯expert-content差。
- 训练对象`training_independent_audit.json`逐值核对192专家初值/同gate与自由gate更新、六运行4096步的orders/LR/曝光一致；`components_independent_audit.json`从cost/raw重算全8条件点/1000CI/64表及4paired contrasts，并用pair-SSE/9与energy-minus-mean两条恒等式验证variance，max点差2.22e−15。`independent_audit.json`重算完整POS F32 logp与所有A/区间，max点差3.49e−9；Dolma重加stored token数据，不冒称重建未保存全词表。
- 主张：新增限定C09=L1，C07/C08保持；实际计算分解稳定性受协议影响，额外分量变动在和中大部抵消。只补E140同完整teacher-gate初态但trainable的单条件，区分初始组织与持续固定协议，不扩拟合/mapper网格。
