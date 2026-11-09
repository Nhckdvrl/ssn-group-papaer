# Key Papers — MoE 与路由（单一入口）

**更新：** 2026-11-09。本页是本目录的入口：先读 §1 认知现状，再按 §2 表找论文、按 §4 索引找详细笔记。只写定位，不写判决（AGENTS.md R6）；去留由人定（R1/R2）。
**证据口径：** 各文件的 `[全文]/[节]/[摘要]` 标签以原文件为准；本页 venue 标"未核对"的是凭记忆。文件代号见 §4。

## 1. 认知现状（2026-11）

专家"分什么工"自 Jacobs 等 1991 起就是 MoE 的核心问题；2017 年后每代大 MoE 都附一节专家分析，反复得出"按词形 / 词类 / 标点分、不按主题分、路由早定"（ST-MoE §7、Mixtral §5、OpenMoE §4、OLMoE §5、Antoine COLING'25），基线几乎都是解析均匀值或干脆没有。
2026 年出现"领域专精是错觉"一支（Standing Committee ACL'26、Expert Strikes Back ICML'26、How Modular 2606.25092），但除后者的预注册消融外，对照只控负载、不控表示几何；Standing Committee 在 Limitations 里自认没有随机 / 频率匹配对照。
Myth 2604.09780 论证线性路由器下"隐状态相似 ⇒ 路由相似"，专精是表示几何的涌现性质，但没有跑随机路由器；Routers Learn Geometry 2605.12476 显示路由器与专家输入权重耦合累积，所以"几何"本身部分由路由塑造，零模型分不干净。
Melton《Rotate the Router》（Zenodo 2026-10，单作者未评审）首次在同一批隐状态上用 Haar 旋转路由器作零模型：任意旋转门已把话题分开 17–26×，训练门 ÷ 旋转门只有 0.33–4.34×（Mixtral、BAR 低于旋转门）；只做话题、只看终点 checkpoint。
我们的 E178/E179（FLORES-200 20 语）把同类控制用到语言：Qwen3-30B-A3B 上随机路由器复现"首尾层语言专属、中层共享"层剖面（U 对比 2.35 vs 2.34，剖面 Spearman .95）；GPT-OSS-20B 只对负载匹配零模型复现；OLMoE 训练路由器本身几乎无 U（1.11），零模型反而有。
三模型上训练路由器都在负载匹配零模型之上乘一个近似与深度无关的常数（1.1–1.8×，首尾 ÷ 中层 0.90–1.02），锐度匹配后不消失；零模型族在 GPT-OSS 与 OLMoE 上把判决翻向相反方向。
稠密模型侧，"首尾层语言专属、中层共享"在神经元计数与 logit lens 上是共识（Tang ACL'24、Kojima NAACL'24、Wendler ACL'24 等 ≥ 6 篇主会），但 Holmström 2609.04819 指出全维探针下中层语言身份只是被挪出主子空间（残差子空间 96–99%）；我们 E179 的全维 token 探针在 Qwen3 / GPT-OSS 上反而呈 U（首尾 .97 / 中层 .92）——U 形是否成立依赖读数层级。
已发表的 MoE 语言专家结论——NLLB-200 §6.2.4（晚解码层分语言）、Bandarkar ICLR'26（"四模型皆 U"，原文自承 OLMoE、Phi-3.5 例外）、Chen 2601.14050（中层"语言无关枢纽"）、Zheng 2604.03592——都没有随机路由器、置换或隐状态对照；Bandarkar 一句 "If the representations are aligned, the routing would also be" 已写出几何解释但未检验。
跨独立训练：Equifinality（2 seed）、视觉 MoE 2605.20610（10 seed，粗划分稳定）、LMC-MoE（损失层面置换等价）都没有重跑上限或未训练地板；冻结 / hash 路由对损失无害已被 Hash Layers、SMoE-Dropout 等 own（到 4.5B，Clark 2022 在更大规模反证）；"解释指标须并报随机基线"的原则归 Heap ICLR'26。
仍开放：路由器何时跟随几何、何时偏离（OLMoE 几何有 U 而路由无 U，原文归因于多语弱）；常数倍从哪来；token 级与语言结论在原模型上超出几何零模型多少；零模型族怎么选才不改判决。

## 2. 关键论文表（29 篇；另 3 篇架构锚点）

