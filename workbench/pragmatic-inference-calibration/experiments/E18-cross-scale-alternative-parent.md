# E18：TACL2023跨scale原string predictor驻留（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 direct language continuation
- **对应：** C02、P02；备选表达可预测性与许可判断不是同一个测量对象。
- **问题（一句话）：** E13的within-scale相关是否延伸到parent原跨scale材料，现代模型是否改变原string predictor的跨数据边界？
- **设置：** 原expectations-over-alternatives commit50a7064290a841b81b2608524000b81a33ddc4b0；四human datasets，原300套test suites中每套预指定strong scalemate一项，VT16三template合并为scale；不修改字串、不生成数据、不删除outlier。原GPT2 SHA607a30d783dfa663caf39e06633721c8d4cfcd7e加已有Qwen2.5-3B/Qwen3-4B/Qwen1.5-14B固定SHA，bare continuation无chat/extra special token，FP32/TF32off。SyntaxGym原region拼接规则、surprisal单位从源码核对；只计region5，不含region6 EOS。不是concept/GloVe predictor复现。
- **读数：** 每strong region总logprob、token count、原公开GPT2强项surprisal逐项parity；各dataset human SI-rate与string surprisal的Pearson/Spearman和2000draw scale-cluster CI，VT16先按scale平均三template。公开人类原均值，不把mean当无歧义gold。原论文.complete-case分析另列，不事后挑能出现显著相关的scope。
- **阳性对照：** 原GPT2 published逐项数值，阈值maxabs surprisal delta<1e-3才称原测量复现；固定首末项batch1/8 logprob差<1e-3，失败隔离，不解释能力。目标token与region边界严格assert；raw/source与脚本SHA保留。
- **噪声地板 + MIE：** deterministic forward，CI按scale非token/template，无模型训练replicate；原300是template读数，非300独立scale。无预设提升MIE。
- **混杂审计：** 显式but-not对比是备选表达expectedness，不是模型自己是否推断；现代instruct bare输入失配不推出训练因果；different family/size混合不能当scale曲线。只reproduce原string主读数，concept主结论尚未复现。stratification、correlation不推因果，不以某单数据null关闭territory。
- **决策表（跑之前写）：** A原GPT2parity且现代维持弱跨scale关联→削弱availability单因素解释，仍需许可层证据；B现代跨dataset稳定增强→original字符串边界有改变，先审token length/lexical因素再检验是否与warrant相同；Cdataset不一致→记录原自然现象边界，不缩成单dataset故事；Dparity/数值失败→技术降级，不报告science。
- **算力预算：** GPU0/1/2用于三Qwen，GPU4用于原GPT2下载完成后；每卡独立300target，≤0.5GPU·时；GPT2约0.55GB外置。现有E15/E17卡不抢占，只有有问题的任务入队。

## 结果
跑前冻结。数据scope与published parity将逐项公开；本轮不声称新metric或alternative availability首次与SI关联。

### 执行前资产校对 / 续跑
输入准备发现6套没有同名canonical published TSV（multiword文件名被原shell截断，以及unkind/nasty缺文件）。初启动仅输入准备失败，未加载权重/产生预测；目录保留，修正后以-r2独立目录运行全部300套，published parity仅294套，不伪造缺失公开数据。没有观察模型结果后选择scope。LM Zoo官方transformers-base源码明确使用bits，原SyntaxGym将非空region用单空格拼接，包含逗号前空格；严格复用，不按排版美化。6个missing suite见summary。
