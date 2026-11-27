# CROSS F · 合成数据（更宽的 2024–2025 主干文献）

日期：2026-11-27。范围：合成预训练/中训练、合成持续预训练、规模与混合比例、推理合成数据的"格式 vs 内容"、坍塌 vs 累积、理论。是 `SCAN_2026-11_B` 的补充，不重复该文已读论文。
**阅读方式的诚实说明**：全文由 WebFetch 摘要器读 arXiv HTML，每篇只能看到前约 100k 字符，附录/证明多数未读（各篇注明）。摘要器偶有口误，下面凡带数字的地方来自摘要器转述的正文表格，未逐一回到 PDF 核对。无一篇仅读摘要。

---
## 一、全文读过（17 篇，按主题）

### A. 坍塌 vs 累积 vs 混合

**1. Is Model Collapse Inevitable? Breaking the Curse of Recursion by Accumulating Real and Synthetic Data** — Gerstgrasser 等，arXiv 2404.01413 v2（COLM 2024）。
- **问题**：合成数据不替换而是累积时还坍塌吗。
- **设置**：GPT-2(9M)、Llama-2(12M/42M/125M) 在 TinyStories(470M token) 上每代 1 epoch，温度 0.3/1.0；扩散(GeoDiff/GEOM-Drugs)；VAE(CelebA)。理论：脊回归、无岭、各向同性、每代 T 样本。
- **结果**：替换：测试交叉熵随代数升（GPT-2 9M，温度 1.0，t=4：+0.58，t=10：+1.09；温度 0.3，t=10：+8.04）；累积：t=4 为 −0.07。Llama-2 累积 −0.12~−0.14，替换 +0.53~+0.66。理论：累积误差 ≤ σ²d/(T−d−1)·π²/6，与代数无关；替换为 ·n 线性增长。把替换数据集放大到与累积等量（对照数据量）t=4 仍 +0.36。
- **局限（作者）**：合成采样为随机，确定性生成未测；不含过滤；VAE 在累积下误差仍缓升；Martínez 2023 在累积下快速恶化，差异未解决；"坍塌"定义不一。**我方注意**：理论里每代噪声独立同分布、真值固定，正是"生成器没有系统偏差"的假设；这正是后续文章（Dohmatob、Kazdan）补的口子。

**2. Collapse or Thrive? Perils and Promises of Synthetic Data in a Self-Generating World** — Kazdan, Schaeffer 等，arXiv 2410.16713。
- **问题**：Gerstgrasser 的结论在新任务、固定算力下是否成立。
- **设置**：多元高斯、KDE、Gemma-2 2B 在 HelpSteer2 上 SFT、线性回归、TinyStories；三种流程：replace / accumulate / accumulate-subsample（固定每代训练量）。
- **结果**：replace 崩（协方差→0，W2 发散），accumulate 稳；高斯累积的极限方差 σ₀²·sin(π/√n)/(π/√n) 有限；accumulate-subsample 介于两者，常平台但高于 accumulate。KDE 固定带宽下累积仍缓慢发散（Thm 6），带宽按 c(tn)^(−1/5) 缩小才有界。SFT：真实样本 ≤1024 时少量合成数据降低测试损失，>1024 时加合成数据多半有害；以 1/√n(真实) 为自变量 R²=0.59，按比例为 0.34。
- **局限**：无质量过滤；SFT 仅一个模型族一个数据集；"坍塌不太可能发生"是作者解读，非直接检验结果。

**3. Strong Model Collapse** — Dohmatob, Feng, Subramonian, Kempe，arXiv 2410.04840 v2（ICLR 2025）。附录/证明未读。
- **问题**：混合合成数据能否修复坍塌；大模型是否更易坍塌。
- **设置**：真实分布 P₁ 与合成分布 P₂ 协方差相同、标签函数差 δ~N(0,Δ)，合成质量 c²=tr(ΣΔ)/d；岭回归与随机特征（宽度 m）；MNIST 两层网络；GPT-2 在 BabiStories（合成数据来自在 BabiStories 上训的 GPT-2-small）。
- **结果**：各向同性、欠参数化下测试误差 ≈ σ²d/n + p₂²c²：存在与 n 无关的误差下限 p₂²c²（"强坍塌"），除非合成比例 p₂→0。最优单步混合权重 α* 在合成质量低时接近 0，任何固定 α>0 都留下 ≥p₂²α²c² 的下限。迭代混合需 ≈log(n/d) 轮，且要求清晰的来源标签、仍不优于只用真实数据。双下降：插值阈值 m=n 处发散，阈值之后更大模型更稳，之前更大模型放大坍塌；GPT-2 实验中更大模型在 >~3×10¹⁰ token 时放大坍塌、<~1×10¹⁰ 时更好。
- **局限**：高维渐近、高斯、线性/随机特征；只有标签偏移无特征偏移；语言实验只有一个数据集、一个生成器。

