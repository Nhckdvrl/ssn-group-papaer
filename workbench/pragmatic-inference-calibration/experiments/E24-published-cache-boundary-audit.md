# E24：原公开模型全表的读数边界审计（2026-10-03）

- **状态：** DONE
- **类型：** D1/D2 cached parent measurement；触发pilot明确POST-HOC
- **对应：** C02/P04，E21/E23 source parity；不把位置/精度当paper贡献
- **问题（一句话）：** 原公开19套open/no-thinking缓存中，order averaging后的recognition/cancellation数字有多少依赖接近决策边界的残差，还是跨顺序稳定的语义偏好？
- **设置：** 不新生成、不下载大模型；原repo当前commit全部19非thinking、非closed缓存，含parent表外Mistral并单列，public LFS按OID校验。不筛模型或items。canonical271、6states、2orders；source原Table6–8与code概率读数先重建。E23触发pilot：Qwen3-4B自然baseline26/50的|averageP-.5|≤.001，median order gap.99917，**此pilot为POST-HOC descriptive，不能作为预注册finding**。本E在读其余17缓存之前冻结全表分析。
- **读数：** 原recognition/cancel/joint三率；baseline与post两顺序单独P(True)、两order argmax语义一致比例、order gap；average距.5与cancel绝对delta≤.001/.01比例，连续量分布（不改原指标/不删小delta）。极限数值扰动±.001下原binary分数lower/upper数学界限，不是真实噪声模型或新science metric。按四phenomenon报告，模型间不混task/dtype/人群norm。
- **阳性对照：** Qwen3/Qwen2.5 cache3252 exact prompt keys全部对应；cache原分数重建source Table6–8，SHA/OID固定；不改parent probability。不稳定条件与稳定大模型正例同报告；把单顺序对齐与order-averaged accuracy区分。threshold敏感度与E23实测数值误差分开。
- **噪声地板 + MIE：** 无新随机生成；.001/.01是事前描述分辨率而非能力阈值，不按结果选最佳cut。CI2000 item bootstrap seed0；不是19个独立training replicate。
- **混杂审计：** order gap/半概率并不证明模型没知识；语义能力必须另readout。原parent的阈值定义仍保留；显著或漂亮数字先当precision/binding/格式可能性。cache无absolute support质量，不能用E21个别model mass推广19模型。cached tokenizer/weight版本未给，source artifact不等于可复现最新checkpoints。
- **决策表（跑之前写）：** A局部小模型边界→仪器限制，回到S1条件证据/真实stage；B多模型跨类均不稳→提高归因门槛，仍不能claimposition bias首次发现；C大模型稳健且human差距保留→保留parent结论，不用局部bug否定领域；D源table/cache不匹配→记录版本边界，未核对不解释。
- **算力预算：** CPU 19×3252缓存约65MB，有界4并发下载各≤60s，≤10min；GPU继续E21/E22与OLMoE队列。不为占GPU重复已有缓存，不用闭源API。

## 结果
跑前冻结。子agent继续禁用；本E是更完整驻留，不包装generic位置偏差或自创metric novelty。
