# E112：来源条件化时序不同，证据形成机制是否相同？（2026-10-11）

- **状态：** PLANNED
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

- **算力预算：** ≤.5 GPU·时，远程独立单卡。**实际：** 待记录。

## 结果（运行后追加）

待运行。raw资产/JSONL留远端或本地，不入git。