**4. Beyond Model Collapse: Scaling Up with Synthesized Data Requires Verification** — Feng, Dohmatob, Yang, Charton, Kempe，arXiv 2406.07515 v2（ICLR 2025）。约后 30% 未读。
- **问题**：用验证器选合成样本能否防坍塌、能超过真值标签吗。
- **设置**：理论：高斯混合 + 线性验证器 + 逻辑回归；p 为生成器标签错误率，φ/ψ 为验证器保留正确/错误样本的概率。实验：Transformer 求 5×5 对称矩阵特征值（≤10M 合成样本）；Llama-2-7B 在 XLSUM 摘要（生成器只在 12.5% 训练集上微调）。
- **结果**：存在**尖锐断点** p* = 1/(1+ψ/φ)：p<p* 时（无穷样本极限）准确率 100%，p>p* 时 0%（学到相反标签）；无筛选 p*=1/2，oracle p*=1。特征值任务：无验证时 10M 合成样本仍不如生成器；oracle 约使准确率翻倍；生成器 50 路 beam 里有 ~60% 含正确解（1% 容差；贪心 ~20%），但自身困惑度选不出。摘要：oracle（ROUGE-1）在每个选择率都胜生成器，12.5% 选择率下还胜用全部原始数据训练的模型；自选（最低困惑度）也胜生成器；**更强的 Llama-3 作验证器的效果接近随机选择**（尽管 ROUGE 更高），作者归因于 p* 低。
- **局限**：100% 是理想极限；只测"选择"；作者承认摘要里的自提升可能部分来自新输入文章（输入分布变了）。与 SCAN_B 的 2510.16657 互补（那篇给出长期不动点在验证器知识中心）。

### B. 预训练规模的合成数据

**5. Rephrasing the Web (WRAP)** — Maini 等，arXiv 2401.16380。末 20% 未读。
- **设置**：冻结 Mistral-7B-Instruct 把 C4 重写成 Easy/Medium/Hard/Q&A 四种风格（≤300 token），与真实 1:1 混合预训练 128M/350M/1.3B，Pile 20 个子集困惑度 + 13 个零样本任务。
- **结果**：约 3× 预训练加速；350M 用 ~15% C4+合成胜过用全 C4 的 1.3B；1.3B 综合理解平均 49.4%（合成+C4）对 47.4%（半个 C4，85B token）。消融：**纯合成**在 PhilPapers、Gutenberg 等域困惑度变差、零样本变差，需要真实数据；多风格混合困惑度略好、零样本无增益；重写器 Qwen-1.8B ≈ Mistral-7B > Vicuna-13B，微调 T5-base 最差但仍优于纯 C4；同义词替换/随机删除不如合成；无单一风格全域最优（oracle 选风格可再降 16% 困惑度）。
- **作者**：合成数据不能增加新事实知识，主要加速学习。**异常**：摘要说困惑度提升 >10%，第 4 节写 ~50%，二者不一致；生成 85B token 约 25K A100 小时。

**6. Nemotron-CC** — NVIDIA，arXiv 2412.02595。
- **设置**：Mistral NeMo 12B，top-p 0.9/温度 0.5；低质量文档用维基风格重写（336B 合成 token 对 403B 原始）；高质量文档用 Diverse QA、Distill、Extract Knowledge、Knowledge List（1537B 对 451B）；中等质量未重写；总 ~1.9T 合成 token。8B 模型 1T token 消融。
- **结果**：重写低质量：平均 52.5→54.0（+1.5），ARC/OBQA/CSQA +1.8~4.75，**MMLU 48.2→47.1**（作者怀疑合成引入错误信息）；把高质量数据 8 个 epoch 中 4 个换成合成：平均 55.8→56.7，MMLU 53.4→53.6，归因于新鲜 token 与 QA 风格。Nemotron-CC-HQ vs DCLM：MMLU 59.0 vs 53.4，平均 60.1 vs 57.0。15T token 的 8B 模型（含 7.2T 此数据集）：MMLU 70.3 vs Llama 3.1 8B 65.3（作者自己的评测环境）。
- **局限**：未验证改写事实性；未去污染；仅英文。

