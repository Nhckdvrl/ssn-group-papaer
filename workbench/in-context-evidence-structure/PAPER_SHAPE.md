# ICES论文形态：当前判断与历史版本

**2026-10-12当前问题：** 多个来源共享输出空间时，来源特定证据怎样形成并被用于新输入？Source身份进入读取，但所读证据已经由完整历史形成。研究解释这一形成过程、私人关联的功能来源，以及具体标准如何在新输入上产生作用。

**上轮完成（历史范围）：** E115 Llama、E116三家族真实MHS文本、E117三家族双方面机制、E118独立criterion×私人约定、E11914B两块确认均完成。24批576contexts/181632评分，36750项独立数值复算和实际token几何通过。已有C21有界L3、C22/C23有界L2；新C24有界L2只陈述不同缓存接口的功能差异。正式I04/ACTIVE状态不改，未宣布投稿就绪。

**工作标题（可修改）：** *How Shared Outputs Shape Source-Specific Evidence in In-Context Learning*。

**主旨：** Source-conditioned retrieval acts on evidence jointly formed from the contextual history. Shared output identities shape which source's learned associations enter that evidence. A causal formation pathway predicts namespace counterfactuals, while criterion–convention interventions show that transferred associations and full criterion-related functional responses require distinct measurements.

**本轮更新：** E120/E121/E122四checkpoint各16→32全完成。原生操作、功能阳性的自然SST与两来源整体政策已接上三条主文认识；独立raw审计与284主文数值核对完成。C21–23有界L3（两benchmark直接实验与§4/5独立审计）、C24单方面框架有界L2。E123真实SST政策×namespace四checkpoint均完成：shared平均+5.4–9.5点、两Actor均正，同时揭露candidate/full输出功能分离；独立raw封版。见[整篇对齐](PAPER_ALIGNMENT_2026-10-12.md)和[独立主文审计](results/e122/manuscript_claim_audit_2026-10-12.md)。

**持续目标更新：** 现有三认识的证据适配是进展，不自动等于整个研究意义已完成。E124公共身份F/R已独立确认，Qwen有形成特异+4.59pp且候选不变、Mistral负/Llama未定，不能统一解释为身份恢复。当前继续围绕“私人关系要独立、哪些公共信息须共享才能共同使用”检查构造性解释；E125公共Source–输出词关系三模型16→32已完成：形成期特异+26.66/+7.71/+8.30pp，直接query期三项未定；错误对应表也有益，不能以字面表路由解释。私人监督历史形成隔离、joint query仍读两缓存，Qwen候选功能代价与M/L来源非对称保留。E126等价表行次序的完整确认显示共同形成背景联合收益Q/M/L +23.49/+10.40/+5.42pp；own私人函数仍强，full效应主要词空间使用。POST-HOC输出多数符合另一Source约定，不是请求code简单换词；不识别ID。E127共享同词但相反约定、同材料far参照，四checkpoint16→32已冻结执行，用Source特异/共同读数辨认规则选择与偏移。

核心解释与证据：

