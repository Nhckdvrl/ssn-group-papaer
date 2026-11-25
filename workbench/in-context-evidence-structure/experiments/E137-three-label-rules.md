# E137：三类标签的规则（SST-5 负 / 中 / 正）——A-only 泄漏、选择性阻断、名字是否仍成立（2026-11-25）

- **状态：** DONE（18 个任务全部完成）
- **对应：** ARR 审稿意见 nsWy-W2（只有二分类、只有完全相反的映射，机制能否推广到更一般的多规则 ICL）、AZuR-W1（二分类、每来源 8 条）。属于对 E123/E136 的小补充，同一查询引擎与读数。
- **设置：** SST-5 原始标签 0 / 2 / 4（很负 / 中性 / 很正）三类，共享标签词 red / green / blue（far 命名空间：B 用 one / two / three）。每个 prompt 随机给 A 一个类→词映射；B 的映射是 A 的映射再做一次循环置换（方向随机），因此三类上两人**全部**不同。两个世界：origin（B 按自己的映射）与 cross（B 的标签词与位置不变，只把每条 B 评论换成同长度签名组里属于“A 映射下该词对应类”的评论，于是 B 的约定与 A 相同）。A 的 token 两世界完全相同。查询每类 4 条（确认材料规则与 E136 相同：来自 SST-5 test，与样例和 validation 不重叠）。
- **两种材料：** k3（每来源每类 3 条，共 18 条样例）与 k6（每类 6 条，共 36 条）；k6 同时回答“每来源只有 8 条”。种子 137101，32 个 prompt；材料脚本 `scripts/e137_materials.py`，运行脚本 `scripts/e137_three_labels.py`。
- **格式变体（跑前追加，23:20，未见任何结果）：** k3 材料再跑一次 alt 格式：开头句与三个字段名全部换掉（"Below are movie reviews and the ratings that individual raters gave them." / Review / Rater / Rating），评论文本不变；回答 AZuR-W1“只有一种提示格式”。Gemma 在 alt 下用 `--bos` 自行加 BOS。默认格式的代码路径不变。
- **政策：** normal、answer_cross_off、all_cross_off、iso_names（shared）；normal、answer_cross_off（far）；读取 native 与 gate。
- **模型：** 与 E134 相同的 6 个（Qwen3-8B/14B、Mistral-7B、Llama-3.1-8B、Gemma-2-2B/9B；Gemma 走 `run_gemma.py` 加 BOS）。
- **读数：** Δ = ½·(m_cross − m_origin)，m = A 的金标签词在三个标签词上的 log-softmax（nats），gate 读取；准确率 = 全词表 argmax 等于金标签词（A、B 两世界平均；A–B 冲突世界单列）；均为 prompt 级 bootstrap 区间。
- **判定（跑前写定）：** Δ（shared, gate）> 0 且 far 下接近 0 → 泄漏推广到三类；answer_cross_off 的准确率提升 CI 不含 0（多数模型）→ 选择性阻断推广；iso_names − all_cross_off > 0 → 名字的作用推广。任何一项不成立都如实报告，不改读数。
- **算力：** 每模型每材料约 0.3–0.6 GPU 小时，空闲卡上跑。

## 结果（2026-11-26，32 prompt；“~”= 区间含 0）
- **k3 默认格式（6/6 模型）：** A-only 泄漏 Δ 0.02–0.07 nats，5/6 区间不含 0（Mistral 0.01~）；far 下 6/6 ≈ 0（|Δ| ≤ 0.01）；选择性阻断后 Δ ≈ 0。选择性阻断（native）准确率 +3.0 – +6.2 点 5/6 显著（Gemma-2-2B +1.9~）。完全隔离 57–61%，重开名字 +2.6 – +7.0 点 4/6 显著（Llama −0.2~，Gemma-2-2B +1.0~）。native 准确率 58.5–66.0%（三类机会水平 33%），far native 66.0–70.6%。
- **alt 格式（6/6）：** 泄漏 4/6 显著（Qwen3-8B −0.04~，Gemma-2-2B 0.01~）；选择性阻断 +3.8 – +7.5 点 5/6 显著（Gemma-2-2B +0.2~）；名字 +2.3 – +5.6 点 6/6 显著。
- **k6（每来源 18 条，6/6）：** 选择性阻断 +3.0 – +6.3 点 6/6 显著；名字 +4.6 – +9.5 点 6/6 显著；A-only 泄漏只有 2/6 显著（Gemma-2-2B/9B 各 0.02），其余 4 个区间含 0——自己的样例加倍后，gate 读取下的泄漏变小到测不出，但 native 读取下阻断路径仍提高准确率。
→ 判定：泄漏推广到三类（默认格式 5/6，far 全部 ≈ 0）；选择性阻断推广（5/6，两种格式）；名字作用默认格式 4/6、alt 格式 6/6、k6 6/6。Gemma-2-2B 在三类任务上基础准确率最低，三项最弱。
