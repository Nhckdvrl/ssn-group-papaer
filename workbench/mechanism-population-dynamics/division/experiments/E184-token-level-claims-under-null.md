# E184：token 级路由结论在公开 MoE 上过几何零模型（词汇 / 词类 / 相邻 / 下一 token）（2026-11-09）

- **状态：** DONE（11-09 19:40；18:05 写定"设置 / 读数 / 决策表"，在任何采集之前；18:55 冒烟后、正式分析前补登记结论 4 判决用量，见补登记节；跑后未改，事后观察标 POST-HOC）
- **类型：** PILOT（[DIRECTION](../DIRECTION_2026-11-06.md) §19 E184 行；桥 B6 / B7 / C2，[BRIDGES](../../../../library/themes/moe-routing/BRIDGES_AND_CONTRADICTIONS_2026-11-09.md)；不推进已登记主张等级；立题由人定，R2）
- **对应：** 桥 B6（同一 token id 稳定路由 ⇒ 词汇专家）、B7（相邻 token 同专家 ⇒ 句法路由）、C2（按 token id vs 按语义 / 预测 token）；CLAIMS C20（Antoine 式词类专精，自训平台）、C21（输入 vs 下一 token，自训平台）在公开大 MoE 上的对应；C24 的零模型管线。
- **问题（一句话）：** 已发表的四条 token 级路由结论——(1) 词汇 / 词形专家、(2) 词类（POS）专门化、(3) 相邻 token 共享专家、(4) 深层按"预测的下一个 token"而非输入 token 路由——在原始公开模型上，按原读数复现后，训练路由器 T 是否超出同一隐状态上的两族随机路由器（N_A Haar 旋转门、N_B 负载匹配 N1 旋转）？
- **对手假设：** H-学到：T 在多数层超出两族零模型（结论是路由器学出来的、几何之外的分工）。H-几何：T 落在零模型的 8 次抽样范围内（结论是残差流几何的性质，任何线性门都会读出）。

## 四条结论与原读数（出处；`[节]` 为 E175 / E176 / BRIDGES 已核对的节号）
| # | 结论 | 原文 | 原读数 | 原文基线 |
|---|---|---|---|---|
| 1 | 同一 token id 稳定路由到同一专家（词汇 / 词形专家；"context-independent specialization"） | OLMoE 2409.02060 §5.4 式 (8)；OpenMoE 2402.01739 §4.1；BASE 2103.16716 §5.2 | OLMoE：Vocabulary specialization = N^(k)_{x,E_i} / N_x（k=1 图 23，k=8 图 30），层值 = 专家平均；BASE / OpenMoE：同一 token id 的出现集中到少数专家（E176 #7 形式化为 top-1 词形纯度） | 无 |
| 2 | 路由按词类专门化 | ST-MoE 2202.08906 §7（定性：标点、动词、专名等专家）；Antoine 2412.16971 | Antoine Spec_POS：某 UPOS 全部路由槽位中被"拿槽最多的 K 个专家"占去的份额，对比均匀 U = K/E；模型值 = 按词数加权的 UPOS 平均（E172 `e172_antoine_readouts.py` 同定义） | 均匀 K/E |
| 3 | 相邻 token 常同专家（"structured syntactic behavior"） | Mixtral 2401.04088 §5（表 5：连续 token 的 first-choice 相同比例、first-or-second 至少一个相同比例） | rep1 = P(top1(t) = top1(t+1))；repAny = P(S_t ∩ S_{t+1} ≠ ∅) | 随机 1/8 与 46%（Mixtral 8 选 2） |
| 4 | 深层路由更跟**预测的**下一个 token 而非输入 token | OLMoE §5.4（"Later layers also specialize more on predicted output token IDs rather than input token IDs"）；本仓库 E175 / C21 的交叉拟合读数 | 同式 (8) 的 x 换成输入 id / 预测下一 id / 真实下一 id；本卡主读数用 E175 交叉拟合预测信息 G（bit） | 无 |

