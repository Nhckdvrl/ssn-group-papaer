# E09：显式推理（Qwen3 thinking）能否恢复潜在层面的时间推断？（2026-10-05）

- **状态：** DONE
- **对应：** C02；与推理模型的关系
- **设计：** E02a 的 100 个 base × 8 个条件（allA、suffix_4、disp_4、noise_2__suffix_4、suffix_8、block_start4、single_1、single_16）。原始 few-shot prompt 去掉末尾 `Label:`，包成 chat 用户消息并追问“最后一个 item 的标签是什么？最后一行写 Answer: <label>”。thinking=1 vs thinking=0（同格式对照），每个 prompt 采样 8 次（T=0.6, top_p=0.95, top_k=20），P(B)=#B/#有效答案。
- **预测：** 若推理能显式维持“当前规则”的假设并检查时间结构，则 suffix_4 ≫ disp_4、前缀噪声降低 P(B)；若推理只是更准确地做集合式计数，则 suffix≈disp。
- **算力：** vLLM，fvcrc13 两卡。

## 结果
**可见 CoT（enable_thinking=False，“想一想再答”，100 base × 8 条件 × 6 样本，无效答案 15/4800）：**
allA 0.370、single_1 0.353、single_16 0.348、disp_4 0.418、suffix_4 0.406、noise_2__suffix_4 0.464、block_start4 0.380、suffix_8 0.469（P(B)）。
→ 时间盲（suffix_4 ≈ disp_4；前缀噪声使 P(B) 上升，方向错），且口头推理损害规则学习（allA 准确率 0.63 vs 原始 few-shot 0.90）；样本显示模型把问题框定为“找一个解释所有 item 的静态规则”（数 on 的个数、构造合取规则）。

**thinking 第一轮（max_tokens 6000）作废：** 只有 886/4800 个样本在预算内想完并给出 “Answer”，其余答案取自截断的推理尾部，不能当作答案。可读样本的定性模式与集合式一致（suffix_4 0.485 ≈ disp_4 0.473；噪声前缀 0.513），仅作参考。
**第二轮：** 50 base × 6 条件 × 4 样本，max_tokens 20000（运行中）。


**可见 CoT 配对检验（`scripts/analyze_think.py`）：** suffix_4−disp_4 = −0.014 [−0.082,0.055]；noise_2__suffix_4−suffix_4 = **+0.068 [0.015,0.120]**（方向错）；suffix_8−block_start4 = +0.102 [0.015,0.190]（弱 recency）。

**thinking 第二轮（50 base × 6 条件 × 4 样本，max_tokens 20000；1156/1200=96% 想完并作答）：**
allA 0.040、disp_4 0.428、suffix_4 0.430、noise_2__suffix_4 0.435、block_start4 0.380、suffix_8 0.457（P(B)）。
配对：suffix_4−disp_4 = +0.002 [−0.163,0.160]；noise−suffix_4 = +0.005 [−0.093,0.103]；suffix_8−block_start4 = +0.077 [−0.092,0.238]。
**判读：** thinking 把规则学习提升到近乎完美（准确率 96%），但对矛盾证据的时间组织完全不敏感（成簇=零散、加噪声无影响、新旧块无差别）——测试时推理不能恢复噪声/变化的区分。

## 事后补记（2026-10-06，流程字段）
- **阳性对照：** 事后补记：本线统一的阳性对照为标签流条件（E05/E06），同一工具下 13/13 模型测到规范方向效应；此卡跑时未单列。
- **噪声地板：** 事后补记：bf16 batch 噪声 ~0.1 nats/条且无方向，200–300 base 配对平均后 ≈0.007；效应以配对 bootstrap 95% CI 判断。
- **决策表（跑之前写）：** 跑前写了预测（见上方“预测”条目），但未写成分支决策表；此字段为事后补记。
