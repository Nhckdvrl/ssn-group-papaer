# 零模型审计（公开 MoE 上的专家分工结论）定位扫描（2026-11-09）

**只写定位，不写判决（R6）；不判死（R1）；去留由人定（R2）。** 主旨来源：`workbench/mechanism-population-dynamics/division/DIRECTION_2026-11-06.md` §15。动机数据：`division/results/e176/summary_table.md`（自训平台上 7 类已发表读数，4 条在 step 0 判定相同）。证据标签：`[全文]` / `[节]` / `[摘要]` / `[旧笔记]`（沿用 `MOE_EXPERT_ANALYSIS_HISTORY_2026-11-05.md`、`READOUT_CATALOGUE_…_2026-11-06.md`、`POSITIONING_RA_2026-11-06.md`）；"未核对"= 没拿到原文或只凭记忆。

**检索主旨（英文）：** "Audit published MoE expert-specialization claims (token class, word form, language, domain, position, early routing) on public MoEs against a geometry null: the same hidden states routed by a random projection of the router; report which claims exceed the null, by how much, and from which OLMoE training step."
**检索范围：** venue corpus `query.py nearest` 6 句（审计主旨、按 token / 语言 / 领域专精、随机路由基线、几何继承、未训练基线、OLMoE 中间 checkpoint），各取前 10 已接收 + 5 被拒；arXiv API 7 组限定查询（按提交日期倒序）+ 按 ID 取 30 篇摘要核对；Web 检索 9 组（含 "random router" / "uninformative router" / "expert specialization illusion / myth" / 多语语言专家 / OLMoE checkpoints / 未训练网络的类别选择性）；HF API 核对 checkpoint 列表。未覆盖：OpenReview 未挂 arXiv 的投稿、非英文文献、Google Scholar 引用链（新预印本尚无引用）。

## 1. 精确撞车检查

**答：核心做法已有人做过一次，但只覆盖"领域 / 话题"一类结论，只在终点 checkpoint。** Melton, *Rotate the Router: A Control for Expert-Specialisation Claims in MoE Models*（Zenodo 预印本，2026-10-09，DOI 10.5281/zenodo.22693777，单作者，未经同行评审，不在 arXiv）`[节：摘要、§1–5、§13–14 局限与结论，PDF 全文已下载到会话 scratchpad]`：
- **控制 = 我们的 N1 的近亲：** W′ = W·R，R 为 Haar 随机正交阵，保留奇异值与行范数，作用在**未改动模型捕获的同一批隐状态**上，"a reference distribution, not an intervention"；另用 Frobenius 范数匹配的高斯门作第二参照；报负载均衡以排除塌缩。我们的 N1 = 读出子空间内旋转 + 重拟合偏置匹配负载（`FINDINGS_2026-11-04.md`），差别只在"子空间内 / 全空间"与"是否匹配负载"。
- **读数：** 只有话题分离（6 话题 × 固定百科体裁，444 篇文档；层内逐 cell 路由分布的平均两两 JSD，对标签置换零假设）。原文写明 "the same construction scores a claim about language, task or user segment"，但**没做语言、词类、词形、位置、饱和、共激活**。
- **模型：** OLMoE-1B-7B、OLMoE-Instruct、Granite-3.1-3B-A800M、Mixtral-8x7B（4-bit，路由器 fp16）、BAR-5x7B；**全部是终点 checkpoint，无训练轴，无 seed，英文**。
- **数字：** 旋转门本身高出置换零假设 17.4–26.0×；训练门 ÷ 旋转门：OLMoE 3.82×、OLMoE-Instruct 4.34×、Granite 1.14×、Mixtral 0.33×、BAR 0.45×；顺序"随专家数"（作者明说 4 个点、不作因果）。另有路由器重拟合、专家删除、装上旋转门跑任务（GSM8K 归零）等干预。
- **其余最近的两篇：** Wang, Hayou, Nalisnick 2604.09780《Myth of Expert Specialization》`[节]`：提出"路由反映几何"的论证与 Lipschitz 界，**没有跑随机路由器零模型**（WebFetch 全文核对：对照是 OOD 打乱、平凡界、同模型异题），不审计词类 / 语言结论。Avinash 2603.11114 `[摘要；经 Melton 转述]`：OLMoE-Instruct 上任务条件路由签名，用了**置换与负载均衡基线**，没有随机路由器。
- **未找到：** 把几何零模型用在 token 级（词类 / 词形 / "token ID 决定专家"）结论、语言专家结论、位置结论上的工作；沿训练过程（OLMoE 中间 checkpoint）报"何时超出几何零模型"的工作；把几何零模型与未训练模型地板（step 0）放在一起比的工作。