| ID | 论文 | arXiv | venue / 年 | 一句话主张 | 对照 | 我们的文件 |
|---|---|---|---|---|---|---|
| MOE04 | ST-MoE §7 | 2202.08906 | arXiv 2022 | 编码器专家按 token 类专精、解码器不专精；多语训练不按语言分 | 均匀熵 ln E | NA、ROC、SURV |
| MOE05 | NLLB-200 §6.2.4 | 2207.04672 | Nature 2024 | 晚解码层专家按语言分、同语系相近 | none | NA、LG、ROC |
| MOE06 | Mixtral §5 | 2401.04088 | arXiv 2024 | 不按主题分；相邻 token 常同专家 | 解析随机 1/8 | NA、ROC、HIST |
| MOE07 | OpenMoE §4 | 2402.01739 | ICML 2024（未核对） | 按 token ID 路由、上下文无关、warmup 即定 | none | NA、RA、HIST |
| MOE08 | OLMoE §5 | 2409.02060 | ICLR 2025（未核对） | 1% 训练 top-8 约 60% 饱和；有领域专家；深层按预测 token 专精 | 解析随机 12.5% | NA、RA、HIST、OLMOE 卡 |
| MOE09 | Antoine 等 POS sensitivity | 2412.16971 | COLING 2025 | 6 个公开 MoE 的 POS 专精高于均匀 +25～+36pp | 均匀 U；词形多数类 .91 | NA、ROC、HIST |
| MOE10 | Hash Layers | 2106.04426 | NeurIPS 2021 | 按 token hash 路由不输 Switch（到 4.5B） | 训练时性能比较 | RA、NA |
| MOE11 | SMoE-Dropout | 2303.01610 | ICLR 2023 | 随机初始化后冻结的路由器，专家 ≥ 16 时优于学习路由 | 训练时性能比较 | RA、NA |
| MOE12 | Clark 等 Unified Scaling | 2202.01169 | ICML 2022（未核对） | 学到的 S-BASE 在所有规模都优于 HASH / RL-R（反证） | 规模扫描 | RA |
| MOE13 | Standing Committee | 2601.03425 | ACL 2026 | 跨领域不变的 2–5 个专家吃 30–70% 路由；领域专精是错觉 | none（自认） | NA、RA、HIST、SURV、GPF、VEN |
| MOE14 | The Expert Strikes Back | 2604.02178 | ICML 2026 | 专家既非领域专家也非 token 处理器，是细粒度任务专家 | 随机专家基线（控负载不控几何） | NA、SURV、VEN |
| MOE15 | How Modular Is a Frontier MoE | 2606.25092 | arXiv 2026-06 | 预注册 6 个模块只剩 1 个；模块性随指标 / 语料翻转 | 预注册 + 同规模随机专家 null | NA、SURV、GPF |
| MOE16 | Myth of Expert Specialization | 2604.09780 | arXiv 2026-04 | 隐状态相似 ⇒ 路由相似；专精是表示几何的涌现性质 | 无随机路由器（OOD 打乱、平凡界） | NA、LG、RA、HFN、SURV |
| MOE17 | Routers Learn the Geometry | 2605.12476 | NeurIPS 2026（见 §5） | 路由器与专家输入权重耦合累积；K-Means 质心路由只差 2.6% PPL | 路由器变体；无零模型 | RA、NA、FTR、SURV、ROC |
| MOE18 | Melton, Rotate the Router | Zenodo 10.5281/zenodo.22693777 | 预印本 2026-10 | 话题分离须与同一隐状态上的旋转路由器比；旋转门已分开 17–26× | **Haar 旋转门 + 高斯门 + 标签置换** | NA、LG |
| MOE19 | Bandarkar 等 Multilingual Routing | 2510.04694 | ICLR 2026 | 路由与英语的散度首尾高、中层低（U）；中层干预改善跨语迁移 | 路由读数 none；干预有随机子集 | LG、NA、HIST、VEN |
| MOE20 | Chen 等 Multilingualism in MoE | 2601.14050 | arXiv 2026-01 | 中层为语言无关"容量枢纽"、首尾语言专属（功能分层） | none（屏蔽他语独占专家） | LG、NA、HIST |
| MOE21 | Zheng 等 Language Routing Isolation | 2604.03592 | arXiv 2026-04 | 路由中层收敛、浅深层分化（Qwen3 Jaccard 表） | none | LG、HIST |
| MOE22 | Khandelwal 等 Routing Dynamics | 2605.29714 | arXiv 2026-05 | OLMoE 续训 7 语后只有末层分语言（不是 U）；路由相似跟词表重叠 | none | LG、HIST |
| MOE23 | Equifinality in MoE | 2604.14419 | arXiv 2026-04 | 跨 seed 专家词表投影 Jaccard .13–.15 ≫ 随机，权重余弦 ≈ 随机 | 解析随机；2 seed | RA、ROC、SURV、HIST |
| MOE24 | Vision MoE: Beyond Routing | 2605.20610 | arXiv 2026-05 | 有生 / 无生粗划分跨 10 seed 与专家数稳定 | none（无随机 / 未训练 / 重跑） | RA、FR、HIST |
| MOE25 | LMC of MoE | 2509.11348 | NeurIPS 2025 Oral | 独立训练的 MoE 经专家置换对齐后线性连通 | 置换对齐；3 init | RA、CRP、GPF |
| MOE26 | Tang 等 Language-Specific Neurons | 2402.16438 | ACL 2024 | 稠密 LLM 的语言专属神经元集中在首尾层 | none | LG |
| MOE27 | Kojima 等 | 2404.02431 | NAACL 2024 | 语言专属神经元主要在首尾若干层，跨模型一致 | none | LG |
| MOE28 | Wendler 等 Do Llamas Work in English? | 2402.10588 | ACL 2024 | logit lens：输入空间 → 中层偏英语概念空间 → 末层回输入语言 | none | LG |
| MOE29 | Holmström 等 Anisotropy-Driven Failures | 2609.04819 | arXiv 2026-09 | 共享层语言身份被挪到残差子空间（96–99%），不是被消除 | 主子空间 vs 残差子空间探针 | LG |
| MOE30 | MultiBERTs | 2106.16163 | ICLR 2022 | 单 checkpoint 的结论未必推广到训练程序 | 25 seed；Multi-Bootstrap | RA、VEN |
| MOE31 | Gurnee 等 Universal Neurons | 2401.12181 | TMLR 2024 | GPT-2 换 seed 只有 1–5% 神经元 universal | 随机旋转基 | RA、NA、SURV |
| MOE32 | Heap 等 SAE on random transformers | 2501.17727 | ICLR 2026 | 自动解释分数分不开训练模型与随机初始化模型 | 随机初始化模型 | RA、NA |

