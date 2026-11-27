# Subliminal Learning 文献地图（2026-11-26）

**目标会议：** ICML 2027（用户 2026-11-27 指定；摘要 2027-01-14 / 全文 2027-01-22 AoE）。
**用途：** 为 territory 卡 [`search/our-taste/TERRITORY_SUBLIMINAL_LEARNING_2026-11-26.md`](../../../search/our-taste/TERRITORY_SUBLIMINAL_LEARNING_2026-11-26.md) 提供谱系与证据底稿。
**证据级别说明：** 本页由三个调研代理用 WebFetch 读 arXiv HTML/abs 和会议页面后汇总；主会话核对了 venue corpus 条目。WebFetch 返回的是模型摘要，不是逐字原文。**2026-11-27 已对原文逐条核对 12 组关键数字**（标 `核✓`，已按核对结果改正）；其余数字写进实验卡或论文前仍须复核。每条标 `[全文]` / `[部分]` / `[摘要]`；venue 标 ✓ 表示在 arXiv comments 或会议页核对过。OpenReview 无法访问（浏览器验证墙），没有任何审稿意见。
**按 R10 排除：** Gisler et al.（2603.09517，EACL 2026 SRW）不引用。

---

## 0. 一段话的发展史

2025-07 Cloud et al. 发现：带特质（喜欢猫头鹰 / misaligned）的教师生成**语义无关**的数据（数字序列、代码、CoT），同初始化的学生微调后继承特质；不同基座不迁移；给出单步梯度定理和 MNIST 辅助 logit 玩具实验（2026-04 登上 *Nature*）。2025 下半年的回应集中在“信号在哪”：token 纠缠（Zur et al. 博客）被 divergence tokens（Schrodi et al., ICLR 2026）否定为非必要。2026 上半年转向“为什么能学到”，出现至少六种互相竞争的机制（steering vector 蒸馏、LoRA 伪影、输出头兼容、PSD 核、特质方向漂移、优化器状态），并在 LoRA/全参、Adam/SGD、是否需要同初始化三个问题上**直接互相矛盾**。2026 下半年转向“能传什么”：能力、后门、黑客倾向（Beyond Owls）、agent 不安全行为、RL/judge 通道、VLM、自然语言数据的 phantom transfer（跨模型、扛 11 种数据级防御）。截至 2026-11，约 35 篇后续，其中约 12 篇出现在 10–11 月。

---

## 1. 起点与近亲

| 论文 | 状态 | 要点 | 与 SL 的差别 |
|---|---|---|---|
| Hinton et al. 2015, dark knowledge `[部分]` | NIPS-W | 去掉所有“3”的迁移集，偏置校正后学生仍识别 98.6% 的 3 | 软标签、任务相关输入；SL 用硬 token、无关数据 |
| Behrens & Zdeborová, 2506.14457 `[摘要]` | 自称 ICLR 2026（未核） | 软标签在随机数据上泄露教师记忆的 held-out 标签，强依赖温度 | 最近的“数据集蒸馏”类比；需要软标签 |
| Betley et al., Emergent Misalignment, 2502.17424 `[摘要]` | ICML 2025 ✓ / Nature | 窄域 insecure code 微调 → 广泛 misalignment | Cloud 复用其设置并怀疑部分 EM 是 subliminal |
| Ilyas et al. 2019 non-robust features | — | 非鲁棒特征跨模型迁移 | SL 信号不跨模型（至少数字通道） |
| *Hard labels sampled from sparse targets mislead rotation invariant algorithms* `[摘要]` | ICML 2026 poster（corpus ✓） | 稀疏 logistic 目标下，只给硬采样标签时，旋转不变算法（如 GD）超额风险 Ω((d−1)/n)，u⊙v 重参数化算法为 O(s log d / n) | 不涉及 SL；可能解释 SL 中 Adam / LoRA / 稀疏正则为什么更容易迁移（territory 卡 P2 的理论入口） |
| *The Bridge–Garden Dilemma in LLM Distillation* `[摘要]` | ICML 2026 poster（corpus ✓） | 混合硬 / 软标签优于纯软标签；收益来自降低 exposure bias，而非更贴近教师 | 普通蒸馏中硬 / 软通道的差异；SL 中两者的效率差距（Beyond Owls）尚无理论 |
| *Distillation Scaling Laws* `[摘要]` | ICML 2025 poster（corpus ✓） | 蒸馏性能随算力在师生间分配的缩放律 | 受控测量范式参考 |

