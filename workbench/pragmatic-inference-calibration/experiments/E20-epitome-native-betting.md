# E20：原SI下注任务的生成读数边界（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 original human-style task elicitation
- **对应：** C02、P02；不能把numeric conditional first-token当完整判断分布。
- **问题（一句话）：** E19的知识/条件推断结构，在原parent的完整下注式任务回答中是否依然出现，还是主要依赖受限首token读数？
- **设置：** 原OSF run_gpt.py的PROMPT_INTRO、warmup、format_dist_q结构静态提取，绝不执行provider代码；story与question从E19 released prompt分离，保留q_posterior版本（source代码另用q_prior，已记漂移）。40SI items、760 unique prior/post/knowledge prompts；仅完整原下注指令这一个protocol。每项温度0、max50（原src）、生成首换行视作原API stop；raw全部保留。causal模型用official chat（GPT2无template用raw；Flanencoder原text），OLMoE三stage统一SFT template。无thought、无新学习、无API。
- **读数：** 原正则的候选次序整数下注、范围0–100、sum100严格有效；原regx命中但sum不等100另列，不隐藏重新归一。有效条件的prior/posterior均值、knowledge与Δp2/3、invalid/truncated率；失败项下accuracy[lower,upper]，同item cluster CI。人类对照用E19校对过的原norm，不筛模型响应或human seed。
- **阳性对照：** PROMPT_INTRO AST literal与source逐字匹配；source-format串与E19 story/question逐项核对；no-API import。每shard item覆盖预分派、join恰760条/模型，无重复遗漏。positive-scoring regex用原warmup examples（已知prob vector）测试，不凭原文自由解释。tok bounds/numerical first-token可作工程控制但generation输出是本E主读数。
- **噪声地板 + MIE：** original deterministic decoding，无随机筛选；bootstrap按40原item，非760独立人群。计算重复prior只有一次。此E与E19同时改变完整下注格式、warmup与生成方式，**不能把差异因果归于sampling或chat单因素**；只检验结论对native elicitation的稳健边界。
- **混杂审计：** max50/首换行停可能导致invalid，按原协议计并保留raw；Flan的0多token由生成完整答案自然表达，不使用其E19失败的atomic readout。不得把格式invalid直接当语用能力错。fractional/不符合原整数回应不事后改parser以救分数。Heterogeneous base/instruct只作observational，stage必须matched。
- **决策表（跑之前写）：** A条件结构与E19一致且valid高→削弱受限首token解释但仍不是representation；B知识正常、推断结构只随readout变→保留elicitation边界，不claim latent changes；C大量invalid/截断→该readout不具可识别性，不能排名模型或补一次prompt救故事；D现象随规范/候选改变方向→回到条件结构，不保global criterion。
- **算力预算：** 原5模型在8卡独立：GPU0/1 Qwen2.5分items1–20/21–40；GPU2/3 Qwen3同分；GPU4/5 Qwen1.5-14B同分；GPU6 Flan；GPU7 GPT2等E17释放。GPU lock，后续stage在E12/E16后独立跑，下载等待不调用不完整模型。5×760=3,800完整生成，预算≤3GPU·时，无新下载。

## 结果
跑前冻结。只回答instrument/native任务边界，不把该读数新颖性或通用“知道vs用”当paper claim。

### 2026-10-03全量结果
七模型各760完成；Q25有效741、Q14有效705、OL-SFT有效40，其余模型有效0，失败均单列。此protocol沿用原parallel风格、published q_posterior；未复现原serial-history版本，不称所有generation路线精确parity。旧OL chat stage归因输入不一致隔离，E27纠正。