**7. BeyondWeb** — DatologyAI，arXiv 2508.10975。末 14% 未读；作者为卖策展平台的厂商。
- **设置**：1B(1T token)、3B/8B(180B token)；14 项基准；与 RedPajama、Nemotron-Synth、Cosmopedia v2 对比。
- **结果**：8B 平均 63.7（RPJ 56.6、Nemotron-Synth 61.1、Cosmopedia 58.6）；8B 达到 RPJ 180B-token 精度只需 23.2B token（7.7×）。消融（20B 预算，50:50）：全量 46.2、重复 2 次 45.5、朴素续写 46.2（可能被生成器见过源文污染）、BeyondWeb 50.4；种子质量：高质量种子 49.2，低质量种子 48.6，纯低质量网页 ~45.6；**重写器家族**：OLMo-2-7B 49.9 > Phi-4-14B 49.5 > Llama-3.1-8B 49.2 > Mistral-7B 48.9，作者称生成器基准强度不预测合成数据质量；**重写器大小**（Llama-3）：1B 47.3、3B 48.8、8B 49.2（3B→8B 仅 +0.4）；会话式内容网页里只占 2.7%，抬到 50% 5-shot 从 43.2 到 44.1，>20% 饱和；Cosmopedia、QA 风格在长训练中平台或过拟合。
- **局限**：作者承认结论"特定于本设置"；主数据集用哪个重写器正文不清；1B 训练达 ~50× Chinchilla。

**8. Demystifying Synthetic Data in LLM Pre-training** — Kang 等（Meta FAIR），arXiv 2510.01631。（SCAN_B 只在背景里提过未读，此处读了。）
- **设置**：Llama-3 风格 100M–3B 从头训，几百个模型；合成类型 HQ 重写、QA 转换、合成教科书(TXBK)；生成器主要 Mistral-7B-Instruct-v0.1，消融用 Llama-3 3B/8B/70B；指标是 14 个 Pile 域 + WikiText-103 的验证损失，不是下游基准。
- **结果**：纯重写数据并不比自然网页快；**1/3 重写 + 2/3 自然**在大预算下加速 5–10×；最优合成占比 HQ 约 30%，QA 随规模从 ~50% 降到 ~30%，TXBK 小规模 <5%、随规模上升；纯 TXBK 损失明显更高，33% TXBK 在 ~20B token 后胜 CC，67% 不如 CC；拟合的规模律预测 200B-token 运行误差 0.41%，3B 模型 0.30%；8B 生成器优于 3B，**70B 并不更好，HQ 上更差**；纯 QA 外各混合的估计不可约损失低于纯 CC。
- **作者**：结论仅对单轮（n=1）训练；TXBK 混合出现坍塌文献所预测的模式；规模仅到 3B/200B token；总数在摘要（>1000 模型）与正文（~600/~700）之间前后不一，我方存疑。

**9. On the Diversity of Synthetic Data and its Impact on Training LLMs** — Chen 等，arXiv 2410.15226 v2。末 50% 未读。
- **指标**：LLM Cluster-agent：LLM 生成聚类标准，对批量文本聚类并自检，得分=簇数/每簇样本数的平均，与启发式（自重复、n-gram、压缩比）、模型型（困惑度、K-means on BERT）对比。
- **设置**：350M/1.4B Llama 风格；真实数据 34B token（网页:代码:数学=4:1:1）；GPT-4o 以 620K 维基主题合成；预训练 50B/150B token；SFT 用 Alpaca+FLAN。
- **结果**：该分数与预训练和 SFT 平均成绩正相关（回归线，正文摘录无相关系数）；更多主题提升多样性，每主题生成数先升后饱和或下降；Topic+Style+Persona 提示 350M 预训练平均 51.92 对 Cosmopedia v0.1 51.61，1.4B SFT 61.32 对 59.46；Cosmopedia v0.2 提示更好但多样性更低；GPT-4o > GPT-3.5，Llama-3.1-8B-Instruct > Mistral-7B-Instruct，混合生成器略好；**合成 token 到约 20B 时准确率升，到 ≥~34B 时骤降**。
- **局限**：≤1.4B；生成器比较只在 350M；指标依赖 LLM 判断；相关性建立在少量点上。