## 2. 定位表（近邻 → 距离 → 谁 own 哪句话）

| 近邻（证据） | venue / 年 | 测了什么 | 模型 | 零模型 / 基线 | 与我们的距离 | 已 own 的句子 | 压缩风险 |
|---|---|---|---|---|---|---|---|
| Melton, Rotate the Router `[节]` | Zenodo 预印本 2026-10 | 话题分离 JSD；训练门 vs 旋转门；干预 | OLMoE×2、Granite、Mixtral、BAR（终点） | **Haar 旋转门 + 高斯门 + 标签置换** | 同一控制；只差读数类别（token / 语言 / 位置 / 饱和）、训练轴、step-0 对照、负载匹配 | "专精分析须与同一隐状态上的随机旋转路由器比较"；"任意投影就能分开话题 17–26×"；"Mixtral 低于自身旋转"；"超出量随专家数排序" | **高**（做法与领域那一行）；审稿人可说"这是 Melton 的控制换几个读数" |
| Myth of Expert Specialization 2604.09780 `[节]` | arXiv 2026-04 | 隐状态相似 ⇒ 路由相似（命题 1）；负载均衡抑制共享方向 | gpt-oss-20b、Qwen3-30B、ERNIE-4.5-21B、Ling-mini、Trinity-Mini | 无随机路由器；OOD 打乱、平凡界 | 他们给论证，我们给逐条结论的数 | "专精是表示几何的涌现性质，不必是领域知识" | 中–高（对手假设本身归他们） |
| Task routing signatures 2603.11114 `[摘要]` | arXiv 2026-03 | 同任务提示路由签名相似 .84 vs .62 | OLMoE-1B-7B-0125-Instruct | 置换、负载均衡基线 | 其结论正是一条可审计对象 | "OLMoE 路由按任务类别分" | 低 |
| Expert Strikes Back 2604.02178 `[旧笔记]` | ICML 2026 | 专家单义性；专家 = 细粒度任务专家 | 12 个模型 | Random Expert Baseline（按层基率抽样） | 他们的基线控负载不均，不控几何（Melton §2 已点明） | "专家既非领域专家也非 token 处理器" | 低 |
| Standing Committee 2601.03425 `[旧笔记]` | ACL 2026 | 跨领域不变的 2–5 个专家吃 30–70% 路由 | OLMoE、Qwen3-30B-A3B、DeepSeek-V2-Lite | **无**（Limitations 自认无随机 / 频率匹配对照） | 审计对象 | "领域专精是错觉，存在常设委员会" | 低–中 |
| Antoine 等 2412.16971 `[旧笔记 全文]` | COLING 2025 | Spec_POS、ΔU、路径探针 | 6 个公开 MoE（含 OLMoE、Mixtral） | 均匀期望 U；词形多数类 .91 | 审计对象（POS 一行的主来源） | "所有模型的 POS 专精都高于均匀" | 低 |
| How Modular Is a Frontier MoE 2606.25092 `[旧笔记 全文]` | arXiv 2026-06 | 预注册 6 个模块，消融 | 218B 前沿 MoE（单模型） | 同规模随机专家集 null | 同为"审计"形态，但测因果模块性、不测路由读数对几何 | "表面模块性多数在预注册检验下消失" | 中（审计形态） |
| Heap 等 2501.17727 `[摘要]` | ICLR 2026 | SAE 自动解释分数 | Pythia 训练 vs 随机初始化 | 随机初始化模型 | 原则相同，对象不同 | "解释性指标须并报随机基线" | 中（原则层面） |
| Geometric Routing 2604.14434 `[旧笔记 全文]` | arXiv 2026-04 | 句法 vs 频率分组轮廓系数 | 自训 rank-1 cosine MoE | 200 次置换 | 自训、单 checkpoint | "路由按句法类组织" | 低 |
| Coherent Overlap 2607.28308 `[摘要]` | arXiv 2026-07 | 专家子空间重叠；选中 vs 匹配替代路由 | 6 个 MoE（OLMoE、Mixtral、DeepSeek 等） | 匹配替代路由、前缀 2×2 | 问专家几何，不审计专精结论 | "路由从共享几何邻域里选相关专家" | 低 |
| Hash / SMoE-Dropout / Self-Routing（2106.04426、2303.01610、2604.00421）`[旧笔记 节]` | NeurIPS'21 / ICLR'23 / 2026 | 用随机 / 冻结路由**训练** | 自训 | 性能比较 | 训练时替换 vs 推理时零模型 | "冻结随机路由性能不输" | 低（不同问题） |
| Three Phases 2604.04230 `[旧笔记 全文]` | arXiv 2026-04 | 拥塞系数随训练三阶段 | OLMoE 20 ckpt + OpenMoE 6 | 无 | 用了同一条 OLMoE 轨迹，测负载不测专精 | "负载均衡随训练三阶段" | 低 |
| SAE Interprets MoE 2611.08089 `[摘要]` | arXiv 2026-11-05 | 专家在 SAE 特征上的贡献分解 | Qwen3-30B-A3B | 无 | 测贡献不测选择；可作"读数不同则结论不同"的旁证 | "专家贡献比门控更集中" | 低 |

