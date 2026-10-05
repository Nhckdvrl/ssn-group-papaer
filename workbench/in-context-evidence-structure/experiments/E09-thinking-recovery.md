# E09：显式推理（Qwen3 thinking）能否恢复潜在层面的时间推断？（2026-10-05）

- **状态：** RUNNING
- **对应：** C02；与推理模型的关系
- **设计：** E02a 的 100 个 base × 8 个条件（allA、suffix_4、disp_4、noise_2__suffix_4、suffix_8、block_start4、single_1、single_16）。原始 few-shot prompt 去掉末尾 `Label:`，包成 chat 用户消息并追问“最后一个 item 的标签是什么？最后一行写 Answer: <label>”。thinking=1 vs thinking=0（同格式对照），每个 prompt 采样 8 次（T=0.6, top_p=0.95, top_k=20），P(B)=#B/#有效答案。
- **预测：** 若推理能显式维持“当前规则”的假设并检查时间结构，则 suffix_4 ≫ disp_4、前缀噪声降低 P(B)；若推理只是更准确地做集合式计数，则 suffix≈disp。
- **算力：** vLLM，fvcrc13 两卡。

## 结果
（待填）