1. **测量对象：** 区分来源位置访问与关系信息的功能来源。E90/E91确认query禁读B、A raw固定时，B私人规则仍影响A；分开B输出减弱这种历史依赖。
2. **形成过程：** 历史B答案K→A label近似重建输出命名的因果作用；系数1、无head/layer选择，在独立contexts、第二家族/另一任务中验证。C21不是第一次发现label anchor或上下文化，而是解释共享输出如何改变Source特定证据形成。
3. **所传内容：** 固定B输出stream/位置/Source/输入多重集，跨关联配对相对同类置换的超额作用经历史答案V/KV部分传入。Qwen/Mistral/Llama和14B均有直接证据；signed与absolute分开，不冒称完整程序。
4. **正常使用：** 正常query读取全部来源时，形成效应仍保持，且A/B缓存背景非加性。14B形成作用3.059[2.557,3.571]nats、KV label rule预测r .934/.927；signed交互−.686，与三个8B级模型正方向不同，因此解释背景依赖，不预设统一正向电路。
5. **功能分辨率：** E118独立交叉B criterion与私人代码；E119评分前冻结完整响应矩阵det/normalized rotation。14B native两方面匹配选择性均正，rotation .410[.330,.493]；query禁读B仍.190[.073,.310]。local label/答案形成边的响应结构与whole历史不同、重建有残差；保留负det与小正效果。接口差异不自动识别独立隐藏程序，也不将所有标签信息缩成共同gain。
6. **构造性功能检验：** E122选择性答案形成vs整来源形成隔离vsquery-only，两个Actor共用同一prefix。独立平均收益+2.93/+3.42/+7.37/+2.78点，整来源形成隔离均更差；但一致gold有代价，Llama/14B query-only更强，不称通用最佳策略。保留一般访问不等于固定其它激活，比较是政策层面的功能结果。

### 相关工作定位：解释的具体距离

| 最强已有解释 | 其拥有的认识 | 本文实际增加的对象 |
|---|---|---|
| Cho circuit / information removal | 输入信息汇入label、读取与旁路、task-oriented选择/去噪 | 共享输出下Source历史关系怎样进入本来源证据，并影响正常读取 |
| Contextualize-then-Aggregate | 跨示例上下文化必要性及功能交换 | Source位置归属与关系来源的区别，output-dependent形成子图预测 |
| How Few-Shot Examples Add Up | QK/V对FV聚合的作用、上下文化权重变化 | 历史答案→本Source label的形成操作与具体criterion功能内容 |
| LTV / JIT / Mixing Mechanisms | 局部/时序任务表示、多机制绑定与读取 | 不预设一个Source字段完整存储标准；分别验证关联与方面响应 |
| Test, then Route | 显式规则predicate与token-bound routing | 从多Source demos形成的关系证据；显式/隐式差别本身不自动算novelty |
| CoSToM / Lepori / Yu / Crosbie | 信息重建与部署、QK/OV、组件参与与操作的区别 | 冻结native形成干预→反事实预测→具体功能使用的实验链 |

与这些框架相容，并不要求找完全空白问题。若只写上下文化或QK/V，compression risk很高；主文必须呈现Source功能来源、形成预测与criterion关系的实际证据。定位表和全文阅读范围见综合§31/33–35及library论文卡，不隐藏直接近邻。

### 已完成的论文实验覆盖

| 内容 | 记录 | 状态与有效范围 |
|---|---|---|
| 可靠的输出身份现象与真实个人分歧 | E30–E35、E46–E54 | 已有，E50–E52实际准确率后果有限 |
| 来源身份原生参与读取 | E59–E64、E85 | 已有有界因果证据，E85均值预测保留 |
| 位置选择与功能来源分开 | E90/E91 | 独立确认，形成问题入口 |
| 历史形成路径及冻结预测 | E108/E109/E111/E112 | 两家族/3模型任务组合，有独立校对 |
| 固定输出的关联内容 | E111/E113/E114/E115/E119 | 三家族＋更大Qwen，部分而非完整运输 |
| 形成过程进入正常多Source判断 | E114/E115/E119 | 4模型均有背景条件作用，signed方向完整保留 |
| 原生形成操作贡献和受限恢复 | E120 | 四checkpoint新材料，恢复方向依读取环境；不只是donor构造路径 |
| 真实文本中的native形成作用与private功能 | E116/E121 | MHS局部margin/single弱；SST5独立test query/private两方向能力明确，同一冻结预测有效 |
| 两来源共享prefix的整体使用预测 | E122 | 四world×两Actor、4模型16→32全部完成；政策收益、Actor/一致代价与query-only差异保留 |
| 自然文本整体政策与输出namespace | E123 | 真实SST原文、两个私人约定、shared/far×形成/query；四模型全部完成，22,824项独立复核，完整输出损失公开 |
| 联合方面与私人约定的功能测量 | E117/E118/E119 | 完整matrix/bias/FS；14B方向observerprospective，固定方面词序 |
| 私人监督独立时公共关系形成与联合使用 | E124/E125 | 名单有家族差；Source→词集关系形成收益三家族确认，交换表也有益 |
| 信息等价背景的缓存组合 | E126 | 16→32三家族确认，allpair/allActor/private控制；公共背景有联合功能依赖，非独立latent ID证明 |
| 共享输出下的规则选择竞争 | E127 | 四checkpoint16→32全部确认，同词相反约定primary与Source特异响应正；小L/局部方向与部分joint能力保留 |
| 数字/实现可信 | 三轮新raw独立审计 | E115–119共24批，全部条件与种子保留；非独立GPU复跑 |