## 3. 待审计的已发表结论清单

"E176" 列 = 自训平台上训练后 / step 0 的判定（`results/e176/summary_table.md`）；"—"= 平台上未测。

| # | 结论（简） | 来源 | 原模型 | 读数定义 | 原文对照 | E176 |
|---|---|---|---|---|---|---|
| A1 | 编码器专家按 token 类专精、解码器不专精 | ST-MoE 2202.08906 §7 | ST-MoE-32B（编–解） | 某类 token 的路由熵 vs ln(E) | 均匀熵 | #6：0/9，step0 0/6 |
| A2 | 所有模型 POS 专精高于均匀 +25～+36pp | Antoine 2412.16971 §3–4 | Mixtral、OLMoE 等 6 个 | Spec_POS − U；专家 POS 分布 KL；路径探针 | 均匀 U、词形多数类 .91 | #8：9/9，step0 未判 |
| A3 | token ID 决定专家、与上下文无关 | OpenMoE 2402.01739 §4.1；BASE 2103.16716 §5.2；Shazeer 1701.06538 附录 E | OpenMoE-8B/34B；BASE；LSTM-MoE | 同一 token 的专家集中度；每专家 top token 表 | **无** | #7a：9/9，**step0 0/6**（唯一由训练产生的） |
| A4 | 深层按预测输出 token 专精，浅层按输入 token | OLMoE 2409.02060 §5.4 | OLMoE-1B-7B | N(x,E)/N(x)，x = 输入 / 预测下一词 | **无** | — |
| A5 | 路由早定（1% 训练 top-8 约 60% 饱和；warmup 即定；早期稳定） | OLMoE §5.1；OpenMoE §4.2；FLAME-MoE 2505.20225 | OLMoE、OpenMoE、FLAME-MoE | 中间 ckpt 与终点 top-k 交集比例 | 解析随机 k/E | #1a 0/9；#7b 0/9 |
| A6 | 层内共激活弱、少数例外 / 共激活矩阵稀疏 | OLMoE §5.2；FLAME-MoE | 同上 | N(Ei,Ej)/N(Ei) | **无** | #2：0/9，step0 0/6 |
| A7 | 有领域专家（arXiv / GitHub）；Mixtral 很少 | OLMoE §5.3；Mixtral 2401.04088 §5；OpenMoE §4（不按领域） | OLMoE、Mixtral、OpenMoE | N(E,D)/N_D | 解析随机 12.5% / 1/8 | #3：9/9，**step0 6/6** |
| A8 | 无辅助损失均衡 → 更强领域专精 | DeepSeek-V3 2412.19437（节号未核对）；Demons 2501.11873 | DeepSeek-V3 小模型对照；Qwen 自训 | Pile 各领域的专家负载 | 不同均衡方式互比 | — |
| A9 | 领域专家存在 / 常设委员会 / 模块化 vs 分布式 | 2604.05267；2601.03425；DBES 2605.18498；Hu 2601.10159 | 10 个公开 MoE；OLMoE、Qwen3、DSV2-Lite；Qwen3/GLM/DeepSeek；Mixtral、DeepSeek-MoE、Qwen1.5-MoE | g(e)；ECI；S_spec / S_iso / R_eff；熵 + 因果 | 无 / 均匀 / Rademacher | #13：0/9，step0 0/6 |
| A10 | 晚解码层语言专属、同语系相近；中层语言无关、首尾层分语言 | NLLB-200 2207.04672 §6.2.4；Bandarkar 2510.04694（ICLR'26）；2601.14050；2604.03592；2605.29714 | NLLB-MoE-54B；Qwen3、Phi-3.5-MoE、GPT-OSS、OLMoE；Qwen3-30B-A3B；OLMoE 续训 | 语言平均门控余弦；与英语的 JS 散度；top-K Jaccard | **无**（只对英语） | —（平台无多语数据） |
| A11 | 多语混合训练的专家**不**按语言专精 | ST-MoE §7 | ST-MoE | 人工检视 | 无 | — |
| A12 | 相邻 token 同专家（第 0 层近随机，15/31 层显著高） | Mixtral §5 表 5；DBES n-gram 持续 | Mixtral；Qwen3 等 | P(t、t+1 同专家) | 解析随机 12.5% / 46% | — |
| A13 | 句首 / 早位置 token 触发 driver 专家；super experts 与注意力汇点相关 | Hu 2601.10159；Su 等 2507.23279 | Mixtral 等；Qwen3-30B-A3B、DeepSeek | 按位置的激活；激活幅值 | 无（未核对） | — |
| A14 | 按任务类别路由；专家 = 细粒度任务专家 | 2603.11114；2604.02178 | OLMoE-Instruct；12 个模型 | 路由签名；unembedding 聚类 JSD | 置换 + 负载；随机专家 | — |