## 设置
- **模型（单卡 bf16，fvcrc20 GPU 0，A100 80GB，transformers 4.57.6，同 E179 / E180 加载方式）：** `Qwen/Qwen3-30B-A3B`（48 层，128 选 8，d 2048）、`openai/gpt-oss-20b`（24 层，32 选 4，带偏置路由器，MXFP4 默认反量化，eager）、`allenai/OLMoE-1B-7B-0125-Instruct`（16 层，64 选 8）。依次跑，同一张卡。
- **数据（两份语料，均为英语）：**
  - **C_F = FLORES-200 dev 英语全部 997 句**，每句单独一条序列，`add_special_tokens=False`（同 E179）。结论 1、3、4 的**主语料**。
  - **C_U = UD English EWT dev + test**（`~/mechpop_cache/lingdata/en_ewt-ud-{dev,test}.conllu`，金标 UPOS）。按文档切成 ≤ 400 词的段（复用 `ud_passages.sentences` 的句子与多词 token 规则：多词 token 区间如 "don't" 只保留表层文本、组成词不作词），段内句子以空格连接，每段一条序列，`add_special_tokens=False`。用 fast tokenizer 的 offset 把词映射到 token：**词末 token** = 覆盖该词最后一个字符、且不越过词尾的 token（同 `capture_routing.word_token_index`，不加 EOS）。结论 2 的**主语料**；结论 1、3、4 在 C_U 上作**复核**（同读数、同判决规则，报但不改主判决）。
  - **校准集（只用于 N_B 偏置重拟合）**：FLORES-200 **devtest** 英语前 500 句（与两份测量语料不重叠）。与 E179 不同：E179 在 20 语上校准，本卡只测英语，故在英语上校准使 N_B 匹配 T 的**英语**负载；测量语料上的 N_B vs T 负载 TV 照报。
- **路由器（同一隐状态、模型自身 top-k；只打分不干预）：** T；**N_A**（W·R，R 为 O(d) Haar，8 draws；GPT-OSS 保留训练偏置）；**N_B**（`moe_measure.py` N1：W_c V Q Vᵀ，偏置在校准集上重拟合到 T 的校准负载，8 draws）。随机数：每层 `torch.Generator().manual_seed(184000 + l)`，抽取顺序 N_A → N_B（构造代码照抄 e180_capture.py，不改 e179 / e180 脚本）。
- **采集（`scripts/e184_capture.py`，以 e180_capture.py 为底）：** 每层路由器 forward hook 取输入 h；T 的 logits 同 E179（GPT-OSS 在 hook 内以与模型相同的 bf16 `F.linear` 重算）。前向调用 `model.model(...)` 取末层隐状态，分块乘 `lm_head` 取 argmax 得**预测下一 token**（同 E180）。存：每层 × 每 token × 17 个路由器的 top-k 专家 id（uint8；`torch.topk` 降序，第 0 位 = top-1）；每 token 的语料、序列 id、位置、输入 id、预测下一 id、真实下一 id（序列末 = −1）；C_U 每 token 的 UPOS（词末 token 记该词 UPOS，否则 −1）与所属词号。原始数组在 `~/mechpop_cache/e184/<model>/`（不进 git）。
- **分析（`scripts/e184_analyze.py`，CPU）：** 读数、地板、判决、表；`scripts/e184_figure.py`：每条结论一张图（T vs 两族零模型，逐层，三模型）。
- **算力：** 三模型合计约 10 万 token（C_F ≈ 2.6 万、C_U ≈ 6–7 万 / 模型）+ 校准 1.3 万；参照 E179（53 万 token、41 个路由器，0.08–0.26 GPU h / 模型），估计 ≤ 0.6 GPU h（含加载）；上限 3 GPU h。日志 `results/e184/_logs/`。

