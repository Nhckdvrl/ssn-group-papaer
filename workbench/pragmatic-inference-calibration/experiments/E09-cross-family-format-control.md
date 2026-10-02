# E09：原Flan模型能否用一句格式要求恢复Multi原题读数（2026-10-02）

- **状态：** DONE
- **类型：** REPRO / instrument control
- **对应：** C01、P03；与E06形成第二family的读数校对，不是training-stage实验。
- **问题（一句话）：** 原生MCQ答案的可评分性与格式提示依赖是否只存在于Qwen聊天模型？
- **解释与设置：** A语言理解不支持gold；B理解可用但输出没有绑定字母；C指令改变选择本身。固定英文300原题、google/flan-t5-xl revision7d6315df2c2fb742f0f5b556879d730926ca9001、slow T5Tokenizer/float32（原Hu anchor已复现）。seq2seq原用户文本，无chat template；native与附加E06同一句letter-only指令，两条件均max_new_tokens=256、T=.5/top_p1/top_k0、seeds0/1/2、batch32；相同token预算，减轻E06截断混杂。不同architecture/语言预训练不能归训练阶段。
- **读数：** invalid/truncated、maxim240/literal60 accuracy及invalid导致的上下界；按item聚合三次采样、paired native/format分歧。解释性文本没有唯一letter仍标invalid，不从gold猜答案。
- **阳性对照：** Flan Hu1,365/1,365原公开选择匹配；Multi1,200 oracle/wrong roundtrip；记录T5答案字母tokenization、unknown token比率。输入/hash/seed全部保存。
- **噪声地板 + MIE：** 三次固定sampling与item bootstrap CI；300固定题不是总体语言能力，恢复格式只说明这套readout对指令敏感，不宣称恢复知识。
- **混杂审计：** 同一模型同题同token预算只动格式要求；encoder-decoder无chat是模型原定义，不能和Qwen不加限制做家族能力因果。至少逐项检查invalid与unk，不做FPR/SDT。
- **决策表（跑之前写）：** A invalid高而format恢复 → 该family的native生成不是可靠objective choice readout，保留parent协议与format控制；B invalid低但accuracy变化 → elicitation混杂，概率读数核对后解释；C两者均低分 → 不先解释能力，查T5输入长度/词表/原task；不确定 → 固定原文agent复核而非新prompt刷分。
- **算力预算：** GPU4单卡两条件各900回答，≤0.4GPU·时；当前用户八卡授权。实际待记录。

## 结果
运行前已冻结；结果与原生source均外置，不覆盖其他E02/E06。