**10. Scaling Laws of Synthetic Data for Language Models (SynthLLM)** — Qin 等，arXiv 2503.19551 v3。
- **设置**：从 FineWeb-Edu 里筛约 520K 数学文档；三级问题生成（L1 抽取改写；L2 单文档概念重组；L3 全局概念共现图随机游走、两文档接地）；Mistral-Large 出题、Qwen2.5-Math-72B 答题，**不验证**；Llama-3.2-1B/3B、Llama-3.1-8B SFT，共 7.4M 样本。
- **结果**：合成数据符合 rectified scaling law L(D)=B/(D_l+D^β)+E；1B 的衰减指数 β≈0.34（受益于更多合成数据较少）；约 300B token 后收益递减，外推 8B 在约 1T、3B 在约 4T 触顶；SynthLLM-8B 在 MATH 71.3，六基准平均 54.9（OpenMathInstruct-2-8B 为 50.3，Llama-3.1-70B-Instruct 为 54.2）。
- **局限**：数学为主；每文档只生成 5（L3 为 3）题；答案未验证（作者称过滤只带来边际收益）；触顶点是外推。

### C. 知识：能否超出源/生成器

**11. Synthetic Continued Pretraining (EntiGraph)** — Yang, Band, Li, Candès, Hashimoto，arXiv 2409.07431 v2（ICLR 2025）。后 53% 未读。
- **设置**：QuALITY 265 篇、1.3M token；4609 道四选一题（改写成无需原文即可作答）；GPT-4-turbo 提实体并写实体对/三元组文本，共 455M token；Llama 3 8B Base，2 epoch，混 RedPajama 回放。
- **结果**：闭卷 39.49%→56.22%（GPT-4 51.30%，GPT-3.5 44.81%）；对合成 token 数**对数线性**增长至 455M；原文继续预训练不如基座，Rephrase 扩展差（止于 38M）；RAG：EntiGraph+RAG 62.60% vs 基座+RAG 60.35%；EntiGraph 单独增益 16.73 点，约占 RAG 增益 20.86 点的 80%；指令微调后摘要幻觉率只轻微上升。数学模型：实体关系随机有向图，合成过程沿路径增加可达关系，推出三段曲线（近线性、对数线性、平台）。
- **作者明说**：EntiGraph 不增加源之外的事实，只重排；生成器 GPT-4 的蒸馏不能解释（训练后超过其闭卷准确率）；**让模型自己生成训练数据未测**，留作未来工作；手工查部分书未发现事实错，怀疑与生成器强有关。

**12. Physics of Language Models, Part 3.1: Knowledge Storage and Extraction** — Allen-Zhu & Li，arXiv 2309.14316（ICML 2024）。末 25% 未读。
- **设置**：bioS（10 万人，6 属性，每属性 ~50 模板）与 bioR（Llama 生成）；GPT-2 式从头训练；对未见过的人做 QA，精确匹配。
- **结果**：只对 bioS single（每人 1 条）预训练再 QA 微调，对留出者 QA 0%（传记逐字记忆近完美）；每人 5 条多样改写：QA 微调 9.7%→96.6%；单做多重性 ~41%，单做排列+重复句 ~70%（起点 4.4%），排列加到单条上反而变差；混合训练（全部传记 + 半数人的 QA）：OOD QA 86.6%(bioS single)/77.7%(bioR single)；P-probing 显示充分增强时属性可由姓名 token 线性读出，Q-probing 与 QA 准确率高度相关，推出"知识必须存在名字 token 上"；**名人**增强传记使少数人群 QA 4.4%→86.8%(bioS)/10.0%→76.3%(bioR)，但需与目标格式相似，WikiBook 无效；BERT 式（MLM）对多词属性差。
- **局限**：模板化、均匀属性采样、小模型；精确匹配评分；bioR 只有一个 Llama 分布。

### D. 推理合成数据：格式与内容

**13. LLMs Can Easily Learn to Reason from Demonstrations: Structure, not Content, is What Matters** — Li 等，arXiv 2502.07374。
- **设置**：Qwen2.5-32B-Instruct，~17k 条 R1 长 CoT（另有 QwQ 的 12k 数学 + 5k 代码），全参数或 LoRA(rank 64)。
- **结果**：AIME24 56.7%（+40.0）、LCB 57.0、MATH-500 90.8、AMC23 85.0、OlympiadBench 60.3；LoRA 7k 与 17k 相当。4618 条子集扰动（正确 trace 平均 66.3）：**最终答案错** 63.1；**70% 数字被篡改** 62.0（全部篡改 2.7）；去掉全部反思关键词 63.0；**步骤全打乱** 56.1，删光步骤 49.5，插入其他 trace 步骤（100%）44.5。结论：全局逻辑结构 > 局部正确性。
- **局限**：只测数学/代码；**未报种子方差**；8 个学生模型中 7 个明显提升；Best-of-N 超过 128 时可能追平。