## 4. 平台可用性（HF API 2026-11-09 核对 checkpoint；显存按 bf16 2 字节/参数估算）

| 模型 | 总参数 / bf16 | 1–2×A100 80G | 中间 checkpoint | 多语训练数据有文档 |
|---|---|---|---|---|
| **OLMoE-1B-7B-0924** | 6.9B / ~14 GB | 1 卡 | **有：244 个分支 `step5000-tokens20B` … `step1220000-tokens5117B`，等距每 5000 步（≈ 21B token）**，另有 `main`、`fp32`；**没有 step 0**（最早 = 20B token，原文称此时已约 60% 饱和） | 数据公开（OLMoE-mix），英文为主，非多语 |
| OLMoE-1B-7B-0125 | 同上 | 1 卡 | 只有第二阶段退火：3 个 ingredient × 5 个点（21B–101B）；无预训练轨迹 | 同上 |
| OpenMoE-8B | ~8B（未核对）/ ~16 GB | 1 卡 | 有：独立仓库 200B / 400B / 600B / 800B / 890B / 1T token，另有 34B-200B；需自定义代码（加载未核对） | RedPajama + The Stack，有文档，英文为主 |
| FLAME-MoE（7 个尺寸，38M–1.7B 激活，最大 10.3B 总参数） | ≤ ~21 GB | 1 卡 | 有：每个尺寸约 10 个 `iter_*`（1.7B 版 iter 1100…11029，约每 10%）；Megatron 格式，HF 加载未核对；无 step 0 | DCLM，英文 |
| Switch-base-8…256（T5 编–解） | ≤ ~15B | 1 卡 | 无（未核对） | C4 英文 |
| Granite-3.1-3B-A800M | 3.3B | 1 卡 | 无 | 未核对 |
| Qwen1.5-MoE-A2.7B / DeepSeek-V2-Lite / DeepSeek-MoE-16B | 14.3B / 15.7B / 16.4B（~29–33 GB） | 1 卡 | 无 | 多语（中英为主）宣称，数据不公开 |
| Qwen3-30B-A3B / gpt-oss-20b / ERNIE-4.5-21B-A3B | 30.5B（~61 GB）/ 21B（原生 MXFP4）/ 21B | 1 卡（Qwen3 偏紧） | 无 | Qwen3 宣称 119 种语言，数据不公开 |
| Mixtral-8x7B / Phi-3.5-MoE | 46.7B（~93 GB）/ 41.9B（~84 GB） | 2 卡 | 无 | 宣称多语（Mixtral 英法德西意），数据不公开 |
| NLLB-MoE-54B | ~109 GB | 2 卡 | 无 | **200 种语言，数据与语言标签有文档**（A10 原始结论的模型） |
| DeepSeek-V2 / V3、Qwen3-235B、dots.llm1（142B，报告称每 1T token 放中间 ckpt，未核对） | ≥ 280 GB | 否 | dots.llm1 可能有 | — |

