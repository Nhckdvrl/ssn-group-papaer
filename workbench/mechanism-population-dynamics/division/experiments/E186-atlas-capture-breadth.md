# E186：路由方差图谱的广度采集——更多 MoE 家族 + OLMoE-0924 训练时间轴（2026-11-09）

- **状态：** PLANNED（11-09 21:35 写定"存储 / 模型 / 语料 / 层段 / 阳性对照 / 噪声地板 / 会改变判断的结果"，在任何正式采集之前提交；冒烟与架构检查的数字不报、不作依据；跑后不改，事后分析标 POST-HOC）
- **类型：** EXPLORE（[DIRECTION](../DIRECTION_2026-11-06.md) §20 / §21：测量，不是假设检验；**不写二元判决表、不写分支字母**；不推进任何主张等级；开关线由人定，R2）
- **对应：** §21 的五条结构观察与三条新残差（E185 卡 (i)(ii)）；C24（常数倍）、C25（文字 / 语言）、C26（token 级结论）的跨家族 / 跨训练检验；桥 B3（早饱和）；E184 结论 4 / E185 残差 (a) 在 OLMoE §5.4 原模型（0924 base）上的复现。
- **问题（一句话）：** E185 在 Qwen3 / GPT-OSS / OLMoE-0125 上画出的"因子 × 层 × 路由器族"图谱（词表锐化处处、给定 token 后局部序列信息、中层跨语共享内容、语言 / 文字不在训练新增部分）在另外三个 MoE 家族上、以及在 OLMoE-0924 训练过程中各长什么样？

## 模型（公开权重，只推理，bf16，transformers 4.57.6 原生实现，不用 trust_remote_code）
| 键 | HF 仓库（revision） | 结构 | 卡数 |
|---|---|---|---|
| `phimoe` | microsoft/Phi-3.5-MoE-instruct（main） | 32 层，16 选 2；sparsemixer 门：推理时选择 = logits 的 top-1 与去掉 top-1 后的 argmax = 普通 top-2（只有门值不同，存的是 logits） | 2 |
| `mixtral` | mistralai/Mixtral-8x7B-Instruct-v0.1（main） | 32 层，8 选 2，softmax 门 | 2 |
| `dsv2lite` | deepseek-ai/DeepSeek-V2-Lite（main） | 27 层，第 0 层为稠密 MLP（`first_k_dense_replace = 1`），第 1–26 层 64 个路由专家选 6 + 2 个共享专家；`topk_method = greedy`、softmax、无偏置、`norm_topk_prob = False` | 1 |
| `olmoe0924_{s5k,s20k,s80k,s320k,s1220k,main}` | allenai/OLMoE-1B-7B-0924，分支 step5000-tokens20B、step20000-tokens83B、step80000-tokens335B、step320000-tokens1342B、step1220000-tokens5117B（预训练末）、main（退火后的发布版） | 16 层，64 选 8 | 各 1 |

- **DeepSeek 的共享专家**：每个 token 都经过、不被路由，**不记录**；存储与零模型只覆盖 64 个路由专家（E = 64，K = 6）。存储的层号是 MoE 层序号 0–25，对应模型层 1–26（`meta.json` 的 `moe_layers`）。路由器 T 的 logits 按模型自己的算法重算（fp32 `F.linear`，与 `DeepseekV2MoEGate.forward` 同精度）。
- **checkpoint 选择**：步数约按 4 倍等比（5k / 20k / 80k / 320k / 1220k）+ 发布版；首点 20B token 已是左删失（OLMoE 原文早饱和的"1%"约在 50B），如实报。各分支的 safetensors LFS sha256 互不相同（21:15 已核对，排除 Pythia 式"分支挂主干权重"的陷阱）。
- **如架构使 hook 失效**（分组路由、sigmoid 门、专家偏置）→ 改 hook 并写进本卡；做不到就跳过该模型并写明，不近似。三家族都已核对：无偏置、无分组、选择 = logits top-k。

