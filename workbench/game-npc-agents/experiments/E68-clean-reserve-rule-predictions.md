# E68：未用于本地模型探索的保留世界预测检验

- **状态：** RUNNING
- **类型：** CLAIM / 独立场景验证
- **对应：** C04/C05、I04/P12；用户最新授权。预测在模型接触reserve前冻结，不等E67结果选择条件。
- **问题（一句话）：** 使用/防卫/交付的规则效应、上下游交叉效应及非目标资产的persona合作差能否预测新原生世界？
- **设置：** 从原E50 reserve120世界按图SHA和canonical graph匹配全部既有LIGHT推理轨迹、manifest与旧E14/E22来源，排除已经用过的世界；全部剩余合格世界按原顺序纳入，不按任务/模型结果择优。精确N与排除清单在首个模型调用前锁定。这里未曝光仅指本研究本地探索，不声明模型预训练未见LIGHT。复用E63原生资格方式/中性请求，不调用Step生成新文本。
- **运行条件：** Gemma与Qwen3-32B，两traits全链一致，三个固定seed6801–6803；全部新世界goal-item跑generic/generic、asset/asset、negative/negative；wear/wield子集另跑asset/generic、generic/asset交叉；有合法自持other-item者另跑generic/generic非冲突合作。所有分支使用E67同一block_status普通反馈，world/菜单/8步终止不改。各上游输出在相应下游条件间直接共享；不按计划正确性过滤。
- **预注册预测：** (P1) generic相对asset提高原goal执行及首步goal；(P2) negative相对generic提高首次合法block并降低请求Give；(P3) asset相对generic增加真实请求Give，examine/speech分别作为动作去向，三者不相加冒称互斥；(P4) 固定上游asset时Exec generic恢复实体goal，固定上游generic时Exec asset削弱goal，交互允许存在；(P5) other-item generic下A−F真实Give与同轨迹both为正，同时分别报告goal差，不假定零代价。保留模型/任务异向，逐预测交代，不拼成全部必过bar。
- **读数：** 与E67同原生事件、首次/后续顺序与重复拒绝，特别区分首步block和episode内any block；合作只在同other-item窗口比P，不以跨mode总率推物品价值。三seed先图内平均、图簇CI；共享世界不乘模型当独立N。
- **阳性对照：** 每新图原goal/目标Give实体见证；other Give后原goal仍合法并实际可执行；源角色/可见请求者/当前合法物品不变；首调用前锁数据hash/模型/条件/种子。
- **噪声地板 + MIE：** 纳入全部可用clean reserve而非凑200；精确N与wear/wield/other分层见资格结果。区间与原计数呈现，无自动通过阈值；少量任务类型结果只描述。
- **混杂审计：** 只用同源benchmark但独立图，不伪称跨环境泛化；中性请求和框架与E63一致，不能包装真实玩家行为。已有reserve曾10图用于E57/E64，必须继续查旧来源；纯CPU资格不算行为曝光，未知记录则标未证清洁并排除。
- **决策表（跑之前写）：** 逐P检验，保留正负/反向。预测成立→范围内主张更强，核对主要竞争解释；只有部分成立→用保留集确定解释边界，不回头重写预测或重新挑reserve。错误反馈消除了行为分流则接受普通解释，不制造新世界维持结论。0追加seed/措辞网格。
- **算力预算：** N锁定后精确episode数写manifest；预计3–6GPUh，两模型独立单卡分片，现有环境缓存、全时≤8卡；0API/训练/patch。

## 首次推理前数据锁定
109图锁定，已曝光排除11图；扫描286个实际推理/白盒记录文件与相关源输入，E57/E64不同pair ID用canonical原图核对。首次简单ID扫描漏掉pair别名，未调用任何新模型；该不完整扫描保留在cache，最终图级结果覆盖它。

目标give58/wield25/wear16/eat9/drink1，41个wear/wield；60图有合法其他物品。两模型各2814完整episode（全部goal三规则1962＋41图两交叉492＋60图other generic360）。数据SHA `5bee70eeda144f3dd176ba1847c18d3a08b815e07e115a844368f2c19be7505b`；109/109原goal/目标Give、60/60其他Give后goal实际执行均通过。0模型调用。曝光与资格分别见`results/E68_reserve_exposure.json`和`E68_native_qualification.json`。所有预测保持运行前文本。


### 保留集任务类型的推理前解释限定
E68尚未产生模型输出时核对：58个原目标是Give，negative_only的笼统“不交出quest所需物品”可能直接与原Give任务冲突。P2的与E65同类、规则不禁止原使用动作的验证因此以已登记41 wear/wield分层呈现；109图主表与give/eat/drink所有分层照常保留，不删除场景或改变条件。Give层的原任务减少不能自动称防卫目标偏移；必须同时看第一合法block、实际请求Give与源目标Give的不同受领人。此处是已登记任务类型的逻辑范围说明，不依模型结果改预测。所有模型/种子/条件与原队列不变。


### 执行资源调整（未改变实验）
远端32B两worker冷权重读取1750秒仍无模型调用/episode；E67的32B本地两卡已释放，停止远端这两个进程组并保存启动日志/manifest，原条件与数据完整迁至fvcrc21 GPU2/3。两次中断启动按全时预约保守计0.97222GPUh，0输出/0种子被淘汰；见results/E68_interrupted_startups.json。Gemma继续fvcrc20。新旧运行路径和计费分别保留，不覆盖输出。