### 主文的论证与图表链

| 读者的问题 | 主证据 / 图 | 它解释什么 |
|---|---|---|
| 为什么Source位置读取不足以描述规则来源？ | E90/E91与自然两人规则例子 | 当前证据有历史功能依赖 |
| output身份在什么计算过程中起作用？ | [形成预测图](results/figs/fig_evidence_formation.png) | 固定系数1历史答案→label子图重建 |
| 是static label还是learned association？ | [关联图](results/figs/fig_relation_transfer_interfaces.png)，E115/E119 | 输出词固定的关系反事实有额外作用 |
| 它在正常读取时还起作用吗？ | [原生计算图](results/figs/fig_native_evidence_use.png)及四模型表 | 形成与读取缓存条件作用、不同交互方向 |
| 对整体规则使用有什么可预测后果？ | [政策功能图](results/figs/fig_source_function_tradeoffs.png)，E122；E123自然检验封版 | 不同形成/读取政策保留或破坏哪些功能，所有方向与代价共同解释 |
| 这份内容是否规定具体判断标准？ | [三家族完整功能图](results/figs/fig_criterion_code_responses.png)、[14B方向图](results/figs/fig_stronger_model_functional_responses.png) | 关联幅度不等于完整criterion功能，接口响应可分开验证 |
| 哪些结果不能外推？ | E116single、固定词序、E50–52、E99、E110与预测残差 | 真实标准/应用后果/独立抽象程序范围 |

[英文主文](PAPER_DRAFT.md)与[附录](PAPER_APPENDIX.md)已整合E120–122结果，E123也已加入§6.2/附录F，完整政策/输出词表与每Actor结果保留。下一项研究动作由尚未回答的具体科学问题决定，不由剩余误差或卡数决定；不自动追加微观标准，也不因已有理论能容纳现象而撤回实测形成解释。是否正式转candidate由人判断；持续完成用户已授权的整篇科研执行与main同步。

## 论文形态卡 — in-context-evidence-structure — 2026-10-06（agent 草稿，待人审）

- **一句话主旨：** In-context learners index evidence by output. 冻结 LLM 按输出标签存放输入-输出证据：同一输出下的证据按输入相似度加权、在时间与上下文上可交换；因此改变“用哪些输出”的漂移被规范追踪，而把已有输出重新分配给不同输入的漂移（concept drift、因人而异的映射）被混在一起，混合程度随新旧输出标签的语义相似度增加。
- **工作标题：** *In-Context Learners Index Evidence by Output: Why LLMs Detect Output Drift but Miss Concept Drift*
- **论文形态：** C（理论 + 受控）+ B（测量）。
- **manuscript-critical contributions（证据等级见 CLAIMS）：**
  1. 测量：exact 层级 Bayes oracle + 方向相反检验（C01，L2 → 待校对 L3）。
  2. 普遍地图：输出侧变化规范、条件结构可交换；13 模型 0.6B–32B，thinking/指令/时间戳不救（C02、C03、C05，L2）。
  3. 同一答案内的解离与“不重置”（C07，L2）；时间结构只在“偏向新输出”的成分上（C08，L2）。
  4. 按输出存放：分隔阶梯、上下文交互泄漏、语义泄漏定律（C09、C10，L2）。
  5. 建设性修复：换输出词使 concept drift 可追踪（C11，L2）。
  6. 机制：读标签头 + 不可改写的锚点 + 因果修补（C12，L2；L4 需头消融与非 Qwen 复现）。
