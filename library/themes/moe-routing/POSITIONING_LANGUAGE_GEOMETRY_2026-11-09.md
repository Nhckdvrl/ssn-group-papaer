# 稠密多语几何 × MoE 语言路由 定位扫描（2026-11-09）

**只写定位，不写判决（R6）；不判死（R1）；去留由人定（R2）。** 触发：E178（`workbench/mechanism-population-dynamics/division/DIRECTION_2026-11-06.md` §15.1，`division/results/e178/tables.md`）——Qwen3-30B-A3B、FLORES-200 20 语：随机路由器在同一隐状态上复现"首尾层语言专属、中层共享"层剖面（U 对比 T 2.35 / N_A 2.34 / N_B 2.34；剖面 Spearman T vs N_B .95），训练路由器只多乘一个与深度无关的常数（T/N_B 中层 1.58×、首尾 1.61×）。MoE 零模型文献（Melton、Myth、Standing Committee 等）已在 `POSITIONING_NULLAUDIT_2026-11-09.md`，本文不重复。
**证据标签：** `[全文]` 读了 HTML 全文并核对引文 / `[节]` 读了相关节 / `[摘要]` 只读 arXiv 摘要 / `[检索]` 只来自检索摘录；"未核对"= 没拿到原文。arXiv id 均经 arXiv API 核对标题与第一作者。按 R10 不纳入 EACL 文献（如 2510.07213）。
**检索范围：** venue corpus `query.py nearest` 2 句（MoE 语言路由跟随残差流几何；稠密逐层语言可分性）；Web 检索 9 组（MoE 语言路由 × 隐状态几何 / 随机路由器 / 逐层语言探针 / 语言混淆 / 语言神经元批评 / 语言注意力头 / NLLB-200 §6.2.4）；WebFetch 读 2510.04694、2601.14050、2604.03592、2605.29714、2609.04819、2502.15603、2402.13089 原文。未覆盖：OpenReview 未挂 arXiv 的投稿、引用链。

## 1. 稠密模型的多语逐层几何

**一句话：** "首尾层语言专属、中层共享（偏英语或语言无关）"在**神经元计数、logit lens、跨语相似度 / 共享度**这三类读数上是稠密文献的共识，2024 起至少 6 篇主会论文独立报告；但在**全维线性可分性**上不成立——全维探针在每一层都能 >.9 认出语言，中层的"共享"是方差主方向上的共享（见 1b）。

### 1a. 报告 U 形 / 三段式的工作

| 工作（证据） | venue / 年 | 模型 | 逐层读数 | 是否 U 形 | arXiv |
|---|---|---|---|---|---|
| Wendler 等, Do Llamas Work in English? `[摘要]` | ACL 2024 | Llama-2 7/13/70B | logit lens：中间嵌入解码为英文 vs 输入语言的概率；token energy | **三段式**：输入空间 → 中层"概念空间"偏英语 → 末层进入输入语言区域 | 2402.10588 |
| Zhao 等, How do LLMs Handle Multilingualism?（MWork）`[摘要]` | NeurIPS 2024 | Llama-2、Mistral、BLOOMZ 等（未核对全表） | 逐层解码 token 的语言比例；PLND 语言专属神经元，逐层停用 | **是**：首层理解并转向英语、中层用英语"思考"、末层回到原语言 | 2402.18815 |
| Tang 等, Language-Specific Neurons `[摘要]` | ACL 2024 | LLaMA-2、BLOOM、Mistral | LAPE（语言激活概率熵）选出的语言专属神经元的层分布 | **是**："primarily situated in the models' top and bottom layers" | 2402.16438 |
| Kojima 等, Finding and Controlling Language-Specific Neurons `[摘要]` | NAACL 2024 | XGLM、BLOOM、Llama-2（6 语） | 语言专属神经元（跨语重叠 <5%）的层分布 | **是**："mainly distributed in the models' first and last few layers"，跨语言跨模型一致 | 2404.02431 |
| Schut 等, Do Multilingual LLMs Think In English? `[节]` | 2025（venue 未核对） | Aya-23-35B、Llama-3.1-70B、**Mixtral-8x22B**、Gemma-2-27B | logit lens：实词在中层先以英文出现 | **部分**：只报中层偏英语，原文不把首尾层称为语言专属；Mixtral 未分析路由 | 2502.15603 |
| Dumas 等, Separating Tongue from Thought `[摘要]` | ACL 2025 | Llama-2 等 | 激活修补：输出语言 vs 概念在哪层编码 | 间接：语言比概念更早编码；有语言无关概念表征 | 2411.08745 |
| Wu 等, Semantic Hub Hypothesis `[读数凭记忆，未核对]` | ICLR 2025 | Llama-2/3 等 | 中层跨语 / 跨模态表征相似度；logit lens | **是**（中层共享"语义枢纽"，首尾按语言 / 模态） | 2411.04986 |
| Liu & Niehues, Middle-Layer Alignment `[摘要]` | ACL 2025 | 多个指令模型 | 逐层跨语表征相似度 | 中层最对齐（只报中层峰值） | 2502.14830 |
| Riemenschneider 等 `[摘要]` | ACL 2025 | 3 个多语 LM 的预训练轨迹（含 BLOOM-560M） | 逐层语言识别探针 × 训练步 | **随训练出现**：早期各层同样可识别语言，后期中层语言信息减弱、末层保留 | 2506.01629 |
| Tamo 等, LinguaMap `[摘要，venue corpus]` | ICLR 2026 | Qwen3-32B、BLOOM-7.1B | 逐层语言概率（logit lens）+ 跨语隐状态相似度 | **三段式**：早层对齐到共享语义空间、中层推理、晚层语言专属生成 | 2601.20009 |
| Harrasse 等, Cross-Layer Transcoders `[摘要+检索]` | arXiv 2025（在审） | 自训多语配比模型 | CLT 特征、归因图；逐层多语熵 | **是**（检索摘录称多语熵 U 形）；无英语训练时结构相同 | 2511.10840 |
| Nie 等, Mechanistic Language Confusion `[摘要]` | EMNLP 2025 Findings | 英语中心 LLM | TunedLens：混淆点上的逐层语言 | 末层"转换失败"导致语言混淆 | 2505.16538 |
| Tezuka & Inoue, Transfer Neurons `[检索]` | EMNLP 2025 | 多语 LLM（未核对） | 在语言专属空间与共享空间之间搬运的神经元 | 是（前提即三段式） | 2509.17030 |