**14. LIMO: Less is More for Reasoning** — Ye 等，arXiv 2502.03387。
- **设置**：2125 题中选 800（页面写 800，非 817）；用 Qwen2.5-Math-7B-Instruct 滤掉易题，DeepSeek-R1-Distill-Qwen-32B 采样 32 次保留只解对 1–3 次者；解答按规则打分（长度 30%、验证词 20%、试探词 25%、连接词 25%）；Qwen2.5-32B-Instruct 全参 SFT，15 epoch。
- **结果**：AIME24/MATH500/AMC23 = 63.3/95.6/96.3（均值 78.1），对 QwQ-32B-Preview 66.9、OpenThoughts(114k) 58.3、NuminaMath(100k) 32.3；链质量由高到低单调下降；最难集 500 题 AIME24 51.5；**预训练知识库**：Qwen2.5 63.3% vs Qwen1.5 9.2%；模型规模 3B 2.5 → 72B 68.3；400 样本 57.5，800 后趋平，2k 为 69.6。
- **局限**：单一模型族；筛题依赖特定模型；AIME 等小基准每题只采 4 次；对比模型配方不同；摘要的"45.8% OOD"未能在表中核实。

**15. Beyond Semantics: The Unreasonable Effectiveness of Reasonless Intermediate Tokens** — Valmeekam, Stechly, Kambhampati 等，arXiv 2505.13775 v4。末 20% 未读。
- **设置**：~380M Qwen2.5 式小 Transformer 从随机初始化，30×30 迷宫最短路径，50 万题的 A* trace + 计划，形式化验证器判 trace 有效性。
- **结果**：Wilson 训练模型 Wilson 迷宫计划准确 79.9%，其正确计划中 97.7% 的 trace 有效；**交换 trace**（每题配另一题的 trace，trace 有效率 0%）的模型持平或更好（Drunkard 迷宫 11.7% vs 0.0%；Searchformer 式 95.4% vs 62.1%）；不给 trace 只给解：Wilson 10.0%；GRPO 提高计划准确率但 trace 有效率不一定提高（正常模型的 trace 有效率从 80% 多降到 40–50% 多）；trace 长度与 A* 长度几乎不相关（r≈0.008、0.02）。
- **局限**：单一可验证任务、小模型；预训练模型(Qwen3 8B)实验有混杂，未给细节。

### E. 理论

**16. Towards a Theoretical Understanding of Synthetic Data in LLM Post-Training: A Reverse-Bottleneck Perspective** — Gan & Liu，arXiv 2410.01720 v3（ICLR 2025）。附录 G 未读。
- **设置**：S_anchor→提示 p→S_gen 构成马尔可夫链；生成器 M；信息增益 ΔI = H(M(p)) − I(h(e_p),M(p))（生成器在提示之外贡献的信息）；压缩瓶颈 B_syn；GGMI = I(S_anchor,W′) − I(S_gen,W)。
- **结果**：学习器在合成数据上的泛化间隙 ∝ √(2σ²[−ΔI + B_syn + H(e_M) + δ]/n) + 任务/生成分布 TV 距离项；n 越大越紧，但 ΔI、B_syn、H(e_M) 决定水平；生成器熵 H(e_M) 越大界越松（建议选与任务对齐的生成器）；Thm 4.10 用 ΔI、ΔH=H(S_anchor)−H(S_gen) 等界 GGMI。验证只有 2D GMM（K=J=L=2，各取 2–15，100 轮）：J↑ gap↑，K 或 L↑ gap↓；作者自陈没有真实 LLM 验证。
- **局限**：σ-次高斯、收缩层、可逆提示映射等强假设；ΔI、H(e_M)、λ 不可测；推导符号有处含糊（把不等式当等式再定义 δ）。**我方注意**：这是"生成器贡献信息 ΔI"的形式化，但 ΔI 不可测，所以它说"需要什么"但不给"如何测"。

**17. Self-Improvement in Language Models: The Sharpening Mechanism** — Huang 等，arXiv 2412.01951（ICLR 2025）。后 59% 未读。
- **设置**：自奖励 r_self=log π_base(y|x)，目标是序列级 argmax y*(x)；"(ε,δ)-锐化"；采样-评估框架。算法 SFT-Sharpening（best-of-N 后微调）与 RLHF-Sharpening（KL 正则最优解 ∝ π_base^{1+1/β}，DPO/XPO 实现）。
- **结果**：覆盖系数 C_cov=E[1/π_base(y*|x)]，下界样本复杂度需随 C_cov 与 log|Π| 增长；SFT-Sharpening 在可实现性下达到下界（对数因子内）；XPO 把 C_cov 换成 SEC（线性 softmax 下 Õ(d)，C_cov 可指数大），收益可指数；实验：best-of-N（N≤50）用对数似然作自奖励通常胜贪心，N≈10–20 饱和；基模型弱或判据偏短回答时 N 增大反而降；正确回答的对数概率随机占优于错误回答；训练期 SFT-Sharpening 在约 256 例/任务上有正效果。
- **作者明说**：锐化只能提取模型已有的"隐含知识"，不产生新信息；与数据处理不等式不矛盾。
- **局限**：可实现性、覆盖、边际假设；只分析对数似然自奖励；经验上只展示相关性。

