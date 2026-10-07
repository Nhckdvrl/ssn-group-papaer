# E64：问答和角色表达读取修补后的哪个源位置？（2026-10-07）

- **状态：** RUNNING，科学运行前登记；生成器E431改为本线E64。
- **对应：** I03/I04、C09；来源E63完整结果，明确POST-HOC选题、前瞻干预。
- **问题：** E63同一个源词修补可以改变问答，却没有三族一致角色恢复。任务是在读取被修补的歧义词，还是读取修补经后续源计算传播出来的其他位置？一个whole-vector功能入口不能回答这个问题。
- **数据：** 完全固定E63原公开S/Q/gold、输入资格236QA/108源units、三族交集；MVRR19/NPZ9/NPS26 GP源，NPVP缺失不填零。不新造句，不重新审计可信源。保持每族第一1/4层（8/11/7）、同词donor、native frame、FP32/eager及cap256。
- **方法：** 为每个任务未知源，缓存所有block后的两套完整源轨迹：原BASE和E63自然cue局部修补后PAIR。随后任务完整prefix推理在每个block后覆写全部源位置，使其只能读取指定的固定源库。四个科学条件：BASE_BANK（全部原轨迹）；FULL_BANK（全部PAIR轨迹）；TARGET_BANK（仅原歧义词token使用PAIR轨迹，其余源用BASE）；CONTEXT_BANK（歧义词BASE，其余源PAIR）。两组源位置不重叠、并集为全部S，FULL是二者同时替换的阳性对照。不同用途/问句/答案都不能进入缓存。
- **解释边界：** TARGET的晚层轨迹也包含它原先受到的传播影响，不能叫纯早层原向量；CONTEXT包含全部其他词，不只消歧词。操作分解消费者访问的源位置中介，不能证明这些向量只编码语义、不能将两项效应相加或据此证明原GP拥有正确解析。冻结原源轨迹可能有数值差异，先通过原BASE/FULL完整原生重算复现再解释。
- **主读数：** 原QA正确率与p_correct（words/letters、两mapping、initial/final/all、samegold与全部）；新复述CORRECT_ROLES/GP_MISREADING/OTHER/cap/unknown。BASE_BANK为统计参考，FULL/TARGET/CONTEXT收益与原正确损失全部报告；QA×角色共同修复、角色已正确但QA错误分开。按E63源unit→相同S→词汇cluster平均，10k bootstrap95%CI，seed64；不筛baseline错误、cue成功、族/构式或最佳condition。
- **阳性对照、噪声地板：** 固定输入排序首4源及所有对应QA仪器：BASE_BANK对NATIVE_BASE、FULL_BANK对原E63单层PAIR，候选LP差<.001；16步greedy须相同。每层保存轨迹，source-only与native full-prefix所有源位置abs<.001或relativeL2<1e-5；混合轨迹的源输出必须与指定bank完全一致；非源输出不能被覆写。全部三族仪器通过后才运行科学条件。冻结条件中完整源不依赖任务，提前已逐字验证所有用途的源prefix相同。
- **决策表（跑之前写）：** FULL复现但TARGET独有→入口在歧义词的任务读取，追词关系/内容分解；CONTEXT独有→源后续位置介导，追后段绑定形成/更新；两组单独都弱但FULL强→互补/交互，需独立机制变量而非直接命名；QA与角色依赖不同组→用途组装的具体证据，设计新用途和自然构式迁移；全部弱/区间宽→该入口不足，回完整E53与任务条件R5线索，不继续局部层数grid。任何结果都不自动认定合格idea。
- **预算与数据质控：** 三族独立单卡0/1/2，各≤3GPU·h，与E53共两个pilot；已缓存HF模型全部离线，禁止直连。只审新output包，复用完全相同S/output已完成双盲标签，其余Step Plan step-5-preview、batch2≤5、4workers且共享总并发≤8，双遍独立顺序/第三遍裁决。完整审核前不读取部分语义比例。原始缓存、轨迹、配置、SHA和全部失败外置E64，小摘要进git。

- 依用户最新指导：NATIVE_BASE仅用于固定小仪器，不全量重复；保留四个能区分两条中介路径的科学条件，不追加控制链。

## 结果
尚未科学运行。C06–C09 L0，无合格idea。

- 三族小仪器已通过：BASE/FULL源库评分复现最大LP差均<.001，首4源16步greedy一致；混合源库各层精确覆写，非源位置不覆写。GPU映射启动失误的OOM日志保留，修复后尚无科学数据时重新校验，未改数据/干预/读数。已铺三族科学运行，原E53另一pilot持续。

- 分析在读取本实验科学效果前固定：额外直接报告TARGET_BANK−CONTEXT_BANK配对CI，用于区分两条路径；其余三个相对BASE的效应及两个用途完整保留。四条件合成panel通过，QA-only修复不混作共同角色修复，unknown仍为missing。不是增加模型控制条件。