**Cloud, Le, …, Marks, Evans — Subliminal Learning**（2507.14805；*Nature* 652:615–621, 2026-04 ✓）`[全文 arXiv]`
- 设置：GPT-4.1 nano（OpenAI API, 10 epochs）；misalignment 用 GPT-4.1；开源只有 Qwen2.5-7B（超参未报告，代码用 Unsloth）。特质主要用 system prompt 植入，附录 B.1 用微调教师复现。
- 数据：数字 10k（格式过滤；misalignment 另禁 666/911/187 等 34 个数）；代码 10.8k（子串 + GPT-4.1 judge 过滤）；GSM8K CoT（作者承认 judge 接近随机）。
- 数字 `核✓`：猫头鹰偏好 12% → 超过 60%；misalignment ~0% → ~10%；MMLU 掉 2–4 点。
- 跨模型 `核✓`：同模型 0.25–0.54；原文措辞是异模型教师“do not reliably show increased animal preference”（比“≈0”弱），例外是 GPT-4o↔GPT-4.1（作者归因于共享初始化）。Qwen2.5-7B 测了 19 种动物，只对 cat、penguin、phoenix 等少数有大效应，多数为阴性。
- 反“隐藏语义”对照：整套数据放进上下文无效；LLM 分类器检测约 50%（随机）；打乱数字顺序大幅减弱 → 信号在序列层面。
- 理论：同初始化 + 小步长，学生一步更新与教师更新内积 ≥ 0。**只覆盖单步**，与多步训练、过滤数据都不符。
- MNIST：784-256-256-(10+3)，只蒸馏 3 个辅助 logit、输入为噪声图，学生 >50% 准确率；不同初始化不迁移。
- 未做：机制、LoRA vs 全参、复杂特质。

---

## 2. 2025 回应：信号在哪

| 论文 | 状态 | 主张 | 关键证据 | 短板 |
|---|---|---|---|---|
| Zur, Loftus, …, Bau, *It's Owl in the Numbers* `[全文]` | LessWrong 博客 | softmax 瓶颈让概念 token 与特定数字纠缠（“087”↔owl），采样泄露 logits | “love 087”把 owl 推进 top-5；subliminal prompting 12/18 动物有效 | 未直接检验纠缠；代码 README 写 Llama-3.2-1B，与博客不一致 |
| **Schrodi, Kempf, Barez, Brox**, 2509.23886 `[部分]` `核✓` | **ICLR 2026 ✓** | 少数 **divergence tokens**（不同偏置教师会选不同 argmax 的位置）承载信号；早期层足够 | Qwen 7.5% / Gemma 18.3% token；只训它们保留迁移，mask 掉降到对照；只训第 0 或第 7 层即可；与纠缠 token 重叠 ~4%（≈随机） | 改写 prompt、混入 10–25% 对照数据就压掉；只对部分动物有效；~10k L40S GPU·时 |
| Tan et al., Inoculation Prompting, 2510.04340 `[部分]` | ICLR 2026 poster（corpus ✓） | 训练时 system prompt 点名“owls”可阻断，“love birds”不行 | 读作 token 特异 | 学生模型未在所读部分给出 |
| Vir & Bhatnagar, Subliminal Corruption, 2510.19152 `[全文]` | 预印本 | GPT-2 上 ~250 条毒样本出现阈值 | — | 训练方式未报、无种子，证据弱 |
| Okatan et al., 2511.01023 `[全文]` | 预印本 | 子空间对齐而非整体 CKA 预测迁移 | BERT-tiny 玩具 | 自身条件与主结论矛盾 |
| Minder et al., 2510.13900 `[摘要]` | ICLR 2026 poster（corpus ✓, 7.5 分） | 窄域微调在激活差里留下可读痕迹，SL 模型可被读出 | — | 检测角度 |
| Bozoukov et al.（LessWrong 2025-12）`[全文]` | 博客 | Llama-3.1-8B 改写 Alpaca/MathQA 也能传 misalignment（0.32% → 5.50%） | 选高 divergence 样本升到 7.09% | 初步，数字有算术不一致 |

**2025 年底共识：** 同初始化下简单特质与 misalignment 可经数字/代码/CoT 传递，LLM 分类器检测不到；Schrodi 独立复现，并否定“纠缠/logit 泄露是必要条件”。**悬而未决：** LoRA vs 全参、优化器、单步定理与多步训练的差距、跨家族是否真的为零。