### 1b. 反例 / 读数依赖（对 E179(b)"直接量几何"最要紧）

| 工作（证据） | venue / 年 | 模型 | 发现 | 对我们的含义 | arXiv |
|---|---|---|---|---|---|
| Holmström 等, Anisotropy-Driven Failures `[节]` | arXiv 2026-09 | 21 个模型 / 5 家族，含 **Qwen3**、BLOOM、SmolLM3 | 共享度指标（λ、ILO）逐层呈倒 U；但在高共享层"principal-subspace accuracy drops to chance levels, while residual-subspace accuracy reaches 96–99%"——"Language identity is not destroyed at sharing layers; it is relocated" | 中层"共享"= 方差主子空间里没有语言；全维仍可分。随机路由器（Haar 旋转保奇异值）读的是哪种几何，必须在 E179(b) 同时报**方差加权**（质心距离 / 主子空间）和**全维探针**两种 | 2609.04819 |
| Bayazit 等, Lingua Franca or Probing Artifact? `[摘要]` | EMNLP 2026 Findings | 多家族、多 checkpoint、≤27 语 | 几何型探针（GMM）比解码型探针（logit lens）更早显示跨语混合；两类探针系统性不一致 | "U 形在哪几层"取决于读数 | 2609.00155 |
| Libovický 等, Language Neutrality `[摘要]` | EMNLP 2020 Findings | mBERT 等 | 语言识别探针在各层都高；减语言均值后才"中性" | 全维语言身份一直在 | 2004.05160 |
| Chang 等, Geometry of Multilingual Representations `[摘要]` | EMNLP 2022 | XLM-R | 均值中心化后各语言占相似线性子空间；语言敏感轴"relatively stable throughout middle layers"，与语言中性轴正交 | 语言 = 均值平移 + 正交轴，给出"随机投影读到语言"的几何机制 | 2205.10964 |
| Xie 等, Low-rank Language Subspaces `[摘要]` | EMNLP 2022 | mBERT、XLM-R 等 | 语言身份集中在低秩子空间，投掉后得到语言无关表征 | 同上；低秩 → 随机投影高概率碰到 | 2401.05792 |

## 2. 有没有人把稠密几何接到 MoE 路由层剖面上

**答：有人用一句话这样解释过（Bandarkar 本人），有人给过一般性论证（Myth），没有人做过检验。** 扫描范围内没有任何工作在多语 MoE 上（a）对语言路由跑随机 / 旋转路由器或探针对照，或（b）把逐层路由语言专属度与逐层表征语言可分性放在一起比。

