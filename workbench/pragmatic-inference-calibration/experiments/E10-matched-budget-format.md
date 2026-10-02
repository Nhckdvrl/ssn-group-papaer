# E10：3B格式控制的同token预算核对（2026-10-02）

- **状态：** DONE
- **类型：** REPRO / confound control
- **对应：** P03、C01；E06不同budget的未决替代解释。
- **问题（一句话）：** Qwen2.5的format变化在与native相同max1024后是否保留？
- **设置：** Qwen/Qwen2.5-3B-Instruct revisionaa8e72537993ba99e69dfaafa59ed015b17504d1；四语言各300×seeds0/1/2，batch32，T=.5/top_p1/top_k0、BF16、native chat user+E06一句letter-only指令；仅将E06 max16改1024，与E02原生相同。记录继承generation_defaults，原结果不覆盖。
- **读数：** 三次采样全保留；同题平均correct与按item配对的format−native及95%CI；与E06逐条raw response匹配；invalid全按错误并提供全部invalid正确的上界、truncated率。不计算FPR。
- **阳性对照：** E08字母batch parity通过；1200源选项与oracle parser通过；Qwen3同预算format已完成、原Flan1,365选择匹配。检查完整900/语言。
- **噪声地板 + MIE：** 固定三seed全部，2000 draw item bootstrap seed0；不是population/model uncertainty。旧/新逐字相同时排除max_tokens预算替代解释（限这些输出），若不同不归能力而先核对EOS/batch RNG。
- **混杂审计：** 固定data/model/script/seed/tokenizer/chat/计算路径与同预算；指令改变任务要求、英语格式指令、choices为metalinguistic仍未消除。parser仍需盲校对，无gold参与提取。
- **决策表（跑之前写）：** A与E06全部一致 → max16不是该差异来源，保留elicitation与response-policy未知；B系统不同/截断 → 降级E06并以同预算readout推进；C故障/parity失败 → 保留原文件作技术失败，不讲故事；任意结果都不能推出pragmatic competence或criterion。
- **算力预算：** GPU3/5/6/7四语言独立、≤0.2GPU·时；与原14B四卡队列互不重叠。

## 结果
待完整后写；这是E06看到结果后提出的prospective confound experiment，并非原初预注册hypothesis。
