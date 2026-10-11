# E113：固定标签的关联形成路径能否跨模型成立？（2026-10-11）

- **状态：** DONE-CONFIRMATION
- **类型：** REPRO / 功能内容的跨家族确认
- **对应：** C22、I04、P17。
- **问题（一句话）：** E111固定输出身份的关联作用是否只是Qwen情绪任务的特例，Mistral能否通过同一历史答案形成边传递关联？
- **设置：** fvcrc20 Mistral-7B-v0.3 base，revision caa1feb0e54d415e2df31207e5f4e273e33509b1（E112资产核对），FP32/eager。E111完全相同任务、24条件、全部层/头/目标A label、B答案word+换行载体；仅架构接口适配，不重新选标签/层/头。discovery n16 seed113001、旧材料；confirmation n32 seed113101、E111冻结validation新词/句式，探索/确认文本交集核对。每context8query，3072/6144评分。
- **读数：** cross-polarity相对within-polarity的label接口及B答案KV形成边超额作用；K/KV/V全报，完整label关系重建及namespace系数1重建；native label argmax与single A两私人映射能力阳性。context-bootstrap10000、seed910，不筛好seed。
- **阳性对照：** 单来源两映射能力、full-A缓存→cross gate重建、B答案第0层K/V不变、所有token位置/Source/label相同、self edge及源cache指纹、32层真实消费。
- **噪声地板 + MIE：** FP32同形状GEMM，自交换≤.001。关联效应的配对CI区别于0用于判断有无杠杆，不把K/V某个winner当新构件；若single A私有映射<90%或全部label关联弱，不从答案边阴性归因机制缺失。
- **决策表（跑之前写）：**

| 结果 | 认识与下一动作 |
|---|---|
| single阳性、label关联与答案KV超额作用明确 | 固定相同源码/条件做32新词句确认；只提升已检验家族范围 |
| label关联明确但答案消息不能重建 | 载体功能不同或有其它路径；报告差异，不在Mistral找最佳头/词 |
| 原子能力/label接口弱 | 此材料不支持机制阴性，保留完整数据，不通过扩大模型/换词挽救 |
| 数值/几何不通过 | 无科学判断，只修执行并保存失败 |

- **算力预算：** ≤.35 GPU·时，独立单卡；实际.045238 discovery＋.085176 confirmation＝.130414 GPU·时。
- **定位与设计来源：** CTA §3.2用functional mapping donor区分token/type信息；E111已经继承这一方法，不能声称首次关联传播。此次补足中心功能内容的模型范围，不是新idea或能力缺陷证明。CoSToM强调内部干预要支持实际功能，保留私人约定阳性和新输入判断。

## 结果（运行后追加）

16context/3072评分完整完成，single A两私人方向阳性；静态B答案layer0 KV差0、self0、full-A重建0。label cross1.341/within.183，B答案KV cross.624/within.067，K cross.164、V .670；同样的部分关联路径在Mistral有明确杠杆。数值与Source指纹通过，未重新寻找层/标签。

按运行前第一分支，启动已预检/冻结的32新词句seed113101确认，源码/24条件/所有读数不变。确认完成前不升级C22；具体CI与GPU记录补入完整结果。

### 新材料确认完成

32/32 contexts、6144/6144评分，探索与确认评论交集0，正反私人约定各16ctx。single A正向98.44%[96.09,100]、反向95.31%[91.41,98.44]，不是能力阴性。

| 固定标签关联读数（nats） | 确认 |
|---|---:|
| A label cross−within超额幅度 | .980652[.770518,1.199140] |
| 答案KV形成边 cross−within超额幅度 | .404250[.313151,.499477] |
| cross答案KV−K幅度 | .362627[.277627,.454094] |
| cross答案KV−V幅度 | −.012217[−.044150,.018199] |

完整label关联的固定系数1重建：KV r=.913、RMSE.938，零预测1.449；V r=.885、RMSE.952；K r=.130、RMSE1.438。答案消息传递部分关联，V版本复现主要平均幅度；CI跨0不证明KV/V等价，仍不称完整程序。namespace读数全部保留在analysis，不只报正关联路径。

数值/self/full-A corner及static B第0层KV差全0，源cache指纹保持、32层实际调用完整。结果位于`results/e113/mistral_{discovery,confirmation}/{analysis,run,preflight,completeness_audit}.json`，材料交集审计为`results/e113/material_overlap_audit.json`。原始JSONL本地不入git。独立会话正在从原始记录复算，结果范围是两家族/同一明确情绪任务，不随C21的MHS自动泛化。

### 独立校对与实际序列化范围

`results/e114/independent_review_2026-10-11.md`已从原始文件先行复算，E113 123项与作者一致；Mistral192个world/namespace token流也在CPU独立重建通过。沿用E111的§4审计，追加系统范围、能力阳性98.44/95.31%、材料交集0及实际Mistral token化区别。C22扩展家族范围但仍为一个语义任务，不自动升L3。

Mistral SentencePiece的`enc('\n\n')`包含一个metaspace及两个newline，所以历史答案区域scope是word+3个分隔token，8条共32 token；Qwen对应16。分块流解码在Comment前/label后增加空格，不等于整段字面字符串编码。它在全部配对条件相同，label/Source/A原文位置控制成立；数值与native对照均指这一实际序列，不声称跨序列化格式已验证。不为此新增细控制矩阵。