| 工作（证据） | venue / 年 | 模型 | 原文怎么解释层剖面（引文） | 对照 | 距离 |
|---|---|---|---|---|---|
| **Bandarkar 等, Multilingual Routing in MoE** `[全文]` | ICLR 2026 | OLMoE、Qwen3-30B-A3B、Phi-3.5-MoE、GPT-OSS-20B | §4.3："This aligns with findings from dense LLMs that reveal language-universal representation spaces in the middle layers of LLMs." / "If the representations are aligned, the routing would also be." / 中层："other factors, perhaps semantic ones rather than lexical ones, determine routing here." / 首尾层："token overlap and structural similarity lends itself to shared parameterization."；结论："experts in the middle layers serving as language-universal mechanisms for multilingual generalization"；"a causal relationship between cross-lingual routing alignment and cross-lingual transfer"（来自干预实验） | 路由散度**无**随机路由器 / 置换 / 隐状态对照；只有换参照语言（中、法）、熵归一化、语系混杂检查；干预部分有随机子集停用 | **他们已经把"路由跟随表征"写成解释**，但未检验，且同时把中层读成"语言通用机制"。E178 把这句从解释变成测量，并加了他们没有的一条：训练路由器的倍数不随深度变 |
| **Chen 等, Multilingualism in MoE LLMs** `[全文前 100k 字符；附录 F 未读]` | arXiv 2026-01 | Qwen3-30B-A3B | "middle layers function as language-agnostic capacity hubs"；"early and late layers are responsible for language-specific processing"；称为 "functional stratification"；引 Schut、Wendler 作背景，正文不分析隐状态几何 | 无随机路由器 / 置换 / 探针；干预对照 = 屏蔽他语独占专家 | 把层剖面读成功能分层；E178 显示其独占专家数在 T 下不呈 U、负载匹配零模型反而更 U |
| Zheng 等, Language Routing Isolation `[节]` | arXiv 2026-04 | Qwen3-30B-A3B、Phi-3.5-MoE | "routing patterns converge in middle layers (language-agnostic semantic processing) but diverge in shallow and deep layers"；"middle layers appear to support more shared cross-lingual representations" | 无（随机 / TopK 只是 RISE 训练基线） | 同一解释，无检验 |
| Khandelwal 等, Routing Dynamics for Language Adaptation `[节]` | arXiv 2026-05 | OLMoE 续训成 7 语 | 语言专属只在末层出现（**不是 U**）；"routing similarity aligns closely with token-level vocabulary overlap"（JSD 与 token 重叠 ρ = −0.56） | 无 | 反例：英语中心底座续训后首层不分语言；词表重叠解释路由相似——与"首层 U 来自 token 身份"一致 |
| Myth of Expert Specialization 2604.09780 `[节；见 NULLAUDIT]` | arXiv 2026-04 | gpt-oss-20b、Qwen3-30B 等 | 线性路由器 ⇒ 隐状态相似是路由相似的充要条件；"specialization is an emergent property of the representation space" | 无随机路由器 | 一般论证 own；未碰语言、未碰层剖面 |
| Zhang 等, LayerMoE `[摘要+检索]` | ACL 2025 | Qwen1.5 扩语言 | 用**路由器输入隐状态的逐层跨语相似度**决定每层新增专家数（检索摘录：0–4 层与 17–21 层相似度低） | 不适用（设计方法） | 把稠密几何用于 MoE **设计**，不是解释已有路由 |
| Fan 等, MoE Design Choices `[节]` | arXiv 2024-02 | GPT-2-small 4 专家，4 语 17B token | "The learned router also does not show an ability to differentiate different languages"；随机冻结路由器困惑度可比 | 有冻结随机路由器，但只比困惑度，**不比按语言的路由** | 小模型、无层剖面 |
| NLLB Team, NLLB-200 §6.2.4 `[检索+旧笔记]` | Nature 2024 / arXiv 2022 | NLLB-MoE-54B（编–解） | 晚解码层把语言分到不同专家组、同语系相近；早编码层弱；晚编码 / 早解码语言无关 | 无 | 不是 U：编–解结构下"晚解码"对应生成端；几何解释未见（未核对正文） |
| Olson 等, Semantic Routing `[摘要]` | arXiv 2025-02 | DeepSeek-R1、DeepSeek-V2-Lite、Mixtral | 语义差异化路由在中层最明显 | 同句 / 异义对照 | 话题是语义不是语言 |

