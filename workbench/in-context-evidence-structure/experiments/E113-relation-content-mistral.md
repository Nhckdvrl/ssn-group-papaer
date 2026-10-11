# E113：固定标签的关联形成路径能否跨模型成立？（2026-10-11）

- **状态：** PLANNED
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

- **算力预算：** ≤.35 GPU·时，独立单卡；实际待记。
- **定位与设计来源：** CTA §3.2用functional mapping donor区分token/type信息；E111已经继承这一方法，不能声称首次关联传播。此次补足中心功能内容的模型范围，不是新idea或能力缺陷证明。CoSToM强调内部干预要支持实际功能，保留私人约定阳性和新输入判断。

## 结果（运行后追加）

待运行。
