# E68：已缓存正常端点的缺失控制（2026-10-03）

> 关闭后保留的历史证据：2026-10-03用户决定终止；原始输出、数据和实验runner现已删除。文中local raw路径为历史定位，不能再逐条重算；最终汇总保留。代码可从关闭前Git快照51a578c1追溯。

- **状态：DONE；POST-HOC于E67 stage结果，先于本卡新控制推理。** C02/P02。
- **问题：** E28 Qwen3-8B/14B的format候选mass近1、顺序差近0，是否也能处理E67同一批明确affirm/deny控制？这是决定已有graded语境观察能否解释的缺失检查，不恢复OL阶段解释。
- **数据/设置：** 原E67固定32 q×affirm/deny×2order=128，仅控制；两原端点、原native common聊天入口、parent/format两读数，共512。原natural预测不重跑、不换提示、不加模型/语义分组，不筛控制/项目；每个q保留。
- **读数/gate：** 每端点format控制accuracy≥.9，mean mass≥.8，order median差≤.15。source/render/token/hash/FP32/padding差<.001；parent恢复对照。q前固定Claim、明确声明affirms/rejects、固定interpretation，控制不是对q事实真假或语用许可的新human标签。
- **阳性/噪声：** 与E67相同控制文本与expected labels；选项逆序概率归一，严格唯一key与256行/端点；EOS/generation不在本任务；两个token均须单token。支持控制只证明明确声明/否定和输出理解，不证明所有自然长篇理解。
- **决策：** A通过→可以描述已有模型对canonical人类语境变化的接受响应；不能由此证明stage或独立novelty。B不通过→端点缓存仍只作协议受限描述；不换更容易题或提示继续修。无论A/B均不添加新模型/大规模数据，有限重建交人判断。
- **算力：** 两独立单卡，每个最多15分钟=最多.5GPU·小时；E67已.3619，总预算15，新权重/API/训练0。

## 结果
512预测全部完成，.0203GPU·小时；8B/14B format为128/128与127/128准确、候选mass>.999999、median order差<2e−7；两模型输入hash相同，数值padding控制过关，决策A。parent控制为128/128与123/128，但mass分别仅.000091/.004705，不把它解释为正常数字输出协议。

明确支持“存在正常端点，可观察同一q的人类语境条件响应”；不支持全量自然材料都读懂、二分类许可、阶段机制或论文增量。OLMo2 gate没有被此结果替代。没有新增natural材料/模型/提示优化；有限重建至此收尾。

[完整结果](../results/E68-cached-endpoint-controls.json)。E67+E68新推理共.3822GPU·小时，0训练/API/权重下载。
