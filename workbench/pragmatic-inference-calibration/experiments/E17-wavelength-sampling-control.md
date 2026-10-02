# E17：Wavelength原任务的采样与受限概率对照（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 readout boundary
- **对应：** C02、P02；Wavelength人类分布不能直接当单模型解码不确定性。
- **问题（一句话）：** 同一原任务下，对21个答案序列归一的parent likelihood与实际回答采样是否支持相同的模型排序和human对齐？
- **设置：** 已固定revision的Qwen2.5-3B、Qwen3-4B、Qwen1.5-14B；原100clues/50pairs、原INSTRUCTION和chat template，thinking关闭；每题32seed(0–31)，各3,200共9,600回答。FP32，温度1、top_p1、top_k0、repeat_penalty1与raw likelihood一致；batch16、max128，不筛seed。完整generation defaults保存。
- **读数：** raw回答、唯一answer XML且数值在原0–100 step5 grid则valid，其余原样invalid；valid-conditional分布、均值/MAE与human，invalid比例及无条件MAE[lower,upper]，截断率。50pair cluster CI，32samples不当32独立模型；总体人群方差不等价于单模型uncertainty。比较E03/E15同model的parent受限分布。
- **阳性对照：** 原source SHA/prompt严格复用；XML解析明确唯一、范围/grid检查；生成prefix无special tokens与parent一致，原概率prefix断言已运行。现有FP32数值控制；14B待独立parity，不通过不解释概率比较。
- **噪声地板 + MIE：** sampling32次的有限样本误差显式bootstrap按pair；只有跨family/readout稳定的结论才支持后续，不把采样分布距本身当能力分数或新metric。
- **混杂审计：** forced候选归一分布与unrestricted generation不同支持；invalid不偷偷删除。goal/mode不改变，仍是prompted任务，不能冒称直接语用知识。128截断发生则保留并用原冻结边界降级，不事后挑正常seed。
- **决策表（跑之前写）：** A排序/对齐稳→削弱候选条件归一解释；B差主要由invalid/support或mean-vs-sample变化→先审readout，不解释人类不确定性；Cphenomenon/模型边界→记录完整分布再解释；D截断/协议失败→降级对应结论。
- **算力预算：** GPU5/6/7在E16小模型后，资源锁排在下载完成的E12前或后，无同卡重叠；三模型各单卡≤90GB，总≤1GPU·时，现有weights，无新API/训练。

## 结果
跑前冻结。不是为了占卡重复旧实验，而是检验领域结论所依赖的分布读数。