**要点：** 带中间 checkpoint 且 1 卡可跑的只有 OLMoE-0924（密、等距、5T token）、OpenMoE（6 点）、FLAME-MoE（7 个尺寸 × 约 10 点）。三者都是英文为主，**语言类结论（A10）只能在没有训练轴的模型上审计**（NLLB-MoE、Qwen3、Mixtral）。三者都没有 step 0；"未训练"只能按公开配置重新初始化得到同分布的随机模型，不是同一个初始化。

## 5. 不含判决的小结

**候选的"可 own 句子"（扫描范围内无近邻 own）：**
1. **token 级结论的几何审计：** 词类（A1、A2）、词形 / "token ID 决定专家"（A3、A4）这批最常被引用的结论，逐条在原模型（OLMoE、OpenMoE、Mixtral 等）的同一隐状态上对随机投影路由器打分，报每条超出零模型多少。Melton 只做话题；Myth 只给论证；Antoine 等的基线是均匀分布。
2. **"何时超出零模型"的训练轴：** 在 OLMoE-0924 的 244 个等距 checkpoint（及 OpenMoE 6 点、FLAME-MoE 多尺寸）上，逐条读数报"训练路由器 ÷ 几何零模型"随训练步的曲线。现有工作要么有轨迹无零模型（OLMoE §5.1、OpenMoE §4.2、Three Phases、FLAME-MoE），要么有零模型无轨迹（Melton）。
3. **语言专家结论的几何审计：** NLLB-200"晚解码层语言专属"、Qwen3"语言专属专家"、Bandarkar"首尾层分语言、中层共享"这类结论，有多少是残差流里语言身份本来就线性可分、任何同条件数的投影都会分开的。Melton 说过"可以用于语言"，没做。

（较弱的第四句：几何零模型（训练后隐状态 + 随机投影）与未训练模型地板（step 0）是两种零模型，E176 显示 4/7 条结论在 step 0 已成立；两者在同一条结论上给出的判定是否一致，没人报过。但公开模型都没有 step 0，只能在自训平台上答。）

