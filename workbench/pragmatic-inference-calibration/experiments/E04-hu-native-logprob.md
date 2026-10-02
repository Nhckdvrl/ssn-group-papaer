# E04：Hu fine-grained 原生概率评测（2026-10-02）

- **状态：** DONE
- **类型：** REPRO
- **对应：** C01、C02、P03
- **问题（一句话）：** 原 next-token restricted-choice scorer 能否复现并保留正确、literal与各类distractor的区别？
- **设置：** 原CSV prompt逐字不改；7现象、169 items ×5个option-order seeds=845；5种no-story原parent control共520，另报；全部1365条件保留。Qwen2.5-3B与Qwen1.5-14B（现代迁移不等于Hu官方模型复现）；优先另下载原Flan-T5-XL公开强anchor。causal raw continuation，T5 raw encoder，下一token仅合法数字集softmax；token必须单token。
- **读数：** 原每现象/条件accuracy、prob_true_answer、原label response mass，option-order方差；按 item_id 成簇bootstrap CI，不把5种option排列当5倍独立样本；与repo已发布对应模型model_data逐项对照。
- **阳性对照：** gold数字单token确认；oracle accuracy100%/交换0%；与原query_hf.softmax/get_completion在fixture上同结果；batch1/16首末项logprob差。
- **噪声地板 + MIE：** deterministic模型；5种option-order测response-label偏好，原有public结果误差与FP16/BF16分开；不是预注册科学效应方向。
- **混杂审计：** 原prompt包含Answer:与尾空格保持；no-story不是literal context；Coherence无literal/nonliteral speaker，单列；instruct raw非默认chat但正是parent范式，不能越界解释；污染未知；不用API judge。
- **决策表（跑之前写）：** A 原模型对应官方逐项一致 → D1anchor；B 差异大 → 查token前缀/精度/特殊token/config；C 只现代模型成功 → D2迁移，不叫官方复现；不确定 → 固定首末项复测，保留全部失败。
- **算力预算：** 第一轮各模型 <0.5 GPU·时。**实际：** 待记录。

## 结果
待运行。

### 原论文模型运行前冻结
Flan-T5-XL 权重下载已完成（snapshot_download返回成功），revision=7d6315df2c2fb742f0f5b556879d730926ca9001；与parent query_hf.py一致用float32和slow T5Tokenizer。完整1,365个原始continuation读数，GPU5；结果与仓库原版model_data逐行对比。注意default generation processors与batched forward仍要做单项数值校对，不能凭同模型名宣布严格复现。