**Phi-3.5-MoE / GPT-OSS：** 除 Bandarkar（4 模型同一读数）与 Zheng（Phi-3.5-MoE）外，未找到单独的多语路由分析；两者都无对照。

## 3. 相邻领域："模块化组件的层剖面其实继承自输入表征"

| 领域 | 模块化组件上的"专精"层剖面 | 输入表征的对应事实（证据） | 是否有人做过"换成随机组件"检验 |
|---|---|---|---|
| 语言专属神经元 | 语言神经元集中在首尾层（Tang 2402.16438、Kojima 2404.02431） | 首尾层语言均值平移大（Chang 2205.10964）；不同识别方法选出的神经元集合大部分不重合、对迁移无用（Mondal 2503.17456，NAACL'25 InsightsNLP `[摘要+检索]`） | **否**：未见"随机旋转基下语言神经元层分布不变"的检验；Antverg & Belinkov 2110.07483（ICLR'22）`[摘要]`指出神经元排名混了"编码"与"被使用" |
| 语言适配器（模块插在冻结骨干上） | 目标语言只在最后几层显现 | Alabi 等 2402.13137（ACL'24）`[摘要]`："adapters operate on top of the model's frozen representation space while largely preserving its structure" | 部分：骨干冻结，层剖面显然由骨干决定；未与随机适配器比 |
| 视觉 MoE | V-MoE 晚层路由与类别相关、早层不相关（Riquelme 2106.05974 `[凭记忆，未核对]`） | 类别线性可分性随深度单调上升（Alain & Bengio 1610.01644 `[摘要]`） | **否** |
| 多模态 MoE | LIMoE 出现模态专属专家（Mustafa 2206.02770 `[摘要]`） | 模态间隙**在初始化时已存在**（锥效应），对比学习只是维持（Liang 等 2203.02053，NeurIPS'22 `[摘要]`） | **否**；最强的"继承自几何"先例 |
| 语言注意力头 | 多语模型只在需要时用语言专属头 / FFN（Zhang 等 2410.09223，ICLR'25 `[摘要]`） | 语言身份可由残差流差均值方向直接控制，优于神经元 / 探针方向（CLaS-Bench 2601.08331 `[检索]`） | 否 |
| 话题专家（已有） | MoE 话题分离 | 任意旋转门分话题 17–26×（Melton，见 NULLAUDIT） | **是**（唯一做过的） |

## 4. 可 own 的句子与风险

**4a. 三句（含谁已经占了哪部分）：**
1. **"已发表的多语 MoE 层剖面（首尾语言专属、中层共享）由同一隐状态上的随机路由器复现，是残差流几何的读出，不是路由训练产生的分层。"**——解释层面已被 Bandarkar 一句话写出（"If the representations are aligned, the routing would also be"，只针对中层，未检验），一般论证归 Myth 2604.09780，方法归 Melton；**检验与数字**（层剖面 Spearman .95、U 对比 2.35 vs 2.34）扫描范围内无人 own。压缩风险：**高**（"你验证了 Bandarkar 自己的那句话"）。
2. **"训练路由器在几何之上乘的语言专属倍数与深度无关（Qwen3 中层 1.58×、首尾 1.61×）：训练改变的是幅度，不是层剖面。"**——无人 own；这是 Bandarkar / Chen 的"功能分层"读法没有预测、稠密文献也不蕴含的一句。压缩风险：低–中（取决于 E179(a) 锐度匹配后是否仍是常数）。
3. **"语言专家结论'是否超出几何'随零模型族翻转（Haar 旋转 vs 负载匹配），Chen 式独占专家数在负载匹配零模型下比训练路由器更呈 U 形。"**——零模型选择会改结论在 NULLAUDIT 里已列为风险，语言结论上的翻转无人报过；Melton 只用 Haar + 高斯。压缩风险：中（易被读成方法学脚注）。
（候选第四句，取决于 E179(b)：随机路由器读出的是**方差主子空间**的语言几何，而不是全维可解码的语言身份——Holmström 2609.04819 已在稠密 Qwen3 上 own"中层语言身份被挪到残差子空间"，我们能 own 的只是"路由读的是哪一种"。）