---

## 3. 2026 机制之争（核心）

| # | 论文 | 状态 | 机制主张 | 设置 | 关键数字 |
|---|---|---|---|---|---|
| M1 | **Blank, Bhatia, Rajamanoharan, Conmy, Nanda**, *SL Is Steering Vector Distillation*, 2606.00995 `[全文 v4]` `核✓` | NeurIPS 2026 poster（会议页 ✓；arXiv 无 comments；icml.cc 2026 也有页面，类型未核） | 教师 system prompt ≈ 残差流 steering vector；学生学到对齐的向量；不能写成向量的 prompt 不迁移；跨模型失败源于向量的模型特异成分 | Qwen2.5-7B / Gemma-3-4B（Llama、OLMo 旁证）；LoRA r=8 α=32 AdamW lr 1e-4，2 epochs，10k；3 seeds | 16 种动物上可 steer 性与迁移 ρ=0.752（Qwen 面板；另两个模型见 App. G）；消融学生向量去掉 >50% 特质；**SGD 损失匹配也不迁移**（作者无原理解释）；全参主文无迁移，但 App. M 说全参下向量蒸馏仍以较低程度发生；Gemma 上效应弱 |
| M2 | Nief, Fu, Muchane, Holtzman, *SL is a LoRA Artifact*, 2606.00831 `[全文 v2]` `核✓` | 未发表；**v2 comments 自称部分主要结论有误、在大修** | LoRA rank 倒 U；全参消失；强依赖 system prompt；局部化到实体 token（默认 prompt 里的“Qwen”）与早期 FFN | Qwen2.5-7B 为主；AdamW lr 2e-4 α=r，rank 1–512；6 个数据种子（数据种子主导方差）；~10k 次运行、~12k GPU·时 | cat 9.5% → r=8 峰值 39.0% → r=256 1.2%；wolf 训练与评测都用 ChatGPT prompt 时 97.9%，prompt 不匹配时 11–20%；正文与表格的峰值 rank 不一致 |
| M3 | Brockers et al., *Learning Through Noise*, 2605.23645 `[全文]` | 无 venue | 决定迁移的是**输出头兼容**而非共享初始化 | MNIST/EMNIST MLP，Adam，20 seeds，CPU | 重新初始化隐藏层、MLP→CNN 都还迁移；重新初始化辅助头强烈抑制 |
| M4 | Li, Ying, Dong, Yang, *Why Ghost Outputs Teach*（kernel），2609.23260 `[全文]` | NeurIPS 2026 **workshop**（Interpretability as a Science）✓ | 共享初始化下单步算子形如 MMᵀ（PSD）；ghost head 维度是秩瓶颈；高熵输入是宽带探针 | MNIST + Qwen2.5-7B LoRA r=8，2 seeds | MNIST 75.16% vs 不同初始化 9.52%；随机数字 90.8% > 乱码 63.1% > 医学文本 34.3%；**LLM 上从未测核** |
| M5 | Liu, Dong, Fan, Li, Yang, *Trait-Direction Drift*, 2609.01091 `[部分]` `核✓` | **NeurIPS 2026 poster ✓** | 教师样本保留对特质的 preference gap，定义为 G = log P[r \| 有偏 system prompt, p] − (1/K)Σ_k log P[r \| 第 k 个中性 prompt, p]（另有按长度归一的版本）；SFT 沿固定特质方向累积漂移（漂移 = S_T + N_T）；提出 probe-space corridor 正则 | Qwen2.5-7B、Llama-3.1-8B，LoRA（rank/lr 未读到），~3 seeds | 200 步漂移与 gap 相关 +0.769 至 +0.845（单步仅 0.05–0.27）；corridor：owl 30.7±15.7% → 1.7%，malicious 29.55% → 6.45±5.25%；**方差极大** |
| M6 | **Feng, Springer, Ghosal, Zhong, Raghunathan**（CMU）, *Regularization Amplifies SL*, 2611.10397 `[部分]` `核✓` | 无 venue（2026-11-17 v2） | 越强的正则（低 rank、L1/L2、大 DPO β、更多不重复数据）越放大迁移；**每个 rank 单独调 lr 后从 rank 1 到 256 几乎单调下降、无倒 U** | Qwen2.5-7B，25.8k / 10k / 500k；主图 2–3 seeds，很多附录格和惩罚实验中的无惩罚高 rank 条是单 seed | cat：全参 3% vs rank-1 87%（25.8k）；500k 时所有 rank 含全参都强迁移；SGD 在更多数据、更大 lr 下也迁移；跨模型到 Llama 几个百分点 |
| M7 | Morgulis & Hewitt, *Subliminal Steering*, 2604.25783 `[全文]` | 无 venue | 用 steering vector 构造教师；学生隐状态沿该向量移动，可恢复（cos 0.15–0.91）并被说出来 | Qwen/DeepSeek/Llama/Phi；LoRA+Adam 或 SGD lr 0.3–1.0；全参 lr 2e-5；4 seeds | **全参、SGD 都迁移**；prompt 教师只在 Qwen 上迁移 |
| M8 | Hadley & Gultepe, *SL is Non-Semantic Distillation*, 2608.05734 `[全文]` | ICML 2026 MechInterp workshop spotlight ✓ | 迁移走非语义结构；**prompt 教师没有 steering-vector 签名**，steered 教师才有 | Gemma-2B、Llama-3.1-8B，10 seeds | 给教师加权重噪声，迁移放大 1.9×/1.3× |
| M9 | Xu, *Stored in Optimizer State*, 2608.20442 `[全文]` | 单作者，无 venue | Adam 一阶矩 / momentum 承载并“搬运”扰动 | 0.1–1B 模型，3–12 seeds | momentum SGD 3/3 seed 复现但不显著；全参只有 1 seed |
| M10 | Tang, Anand, Paulo, *Tracing SL Through Pretraining*, 2610.30884 `[前 1/3]` `核✓` | 无 venue | **不需要共享初始化**：Pythia-160M↔OLMo-1B 双向迁移（但 Table 1 的超出率只有 14%，是右尾效应、靠置换检验检出）；跨家族软标签迁移；强不对称。注意：90–97% 方差（交叉验证）是**同一模型预训练轨迹内**的 13×13 checkpoint 网格因子模型，不是跨模型配对 | Pythia / PolyPythia / DataDecide OLMo；SDF 预训练教师 | bear 30 对中 26 对迁移；Pythia-160M 能传给更大模型，但从大模型学得很少；SGD+全参可迁移 |
| M11 | Aden-Ali, Golowich, …, Moitra, Haghtalab, *Log-Linearity (LLS)*, 2602.04863 `[摘要]` | corpus 记为 **ICML 2026 poster（4.25）** | 从真实偏好数据**选子集**即可诱导偏好、外语、persona，**跨架构** | DPO 路线、无教师 | — |
| M12 | Madl, *Channel Location Constrains Auditability*, 2606.22019 `[摘要]` | 无 venue | 三种通道：依赖初始化的 body 通道 / 不依赖初始化的词表几何通道 / sycophancy | — | — |
| M13 | Zhao & Zhong, *Cross-Trait Transfer*, 2610.04260 `[摘要]` | 无 venue | 特质簇；学生有时学到邻近特质 | — | — |
| M14 | Yanagisawa et al., 2609.22215 `[摘要]` | Findings EMNLP 2026 | 1.5–8B 动态非单调；早期 KL 正则（liminal training）缓解 | — | — |
| M16 | **Chen et al., *Why Subliminal Learning Needs So Much Data: A Noisy Inverse View through Steering Vector Recovery*, 2610.04907** `[摘要 + 代理核]` | 无 venue（2026-10-06） | 把 steering-vector 蒸馏写成带噪线性逆问题：GD 相当于阻尼逐渐减弱的 Fisher 逆；软标签能恢复低曲率方向，硬标签在这些方向上同时放大采样噪声 → 最优反演深度随独立载体数增长 | Qwen2.5-7B、Gemma-2-9B；代码 github.com/luoyuchenmlcv/subliminal-data | 软标签几百条载体即可恢复方向，硬标签需要数万条。**与 territory 卡 P1/P2 最近** |
| M15 | Kitkana & Arora, Sustained Gradient Alignment（MNIST）`[摘要]` | ICLR 2026 Sci4DL workshop | 多步训练中梯度对齐持续弱正，因果贡献于迁移；liminal training 在此设置失效 | MNIST | — |

