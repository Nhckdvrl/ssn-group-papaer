# E01：公开权重解剖（2026-11-26；对话 E0）
- **状态：** DONE（首轮，待人审；Qwen 1 对 + OLMo 3 对；Think-SFT 两对排队中）
- **类型：** PILOT / 标准测量与资产建设
- **对应：** I01（主），I04（SFT/RL 头部行漂移的符号结构假说，2026-11-26 运行前写入）
- **问题（一句话）：** 真实后训练谱系中，Head 相对骨干如何变化，这种变化对固定输入的输出分布有何实际影响？
- **设置：**
  - 相邻对（`scripts/models.py::PAIRS`，revision 写入结果 JSON）：Qwen3-8B-Base→Qwen3-8B（多阶段、不透明）；OLMo-3-7B：Base→Think-SFT（SFT）、Think-SFT→Think-DPO（DPO）、Think-DPO→Think（RLVR）、Base→RL-Zero-Math（无 SFT 直接 RLVR）、Base→Instruct-SFT（SFT）。全部非 tied head（config `tie_word_embeddings=false`，运行时复核）。
  - 固定输入：`data/e01_texts.json`，64 篇 Pile-10k（≥3000 字符）+ 64 篇 MATH-train 题解，seed 0，截断 512 token，不加特殊 token，父子同 token IDs。
  - token 分桶：pad 行（id ≥ len(tokenizer)）、special/added token、Pile-10k 频数桶（0 / 1–9 / 10–999 / ≥1000）；另记 MATH 题解频数。
  - 环境：`~/.venvs/ices-tf457`（torch 2.8 / transformers 4.57.6），fvcrc11 空闲卡；权重在节点本地 `/tmp/xiang_lmhead/models`。
- **读数：**
  - 权重（`scripts/e01_weights.py`）：各模块组相对/绝对 Frobenius 变化、占总 ‖ΔW‖² 份额、bf16 逐位相等比例、|Δ| 的 bf16 ULP 数；Head 与输入 embedding 的行能量集中度、分桶份额、ΔW 谱（FP64 Gram）与 entropy/stable rank、BF16 舍入零基线（两端独立 U(±ulp/2)，σ1(E) 以上奇异值数）、col(W0)/col(W1) 主角余弦、**公共行平移分量**（ΔW≈1cᵀ，softmax 不变，功能为零）与 **W0 比例分量**（ΔW≈αW0，整体缩放/温度）。
  - 功能（`scripts/e01_function.py`）：z_ab=W_a h_b 四组合与三项恒等式；KL(p11‖p00)、KL(p10‖p00)（只换头，给定 h0）、KL(p01‖p00)（只换骨干，给定 W0）、KL(p11‖p01)；中心化 logit RMS；top-1 flip；目标 token logprob 变化；实际 logit 变化落在 col(W0) 内的能量比例；均值隐状态 μ0 与 ΔW 主右奇异向量的余弦；头部变化把哪些 token 往下/往上推。原生坐标，非唯一功能归因。
- **阳性对照：** 合成矩阵工具测试 `scripts/test_geom.py`（21 项全过，2026-11-26）；同 checkpoint 自比（`qwen-post__self`，应 ΔW=0、KL=0）；已知 50 行扰动的 selftest（z10−z00 必须等于 δh0，KL 只来自扰动）；原生 forward 与手工 head 的 logit 差；三项恒等式 FP32 误差。
- **噪声地板 + MIE：** 权重侧以 BF16 舍入零基线为地板（σ1(E)）；功能侧以 selftest/自比为数值地板，题目（文档）为统计单位做 bootstrap CI。有意义 = 超出地板且会改变下一步（例如决定 E02 是否以头部通道为重点）；不预设稀疏率或 KL 阈值。
- **I04 预测（运行前写）：** 机制线索来自 Han et al. 2610.09835（Adam 把未出现 token 的单边 softmax 梯度放大为满步长）。SFT 的非目标行梯度 Σ p_tj h_t 单边、方向一致；on-policy RL 的 Σ A_t(p_tj−1[a_t=j]) h_t 随优势符号抵消。若成立：SFT 对（Base→Think-SFT、Base→Instruct-SFT）的 head ΔW 行能量更均匀地铺在低频/未出现行上，主方向与 μ0 对齐，功能上压低稀有 token；RL-Zero 对的低频行漂移显著更小。若 RL-Zero 同样铺满低频行，或 SFT 主方向与 μ0 无关，则 I04 不成立，记为负结果。混杂：两条线的步数、学习率、数据量完全不同（自然谱系），只能作现象；因果需 E02 梯度一致性测量或后续受控训练。
- **混杂审计：** 自然谱系，训练数据/目标/步数/学习率未控制；公开权重为 bf16 存储（FP32 master 的真实更新不可见）；固定 h 的头部反事实可能脱离联合分布；Qwen 后训练流程不透明，只作参照；未测泛化。
- **决策表（跑之前写）：** 稳定功能变化→定位 token/模块，和 E02 交叉解读；只有参数变化无功能信号→先报告，暂不干预；I04 预测成立→E02 增加头部行梯度符号一致性读数，人审是否值得受控小训练；工具/数值错误→修正再测；不确定→扩大相同条件样本或复算，而非增加新轴。
- **算力预算：** 权重解剖每对约 10–20 分钟（单卡 + CPU）；功能分解每对两次 8B forward（128×512 token），预计 <10 分钟/对。总计 ≤3 GPU·时。 **实际：** 每对权重 3–4 分钟 + 功能 1–2 分钟（A100），4 对合计约 0.5 GPU·时。