- **主图：** Fig1 范式与 oracle 的方向相反预测；Fig2 跨任务 × 模型地图（`fig_structure_selectivity.png`）；Fig3 同一答案内的解离（`fig_marked_drift.png`）；Fig4 看最近邻不看最近期（`fig_nearest_not_newest.png`）；Fig5 分隔阶梯 + 语义泄漏定律（`fig_label_similarity_leakage.png`）；Fig6 换词修复（E32）；Fig7 机制（读标签头注意力键 + 因果修补层曲线）。
- **基线：** set / sequence / meta oracle；固定位置核（可加）；样例模型（GCM）；指令；可见 CoT / thinking；边缘-only oracle（E28）。
- **证据标准：** 每格式 200–300 base 配对设计、bootstrap 95% CI；确认版全新种子；机制实验带健全性检查与阳性对照。
- **定位表摘要：** 机制层最近邻 Wang et al. EMNLP'23（标签词锚点）；行为层 Kossen'24、Falck'24、Zhao'21、Xiong'25、Dudley'26 / Qin'26、Cho'25 / Yang-Cho-Inoue'26。增量见 `ideas/I04-output-indexed-evidence.md` §6。
- **风险登记：**
  - 压缩为“ICL = kNN + 标签偏置” → 用方向相反检验、同一答案内分离、语义定律与因果机制回应。
  - 偏置成分的规范符号在弱信号下部分来自注意力竞争（E37）→ “输出侧近似 Bayes”的主张以标签流与格式通道为主证据，E28 只作为分解证据。
  - 机制只在 Qwen 家族 → 恢复推进时先做非 Qwen 复现与头消融。
  - 尚未做独立校对 → 进入 candidate 前必须做。
- **目标会议：** ICML / ICLR（主）；ACL / EMNLP 叙事并行。
- **本次决定（人，2026-10-06）：** I04 为主 idea；暂停推进，留作之后主推的 candidate。


## 论文形态卡 — 2026-10-09 更新（agent 草稿，待人审）
- **一句话主旨（候选）：** In-context evidence is indexed by output, not by source. 把多个来源（标注者 / 用户 / 规范版本）的样例放进同一上下文时，LLM 按输出标签汇集证据：来源标签（名字、时间、领域）分不开证据，只有输出词能分开；因此带 ID 的多人提示丢掉约一半的个人信号，而每个来源用独立的输出词即可恢复。
- **证据链：** 受控现象与语义泄漏定律（E30–E35，13 模型）→ 真实数据后果（E46 / E47 / E49：Measuring Hate Speech、GoEmotions，8 模型 4 家族，同词保留 0.35–0.58，换词恢复 0.80–1.27）→ 机制（E36–E39、E48：读标签头读入他人锚点，换词后读出层面分隔）→ 指令只在部分模型有效（E46b）。
- **社区在用、被检验的推断：** perspectivist / 个性化 ICL 认为模型会按 ID 条件化各人的标注习惯（近邻：arXiv 2605.28802 提示有限且不稳定；ACL'25 2502.20897 微调更好；均未解释原因，也未给出词表修复）。
- **剩余风险：** E50：在主效应、远离决策边界的真实情形下，logit 层面的一半区分损失几乎不影响个人标签准确率（保留 86–98%）→ “有什么用”需改为“何时有代价”（交互型 / 靠近边界），尚缺真实个人标签的交互型数据；机制已在 Qwen3-8B、Qwen2.5-7B、Mistral 复现；独立校对未做；gemma 换词只部分恢复；真实数据只有两个（都是社交媒体文本标注）。
- **目标会议：** ACL / EMNLP（perspectivist 与个性化叙事）为主；ICML / ICLR（ICL 机制叙事）并行。