## 读数（跑前固定；层号 0 起；每层、每路由器、每语料各算一次）
- **结论 1，R1（主）：token id 纯度（top-1）。** 取在该语料中出现 N_x ≥ 5 次的输入 token id x；R1 = Σ_x max_e N^(1)_{x,e} / Σ_x N_x（每个 token id 的出现中去往其最常用 top-1 专家的份额，按出现数加权）。**地板**：把 token id 在语料全部位置间随机置换（保持 N_x 与专家边缘分布）后的同一量，5 次（种子 184）取均值。**判决用量 = R1 − 本路由器自己的置换地板**（去掉负载边缘分布不同带来的差异；原值照报）。
  - 补充（只报）：OLMoE 式 vocabulary specialization（输入 id，k=1 与 k=K）：专家值 = Σ_x (N_{x,e}/N_e)·(N^(k)_{x,e}/N_x)（E175 读数 A 的聚合），层值 = 有样本专家的平均；同门槛、同地板。
- **结论 2，R2（主，C_U 词末 token）：Antoine Spec_POS。** 对每个 UPOS p：该类所有词末 token 的 K 个槽位里，被槽位数最多的 K 个专家占去的份额；模型值 = 按 n_p 加权平均（纳入 n_p ≥ 50 的 UPOS）。均匀 U = K/E 照报。**地板**：在词末 token 间置换 UPOS 标签 5 次取均值。**判决用量 = Spec − 本路由器置换地板**。
  - **R2w（次，预登记、单独判决）：词形之外的词类信息**——地板换成"在同一输入 token id 的出现之间置换 UPOS"（5 次）；R2w = Spec − 词内置换地板。若路由纯由 token id 决定，R2w ≈ 0。
  - 补充（只报）：ST-MoE 式 UPOS 类 top-1 路由熵 / ln E（按 token 加权，E176 #6 口径）。
- **结论 3，R3（主）：相邻 first-choice 重复率 rep1** = P(top1(t) = top1(t+1))，t 与 t+1 在同一序列内。**地板**：把所有 token 的位置随机置换后配对（5 次取均值；= 负载决定的偶遇率）。**判决用量 = rep1 − 本路由器地板**。
  - 补充（只报）：repAny = P(S_t ∩ S_{t+1} ≠ ∅)（Mixtral first-or-second 口径的 K 选版）、平均重合 |S_t ∩ S_{t+1}|/K，同地板。
- **结论 4，R4（主）：交叉拟合预测信息 G(x)（bit；E175 估计器）。** e = top-1 专家；按序列 id 分两折（序列 id 奇偶），一折估 p(e|x) = (N_{x,e} + A·p(e)) / (N_x + A)，A = 8，p(e) 加一平滑，另一折算对数损失下降，交换取均值。x ∈ {输入 id, **预测下一 id（主）**, 真实下一 id（次）}；只用有真实下一 token 的位置（各 x 同一组位置）。**地板**：x 在位置间置换一次后的 G（应 ≤ 0）。
  - **主量：ρ_l = G(预测下一) / G(输入)**（**11-09 18:55 补登记改为差值 ΔG，见文末补登记节**）（尺度无关；T 整体更"有信息"会同时抬高两者）。**交叉层** = ρ_l > 1 的最小层；**持续交叉层** = 使 ρ > 1 对其后所有层都成立的最小层；无则记"无"。T 与每个零模型 draw 各算。
  - 次：真实下一 id 版 ρ'；OLMoE 式 vocabulary specialization（k=1）输入 / 预测 / 真实三版（只报）。
- **代表层**：报数时取 l* = ⌊L/2⌋（Qwen3 24、GPT-OSS 12、OLMoE 8）与末层。
- **层剖面一致性（只报）**：Spearman(T 的判决用量剖面, N_B 8-draw 均值剖面)、同 N_A，跨全部层。

## 决策表（跑之前写）
**逐层分类**（对每个读数的判决用量；"族范围" = 该族 8 次抽样的 [min, max]）：
- **above**：T > N_A 的 max 且 T > N_B 的 max；
- **below**：T < N_A 的 min 且 T < N_B 的 min；
- **within**：T 落在 N_A 族范围或 N_B 族范围之内；
- **split**：其余（如高于一族、低于另一族，或落在两族之间的空隙）。