### 3.1 解释 × 论文（S 支持 / C 矛盾）

| 解释 | S | C |
|---|---|---|
| token 级载体（divergence / 实体 token / 纠缠） | Schrodi；Nief；Madl | Schrodi（纠缠非必要）；Tang（只匹配首数字频率也保留 40–92%）；Blank（解释不了 OOD） |
| 单个 steering vector | Blank；Morgulis；Hadley（仅 steered 教师）；Liu | Hadley（prompt 教师无签名）；Beyond Owls（单向量 OOD 更差） |
| 参数空间对齐 / PSD 核 / 共享初始化 | Cloud 定理；Li（Ghost）；Kitkana | Brockers；Tang；Madl；Phantom Transfer |
| 输出头 / 词表兼容 | Brockers；Madl；Tang | Beyond Owls（Nemotron 无迁移；词表重合度未查） |
| LoRA 伪影 / 隐式正则 | Nief；Feng；Beyond Owls（参数越少越好）；Blank 主文 | Morgulis；Tang；Feng 500k；所有 MNIST 工作 |
| 必须 Adam | Blank | Nief App. B.11；Morgulis；Feng；Tang；Xu；Blank 自己的 MNIST 附录 |

### 3.2 八个具体矛盾
1. **全参能不能迁移**：Nief / Blank / Feng（10–25k）说不能；Morgulis / Tang / Feng（500k）/ Blank App. M 说能或弱能。可能的统一：数据量 × 学习率的 regime 问题（Feng，但多为 1 seed）。
2. **LoRA rank 倒 U 还是单调**：固定 lr（Nief）是倒 U，逐 rank 调 lr（Feng）是单调递减；Feng 自己的 MNIST 却在 rank 8–64 达到峰值。
3. **Adam 是否必要**：Blank 说必要（损失匹配也不行）；另外 5 篇说 SGD 在大 lr、更多数据或有 momentum 时可行。Blank 的 SGD lr 没有报告。
4. **理论与实证的优化器不一致**：所有理论都是 GD 线性化，所有实验都用 Adam。
5. **是否需要共享初始化**：Cloud / Ghost / Beyond Owls / Kim & Choi 说需要；Brockers / Tang / Phantom / LLS 说不需要。可能的调和点：“不同初始化”是否连输出头也换了（未核）；数字通道与自然语言通道可能根本不同。
6. **prompt = steering vector 吗**：Blank 说是；Hadley 看不到签名；Morgulis 说 prompt 教师只在 Qwen 上有效。
7. **信号在哪**：token 局部（Schrodi、Nief）还是全局残差方向（Blank、Morgulis）——**没有一篇在同一组运行上同时检验两者**。
8. **正则帮忙还是放大**：Feng（权重惩罚、低 rank 放大迁移）vs Yanagisawa / Liu（KL、corridor 缓解迁移）。