- **2026-10-09 判定（E50–E52）：** 三个现实情形中，logit 层面的一半区分损失都没有转化为明显的实际预测代价（剩下的区分通常已足够；指令常能补救）。站得住的是机制（读出层面分隔，2 家族 3 模型）、语义泄漏规律、logit 层面的现象；“读者应改变的做法”缺乏有分量的证据。**agent 判断：作为“ICL 证据按输出存放”的机制与规律分析尚可，未达到“合格的强贡献”；是否以此形态投稿由人决定。**

## 2026-10-10 证据校正（保持旧形态卡作历史，不重写论文）
E58–E64未把ICES判为trivial，也未确认其为强机制论文。C14–C16新增L1：来源差分可跨label、native source效应经name-key及query内部消息传递；Qwen与Mistral的label消息时序不同。旧标题保留为候选，不锁定全文。
- source probe可读出不定位自然路由；trained query adapter成功不证明native完整算法存在；E56共20层、1.31M trainable weights。
- “native默认完全不用source”撤回；“entity binding＋ICL不能组合”仍不是成立的中心发现。
- 目前较好的切入点是**source-conditioned computation在query内部怎样形成、后续label检索怎样处理它**；末位直接读取不足以代表全部ICL学习/绑定过程。
- 是否为新认识取决于能否正面对齐Cho shortcut/FV、CBR、Mixing Mechanisms与Test then Route，并预测新query布局、任务与强模型边界。“有更早计算”“QK/V不同”本身不构成novelty。
- real-text控制任务不等于真实个人标注者规则；全文与独立机制校对均未完成。详见`REVIEW_2026-10-10.md`与各卡原始CI。

## 2026-10-10 综合后的形态建议（候选解释，不改正式状态）

**候选主旨：** 来源身份怎样成为ICL的证据选择坐标？在当前来源条件化分类任务中，query内部读取、信息载体的结构角色、载体组可见性与组内来源选择可以拆开研究；提高预测不保证同样恢复来源绑定。详见[`RESEARCH_SYNTHESIS_2026-10-10.md`](RESEARCH_SYNTHESIS_2026-10-10.md)。

- **建议形态：** 有界计算解释＋受控因果测量；先组织已有E59–E71，不追求全部ICL的统一理论。I04为现象起点；原“只有输出能分隔/默认完全不用source”不作当前摘要结论。
- **已有证据：** whole-query与末位中介比较（C15/C16）；关系码×位置独立accuracy交互+10.9点（C17/E71）；公共prefix组偏移恢复52.7%margin/accuracy+5.9点，而source排序仍低于native（C19/E70）。新身份35%恢复与+3.1点accuracy是正的部分迁移，有界但非零；全部新主张仍L1。
- **论文可能改变的认识：** 对source-conditioned ICL，只看末位、只看信息可读性、只看预测修复，都可能误读实际条件计算；将载体访问与关系选择做可区分预测。上述一般区分已有文献，增量须由ICES的具体解释及结果支撑。
- **主图建议：** 原现象与真实数据范围；whole-query因果范围；相同namespace下关系×位置；公共载体偏移的预测/来源选择解离。E74–E79作为诊断/边界材料，不强塞入同一机制故事。
- **下一动作：** 综合现有证据，只围绕载体可见性与组内选择做一个候选区分pilot，不追加函数/词典能力链。本次不重写论文、不运行新实验、不改目标会议或ACTIVE/I04。
- **当前判断：** 有实质进展，值得继续澄清；是否形成强机制贡献尚未确定。局部控制失败不自动抹掉主线，也不因已有投入强保叙事。

### 后续人审计与E81的认识更新