**两个最大的科学风险（不是审稿措辞问题）：**
1. **零模型本身不能把"路由器学到的"和"几何继承的"干净分开。** 隐状态是与路由器共同训练出来的：专家输出写回残差流，路由器行与专家输入权重耦合累积（Routers Learn Geometry 2605.12476）。所以"同一隐状态上的随机投影"给出的分离，部分可能本来就是路由学习塑造的几何；"超出零模型"测到的是路由器朝向，而不是"专精由谁产生"。另外零模型的构造会改结论：全空间 Haar 旋转（Melton）、读出子空间内旋转 + 负载匹配（我们的 N1）、高斯门、按负载随机分配，各给一个分母；2606.25092 已示范过"判定随测量翻转"。对手假设要成立为可判的二选一，需要在跑之前写死零模型族和"翻转"的处理。
2. **OLMoE 训练轴左删失、只有一条轨迹。** 最早的公开 checkpoint 是 20B token，原文称那时 top-8 已约 60% 饱和；自训平台锁定在第 100–200 步。可能所有读数在第一个 checkpoint 就已定型，于是"从哪一步开始超出零模型"的答案对每条结论都是"第一个点之前"，训练轴不提供区分信息。OpenMoE（首点 200B）与 FLAME-MoE（首点约 10%）同样左删失；三者都是英文，语言结论没有训练轴可用。早期段只有自训平台能补，而那正是 §15 想离开的平台。

**定位层面的事实（供人判断时用）：** 做法本身（同一隐状态上的随机旋转路由器）已被 Melton 2026-10 own，领域 / 话题那一行压缩风险高；它是未评审的 Zenodo 单作者预印本，但按 R6 仍须列为 claim owner 并引用。Melton 的"超出量随专家数排序"（4 个点）与我们配方轴"init÷重跑随专家数单调"（§14）方向一致，可作旁证，不能写成我们的发现。

## 6. 相邻领域："专精 / 选择性"结论的零模型先例

| 领域 | 工作（证据） | 零模型 | 结论 | 对本提议的意义 |
|---|---|---|---|---|
| 探针 | Hewitt & Liang 1909.03368 `[摘要]` | 控制任务（随机词型标签） | 高探针准确率可能来自探针本身的容量；报 selectivity | "专精读数高"要减去任意标签也能得到的部分 |
| 探针 | Zhang & Bowman 1809.10040；Wieting & Kiela 1901.10444 `[摘要]` | 随机初始化编码器 | 未训练编码器已有相当的句法 / 分类表现 | 与 E176 "step 0 已成立"同形 |
| 探针 | Pimentel 等 2004.03061 `[摘要]` | 信息论框架 | 用控制函数度量"表示增加了多少信息" | 读数应报超出零模型的增量，不报原值 |
| 显著性图 | Adebayo 等 1810.03292 `[摘要]` | 模型参数随机化检验 | 若干解释方法对随机化不敏感 | 最早的"换成随机权重看结论是否不变"范式 |
| SAE / 自动解释 | Heap 等 2501.17727 `[摘要]` | 随机初始化 Pythia | 指标分不开训练 / 随机模型 | 原则归他们（§2 表） |
| 神经元 | Gurnee 等 2401.12181 `[旧笔记]` | 随机旋转基 | 只有 1–5% 神经元跨 seed 通用 | 随机旋转作基线 = N1 / Melton 的同一思路 |
| 神经元选择性 | Morcos 等 1803.06959；Leavitt & Morcos 2003.01262 `[摘要]` | 消融 / 正则化选择性 | 类选择性高不等于对功能重要 | "专精 ≠ 重要"，与 Melton 干预部分、2606.25092 同向 |
| 计算神经科学 | Baek 等 2021 Nat Commun（doi 10.1038/s41467-021-27606-9）`[摘要]`；Kim 等 2021 Sci Adv（数感，doi 10.1126/sciadv.abd6127，未核对正文） | 未训练 AlexNet | 面孔 / 数量选择性单元在随机初始化网络中出现 | "类别选择性不需要学习"的最强先例；对应 E176 体裁专精 step 0 6/6 |
| 随机 Transformer | Zhong & Andreas 2410.04368 `[摘要]` | 只训练嵌入的随机 Transformer | 很多算法能力在初始化时已存在 | "能力归因须减去初始化已有的" |