---
## 二、其他论文（短表，仅摘要或未读）

| 论文 | 来源 | 一行 | 状态 |
|---|---|---|---|
| Cosmopedia / Phi 教科书系列 | HF blog、Phi-1/1.5 | 前者开放的大规模合成教科书；多篇（BeyondWeb、Kang、Chen）把它当基线并报告长训练平台/过拟合 | 未读原文，仅经上述三篇转述 |
| Physics of LM Part 3.2/3.3 | Allen-Zhu & Li | 知识操纵（需 CoT）、知识容量（~2 bit/参数） | 未读 |
| Small Models Struggle to Learn from Strong Reasoners / weak-to-strong 相关 | 2025 | 未检索确认 | 未读 |
| Ferbach 等 "Self-consuming generative models with curated data" | 2024 | Strong Model Collapse 的迭代混合分析引用其 | 仅转述 |
| Statistical Analysis of Synthetic Data with Verification: A Linear Regression Framework | arXiv 2610.40254 | 搜索结果所见，与 Feng/2510.16657 同线 | 仅标题 |

---
## 三、事实：共识与争议

**较一致**
1. **替换式闭环发散，累积式有界**（Gerstgrasser、Kazdan 理论与小规模实验一致）；但累积有界依赖"每代噪声独立、真值固定、无系统偏差"。一旦合成分布与真实分布有系统偏移（标签函数差 Δ），出现与 n 无关的误差下限 p₂²c²（Dohmatob）。两篇不矛盾，是不同假设下的两个结论。
2. **纯合成不如混合，混合比例有内点最优且随规模/类型变化**（WRAP 纯合成变差；Kang HQ ~30%、TXBK <5% 起；Chen 20B 升 34B 降；BeyondWeb 会话占比 >20% 饱和）。
3. **生成器大小/强度不单调预测数据价值**（BeyondWeb：1B→8B 仅 +0.4~2；Kang：70B 不比 8B 好；SCAN_B 的 FinePhrase：1B>27B；WRAP：Qwen-1.8B ≈ Mistral-7B > Vicuna-13B；Feng：更强 Llama-3 作验证器近似随机）。注意是"在重写/转换类任务上"。
4. **重写类合成数据不增加源外事实**（WRAP、EntiGraph 作者自述；Nemotron-CC 低质量重写 MMLU 下降，作者怀疑错误信息），收益来自改变信息的呈现形式：加速、换格式、提高可提取性。
5. **知识可提取性依赖表示多样性而非单纯暴露**（Allen-Zhu & Li：同一事实单一表述→QA 0%，5 种改写→96.6%；EntiGraph 对数线性）。
6. **推理 CoT 数据的收益主要在结构/格式一致性，不在局部语义正确**（Li：错答 −3.2、篡改 70% 数字 −4.3、打乱步骤 −10.2；Stechly：交换 trace 反而更好）。
7. **验证器偏差决定上限，且更强的模型不等于更好的验证器**（Feng p*；SCAN_B 的 2510.16657）。

**争议/未解**
- **"少量高质量即可"vs"规模"**：LIMO（800 条 AIME 63.3）与 Li（7k LoRA ≈ 17k）都依赖强预训练基座（LIMO：Qwen2.5 63.3 vs Qwen1.5 9.2）；两者的数据都由更强教师（R1/QwQ）生成，不是自生成。
- **多样性指标是否预测效果**：Chen 的 LLM-cluster 分数与效果相关，但点数少；Cosmopedia v0.2 提示更好却多样性更低，指标与"提示质量"的关系不一致；BeyondWeb 与 SCAN_B 的 FinePhrase 又显示模板遵从率与效果不一致。未见有人把多样性指标放进反事实干预（固定内容、仅改多样性）里检验。
- **自生成能否净增**：EntiGraph 作者说未测；Feng 的摘要自选胜生成器但可能来自新输入；sharpening 理论只许"提取已有"。无 ≥7B 规模、多代、无外部强教师的净增实验在本次所读文献里出现。
- **规模方向**：Dohmatob 的双下降给出"阈值前大模型更差、后更稳"；SCAN_B 中同一过滤 3B 有益 8B 有害；二者是否同一机制未核对。
- **摘要器转述中的内部不一致**（WRAP 的 >10% vs ~50%；Kang 的模型数；LIMO 的 800 vs 817；BeyondWeb 图注 46.8 vs 47.1）：数字使用前须回 PDF。