## 结果

**对照：** 同 checkpoint 自比 ΔW 全零、逐位相等 100%；selftest 已知行扰动只出现在头项，骨干项 0，恒等式 FP32 误差 1e−4，原生 forward 与手工 head 差 0；随机行扰动的 ρ=0.0288（d/V=0.0270）。

**Qwen3-8B-Base→Qwen3-8B（多阶段、不透明；128 文档，55,644 位置）：** `results/e01/weights_qwen-base__post.json`、`function_qwen-base__post.json`。
- 权重：head 相对变化 8.9%，与骨干线性层（7–9%）同量级，占总 ‖ΔW‖² 的 8.6%；输入 embedding 6.7%。逐位相等仅 2.2%，ΔW 全部 4096 个奇异方向高于 BF16 舍入地板。head ΔW 行能量很分散（top 1% 行占 3.3%），Pile 中未出现的 token 行（41% 的行）占 34% 能量；公共行平移（功能为零）占 5.2%，W0 比例分量 α=−0.028（整体收缩 2.8%，占 9.8% 能量）。col(W0)/col(W1) 平均主角余弦 0.997，但有 122 个方向 <0.99、最小 0.60。head 与 embedding 的行能量 Spearman 0.70。
- 功能（KL 为位置均值，文档 bootstrap CI）：

| | 全部 | Pile | MATH |
|---|---|---|---|
| KL(p11‖p00) 总 | 0.45 [0.39, 0.51] | 0.22 | 0.68 |
| 只换头 KL(p10‖p00) | 0.26 [0.23, 0.29] | **0.43** | 0.10 |
| 只换骨干 KL(p01‖p00) | 0.53 [0.48, 0.59] | 0.39 | **0.67** |
| 给定新 h 换头 KL(p11‖p01) | 0.18 | 0.30 | 0.05 |
| top-1 翻转：头 / 骨干 | 0.19 / 0.23 | 0.30 / 0.28 | 0.09 / 0.17 |

  实际 logit 变化 91% 的能量在 col(W0) 内；头项 ΔW h0 有 67% 在 col(W0) 内（随机为 2.7%）。头部变化压低的 token：`<|endoftext|>`、粗俗/口语词（shitty、crappy 等）；抬高的是一批稀有的代码/泰文碎片 token（与整体收缩 α<0 一致：原本 logit 极低的行被缩向 0）。ΔW 主右奇异向量与均值隐状态 μ0 的余弦仅 0.06–0.20。
- **解读：** 在这条不透明的多阶段谱系里，输出头不是“几乎没动”的旁观者：它在通用文本上单独造成的分布变化与骨干相当，在后训练主领域（数学）上则几乎全部由骨干完成。给定新 h 时头的作用变小（0.18 < 0.26），提示头与骨干部分共同适配。

**OLMo-3-7B 透明谱系（同一 128 文档；revision 见各 JSON）：**