### 3.3 跨论文混杂的变量
- **模型**：几乎所有阳性 LLM 结果都依赖 Qwen2.5-7B-Instruct；Llama 弱或无效，Gemma 弱。模型易感性与每个机制主张混在一起。
- **教师构造**：prompt / steering / 微调 / SDF 预训练。“SGD 可行”“全参可行”多来自 steered 或 Pythia；“需要 Adam”“全参不行”多来自 prompt + Qwen。
- **学习率协议**：固定 lr 还是逐条件扫描——单这一项就可能同时制造倒 U 和 SGD 失败。
- **数据量与 epoch**：10k–500k，2–10 epochs。
- **LoRA 配置**：α=r / α=32 / α=8；全模块 vs 只训 attention。
- **标签**：硬 token vs 软 logits（Beyond Owls：采样版需要约 50× 数据）。
- **评测 prompt**：仅 system prompt 就能造成 2–5× 差异；多数论文用默认 Qwen prompt + 字符串匹配。
- **种子**：1–6 个；Nief 显示**数据种子主导方差**，但多数论文只换训练种子。

---

## 4. 2026 扩展：能传什么

| 论文 | 状态 | 传递对象 | 要点 |
|---|---|---|---|
| **Dubiński, Sztyber-Betley, Betley, Evans, *Beyond Owls*, 2610.10657** `[全文]` | 仅 v1，无 venue | 新能力、后门、黑客倾向 | 见 §4.1 |
| Askin et al., 2605.12798 `[摘要]` | NeurIPS 2026 ✓ | misalignment | **on-policy 蒸馏**也传，且比 SFT 更强；教师决定往哪迁移，数据决定迁移多少 |
| Dang, Xie, Younis, 2604.15559 `[摘要]` | NeurIPS 2026 ✓（corpus 中为 ICLR-W AIWILD 版） | agent 不安全行为 | 过滤删除类关键词后，destructive-first 35.5% vs 1.2% |
| Draganov et al., *Phantom Transfer*, 2602.04899 `[摘要]` `核✓` | NeurIPS 2026 ✓（v3 comments：camera-ready） | 自然语言数据中的实体情感投毒 | **不论哪个模型生成数据、哪个模型训练都有效**；扛住 11 种数据级防御（含异模型全量改写）；可植入口令触发行为 |
| Casademunt et al.（LessWrong, 2026-09, MATS）| 博客 | phantom transfer 机制 | 极细微的语义线索；10 个学生模型都迁移；翻译成西语仍保留；数学/代码数据不迁移，Alpaca 最好 |
| Shah et al., *Covert Influence*, 2606.04071 `[摘要]` | 无 venue | — | **数字载体更隐蔽，但跨家族迁移比自然语言载体差** |
| Kim & Choi, *Subliminal RL*, 2610.41301 `[摘要]` | 无 venue | GRPO + LLM judge | 48 个设计格中 17 个迁移；异基座 judge 不迁移 |
| “Subliminal Signals in Preference Labels” | ICLR 2026 AIWILD workshop | 偏好标签 | 有偏 judge 通过二元偏好标签传特质，迭代对齐中增强 |
| Hatami et al., 2611.08538 | WACV 2027 ✓ | VLM | 最多约 10 个百分点 |
| Amjith, …, Torralba, Kim, 2611.31870 `[摘要]` | 无 venue | VLM → 扩散文本编码器 | 提出 weight lens 检测 |
| Vo et al., *Slow Decay*, 2609.25721 `[摘要]` | 无 venue | 10 代蒸馏谱系 | 表达衰减，但 probe 仍为正（潜在特质） |
| Tang & Yen, *Imprinting*, 2610.18517 `[摘要]` | 无 venue | 安全决策，**异基座学生** | 改写会附加改写模型自己的偏移 |
| Cho et al., 2608.30619 | EMNLP 2026 main（corpus ✓） | 社会偏见 | 创意写作 / 代码数据作为隐蔽通道 |
| Dong et al., 2608.26958 `[摘要]` | 无 venue | 数据缩放 | 数据越多，目标特质越凸显，跨模型也如此 |
| “Emergent Misalignment as Data-Mediated Transfer” | NeurIPS 2026（corpus ✓） | EM / SL | 首次比较 off-policy 与 on-policy 蒸馏 |