**结论级判决**（每条结论 × 每个模型，主语料主读数）：
- **survives**：above 层数 ≥ ⌈2L/3⌉；
- **geometry**：within 层数 ≥ ⌈2L/3⌉；
- **below-null**（跑前补的第四类，不归入"零模型依赖"以免误读）：below 层数 ≥ ⌈2L/3⌉；
- **null-family-dependent**：其余。
- **量级附注（预登记，防止把微小超出读成"学到"）**：对判 survives 的格，报 above 层上 T / max(两族) 的中位数；中位 < 1.25 记为"survives（边缘，< 1.25×）"。
- **结论 4 的附加判定**：除 ρ 的四类判决外，比较交叉层——**earlier**：T 的持续交叉层 < 16 个零模型 draw 的持续交叉层最小值（零模型无交叉视为 L）；**same**：落在零模型 draw 的 [min, max] 内；**later**：大于 max；T 无持续交叉则记 **T 无交叉**。预期（跑前写明）：零模型也是当前隐状态的函数，若残差流在深层编码了将要预测的 token，零模型同样会显示"下一 token 信息上升"，所以结论 4 默认是几何性质；只有 T 的 ρ 判 survives **且**交叉 earlier 时，才写"深层按预测 token 路由是路由器学到的"。
- **怎么读（写死）**：
  - 某结论在三个模型上都 survives（非边缘）→ 该结论在公开模型上有几何之外的成分，原文结论成立但应改写为"超出随机路由器 x 倍"；
  - 都 geometry → 原文结论是隐状态几何的性质，"词汇 / 词类 / 句法专家"的措辞不成立，作为纠偏结论报；
  - 模型间不一致或 null-family-dependent → 如实报格表，不选一个；
  - 以上都不是关线条件，不据此开 / 关线（R2）。

## 阳性对照
- **训练路由器自一致**：同一 batch 前向两次 T 的 top-k 集合逐 token 完全一致率 = 1.0（min over layers）。
- **hook 正确性**：fp32 重算 top-k 与模型实际选择的重叠率（≥ .99 预期）；T logits vs 模型选择（预期 1.0）。
- **N_B 负载匹配**：校准集上 N_B 与 T 负载 TV 的均值 ≤ .01（最大值照报；测量语料上的 TV 只报）。
- **标签置换在地板**：把置换 draw 0 当作"数据"、对其余 4 次的均值算判决用量，|·| ≤ .01（R1、R2、R2w、R3）在 ≥ 95% 的（层 × 路由器）格成立；R4 的置换 G ≤ .02 bit 在所有格成立。
- **读数敏感性（构造性）**：第 0 层 T 与零模型的 R1 都应显著高于地板（第 0 层路由器输入 ≈ 输入 embedding，任何线性门都按 token id 路由；E175 未训练第 0 层同理）。

## 噪声地板 + MIE
- 判决本身以零模型 8 次抽样范围为参照（同一 token、同一隐状态，语料抽样噪声对 T 与零模型共用）。**语料半分复核**：C_F 按序列 id 奇偶分两半，各算一次结论级判决，报两半与全量是否一致（不一致的格在表中标 *）。C_U 复核同上。
- 不设通过线之外的 MIE；"边缘 < 1.25×"见决策表。

## 混杂审计（EXECUTION §4）
- **负载边缘分布**：T 在英语上可能严重不均衡（E179：FLORES 多语 6–11×）。纯度、Spec、rep1 都随负载集中而升高——已控制：判决用量减去本路由器的置换地板；N_B 另在英语校准集上匹配负载。
- **词频**：高频 token 主导 R1 的加权平均。未控制（与原读数一致）；补充读数（专家平均的 OLMoE 式）对频率加权不同，照报。
- **POS 与 token id 共变**：R2w 处理（词内置换）。
- **结论 4 的输出依赖**：零模型同样是当前隐状态的函数——这正是被检验的对象，不是混杂。
- **只英语、两份语料**：结论的语言范围限英语；Mixtral 原文用 The Pile，OLMoE 用 C4 / 自家数据，绝对值不可直接比，只比 T vs 零模型。

