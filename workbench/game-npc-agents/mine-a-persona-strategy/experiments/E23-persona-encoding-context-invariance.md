# E23：persona 编码与推理上下文的资格核验（2026-10-14）

- **状态：** DONE
- **类型：** REPRO / measurement gate（不是发现代码问题就宣称新颖性）。
- **对应：** C01 / P06；E17–E19后剩余形成机制问题。
- **问题（一句话）：** 同一原作者persona文本的编码是否独立于一起编码的其他文本；后续语义/utility干预能否建立在正确的原始编码复现上？
- **设置：** PCSP pin5420f7b研究compute_embeddings_500.py用Qwen3-Embedding-0.6B、fp16、max_length128、batch32、sort id、取out[:, -1]后L2归一；作者smoke_test则已有last_nonpad helper。先核官方tokenizer padding_side与原500.npy来源；本地官方模型，仅下载公开权重不调用推理API。按原全部500重算（fp16原批次/截长/无instruction）与公开.npy余弦/最大误差核验，先4个固定ID1/2/401/402检查成本。原文完全不变，分别单条、同短长度伙伴、同原source batch伙伴、固定最长原persona伙伴、固定max128 padding，重复原batch两次测数值地板；正确last_nonpad为控制，不改既有checkpoint或原缓存文件。所有编码结果另存cache。
- **读数：** token length、padding_side、原末列是否pad、源码pool与正确pool余弦、跨伙伴batch编码差/重复数值差、原公开.npy逐行余弦parity。如果原编码可复现，再以原同state/full和no_consist三个公开政策测action JSD/KL与φ角度；此阶段仅诊断数值，实际game utility需另卡原生episode，不把KL新颖性或独立人格有效性混入。
- **阳性对照：** 全500原批次重算cos≥.999/多数≥.9999才能称原资产复现；正确last_nonpad的same-text batch变化应接近重复浮点地板；原token化内容截长保持一致，其他伙伴不成为目标文本attention key。不能用另一个模型替代QwenEmbedding。
- **噪声地板 + MIE：** 重复原batch差为浮点地板；文本未变的跨batch编码/政策改变若只在数值地板内则无异常，不扩大。原artifact parity不足→先定位checkpoint/tokenizer/pooling/pad/版本，结果不归因persona。确有编码变化也先记工程/评价解释，再决定是否有跨角色真实utility研究价值。
- **混杂审计：** 模型revision未由作者明确pin，下载revision/hash记录；transforms/torch版本不同可能造成误差；源脚本paths写research/results而公开数组根results，两者不偷偷互换。正确pool不替换既有trained code，编码修复可能改变训练分布，所以不能直接宣称更好的policy。PCSP正文§V-E已有50 English designer NPC跨语言utility overlap与raw→φ几何；不冒领语言无关语义或简单文本稳健性。PHASE5 MeltingPot报告已经说retrieval head读不出存在的policy signal，也不冒领。
- **决策表（跑之前写）：** 编码稳定且原parity通过→进入形成机制/语义干预；编码不稳定且原parity通过→先审claim范围，再原生utility episode判断实质影响；parity失败→核资产不编结论；原源已明确覆盖→仅补审计。
- **算力预算：** 1GPU≤1小时，0.6B模型；现有fgvd复用、0付费API，07:00后项目≤8GPU；raw/权重不进git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

原公开500编码全部复现：余弦最小.9999883、均值.9999956。运行时tokenizer为right padding，480/500行原末列实际是padding位置；作者smoke_test与官方示例已有正确last-nonpad算法。同原文singleton/最长伙伴编码余弦均值.947355、最小.920235；正确pool跨batch均值.9999962、最小.9999905，重复原batch4个固定ID逐byte同一。六个公开policy在其各自原状态库中有不同幅度的动作分布变化，未建立Full/NoCons稳健性排序，也不是独立人格构念评价。

31.95秒单GPU、0API。模型revision97b0c614、权重SHA与原数组SHA见[E23结果](../results/E23_encoding_context_gate.json)，raw在cache/runs/e23_embedding_context。**执行偏差（POST-HOC记录）：** 实现先批量重算全部500，再做预定4个ID的成本/重复控制；未按卡先做4例。未更换指标或根据结果选ID。当前是公开资产的编码资格/部署审计；普通正确pool已解决此批次依赖，不计新科学增量。