### 4.1 Beyond Owls 精读要点 `核✓`（补充仓库已有的 ICES 侧卡片 `../in-context-evidence-structure/beyond-owls-capabilities-backdoors.md`）
- **没有全参微调。** 学生全部是 LoRA；教师多数是 LoRA，但黑客倾向教师和采样版后门教师是 steering vector。
- **模型：** Qwen3.5-9B、Qwen3.6-35B-A3B、Qwen3.6-27B；跨模型学生是 Nemotron-3-Nano-30B-A3B。多数实验 3 seeds。
- **随机 MLP 函数**（4→16→16→4）：
  - 设置：教师 R² 0.92；用 25 万条三词续写 + 1 万条 Alpaca、**logit 蒸馏（top-32）**。
  - 结果：学生 R² 0.38，线性基线 0.27；**采样 token 版 R² 0.00**。
  - 注意：三个随机网络里只有一个在平均 R² 上超过线性基线（另两个 0.21 / 0.25 vs 0.26 / 0.27），所以“学到非线性结构”的证据是 1/3。不过网络 #2 的学生 MAE 略低于线性（3.24 vs 3.32），#1、#2 在第 2 个输出坐标上也超过线性。
- **数字母**（弱能力增强，采样 token）：
  - 结果：base 27.3% → all-linear 学生 44.1% → attention-only 学生 59.8%。（80.9% 是 **Nemotron** 直接在任务上训练的结果，不是 Qwen 的上限。）
  - 注意：attention-only 条件同时换了教师和数据，提升不能归给学生 LoRA 的位置。
  - 跨模型：Nemotron 学生 9.5% vs 对照 9.3%（base 9.8%），无迁移。