## 补登记（11-09 18:55，冒烟测试后、任何正式数据分析之前）
冒烟测试（OLMoE，FLORES 40 句 + UD 10 段，约 3.5k token，只用于检查管线）暴露一个读数设计缺陷：N_A（全空间 Haar 旋转门）在中层对输入 token 的交叉拟合信息 G(输入) ≈ 0 bit，比值 ρ = G(预测下一)/G(输入) 的分母接近 0，单个 draw 出现 −147 这样的值，使"落在零模型范围内"的判定失去意义。修改（只改结论 4 的判决用量，其余不变）：
- **结论 4 判决用量改为差值 ΔG_l = G(预测下一) − G(输入)（bit）**；交叉层定义随之改为 ΔG > 0（G(输入) > 0 时与原 ρ > 1 等价）；次读数 ΔG' 用真实下一 token。ρ 只在 T 与该零模型 G(输入) 都 > .05 bit 的层上描述性报告，不进判决。
- **结论 4 的量级附注**改为：above 层上 T − max(两族) 的中位数 < .05 bit 记"survives（边缘）"（结论 1–3 仍为 < 1.25×）。
- 冒烟数据（约 4% 规模）上的数值不报、不作任何结论依据；正式采集脚本与冒烟同一份，未改。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

**执行：** fvcrc20 GPU 0（A100 80GB），三模型依次采集（`scripts/e184_capture.py`、`e184_job.sh`），CPU 分析 `e184_analyze.py`、表与图 `e184_figure.py`。卡占用 ≈ 1.1 GPU h（18:13–19:17；其中约 40 分钟是 NFS 读权重，计算本身 < 15 分钟）。语料：FLORES dev 25.5–26.3k token / 模型；UD EWT dev+test 56.6–59.4k token、词末 token 48.4–48.6k（17 类 UPOS 全部 n_p ≥ 50）；R1 合格 token 16.6–17.4k（730–792 个 id）。结果文件：`results/e184/tables.md`（全部数字）、`summary.json`、`<model>.json`（逐层逐路由器读数）、`fig_claim{1,2,3,4}.png`；原始 top-k 在 `~/mechpop_cache/e184/<model>/`（不进 git）。

**判决表（主语料主读数；括号 = above / within / below / split 层数；survives 后为 above 层上 T / max(两族) 的中位数）**

| 结论 | Qwen3-30B-A3B（L=48） | GPT-OSS-20B（L=24） | OLMoE-1B-7B-0125-Inst（L=16） |
|---|---|---|---|
| 1 词汇 / token id 专家（FLORES，R1 纯度 − 置换地板） | **survives**（42/6/0/0；1.46×） | **survives**（17/7/0/0；1.35×） | **survives**（15/1/0/0；1.54×） |
| 2 词类专门化（UD，Antoine Spec_POS − 置换地板） | **survives**（48/0/0/0；1.85×） | **null-family-dependent**（13/11/0/0） | **survives**（16/0/0/0；1.87×） |
| 3 相邻 token 同专家（FLORES，rep1 − 随机配对地板） | **survives**（45/1/2/0；1.47×） | **null-family-dependent**（11/10/3/0） | **survives（边缘）**（12/2/1/1；1.23×） |
| 4 深层按预测下一 token 路由（FLORES，ΔG = G(预测下一) − G(输入)） | **below-null**（1/7/40/0）；T 无交叉 | **below-null**\*（2/6/16/0）；T 持续交叉 23 = same | **below-null**（0/1/14/1）；T 无交叉 |

\* GPT-OSS 结论 4 两个语料半各判 null-family-dependent（全量 below-null）；其余格两半与全量一致。

