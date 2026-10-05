# E17：任务向量本身是否整合了时间？（函数向量 patch）（2026-10-05）

- **状态：** DONE（Qwen3-8B, confirm_v1）
- **对应：** C02 机制；接 Hendel'23 task vectors / Todd'24 function vectors / Yin & Steinhardt'25 / Yang-Cho-Inoue'26
- **方法：** 取 context 在第 L 层、最后一个 prompt token 的残差 θ(C)；把 θ patch 到一个新 query 的零样本 prompt（仅 header + 新 query）的同一位置/层，读新 query 的 B-regime vs A-regime 答案 log-odds。L 在 40 个独立校准 base 上用“全 A vs 全 B context”的可迁移对比选定（arith、mag_nat 都选到 L*=22），测试 200 个 base，测试模式不参与选层。
## 结果
| | arith ±3（变换） | mag_nat small/large（分类） |
|---|---|---|
| 校准：全B−全A 可迁移对比（L22） | 3.46 | 0.23（晚层为负） |
| suffix_8 − allA | 2.03 [1.79,2.29] | 0.07 [−0.05,0.19] |
| suffix_4 − disp_4 | **0.62 [0.49,0.76]** | 0.05 [−0.06,0.17] |
| noise_2__suffix_3 − suffix_3 | **−0.30 [−0.37,−0.23]** | −0.04 [−0.13,0.04] |
| late block − start block | **0.58 [0.45,0.73]** | 0.08 [−0.04,0.20] |
| single_16 − single_1 | 0.81 [0.68,0.94] | 0.09 [−0.02,0.20] |
**判读：** 变换型 regime 被压缩为一个可迁移的任务向量，且这个向量本身就编码了时间结构（成簇、噪声方向、过时折扣都与 oracle 同向）——函数推断是一个随时间更新的信念。分类映射没有可迁移的任务向量（全B vs 全A 都迁移不过去），只能在 query 处按内容检索求解，因此没有时间维度。