自然问题保留为“多规则上下文怎样选相关证据”。E81独立64context表明：固定码carrier m/pi，改变其它token的whole-query读取，Tag accuracy+13.3[9.4,17.2]点；固定m/kind翻Source pi，使Prefix−11.3[−15.2,−7.8]点。C20 L1，直接Source分配操作比output ranking更接近选择证据，但仍非完整native策略。局部码carrier统计不能充分转移结构角色收益，是值得组织的具体解释边界。

修正旧推断：mass不是越多越好；prediction/ranking分离可能来自Source contrast强度与共同label bias，不能直接当双模块已区分。当前候选认识是**Source cue怎样改变query对相关证据的作用权重，以及cue读取与其它证据读取怎样协调**。一般QK/V、校准或query选择规则已有强近邻；novelty须落在具体因果解释与预测，不能只换术语。先消化这项聚焦结果，不增列新门槛、不改正式状态。

### E82–E85后的形态建议（不重写论文、不改正式状态）

候选认识更具体：**来源字段和输出侧冗余身份线索怎样通过不同读取依赖约束共享标签证据，并与映射内容组合。** E82把布局收益落到Label读取接口；E83不按gold拟合的关系模型有平均作用、逐context预测不足；E84拆开Source字段/code；E85在64新context确认NameK的cue-specific影响，并冻结预测联合干预均值（绝对残差.007–.036nats）。这条链的价值是解释与预测互相约束，不是累计实验数。

可以组织成有界的证据选择机制分析，但还不能称完整算法：身份/码冲突是诊断、TF改变条件语义、hybrid包含上下文化信息、均值乘法不是新原则、两Cue不同依赖不证明两个Source ID。CoSToM、Cho、Mixing Mechanisms、CTA/FV及新适用性论文各自拥有宽泛认识。是否具有足够科学收益，由具体预测和人审判断；不因近邻直接关线，也不要求解释全部ICL才值得保留。

### E86与最新人纠偏

E86仅16-context pilot：alias/class强关联使gap增加14–16nats，冻结外推失败。保存为诊断，未启动确认，不直接提升为论文中心。详细阅读后的候选问题仍是多规则证据选择：Source何时改变输入中被使用的信息，何时改变同一输入表示上的输出映射？自然的不同判断标准与旧相反映射要区分，不能靠重命名证明机制。下一动作先组织这个解释缺口，不再让Tag/prefix/码词控制自行决定问题；C20/I04/正式状态与旧证据保留。见综合§13。

### 最新人审计后的设计重构（无新科学运行）

综合§14指出原候选解释尚不互斥：输出敏感性及评论缓存作用不单独识别输入过滤。更具体的候选变量是Source证据地址与criterion含义；未来可比较名字/位置保持、从示例推断的标准改变时，对多个新输入的功能响应。已有Task-vector/JIT与binding所有权明确，尚不宣布novelty；E85均值预测有效，但范围有限，不要求完整算法或新组件才允许贡献。E87仅候选记录，本轮按最新指令不实施，不改I04/ACTIVE或科学等级。

### E88/E89实际推进后的研究判断

E88 24→32新措辞确认Source-field接口隐式criterion迁移约0、显式+.182nats；E89完整回答核对后仍未形成可靠标准识别/使用分离，初版请求歧义与预算/内容parser问题全部保存。本轮所得是解释约束与有界功能分离，尚非新的完整算法；E85定量反事实价值保留，C16/C20不升级。

候选更自然的问题是来源关系如何约束规则形成中的信息共享：另一人的示例何时必须帮助推断当前人的标准，相关信息在上下文化还是query时进入计算。既有MT-Bayes/CTA/LTV/Binding已占据宽认识，增量要用标准相关状态的反事实预测建立；不把Source隔离默认当正确算法，不继续Source-field/格式优化，不改变正式I04/ACTIVE或目标会议。细节、证据边界与未执行候选见综合§15。

### E90后的认识与取舍

新增实证区分：Source位置选择、rule信息的功能独立、正确输出不同。Source仅可读A的32新contexts中，B改rule仍改变A的17.6%答案；同一query模块在没有B时独立提高27.6点。原signed正方向未确认，功能幅度观测另有独立批验证，不能混称同一确认。