**论文自己报告却未解释的**
- Nemotron-CC：重写低质量使 MMLU 降而 ARC/OBQA 升。
- Stechly：RL 后准确率升而 trace 有效率降；交换 trace 模型在分布外更好。
- Allen-Zhu：排列增强在没有多重性时反而变差。
- Kazdan：真实样本 >1024 时加合成数据有害，≤1024 时有益，转折点未解释。
- BeyondWeb：朴素续写与重复 2× 无差别，但此处可能被生成器见过源文污染。

---
## 四、可能与 data-centric RSI 的联系（**推测，非结论**）

按 brief 的现象编号：

**现象 5（验证器不动点）/ 现象 6（自评奖励被利用）**：Feng 的尖锐断点 p* = 1/(1+ψ/φ) 提供一个**可在训练前计算**的量：只需验证器对"对/错生成"的保留率比 ψ/φ（用少量带真值标注估计）。推测：RSI 回路里"gate 开关决定稳定性"（现象 1）可以在这个量上定量——gate 严格度 ε 变化时 p* 跨过生成器当前错误率 p 即发生相变；Survive or Collapse 的"低 ε 时训练侧指标先脱钩、验证后掉"与 p 接近 p* 时的临界行为形态相似。可检验：在已有的 proposer–solver 回路中估计 ψ/φ 与每轮 p，看崩溃点是否落在 p≈p*。又：Feng 里 Llama-3 作验证器 ≈ 随机选择，与现象 6/9 "judge 集成共享假阳性"同向：验证器的价值取决于它与**生成器错误**的相关性，而不是自身强度。

**现象 1（泄漏 5% 解耦、20–40% 突变）**：Dohmatob 的 p₂²c² 下限和 Kazdan 的"真实样本>1024 后合成有害"都说明**固定比例的有偏数据产生不随 n 消失的下限**，且存在由数据量决定的转折点。推测：泄漏比例 5%→20–40% 的突变可能是"有偏分量的下限项超过噪声项"的交叉点；可检验：在不同训练池大小下重复，看突变阈值是否随 n 移动（若如 σ²d/n vs p²c² 则阈值随 n 变）。

**现象 2（选择≠学习）/ 现象 3（上升–平台–下降）**：EntiGraph 的数学模型（可达关系沿图路径增加，三段曲线：线性→对数线性→平台）给出"信息有限的种子 + 重组"的饱和形式；SynthLLM 的 rectified law 也在 ~300B 后收益递减。推测：RSI 里"learnable information 降到 0"可能就是 EntiGraph 式平台：回路里的生成器只重排了其起点已有的关系，可达关系集合耗尽。可检验：把回路每轮新增数据映射为"新增关系数"，看是否符合 1−exp 型饱和；平台高度是否由种子（含生成器知识）决定。**与"下降"不同**：EntiGraph 的平台不下降，下降需要偏差项（Dohmatob）。因此"上升–平台"与"下降"可能由两个不同项产生（饱和 vs 偏差累积），可以用该两项的不同规模依赖（n 或 TPP）分开。

**现象 4（improver 增益缺失）**：Gan–Liu 的 ΔI（生成器在提示之外贡献的信息）与 sharpening 的 C_cov 是两个相反的视角：前者要求生成器**有**额外信息，后者说自奖励只能抽取已有信息，且样本复杂度随 1/π_base(y*) 增长。若 improver 是同一个模型，ΔI 在信息论意义上无来源，improver 能改进的只可能是"提取效率"（锐化）。推测：improver 增益测量应分两类——(a) 提取型（把已有但低概率的 y* 抬高，可用 C_cov 衡量；预测增益在 best-of-N 饱和处 N≈10–20 耗尽）；(b) 增信息型（需外部来源）。已读文献里没有 (b) 的自生成例子。