## 语料（与 E184 / E180 同口径）
- **FLORES-200 dev，21 个语侧 × 997 句**：E180 的 20 个语侧（斯拉夫 11 含 srp_Latn 转写——复用 `~/mechpop_cache/e180/srp_Latn/`（`e180_translit.py` 产物）、印地组 6、中文 3）**+ eng_Latn**（E184 的英语语料；D184 式分析需要它，任务原文未列，补上并说明）。每句一条序列，`add_special_tokens=False`。语侧编号 0–19 与 E180 相同，eng = 20。
- **UD English EWT dev + test**：E184 的段落切分与词末 token 规则逐字复用（≤ 400 词 / 段，金标 UPOS）。
- 规模：分词器不同，FLORES 21 侧 ≈ 1.46–1.51M token / 模型（CPU 预估），UD ≈ 6 万；与 E180（OLMoE 1.54M）+ E184 相当。
- **N_B 校准集 = 测量语料本身的随机子集**（序列级随机置换取前缀，种子 186，≥ 6 万 token，按比例覆盖 21 侧 + UD）：E184 观察 4 显示负载匹配不跨语料，所以在测量分布上匹配。

## 存储（`scripts/e186_capture.py`，原始数组在 `~/mechpop_cache/e186/<键>/`，不进 git）
- 路由器（同一隐状态、模型自身 K）：**T**；**N_A** ×8（W·R，R 为 O(d) Haar）；**N_B** ×8（N1：W_c V Q Vᵀ，偏置在校准子集上重拟合到 T 的负载）；**N_F** ×2（新增：与模型权重无关的固定高斯矩阵，种子 186500 + 层，同一架构的所有 checkpoint 用同一组矩阵；只为训练时间轴的饱和读数）。随机数：每层 `manual_seed(186000 + 层)`，N_A → N_B 顺序（构造代码照抄 e184）。
- 每层 × 每 token：17 个路由器的 top-k 专家 id（uint8，降序）、**对应的 top-k logits（fp16）**、**全部 E 个 logits 的 logsumexp（fp16；softmax 门值 = exp(logit − lse)）**；N_F 的 top-k id。
- 每 token：语料、语侧、句 / 段 id、全局序列 id、位置、输入 id、**lm_head argmax 预测 id、预测熵（bit，fp16）、真实下一 token 的 log₂ 概率（fp16）**、真实下一 id、UPOS、词号。
- **每层 × 每序列：路由器输入 h 的序列均值（fp16）**——几何读数（E179 G1 / G2 式），不存逐 token 隐状态。
- 诊断：两遍一致、hook 一致（逐层）、校准集上 N_B 负载 TV、测量语料上 17 个路由器对 T 的负载 TV（合并与 FLORES 非英 / FLORES 英 / UD 三组分开）、英语下一 token 准确率（加载正确性的粗检）。

## 分析（复用 E185 管线，不改它对旧存储的行为）
- 把每个 E186 存储切成两个 E185 兼容视图：**D184 式**（FLORES eng + UD；17 个路由器）与 **D180 式**（20 个非英语侧；**17 个路由器，零模型由 E185 的单 draw 变成 8 draws**），用 `E185_CACHE / E185_OUT / E185_RES` 环境变量把 `e185_atlas.py`、`e185_crossfit.py`（补登记 2 的 G_freq）、`e185_tokens.py`、`e185_residuals.py --part a` 指到新视图；`e185_lib` 只新增模型条目（层段、名字、分词器路径），不改旧条目。
- 读数与 E185 完全相同：边际份额 Î/H(e)（置换地板）、条件份额 Î(e; X | 输入)、交叉拟合 G_freq(X | 输入)（只在 ≥ 20 次的 id 上评估；检测限约 .08 bit；都是下界）、token 上下文依赖 H(e | id)（等 n = 30）、残差 (a) 的条件量与逐 id 分解；多语加语言 / 文字 / 平行句 id、Î(e; 语言 | 输入, 文字)、Î(e; 文字 | 输入, 语言)。
- **新存储才有的读数（预登记）：**
  1. **连续上下文依赖**：每个高频 id（≥ 30 次）在每层的 T top-1 logit margin（top-1 − top-2）与 softmax top-1 概率 exp(v₀ − lse) 的跨出现标准差 / 均值；T vs N_B。
  2. **置信度分层的残差 (a)**：按预测熵三分位重算 Î(预测下一 | 输入)（替代 E185 的"预测是否正确"代理）。
  3. **几何**：hmean 的语言质心距离与 E179 G1 / G2 同形读数（只报，用于与路由读数并列）。
  4. **训练时间轴（OLMoE-0924 6 点）**：每个 checkpoint 一张完整图谱；另加 (a) **饱和**：T 在 checkpoint t 与 main 的逐 token top-k 重合 |S_t ∩ S_main| / K（逐层），同一读数在 N_F 上（同一固定矩阵作用于两个 checkpoint 的隐状态）——B3 的零模型；(b) 第 0 层前一 id vs 输入 id 份额随训练；(c) 词表锐化倍数 T / N_B 随训练；(d) OLMoE §5.4 原式 (8)（输入 vs 预测下一 vocabulary specialization，k = 1）与 E184 ΔG 在 main 上复现。