这是值得组织的机制约束，尚不是完整新算法或最终中心贡献。CTA/Atlas/InvICL的宽认识不重命名；下一步优先解释Task特征与各Source输出映射怎样共享/分开，使分标签与来源条件化产生不同预测，不再增加本组mask/层/头细分。维持I04/正式状态与E85价值。

### E91后可组织的具体解释扩展

48新contexts确认：只改B的标签词，在整个query只可读A、A所有raw输入/输出不变时，B-rule幅度仍.683→.193nats；固定A缓存Value只换Key也转移.228nats，Value-only另转移.248。因而输出词不只是最后答案的实现，它还改变来源自己的可读证据；source位置选择与历史监督的来源边界应放在同一计算解释里。A-only accuracy收益CI跨0，仍以正确计算过程为问题，不能另造应用损害。

宽泛上下文化、label vectors、QK/Value区分均已有所有权；具体增量在多规则共享输出下，输出编码怎样改变来源内规则依赖。E48/E85保留，不把整个算法全解释或新组件作为下一道资格门槛。当前仍需让该解释预测新的共享/私有映射情形；结论限定本模型/规则，C16/C20 L1。细节见综合§17与E91，不在这里复制全矩阵。

### E95–E97后的候选机制问题

Source分组推断共同标准与根据私人偏好执行标准已形成完整功能链：thinking标准Goal可靠，自推标准文字可让Own-only完成未见组合；review和答案形式不是当前Goal差别的充分解释。自然问题收束为**从多人示例形成的共同任务信息，怎样与当前人的私人映射组合**。内部运输的成功目标应是recipient偏好×donor标准，不能混为整套donor函数或上一步答案偏置。保留E91历史证据形成结果，下一步固定一个有阳性基础的内部接口，不再扩展格式/层搜索。它仍是待检验的机制切入点，不宣称已经形成顶会完整贡献。

### 2026-10-11：E105/E106与原生续写中的贡献边界

32独立context确认：自己的label KV替换减少历史B-rule作用.429[.250,.632]nats，而评论内容→label中介弱（.0059[−.0251,.0447]）。这在E91之上区分了一个有边界的形成路径；不称所有输入端作用消失，也不泛称第一次发现contextualization。

E105仅部分共享criterion控制，存在EOS，E107正在原生续写；不把完整Owner cue100%当内在程序已独立存在。当前最有意义的解释对象是“Source条件化读取的Task证据如何形成、能共享什么”，已有label-anchor、binding、TaskVector、hybrid memory理论为参照，不能靠命名组件填novelty。核心解释尚未闭环，科学问题与已确认因果事实保留，不因未找到完美接口停止研究。

E107完整480＋4校对后，私有KV参与得到固定teacher tensor因果支持，但共同标准控制仍弱；不用新增层/Goal追阳性。形成路径E106是本轮更可靠的知识增量。候选解释回到学习到的label含义/检索坐标如何改变Source条件化的证据，尚未宣布novelty成立。


**2026-10-12本轮执行封版：** E120–123核心原生操作/自然关联/双来源功能预测与复现、主文/附录完整条件、近邻定位已交付；[最终独立主文审阅](results/e123/manuscript_claim_audit_2026-10-12.md)核新增304个数值，未发现当前三认识必须补做新决定性实验。不得由此叫完整ICL唯一路径或自动改投稿状态；也不再将未解微观残差当已有结论的新资格标准。正式candidate/目标venue属于人审判断。

**E127整篇更新：** 主文§6.5将等价形成背景与同输出映射使用合并为同一机制问题；四模型primary +8.89/+5.86/+.78/+9.38pp、35528独立数值复算。已有3项认识继续由原生操作/固定关系/功能政策/公共协调串联。E128目前0评分，唯一后继为不同food/service标准、同private code，区别只label remapping与输入标准功能。