**次级判决：** R2w（词形之外的词类信息）Qwen3 survives（47/1/0/0）、GPT-OSS null-family-dependent、OLMoE survives；ΔG'（真实下一 token）三模型 below-null；UD 复核：结论 1 Qwen3 / OLMoE survives、GPT-OSS null-family-dependent；结论 3 Qwen3 survives、GPT-OSS geometry、OLMoE null-family-dependent；结论 4 三模型 below-null。

**代表层数字（判决用量；T vs 零模型 8-draw 均值 [min, max]）：**
- 结论 1，l*：Qwen3 L24 T .146 vs N_A .067 [.055, .076]、N_B .109 [.094, .118]；GPT-OSS L12 .176 vs .065 [.049, .079]、.105 [.068, .129]；OLMoE L8 .257 vs .074 [.061, .082]、.191 [.163, .218]。末层 GPT-OSS 例外：L23 T .098 落在两族范围内（N_A .122 [.065, .173]）。层剖面 Spearman(T, N_B) .88 / .85 / .81。
- 结论 2，l*：Qwen3 .090 vs .012 [.006, .018]、.038 [.025, .046]；GPT-OSS .065 vs .016 [.006, .030]、.026 [.008, .043]；OLMoE .313 vs .027 [.017, .036]、.120 [.112, .126]。GPT-OSS 的 within 层集中在后半（above 前半 8/12、后半 5/12；L23 T .015 vs N_B .014）。
- 结论 3，l*：Qwen3 .204 vs .083 [.077, .093]、.131 [.126, .136]；GPT-OSS .373 vs .166 [.158, .176]、.259 [.230, .293]；OLMoE .135 vs .096 [.089, .100]、.099 [.092, .116]。末层 T 跌到零模型之下：Qwen3 L47 .011 vs N_A .108、N_B .076；GPT-OSS L23 .107 vs .125、.159。
- 结论 4，l*：Qwen3 ΔG −.287 vs N_A −.123 [−.140, −.109]、N_B −.216 [−.255, −.180]；GPT-OSS −.106 vs −.095、−.106；OLMoE −.488 vs −.074、−.348。末层：Qwen3 −.277 vs −.049、−.155；GPT-OSS +.015 vs −.094、−.033；OLMoE −.270 vs +.028、−.100。

**结论 4 交叉层（ΔG > 0；首层 / 持续交叉层）：** Qwen3：T 无 / 无；N_A、N_B 16 个 draw 在 FLORES 上全部无交叉（UD 上 1 个 N_A draw 在 47）。GPT-OSS：T 21 / 23（FLORES）、21 / 21（UD）；N_B FLORES 上 1/8 个 draw 持续交叉于 23，UD 上 8/8 个 draw 于 21–23；N_A 全无 → 判定 **same**（T 不早于零模型）。OLMoE：T 无 / 无；N_A 6/8 个 draw 持续交叉于 14（N_A 在该层两种 G 都只有约 .1 bit），N_B 全无。OLMoE 原式 (8) 的 k=1 vocabulary specialization 同向：末层输入 .245 vs 预测下一 .158（T）。

**阳性对照：** 两遍一致 1.0000（三模型）；hook fp32 重叠 .9931 / .9983 / .9993，T logits vs 模型 1.0000；**N_B 校准负载 TV 均值 .0105（Qwen3，超阈值 .01 一点）/ .0085 / .0054**（最大 .025 / .056 / .018）；置换对照 |·| ≤ .01 在 R1 / R2 / R2w / R3 的全部格成立（比例 1.000）；置换 x 的 G 最大值 −.148 / −.043 / −.226 bit（≤ .02 成立）；第 0 层 R1 T 原值 .726 / .888 / .385 vs 地板 .159 / .240 / .158（读数能测到按 token id 路由）。

