# E67：同一候选含义的语境响应与全局阶段变化（2026-10-03）

- **状态：DONE。** 本卡冻结于新推理与阶段分析之前；E66覆盖/文本差异、E27旧OLMoE位置伪影已知。
- **对象：C02/P02，有限可行性检验。** 不预设能力下降、criterion shift或论文贡献。
- **问题：** SFT→DPO对同一q的baseline/cancel接受变化能否由全局响应映射预测？额外条件响应是否随原人类证据强度变化，并能在未拟合来源上预测？
- **数据：** 271 canonical全保留；primary是E66按文本匹配预定的243项，271为差异敏感性；不按human效果、model正确性或p值筛选。原1–7和per-worker z只作graded描述，不概率化/强制Hit/FPR。派生prior/negation/strengthen/irrelevant不入核心，没有human norm。
- **端点：** 仅新增与E59同对OLMo-2-1124-13B-SFT/DPO，common SFT tokenizer/template、相同prompt/token/FP32。Qwen3-8B/14B E28缓存作正常端点边界描述；E27旧OLMoE巨大位置依赖，不作为阶段主结论。不要求弱/Base全部接口可用。
- **输入/读数：** 原canonical prompt、两选项顺序、parent与一句`Reply with only 1 or 2.`恢复对照；原next-token候选p_true、总mass、global argmax。True/False判断不是内部belief。每order和预定算术平均分别分析，不用平均隐藏顺序效应。
- **控制：** E66每phenomenon8个q，seed20261003，共32个；显式affirm/deny×2order=128任务控制，非human norm。`The speaker explicitly affirms/rejects this claim`→判断`The speaker affirms the claim`，仅检查明确否定/指令理解。所有控制固定保留；每阶段format平均mass≥.8、控制accuracy≥.9、median baseline/cancel order差≤.15才允许主要条件解释；parent另报恢复。失败只报仪器不适用，不按item补筛。
- **来源/数值gate：** source formatter逐条匹配；同stage输入token hash；native/common backend完全一致；completion marker revision；单例/混合padding max概率差<.001；FP32/TF32 off；完整行数/唯一item/state/order/condition、依赖hash。任一失败中止，不能放宽阈值。
- **诊断模型：** 固定5fold来源整组：george/ict/indirect/jhu/some_all各整组，swb按conversation，wsj按article；seed20261003和1都保留。同来源/两condition共同留出。identity；global `sigmoid(a logit p_SFT+b)`，a∈[0,8], b∈[−20,20]；plus-cancel加`d I_cancel`；plus-human再加`e I_cancel × human_raw_delta`，d/e∈[−20,20]。固定1e−6 L2、CE拟合DPO软目标，不调参/增复杂特征。human delta作最后模型的外部诊断特征，不拟合human标签；不做全量fit后声称成功。format primary、parent恢复；平均及每order都fit。
- **读数：** OOF两条件MSE/KL/global对identity误差减少；加condition/human变化增益；取消差预测误差；model delta与human raw/z delta Spearman、source-cluster bootstrap；stage条件响应差及CI。四phenomena、全量敏感性均报。CI条件于固定fit/fold；human每格3–5且共享raters，不将相关当机制/因果。
- **阳性/噪声：** synthetic已知global映射OOF MSE<1e−7；解析/label reversal和归一化0容忍；delta≤.001仅数值边界。a/b/d/e不称内部变量；两个split不能筛。
- **决策：** A global解释≥80%误差、human项两split无稳定增益（<10%相对global MSE改善）→无证据需要语境特有阶段解释，不追重新归因。B human特征/残差两split两order均成立且控制过关→仅留待独立材料检验的结构；parent已拥有撤回/自然任务差异，不能直接升级novelty。C gate/order不成立→端点未识别，不为维持工作量继续换协议/模型/邻接任务。80%/10%为资源heuristic，非能力等价标准。
- **资源：** 两stage各4 item shards，八独立单卡，不训练/下载。本轮15GPU·小时上限，含加载/失败；每worker最多1.5小时，8workers最多12GPU·小时，超时中止保留partial。缓存/CPU额外0GPU。缺新norm只写确切缺口/20–30材料方案，不自动生成。

## 结果
八shard全部完成：2×(1084 natural+128 control)×2入口=4848预测，实际.3619GPU·小时。数值、source与stage输入hash全部通过；243文本匹配为primary，271全量仍报告。

| format端点 | 明确affirm/deny控制 | natural候选mass | median order差 | 综合gate |
|---|---:|---:|---:|---|
| OLMo2 SFT | 114/128（89.1%） | .926 | .259 | 失败 |
| OLMo2 DPO | 97/128（75.8%） | .969 | .147 | 失败 |

按预定C，**不解释阶段能力/criterion**。parent→format提升控制但未共同通过；没有删失败item、换阈值/提示或新模型来救。

来源外global映射在format/order平均中相对identity减少80.84%/80.80%预测误差；增加cancel字段无改善，额外human变化特征相对global改善1.95%/2.30%（相对加cancel模型为2.64%/3.06%，分母分开）。每order则63.6%/86.6%解释度，human特征在order1相对加cancel模型约6.0–6.7%改善、order2反而恶化，未出现跨order稳定结构。**这些是受限协议的诊断，不能绕过gate宣称A或能力不变。**

CPU r1把WSJ同article的`_1/_2`片段误当独立group；r2按预定“article整组”修复，unknown文章统一组，同片段所有条件不泄漏；r1保留本地、不能作为独立验证。primary为48 source groups。单source现象不输出退化为点估计的bootstrap CI；共享human rater的额外不确定性仍未计。

已有Qwen format normal响应由E68补控制核对；其natural取消变化8B −.2739、14B −.3446，human raw变化相关rho=.254/.282。只是graded响应观察，撤回/自然材料差异属parent已有对象，不自动novelty。无binary许可或stage结论。

[完整r4汇总](../results/E67-canonical-stage-summary.json)：r3加入POST-HOC UI敏感性，r4补齐原约定KL和相对global分母，未改变fit、split或原读数；旧输出都留本地。227无cue风险cohort，Qwen8B/14B取消响应−.2765/−.3624、human rho=.252/.253；stage global预测误差降低81.11%/81.13%，human相对global仅改善2.42%/3.37%，未改变受限结论。不继续协议修补、训练或邻接扩展；本轮未达到论文项目通过条件，提议人判断冻结，PROPOSED不擅改。