**4b. 两个最大的科学风险：**
1. **常数倍可能是门的锐度 / 对齐，而非"路由器学到的语言信息"。** Haar 旋转保奇异值但不保与隐状态主方向的对齐；训练路由器行若对齐高方差方向，logit 方差更大、softmax 更尖，同一几何就读出更高 JSD——这会产生一个与深度无关的倍数，且与语言无关。E179(a) 的温度 / 锐度匹配零模型是这条的直接检验；若匹配后倍数消失，句 2 不成立。另：隐状态与路由器共同训练（Routers Learn Geometry 2605.12476，见 NULLAUDIT 风险 1），"几何"本身部分可能是路由塑造的，零模型分不开。
2. **稠密文献 + Bandarkar 原文已经蕴含句 1，贡献可能只是"把这个蕴含说明白并检验它"。** 直说：稠密 U 形（Tang、Kojima、Wendler、Zhao）+ 线性路由器读隐状态（Myth 的命题）⇒ 路由 U 形，这一推理链在 2025 年就齐了，Bandarkar 自己写出了后半句。句 1 单独成文的增量是检验与数字，不是新现象；有新内容的是句 2（倍数与深度无关）和句 3（判决随零模型翻转），而句 2 又悬在风险 1 上。附带：Holmström / Bayazit 显示"稠密 U 形"本身依赖读数（全维探针各层 >.9），若 E179(b) 的全维探针不呈 U、只有方差加权读数呈 U，"来自几何"须改写为"来自各向异性的主方向"，这会改变句 1 的措辞而不一定改变其成立。

## 5. 补：已发表的逐模型层剖面 vs E179（11-09，E179 = `division/results/e179/tables.md`，c6ba1a51）

E179 训练路由器 U 对比（首尾 ÷ 中层，FLORES-200 dev 20 语，全对全 JSD）：Qwen3-30B-A3B 2.35、GPT-OSS-20B 3.16、OLMoE-1B-7B-0125-Instruct 1.11。Bandarkar 2510.04694 `[全文 HTML]` 的设置：FLORES-200（split 未写）、12 语 + 英语（语言清单在附录表 A.2，抽取乱码，未核对）、句数未写；读数 = 逐句平均 softmax 路由权重与**英文配对句**的熵归一 JSD（F = log E − ½(H₁+H₂)）。原文正文**不给逐层数值**，只有图（主文图 2 只画 Qwen3，其余三模型在附录 A.2）。

| 模型 | Bandarkar 原文（§4.3 / 附录图注） | 与 E179 |
|---|---|---|
| Qwen3-30B-A3B | U 形"the most pronounced and least noisy for Qwen3"；中层干预区 8–35 层（1 起） | 一致（2.35） |
| GPT-OSS-20B | 趋势清楚；"the only one where divergence is higher in the first layers than the last"；干预区 4–19 层；中层散度与 Belebele 相关最弱 r ∈ [−0.60, −0.40] | 一致（3.16；首层高于末层是否在 E179 复现，未核对） |
| OLMoE-1B-7B-0125-Instruct | OLMoE 多语能力差"could explain why the big majority of languages studied do not exhibit this U-shape"；图 A.2 注 "We note OLMoE's poor multilingual capabilities"；法、中两语仍有 U（转述，未逐字核对） | **一致**（1.11，近平）；原文自己就说 OLMoE 多数语言无 U |
| Phi-3.5-MoE | 图 A.4 注 "Phi-3.5-MoE does not display the same U-shape"；去掉前两层才见 U，第一层 "perplexingly activates the same few experts … for all languages"；干预区 8–17 层 | E179 未测 |

注意：§4.3 仍写 U 形 "common to all four models evaluated"，但同节附了 OLMoE 与 Phi 两个例外——"四个模型都有 U"在原文里只对 Qwen3、GPT-OSS 干净成立。
**Khandelwal 2605.29714** `[节]`："只有末层分语言"指续训后的 **OLMoE-M7**，不是底座；底座只报了"OLMoE has a dedicated routing pattern for English"、非英语走大体共享的专家、非英语路由熵明显更低，逐层 JSD 只给第 15 层（其余在附录 D，未读）；底座 checkpoint（0924 / 0125）未写。
**Zheng 2604.03592** `[节]`：表 2 只有 Qwen3-30B-A3B，读数 = 与英语 top-K 专家集 Jaccard（数据 MGSM，K 与层组边界在附录未见）：浅 / 中 / 深 = 孟 .12/.22/.05、斯瓦希里 .04/.19/.04、泰 .25/.33/.12、俄 .41/.43/.17、日 .37/.37/.10——中层重叠最高、深层最低（深层分离强于浅层，与 Bandarkar 的 Qwen3 一致方向）。Phi-3.5-MoE 的逐层数在附录 E 表 7–10，未读到。