**按决策表：** 结论 1 三模型 survives（非边缘）→ "词汇专家"在公开模型上有几何之外的成分，应改写为"超出随机路由器约 1.35–1.54 倍"；结论 2、3 模型间不一致（Qwen3 / OLMoE 超出、GPT-OSS 零模型依赖，GPT-OSS 的超出只在前半层）→ 按表如实报格表；结论 4 三模型 below-null，T 的交叉不早于零模型（GPT-OSS same、另两个 T 无交叉）→ "深层按预测 token 路由是路由器学到的"不成立：训练路由器相对零模型**更偏输入 token**。不据此开 / 关线。

**两句事实判决：** 在 Qwen3-30B-A3B、GPT-OSS-20B、OLMoE-0125-Instruct 上，词汇 / token id 专精在三模型的多数层都高于两族随机路由器（中位 1.35–1.54×），词类专精与相邻同专家在 Qwen3 与 OLMoE 上高于零模型、在 GPT-OSS 的后半层落入零模型范围；三条读数的层剖面都与负载匹配零模型同形（Spearman .81–.94）。"深层按预测的下一个 token 路由"在三个模型上都不成立为路由器性质：训练路由器的 G(预测下一) − G(输入) 在 40/48、16/24、14/16 层低于两族零模型，只有 GPT-OSS 在末 1–3 层出现交叉，且与负载匹配零模型同层。

**POST-HOC 观察（看到结果后才算 / 才注意到，不进判决）：**
1. **词类专精几乎全是词形专精。** Spec_POS 超出全局置换地板的部分里，不能由"同一 token id 内置换"解释的份额（中位，跨层）：T .073 / .053 / .060，N_B .070 / .059 / .066，N_A .069 / .057 / .068——训练路由器与随机路由器一样，词类信号约 93–95% 由 token id 携带。R2w 判 survives 是因为这剩下的 5–7% 在 T 上约为 N_B 的 2 倍，绝对值只有 .003–.02。
2. **Haar 零模型在中层几乎不含 token 信息。** 中位 G(输入)：T .79 / .89 / 1.29 bit、N_B .36 / .58 / .81、N_A .03 / .22 / .16。全空间随机方向读不到 token 身份，T 的读出子空间里才有（N_B 与 T 同一子空间）。所以 token 级读数上 N_A 是很低的地板，判决实际由 N_B 决定；"超出零模型"的倍数对 N_A 与 N_B 差 2–3 倍（与 E178 / E179 的"判决随零模型族翻转"同一现象）。
3. **"常数倍"在 token 级读数上也出现。** T / mean(N_B) 的全层中位：结论 1 1.68 / 1.40 / 1.72，结论 2 2.43 / 1.73 / 2.34，结论 3 1.59 / 1.19 / 1.38，层剖面与 N_B 同形——与 C24 的语言读数同一形态（训练路由器在几何读出上乘一个倍数）。但末层是例外：Qwen3 与 GPT-OSS 的结论 3、GPT-OSS 的结论 1–2 在末层降到零模型或其下。
4. **负载匹配不跨语料。** N_B 在校准集（FLORES devtest）上 TV ≤ .011，在 FLORES dev 上 TV 均值已达 .063–.107，在 UD 上更大（OLMoE 逐层 .19–.31）；原因未查。判决用量减去各路由器自己的置换地板，不受负载差直接影响，但"负载匹配"只在校准分布上成立。
5. OLMoE 原文 §5.4 的输入 vs 预测读数在 OLMoE-0125-Instruct 上（本卡读数与原式 (8) 两种）都没有交叉；原文用的是 OLMoE-0924 base 与 C4，未在原模型上核对。

**不确定 / 未核对：** 只有英语两份语料、每模型一个 checkpoint；结论 4 的判决用量在冒烟后由比值改为差值（补登记节），T 的 G 值整体高于零模型，所以差值偏负部分来自 T"对什么都更有信息"——比值版（只在 G(输入) > .05 的层有意义）未进判决；Qwen3 N_B 校准 TV .0105 略超阈值；N_B 跨语料负载漂移的原因未查。

**主张变化：** 无（PILOT）。供主会话改写 C20 / C21 的公开模型对应句与桥 B6 / B7 / C2 的状态。