**现象 7（多样性坍塌）**：Allen-Zhu 的结果说明"多样表述"本身就是知识可提取性的**因果**条件（5 改写 96.6% vs 单条 0%），而非只是质量指标；与 Chen 的"主题数 > 每主题生成数"一致：多样性来自输入分布（种子/主题/人设）而非生成器采样温度。推测：RSI 里生成器的模板坍塌会直接削弱 learner 的可提取性，即使每条数据"正确"（与 SCAN_B 的"入选集合变干净但仍退化"相容）。可检验：固定事实集，仅改变表述多样性，看 learner 提取率。

**现象 8（生产者强度不预测数据价值）**：本文读到的证据比 SCAN_B 更多——BeyondWeb（家族与规模）、Kang（70B ≤ 8B）、WRAP（小重写器可行）、Li/Stechly（错或无意义的 trace 也有效）。推测一个统一解释（未检验）：数据价值 ≈ 与学习器已有分布的**可吸收性**（风格/结构一致，Allen-Zhu 的名人格式相似才有效；Stechly 的 trace 一致性），而非对世界的正确性。于是失败轨迹优于仅成功（brief 里观察）可能因为它们更接近学习器的分布。

**现象 9（噪声与适应性过拟合）**：读到的多数论文（Li、LIMO 的 4 采样、Stechly）不报种子方差；BeyondWeb 是厂商；LIMO 的筛选依赖特定模型。属于该领域的同类风险，但这里未做量化。

**现象 10（偏差传递）**：Dohmatob 的"标签函数差 Δ"只涉及任务标签，不涉及安全行为；没有读到与现象 10 直接对应的合成数据文献。但 Stechly 的结果提示：形式（trace）可以不携带对应语义，因而"能力指标不变、安全行为漂移"可能是同一类现象——学习器学的是分布一致性而非语义。仅为类比。

**未列入 brief 的现象**
- **来源标签/可识别性**：Dohmatob 的迭代混合只有在有"清晰来源标签"时才能恢复；RSI 回路里真实与合成混在一个池里是否可区分，决定恢复界。
- **单轮结论外推到多轮的缺口**：Kang、WRAP、BeyondWeb、Nemotron-CC 都是单轮（n=1），明确不覆盖多代；坍塌文献又多在小模型/小语料。把单轮"1B 重写器优于 27B"当作多轮回路性质需要实证。
- **数据量里的"相变点"**：Chen（合成 token 20B→34B 骤降）、Kazdan（1024）、Dohmatob（3×10¹⁰/1×10¹⁰ token）都给出以 token 数为轴的转折，且来自不同机制。

**"生成器要增加超出自身的信息，这些论文说需要什么？"（推测性汇总）**
1. **外部信号进入通道**：验证器必须含有生成器没有的信息（Feng：p* 取决于验证器与真值的夹角；2510.16657：不动点在验证器知识中心）。强度不是条件，与生成器错误的**去相关**才是。
2. **种子/输入分布变化**：EntiGraph、SYNTH 的知识上限由种子决定；Feng 的摘要自提升可能来自新文章。即"新输入"本身是信息源。
3. **组合性而非事实**：EntiGraph 与 Kabra（SCAN_B）里信息增量是"关系重组/技能"，不是源外事实。能增加的是**可达/可提取**信息，不是生成器的事实库。
4. **对生成器内部信息的提取**：sharpening 说只能提取，且代价 ∝ 1/π_base(y*)；若 y* 概率极低则不可行。
5. **形式上**：Gan–Liu 的 ΔI>0 才能抵消界里的 B_syn+H(e_M)；但没有可测估计量，且未做真实 LLM 验证。
6. **规模条件**：Dohmatob 的下限 p₂²c² 说明只要合成偏差 c²>0，且 n 足够大，噪声项被压下后偏差项就主导；增益只能出现在 n 小（真实样本 ≤1024 的 Kazdan 观察）或偏差为零（oracle）的区间。

**可能的测量/方法（推测）**：(i) 在回路中每轮估计 ψ/φ 与 p，监测 p*−p 边际；(ii) 把每轮新增数据拆成"新可达关系数"与"偏差项"，分别拟合饱和与累积；(iii) 固定事实、改多样性的因果实验；(iv) 对 improver 的增益区分"提取型 vs 增信息型"，前者用 best-of-N 饱和点和 C_cov 估计作基线；(v) 做出"单轮结果能否外推到多代"的受控检验（同一重写器，1 代 vs 5 代，≥1B 规模）。

---
## 五、本次未覆盖
- Phi 系列、Cosmopedia 原文、Physics of LM 3.2/3.3、weak-to-strong 相关论文未读。
- 各篇附录与证明（Dohmatob、Gan–Liu、sharpening、Feng 后段、EntiGraph 后半）未读。
- 摘要器可能引入口误，所有数字使用前请回原文核对。
