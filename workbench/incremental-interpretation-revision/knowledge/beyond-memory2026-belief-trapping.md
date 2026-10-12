# Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States（2026）

**阅读身份：MAIN_VERIFIED_THIS_PASS（作者arXiv v1 HTML 2610.01415，2026-10-12；附录G被截断）。** 预印本。本卡属I07/评分线的近邻，用于说明该线的一般形式已被占。

## 要点
- 失败模式：belief由LLM自己生成，会出现互相冲突或无观测支持的更新（微波炉同时开和关）；以及**Belief Trapping**（belief一致但不推进目标）。
- 方法PoS：实体–状态–关系世界状态带来源/置信/证据；Belief Sentinel用同一backbone审计内部/外部一致性；健康分数H_t检测陷入并按Static/Cycle/Drift×E/A间隙诊断恢复。
- 基准：ALFWorld、LOCA-Bench、RCA-100、ClinDiag；Qwen3.7-Plus/Kimi-K3/GLM-5.3；相对最强基线最高+22.68/+7.53/+37.89/+11.31；去一致性验证ALF −14.93。代价5.06×token。**未与ABBEL对比。**

## 对本workbench
- “belief更新是否被观测支持”在agent线上已经有人把它做成在线审计组件；我们若继续I07只会是更小的版本。这是建议I07 PARKED的文献理由之一（另见ABBEL、Agent-BRACE、ReBel卡）。
- 可借的只有一个概念：把“解释是否被证据支持”与“解释是否推进任务”分开测，这与我们“替代依赖是否建立”与“任务答对”分开是同一逻辑。