| 对 | 阶段 | head Δrel | 骨干 Δrel | emb Δrel | head ΔW 高于舍入地板的奇异方向 | 公共平移能量 / α(W0) | KL 总 | KL 只换头 | KL 只换骨干 |
|---|---|---|---|---|---|---|---|---|---|
| Base→Instruct-SFT | SFT（3.4B token, LR 8e-5） | 43.6% | 27% | 3.1% | 4096/4096 | 40% / −0.165 | 0.35 | 1.83 | 3.98 |
| Base→RL-Zero-Math | RLVR | 0.13% | 0.23% | 0.009% | 1/4096 | 1.1% / 0 | 0.0094 | 0.00024 | 0.0082 |
| Think-DPO→Think | RLVR | 0.15% | 0.14% | 0.008% | 1/4096 | 0.5% / 0 | 0.0037 | 0.00007 | 0.0035 |
| Base→Think-SFT | SFT（45B token, LR 5e-5） | 41.4% | 25% | 2.6% | 4096/4096 | 41% / −0.159 | 0.40 | 2.01 | 4.89 |

- RL 阶段：头的相对变化与骨干同量级，但几乎全在 BF16 舍入地板以下（66–77% 逐位相等，只剩 1 个方向高于地板，该方向与 μ 余弦 0.3–0.4）；功能上只换头的 KL 只占总量 2–3%，top-1 翻转 0.4–0.7%（骨干 2.3–3.3%）。输入 embedding 比头还小一个数量级。RL-Zero 中 Pile 未出现的 token 行几乎不动（中位相对变化 6.8e−5，常见行 1.3e−3，约 20 倍差）。
- SFT 阶段：头动得比骨干还多（43.6% vs 27%），但 40% 的 ΔW 能量是功能为零的公共行平移，另有整体收缩 α=−0.165（像 weight decay）。只换头/只换骨干的 KL 都远大于总 KL，说明 Base 与 SFT 的头和骨干强烈共同适配，固定 h 的反事实在这里脱离了联合分布，三项分解不可解读（技术指南已预警）。
- **复核（人审讨论中，2026-11-26 晚）：** (1) tokenizer：OLMo Base 与 Instruct-SFT/RL-Zero 的 `tokenizer_identical=false` 只来自 11 个保留特殊 token 改名（`<|extra_id_k|>`→`<think>`、`<|user|>`、`<functions>` 等，ID 100256、100266–100275），普通 token 无变化，128 篇输入父子编码完全相同且不含这些 ID，不影响结论。(2) 规范变换：最终 RMSNorm γ 在 OLMo SFT 中只放大 2.5–5%，有效读出 W·γ 仍收缩 12.6–14%（规范补偿约抵 1/4）；Qwen γ +0.3%，可排除 C04 是温度/规范假象。(3) 功能大小的口径：RL 两对只换头的中心化 logit RMS 为只换骨干的 5.5–6.5%，√KL 为 12–23%，此前“KL 占 2–3%”的说法偏小，已在 CLAIMS 降级。
- **I04 的 checkpoint 检验（`scripts/e01_vs_adam.py`，`results/e01/vs_adam_*.json`）：** 用 E02b 在 OLMo-3 Base 上模拟的四种信号头部 Adam 轨迹，逐行预测“沿 μ 的 logit 位移”，与真实 ΔW_j·μ̂ 做秩相关。原始相关：Instruct-SFT 与 SFT 类预测 0.76–0.82、与 RL 预测 −0.51；RL-Zero 与 SFT 类 +0.30–0.34、与 RL −0.25。**控制父模型行投影 w0·μ̂（整体收缩的位移）与 log 频率后**：Instruct-SFT 偏相关 SFT 类 0.09–0.17 / RL −0.12；RL-Zero 同样是 0.10–0.17 / −0.12。真实 SFT 的逐行位移与 w0·μ̂ 的秩相关为 −0.935，原始高相关几乎全是收缩造成的。~~结论：公开 checkpoint 中看不出差异~~ **已修订（见 CLAIMS C06 与作废记录）：** 秩计算改为 average rank，并精确去除 αW0 与 1cᵀ 后，真实 SFT 与 SFT 类预测的残差位移相关 0.75–0.79（与 RL 模拟 −0.50），真实 RL-Zero 也与 SFT 类正相关 0.30–0.33、与 RL 模拟负相关；按秩控制 w0·μ̂ 是过度控制。SFT 侧的头部模式与梯度机制一致，但“RL 抵消”的判别性预测在真实 RL-Zero 上不成立；RL 模拟所用的 OLMo Base rollout 质量差是首要怀疑对象。
- Base→Think-SFT 已自动跑完（表中最后一行），结构与 Instruct-SFT 几乎相同；Think-SFT→Think-DPO 未跑。