- **层段（跑前定）**：Phi / Mixtral（32 层）edge 0–1 ∪ 30–31、mid 5–23；DeepSeek-V2-Lite（26 个 MoE 层）edge 0–1 ∪ 24–25、mid 4–18；OLMoE-0924 同 OLMoE（edge 0–1 ∪ 14–15、mid 2–11）。逐层表照出，层段只用于汇总。
- 产出：`results/e186/tables.md`（每模型同 E185 §1 / §1b 的图谱表 + 模型对照表 + 训练时间表）、每模型一张因子 × 层热图、一张训练时间图、`summary.json`。

## 阳性对照
- **采集：** 两遍一致 = 1.0（每层）；hook fp32 重算 vs 模型选择 ≥ .99；T logits top-k vs 模型选择 = 1.0（Phi 的 sparsemixer 与 DeepSeek 的 greedy 都应 = 1.0，否则说明选择规则理解错，停）；英语下一 token 准确率（发布版模型应与 OLMoE-0125 / E184 量级相当，≥ .3；早期 checkpoint 允许低）。
- **N_B 负载匹配：** 校准子集上 TV 均值 ≤ .01；**测量语料（合并）上 TV 均值 ≤ .01**（E184 只在校准集上成立；本卡在测量语料上校准，应成立；三组分开的 TV 照报）。
- **估计器（E185 管线照跑）：** 置换标签 |Î| ≤ .007；第 0 层构造性（Î(输入) 应是最大因子——E185 在 OLMoE 上不成立，本卡照报各家族）；半分同号率；**合成恢复对照在新 E 上重跑**（`e185_crossfit.py --pc` 的生成器改用 Mixtral（E = 8）与 DeepSeek（E = 64，K = 6）的真实 (输入, X) 分布；G_freq 的检测限与恢复比随 E 变，同家族内比较 T vs 零模型不受影响，家族间比较绝对 bit 要看它）。
- **饱和读数：** checkpoint main 与自身的重合 = 1（构造性）；N_F 的重合下限 = 两个不同固定矩阵之间的偶遇率（报）。

## 噪声地板
- 置换地板 3 次的 SD（|Î| < 3 SD 标"在地板"）；零模型 8 draws 的 [min, max]（多语部分现在也是 8 draws）；语料半分（序列奇偶）逐层同号率；G_freq 检测限约 .08 bit（E185 合成对照），弱效应不可见。
- 家族间比较只比"同一因子的 T 相对本家族零模型"（倍数、高于全部 draw 的层数），不比绝对 bit。