**架构锚点（ID 沿用 2026-09-30 拆分，`library/KEY_PAPERS.md` 引用）：** MOE01 Switch Transformers [2101.03961](https://arxiv.org/abs/2101.03961)（top-1 路由、规模与稳定性基线）；MOE02 Expert Choice Routing [2202.09368](https://arxiv.org/abs/2202.09368)（expert→token 选择，提醒路由原语本身是设计选择）；MOE03 DeepSeekMoE（[ACL 2024](https://aclanthology.org/2024.acl-long.70/)，共享 + 细粒度专家）。新增条目沿用下一个编号 MOE33。

## 3. Claim ownership（我们可能写的句子 → 谁 own 最近的那句）

| 我们可能写的句子 | 最近的 owner 与他们的句子 | 我们的增量 | 压缩风险 |
|---|---|---|---|
| 随机路由器在同一隐状态上复现已发表的语言层剖面 | Bandarkar（"If the representations are aligned, the routing would also be"，只针对中层，未检验）；Myth（一般论证）；Melton（方法，只做话题）；Tang / Kojima / Wendler（稠密 U 形） | 检验与数字；但只在 Qwen3 干净成立，GPT-OSS 依赖零模型族，OLMoE 不成立 | **高** |
| 训练路由器在几何之上乘一个与深度无关的常数（不是锐度） | 无人 own；最近是 Melton 的逐模型"训练门 ÷ 旋转门"（每模型一个数，不分层） | 逐层、三模型、锐度匹配后仍在 | 低–中（GPT-OSS 首尾 ÷ 中层 0.90，"常数"须带范围） |
| 专精是否"超出几何"的判决随零模型族翻转 | 2606.25092（判定随指标 / 语料 / 门槛翻转，不是零模型族）；Melton 并报 Haar 与高斯两种但未报翻转 | 语言结论上 Haar vs 负载匹配方向相反（GPT-OSS、OLMoE） | 中（易被读成方法学脚注） |
| 专家级跨 seed 可重现度低、类别 / 模型级高 | Gurnee（1–5% 神经元 universal）；Paulo & Belrose 2501.16615（SAE 30%）；Equifinality（2 seed Jaccard）；2605.20610（粗划分稳定）；LMC-MoE（损失层面） | 同一套 9 run 上展开粒度，并以精确重跑为上限、step 0 为地板 | 中–高 |
| 冻结 / 随机路由器不损失性能 | Hash Layers、THOR、SMoE-Dropout、Self-Routing 2604.00421；反证 Clark 2022 | 无——只能带引用作背景 | 已 own |
| 解释性读数须并报随机 / 未训练基线 | Heap ICLR'26；Dead Salmons（撤稿）；Hewitt & Liang 控制任务 | MoE 读数上逐条报 step 0 判定 | 原则已 own |

## 4. 文件索引（代号 · 日期 · 一行内容 · 状态）

**现主旨（division §15 零模型审计 / 语言几何）直接用：**
- NA = [POSITIONING_NULLAUDIT_2026-11-09](POSITIONING_NULLAUDIT_2026-11-09.md) · 11-09 · Melton 撞车检查、14 条待审计已发表结论、公开 MoE checkpoint 可用性、相邻领域零模型先例 · 现行
- LG = [POSITIONING_LANGUAGE_GEOMETRY_2026-11-09](POSITIONING_LANGUAGE_GEOMETRY_2026-11-09.md) · 11-09 · 稠密多语逐层几何、MoE 语言路由文献、E179 与原文逐模型对账 · 现行（§2 "四模型皆 U" 以 §5 为准）
- ROC = [READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06](READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md) · 11-06 · 21 种现成读数（能否 CPU 复算）、专家几何度量、Equifinality / Geometric Routing 精读 · 现行
- HIST = [MOE_EXPERT_ANALYSIS_HISTORY_2026-11-05](MOE_EXPERT_ANALYSIS_HISTORY_2026-11-05.md) · 11-06 v2 · 1991–2026 专家分析史与度量目录，逐篇核原文 · 现行
- VEN = [VENUE_PARADIGMS_2026-11-06](VENUE_PARADIGMS_2026-11-06.md) · 11-06 · 顶会 MoE 分析 / 稳健性论文范式卡（评审原话未核对） · 现行
- RA = [POSITIONING_RA_2026-11-06](POSITIONING_RA_2026-11-06.md) · 11-06 · R-A（跨 seed 可重现度）主旨的定位表 · **部分取代**：主旨已转向 §15，(c) 冻结 / hash 路由 ownership 与"未训练地板"先例仍有效
- SURV = [SURVEY_SPECIALIZATION_UNIVERSALITY_2026-11-05](SURVEY_SPECIALIZATION_UNIVERSALITY_2026-11-05.md) · 11-05 · 52 篇专精与跨训练普遍性精读 + 相邻领域 · **部分取代**：数字冲突时以 HIST v2 为准
- [README](README.md) · 11-06 · 题材热度、T05 territory 笔记 · 文件链接列表由本节取代

**旧线背景（已摒弃的 `moe/` 计算组织线 E133–E166，供 lineage 查阅，不针对现主旨）：**
- CRP = [CONTROLLED_REPRODUCIBILITY_PAPER_CARDS_2026-10-25](CONTROLLED_REPRODUCIBILITY_PAPER_CARDS_2026-10-25.md) · 10-25 · LMC-MoE、RouterInterp、GaP-MoE 卡
- EAC = [EXPERT_ALIGNMENT_PAPER_CARDS_2026-10-26](EXPERT_ALIGNMENT_PAPER_CARDS_2026-10-26.md) · 10-26 · 专家对应 / 合并 / 蒸馏 / 统计 MoE 16 张卡
- [NATIVE_ROUTER_DICTIONARY_CARD_2026-10-26](NATIVE_ROUTER_DICTIONARY_CARD_2026-10-26.md) · 10-26 · The Router Already Knows（原生路由选字典）
- OLMOE 卡 = [OLMOE_NATIVE_HISTORY_CARD_2026-10-26](OLMOE_NATIVE_HISTORY_CARD_2026-10-26.md) · 10-26 · OLMoE §5.1–5.2 饱和与共激活
- [EMO_MATURE_ASSET_CARD_2026-10-27](EMO_MATURE_ASSET_CARD_2026-10-27.md) · 10-27 · EMO 涌现模块性预训练资产
- FR = [FUNCTIONAL_ROLES_FULL_READING_2026-10-27](FUNCTIONAL_ROLES_FULL_READING_2026-10-27.md) · 10-27 · Sparsity Moves Computation、Vision MoE Beyond Routing、Basic-Refinement
- HFN = [HISTORY_FUNCTION_NEIGHBORS_2026-10-27](HISTORY_FUNCTION_NEIGHBORS_2026-10-27.md) · 10-27 · Myth 全文卡、MoE Lens
- [LRE_ROME_FULL_READING_2026-10-27](LRE_ROME_FULL_READING_2026-10-27.md) · 10-27 · LRE 与 ROME：可读出 vs 实际计算路径
- [RECENT_PRUNING_DISTANCE_2026-10-27](RECENT_PRUNING_DISTANCE_2026-10-27.md) · 10-27 · Training-Free Halving、OptEP
- [CONTEXTUAL_ROLES_FULL_READING_2026-10-28](CONTEXTUAL_ROLES_FULL_READING_2026-10-28.md) · 10-28 · Hydra、Self-Repair、CoAx 等补偿 / 消融五篇
- GPF = [GLOBAL_POSITIONING_FULL_READING_2026-10-28](GLOBAL_POSITIONING_FULL_READING_2026-10-28.md) · 10-28 · Monet、LMC-MoE、Standing Committee、How Modular 等八篇
- [ERC_FULL_READING_2026-10-29](ERC_FULL_READING_2026-10-29.md) · 10-29 · ERC 路由–专家耦合辅助损失
- FTR = [FUNCTIONAL_TRANSFER_AND_ROUTING_2026-10-29](FUNCTIONAL_TRANSFER_AND_ROUTING_2026-10-29.md) · 10-29 · model stitching 三篇、Routers Learn Geometry、Multi-Way Alignment
- [SELECTABLE_COMPUTATION_AND_HISTORY_2026-10-29](SELECTABLE_COMPUTATION_AND_HISTORY_2026-10-29.md) · 10-29 · HOPE、CD-MoE、Super Experts、Massive Activations 等八篇

**历史结果：** [MOE_ROUTE_CLOSEOUT](MOE_ROUTE_CLOSEOUT.md) · 10-09 · 路由偏好 vs 实际 Top-K 负结果（CLOSED，不恢复）。

**我们的实验：** E176 `workbench/mechanism-population-dynamics/division/results/e176/summary_table.md`；E178 / E179 `division/results/e178/tables.md`、`division/results/e179/tables.md`；对账见 `division/DIRECTION_2026-11-06.md` §15.3。

## 5. 文件间口径差异（以本页为准，原文件未改）

- **E176 "step 0 判定相同"的分母：** RA 写"11 条里 4 条"，NA 写"7 类读数 4 条 / 4/7"。前者按 summary_table 模型级行数（11 行），后者按读数类别（#1/2/3/6/7/8/13）。引用时写明单位。
- **Standing Committee 的模型数：** RA 写"单模型"，NA / HIST 写 3 个（OLMoE、Qwen3-30B-A3B、DeepSeek-V2-Lite）；以 3 个为准（HIST 为全文阅读，RA 只读摘要）。
- **Myth 2604.09780 的模型数：** HIST 写"3 个公开 MoE"，NA 与 HFN（全文 31 页）列 5 个（gpt-oss-20b、Qwen3-30B、ERNIE-4.5-21B、Ling-mini、Trinity-Mini）；以 5 个为准。
- **Bandarkar 2510.04694 的规模：** LG 写 4 模型、12 语 + 英语（全文），VEN 写"3 个公开模型""15+ 语言"（节）；以 LG 为准。"四模型皆 U"只对 Qwen3、GPT-OSS 干净成立（LG §5）。
- **venue：** Routers Learn Geometry 在 SURV / HIST 记为 NeurIPS 2026、在 FTR 记为预印本 v1；RouterInterp 2610.11775 在 SURV / HIST / VEN 记为 ICML 2026、在 CRP 记为 2026-10 预印本。均未独立核对。
- **E178 单模型 vs E179 三模型：** LG 页首的"随机路由器复现层剖面"只针对 Qwen3（E178）；E179 后该句须限定为 Qwen3 干净、GPT-OSS 依赖零模型族、OLMoE 不成立（DIRECTION §15.3）。