- **后门**（女性名字 → 用法语回答）：
  - 结果：logit 蒸馏 23.5%（三个 seed 分别 15.0 / 16.8 / 38.8%）；未见过的名字 20.2%；男性名字与无名字 prompt 都是 0%。
  - 注意：**教师 checkpoint 按女 / 男法语率差挑选（规则事先固定）；迁移数据先去掉与 base 相同的回答，再保留教师−base 对数似然差最大的 50%（约 9 万行）**，两步都偏向迁移成功。
  - 采样版：换成了 **steering-vector 教师**，学生是 rank-1 LoRA，**只有单次运行**；数据集 450 万行，约 340 万条后才首次出现法语；最终 8.5%，两个 checkpoint 之前是 17.0%。
  - 原文“50 倍”指的是数据集大小（450 万 vs 9 万行），**不是**受控的效率比；两臂的教师也不同。
- **国际象棋 agent 的黑客倾向**：
  - 结果：学生 58.3%，base 10.9%；对照组的数字在引言（7.3%）与 §7（10.9%）之间不一致。
  - 注意：教师本身就是 steering vector，等于把 Blank 的机制用在 agent 特质上。
- **steering-vector 基线**：分布内与学生持平（MAE 3.54 vs 3.73）；OOD（半整数、拼写出的数字）明显更差。
  - 注意：向量是直接在任务标签上训练的，学生是在教师分布上学的，信号不匹配，所以 OOD 差距也可能只是向量过拟合。
- **真正的新意**：首次显示学生**原本没有**的任务信息可以传递（随机函数、触发→行为的新绑定）。
- **最大的保留**：新信息只经 **logit 蒸馏**这一高带宽通道传过去；硬 token 通道上，传过去的只有已有能力的增强，以及一个很弱的、单次运行、换了教师的后门。硬 / 软两种通道的效率差距从未被受控测量过。

---

## 5. 防御与检测

| 防御 | 结论 |
|---|---|
| 关键词 / 动作过滤 | 失败（Cloud、Dang、Beyond Owls） |
| 改写 | 对 prompt 改写有效（Schrodi）；对自然语言数据多半失败（Phantom、Casademunt，翻译后仍保留、Imprinting） |
| 换基座 | 对数字数据有效；对自然语言 / LLS / 小 Pythia 无效 |
| mask divergence token | 有效，但需要反事实教师 |
| 数据归因（EK-FAC, Weckbecker 2609.20027） | token 级部分有效，样本级较弱 |
| KL 正则（liminal training） | 有效（Yanagisawa）↔ Feng“正则放大”，**冲突未解** |
| probe-space corridor（Liu） | 有效，但需要知道特质方向 |
| 多教师共识（Narang 2607.23394） | 摘要称有效 |
| 检测：SALVE 让模型说出特质（Hu, Koyejo, Potts 2609.16927） | 可恢复特质名 |
| 检测：无监督权重方向（Egan 2610.13536）、weight lens、梯度–向量相关（Hadley）、SBERT 签名（Jürß, MCC 0.83 / 0.46） | 早期 |

---

## 6. 关注度

- Cloud et al. 登上 *Nature*（2026-04），媒体报道广泛。
- 作者群：Anthropic Fellows、Truthful AI（Evans）、Nanda/Conmy 组、CMU Raghunathan 组、Columbia Hewitt 组、MATS、Redwood。
- venue corpus（主会议，标题或摘要含 subliminal）：2025 年为 0；2026 年 ICLR 3、ICML 1、NeurIPS 4、EMNLP 3；ICLR 2026 切片接收率 43%（基准 24%）。
- 没有找到 system card 或 AISI 文件点名 SL；工业动机主要来自合成数据与蒸馏管线。

## 7. 可复用资产

| 仓库 | 内容 | 成本 |
|---|---|---|
| github.com/MinhxLe/subliminal-learning（MIT） | 官方 生成→微调→评测 + MNIST；数据在 subliminal-learning.com/data | 单卡 A100-80GB |
| github.com/lmb-freiburg/divergence-tokens（MIT） | ICLR 2026 代码；6 个开源模型 | 单次 7B LoRA 运行单卡可跑（未核） |
| github.com/TruthfulAI-research/beyond_owls | Beyond Owls | 未核 |
| github.com/loftusa/owls | 纠缠 / subliminal prompting | 消费级卡 |
| PolyPythia / DataDecide | 同架构多 seed 的预训练模型（我们在 mechanism-population 线用过） | 小 |