## 哪些结果会改变对 §21 的读法（不是决策表；写"看到什么就改写什么"）
1. **词表锐化**：若新家族里 token 相关因子（输入 / 前一 / 下一 / 预测下一 / UPOS）的 T / N_B 倍数彼此一致、层间平坦 → §21-1 跨家族成立；若某家族下一 token 类倍数明显高于输入 id 倍数（> 1.3 倍的差）→ 该家族的"常数倍"不只是词表锐化，§21-1 只写成"三 / n 个家族"。
2. **给定 token 后的语言**：E185 给定 token + 文字后的语言倍数 1.1–1.3、G_freq(语言 | 输入) ≤ .017 bit。若某家族给定 token 后语言 G_freq 超过检测限且 T 高于全部 N_B draw → 该家族存在 token 之外的语言路由，§21 "语言不在训练新增部分"要改成家族依赖。
3. **中层跨语共享内容**：G_freq(平行句 id | 输入) 的 T 与 8 个 N_B draw。若新家族的 T 都在 N_B 范围内 → "内容路由超出几何"只属于 Qwen3 / GPT-OSS；若 T 高于全部 draw 且大于语言项 → §21-4 跨家族成立；把各家族的量级与 E185 的 Qwen3 .44 / GPT-OSS .22 / OLMoE .02 bit 并列（"模型依赖"变成一张有 6 个点的表）。
4. **局部序列信息**：给定输入 id 后，预测下一 / 前一 id 的 G_freq 在 T 上高于全部 N_B draw 的层数。若新家族多数层不高于 → §21-3 是家族依赖；若都高于 → 跨家族成立。
5. **同 token 同语言内文字信息 = 0**：若任一新家族 Î(文字 | 输入, 语言) 在 mid 段显著 > 0 → C25 的建议补句（"同 token 同语言内文字信息 0"）要加家族限定。
6. **残差 (a) 在原模型上**：OLMoE-0924 main 上若原式 (8) / ΔG 在深层出现"预测下一 > 输入"的交叉而 0125-Instruct 没有 → OLMoE §5.4 是 checkpoint 依赖的，C26 第四句要分开写；若 main 上也没有 → "在原模型、FLORES / UD 英语上也不复现"（语料仍与原文的 C4 不同，如实写）。
7. **训练时间轴**：(a) T / N_B 倍数在早期 ≈ 1、随训练上升 → 词表锐化是训练出来的、可定时；从首点起就 > 1 → 在 20B token 前已形成（左删失）。(b) OLMoE 第 0 层"前一 token 路由"出现的 checkpoint；若 main 上没有而 0125 有 → 0125 配方特有。(c) **饱和**：若 N_F（固定随机矩阵）在 checkpoint t 与 main 之间的 top-k 重合与 T 同形同量级 → 早饱和主要是隐状态几何的收敛，不是路由器学习（B3 改写）；若 N_F 明显低于 T → 早饱和是路由器的性质。(d) 中层内容信息随训练的出现时间。
8. **Qwen3 的 12 层周期 / 内容层**：只报新家族的逐层剖面里有没有周期性内容层；有就并列，没有就写"Qwen3 独有"。
9. **共享专家**：DeepSeek 的路由专家图谱若与其他家族同形 → 共享专家不改变路由的因子结构（只能这么弱地说，共享专家本身无路由可测）。

## 混杂审计（EXECUTION §4）
- **分词器不同**：token 数、token 粒度、印地组 / 中文的字节回退程度在家族间不同 → 只比同家族内 T vs 零模型；绝对份额不跨家族比。
- **Instruct vs base**：Phi / Mixtral 是 instruct 版，DeepSeek-V2-Lite 与 OLMoE-0924 是 base；E185 的 Qwen3 base vs instruct 逐格相关 .998，按此不再单独控制，如实标注。
- **负载**：在测量语料上校准（见上）；份额按各自 H(e) 归一，原始 bit 同报。
- **E 与 K 不同**（8 / 16 / 64；K = 2 / 6 / 8）：top-1 信息的上限 log₂E 不同、Mixtral N1 读出子空间只有 7 维（N_B 的随机自由度小）→ 家族间只比倍数与"高于全部 draw 的层数"。
- **checkpoint 间隐状态尺度变化**：N_F 无偏置、无负载匹配，早期 checkpoint 上负载可能很不均衡 → 饱和读数同时报 N_F 的负载熵。
- **POST-HOC 风险**：E185 的结果在写本卡前已看过，"会改变读法"的条目是据此写的；任何在采集后新加的读数标 POST-HOC。

## 算力
- 采集：OLMoE 类 ≈ 0.1–0.3 GPU h / 个（E180 OLMoE 1.54M token 240 s 墙钟，加 topv / hmean 与 NFS 写盘）× 6；DeepSeek ≈ 0.5；Phi / Mixtral 各 2 卡 × ≈ 0.5–1 h。合计估 ≈ 5 GPU h，**上限 14 GPU h**。23:00 前只用 1 张空闲卡做冒烟 / 架构检查；23:00 后只用空闲卡，fvcrc10/11/12/13/15/20/21，不用 fvcrc14，本卡同时 ≤ 8 卡（本线总量 ≤ 16）。
- 权重：直接从 HF 用 curl 下到各节点本地 `/tmp/xiang_e186/models/`（网关总带宽实测约 30 MB/s，共 ≈ 290 GB），用完删除；若某模型的下载 / 读盘使其超出份额，放弃该模型并报告。
- CPU 分析：E185 管线，17 个路由器的多语视图约为 E185 D180 的 6 倍（≈ 20–40 分钟 / 模型 / 24 核），在空闲节点的 CPU 上并行。

## 结果（跑完后填写；上面内容不改，修改需注明日期）
