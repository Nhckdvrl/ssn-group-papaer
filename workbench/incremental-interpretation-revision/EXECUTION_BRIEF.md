# 执行与探究说明（给本地 agent，2026-10-06）

> 人已决定（2026-10-06）：采用 [ROUTE](ROUTE.md) 中的路线，恢复本 workbench 的研究；先广后深；允许一开始就做白盒；标注只用 Step5（step-5-preview）；资源是同一节点上的 8 张 H20，不用任何付费商业 API。
> 本文是**研究说明书，不是逐条脚本**。你的任务是自己建立对领域的整体认知，然后通过高信息量、精确的实验反复"实验 → 分析 → 修正假说 → 再实验"，直到形成一个真正好的 idea。§2 的第一块地图是起点，之后怎么走由证据决定，但必须遵守 §6 的护栏。
> 仓库规则照常适用（`AGENTS.md`）：R3 先写实验卡再跑、R5 不筛结果、R9 文档从简、R11 不排日程。

## 0. 目标与"好 idea"的标准

**核心问题：** 强 LLM 能看到整句话，为什么仍然读错 garden-path（GP）句？把错误定位到具体原因，再用机制解释模型的"修订"在哪里成功、在哪里失败。

**达到以下标准，才算"真正好的 idea"，可以请人审是否进入候选：**
1. 一个普通审稿人听得懂的 RQ，对应一个清楚、不显然的 finding（Sasano 标准：证明出来以后值得兴奋，而不是"当然如此"）。
2. finding 在至少 3 个模型族、至少 2 个构式上成立；在真实错误条目上用可解释的读数（正确率、正确解读的概率）测得，CI 能分开竞争解释。
3. 有机制证据：至少一种因果干预（修补 / oracle / 注意力切断）支持该解释。
4. 相对 §1 列出的最近邻，能用一句话说清增量。

## 1. 先建立整体认知（开跑之前必须完成）

1. **先读仓库：** [DIAGNOSIS](DIAGNOSIS_AND_REDIRECTION_2026-10-06.md)（51 个实验为什么失败）、[ROUTE](ROUTE.md)（领域全景、三方矛盾、为什么选这条路线）、[PROGRESS_SUMMARY](PROGRESS_SUMMARY_2026-10-06.md)（做过什么、哪些仪器坑）。
2. **再读论文全文**（arXiv、ACL Anthology、OpenReview 现在都能访问）。每篇要读出：背景与压力、idea 从哪里来、怎样与近邻拉开距离、数据规模与构造方式、作者留下的开放问题。**不要只读方法和结果。**

| 脉络 | 必读 | 重点关注 |
|---|---|---|
| 人机理解比较 | Amouyal ACL'25（2502.09307）、Amouyal ACL'26（2510.07141）、Li CogSci'24（2405.16042）、Cao & Schuler CMCL'25 | 问句"不一定"的问题；Amouyal'26 的猜想与留白；thinking 对 GP 的效果 |
| surprisal 与人类 | Huang JML'24（SAP）、Timkey/Dillon/Linzen 2026（2605.15440）、Paape/Linzen/Vasishth 2026（2602.04489） | 为什么"LLM 不怎么被 garden-path"，以及独立重分析成本的论证（这条线我们不进入，只借它的结论） |
| 修订机制 | Hanna & Mueller NAACL'25（2412.05353）、Zeng Findings'26（ACL 2026.findings-acl.57）、Tang ICML'26（2605.30233）、Prakash ICLR'26（2505.14685）、Guo et al. 2026 CICM（2609.38866）、Oh & Demberg 2026（2606.08644） | 推迟计算、查询时汇总、"保留但未选中"、非因果 oracle 的做法 |
| 架构与第二遍阅读 | CASTLE（2509.07301）、Prompt Repetition（2512.14982）、Echo Embeddings（2402.15449）、Madureira ACL'24（2402.13113）、Ettin（2507.11412）、Thoughtology §9（2504.07128） | "因果掩码有害"这个前提；重复输入的效果与控制 |

3. **读完后在当天日志里写一页"我的理解"：** 用自己的话说清三方矛盾（理解问答、surprisal、架构）、四种竞争解释（§2.1）、每种解释各自由哪些已有证据支持、哪些反对。读论文的笔记合并进 `library/themes/incremental-language-processing/FIELD_MAP.md`，**不要新建几十张卡**。

## 2. 第一块：广面地图（起点设计；先在全模型面板上铺开，再深挖）

### 2.1 四种竞争解释及其预测

| 解释 | 读两遍 | 先给截断片段再给全句 | 非因果 oracle | 合理性操纵 | 换问句形式 / 复述 |
|---|---|---|---|---|---|
| E4 增量编码过时（因果掩码） | 修好 | 修不好 | 修好 | 弱 | 弱 |
| E1 作答时选择失败（保留但未选中） | 部分修好 | 修不好 | 部分修好 | 中 | 明显 |
| E2 合理性组装（good-enough） | 修不好 | 修不好 | 修不好 | 强 | 复述也错 |
| E3 测量 / 问句语义 | — | — | — | — | 差距消失 |

这四种解释不一定互斥，也可能因构式而不同。人最初提出的三分法（覆盖 / 共存 / 晚补偿）在因果模型里分别对应：读后段位置、读旧位置（E1）、查询时才汇总。

### 2.2 E52 地图（先写实验卡）

- **条目：** 以 §4 定义的真实错误条目为主，"不一定"条目单独报告。不需要修订的难结构（双中心嵌套、depth charge、相似性干扰）作为对照。
- **阅读条件**（同一模型、同一文本，只改变可见范围）：
  - R0 读一遍；
  - R1 读两遍（句子连续出现两次）；
  - R2 先给截断在消歧词之前的片段，再给全句（同样是重复，但看不到后文）；
  - R3 先给一句等长的无关填充句，再给全句（控制长度和额外计算）；
  - R4 早给线索（数据集自带的逗号 / that / 非缩减版本，或换序对照）；
  - R5 问题先行（问题在句子前后各出现一次）；
  - R6 thinking 开（Qwen3 用 `enable_thinking`，解析最终答案）。
- **提示格式：** 两种格式都跑，互相印证。
  - A：Amouyal 的少样本前缀（`prefixes/*.json`，8 种系统提示 × 顺序），便于和他们公开的结果直接对比；
  - B：原生 chat 零样本。
  - SAP 用两选项 wh 问句，两种选项顺序都跑，可以避开 Yes 倾向。
- **读数：**
  - 强制选择下正确选项的归一化概率，以及正确率；
  - simple_question 和填充题，用来估计 Yes 倾向；
  - 同一模型在原句消歧词上的 surprisal（GP 对线索版本），用来逐题检验"察觉了冲突却没有修正"。
- **复述（E53，可与 E52 并行）：** 采用 Amouyal 2025 的"拆成两句"提示，greedy 生成；先用自动指标判（歧义名词是否与第一个动词出现在同一句），再由 Step5 判定复述体现的是 GP 误读、正确解读还是其他。
- **模型面板**（HF ID 已核实存在）：
  - 核心：`Qwen/Qwen3-{1.7B,4B,8B,14B,32B}`、`google/gemma-3-{4b,12b,27b}-it`、`meta-llama/Llama-3.1-8B-Instruct`、`mistralai/Mistral-Small-24B-Instruct-2501`、`allenai/OLMo-2-1124-13B`（及其 Instruct 版，以 HF 上实际存在的为准）；
  - base 与 instruct 对照：`Qwen/Qwen3-*-Base`、`google/gemma-3-*-pt`；
  - 可选：`meta-llama/Llama-3.3-70B-Instruct`（同节点 TP=2 或 FP8 单卡）、OLMo-2 中间 checkpoint；
  - 架构受控对照（见 §5）：`jhu-clsp/ettin-{encoder,decoder}-{17m…1b}`；
  - GPT-5、o3 等前沿模型**只复用** Amouyal 公开的逐提示结果（`results/llm_results/`），不调用 API。
- **阳性对照与仪器校验（吸取 E00 的教训）：**
  - 对与 Amouyal 重合的模型（Qwen3、Gemma-3），先在格式 A 下复现他们公开的逐题结果，在噪声范围内一致之后，才解释新条件；
  - 线索版本 / 对照句和 simple_question 的正确率要高，否则这个模型只作描述，不进入归因。
- **统计：**
  - 按 pair_id 做 cluster bootstrap（10,000 次，95% CI）；
  - 主效应：真实错误条目上的 GP 差距 gap = 对照正确率 − GP 正确率；
  - 关键对比：R1 相对 R0 的差距缩小量，与 R2、R3 的缩小量比较；
  - 另报混合效应逻辑回归（正确 ~ 条件 × 阅读条件 × 构式 + (1|pair) + (1|model)），并按模型、构式分别报告；
  - 噪声地板：8 种提示之间的波动范围。
- **倾向性决策表**（启发式，不是自动判决，结果出来先请人审）：

| 结果 | 倾向 | 下一步 |
|---|---|---|
| 多数强模型中 R1 明显缩小真实差距，R2、R3 不能 | 倾向 E4 | 用 E54 oracle 和 E55 修补定位过时的位置 |
| R1、R2、R3 都不缩小差距，且差距随合理性变化 | 倾向 E2 | 用 E55 探针看正确解析是否在任何位置可读：可读则转向 E1，不可读则是 E2 |
| 换问句形式或复述后差距消失 | 倾向 E3 | 先修正测量，重算领域结论 |
| 因构式或模型而异 | 归因地图本身就是贡献 | 按构式分别做机制 |

- **算力（估算，请实测）：** 打分都是短序列，每个模型大约几十分钟，按模型、条件分片到 8 张卡；复述生成用 vLLM。32B 及以下 BF16 单卡可跑；BF16 与 FP32 的翻转率先在小模型子集上核对（E03 曾测得 0.61%）。

## 3. 之后怎样灵活追问（菜单，不是必做清单）

每一步都要先回答：哪个结果会改变下一步？它区分的是哪两种解释？

| 编号 | 实验 | 区分什么 |
|---|---|---|
| E54 | 非因果 oracle：只放开歧义区 token 的因果掩码，让它们看到全句但看不到问句；对照是放开等量的非歧义 token | E4 对 E1/E2 |
| E55 | 每层探针（歧义名词的角色：V1 的宾语 vs V2 的主语，用同序线索句训练）；位置级修补（把歧义区 / 消歧词 / 句末 / 问句位置替换为同序线索版本的表征）；切断作答位置的注意力 | E1（保留但未选中）对 E2（从未构建）对 E4 |
| E56 | Ettin 编码器 vs 解码器（同数据同配方），用评分或探针读数 | 架构是否是原因 |
| E57 | 模板扩展同序最小对：每构式 300–1000 条，结构由程序保证，Step5 审自然度与合理性 | 机制分析需要的样本量 |
| E58 | 合理性操纵（Amouyal 的不合理变体、SAP 常模作为协变量） | E2 |
| E59 | 问句形式：yes/no、wh、复述、蕴含判断 | E3 |
| E60 | thinking 文本分析：推理链是否复述了误读，在哪一步改正或没有改正 | 推理是否就是"第二遍阅读" |
| E61 | 逐题对应：同一模型在消歧词上的 surprisal 与它的答案 | 察觉了却不修正 |
| E62（第二阶段，人审后） | 推广到词汇（Zeng P-M 数据，github jjtail/dsd）、指代（WSC273 / WinoGrande）、自然 NP/S（UD EWT + GUM） | "词义能改，谁对谁做了什么改不动"是否成立 |

## 4. 数据与标注（Step5）

### 4.1 来源与配对

| 来源 | 位置与版本 | 配对与字段 |
|---|---|---|
| Amouyal'25/'26 | `github.com/samsam3232/comparing_humans_llms_processing_difficulties` @ `072efefa01cb9716c2d14752eb1d4bf9830b0b81` | Subj/Obj：`extended_gardenpath_experiments.csv`，同一 `set_id`（如 `set_10`）下有 GP / nonGP × prob / reflexive，问句分 `GP_question`（初始解读命题）和 `simple_question`。NP/S、RR、NP/VP：`*_human_base_data.csv`，按 `set_id` 前缀分组（`s1_1…s1_4` = GP 的 gp 问、GP 的 simple 问、nonGP 的 gp 问、nonGP 的 simple 问），附 `gp_noun / gp_verb / reduced_verb`。人类逐题数据：`results/human_results/humans.csv`。31 个模型结果：`results/llm_results/*.csv`（`compute_type`：regular / cot / thinking） |
| SAP | `caplabnyu/sapbenchmark` @ `15e61066…`（已有审计） | `Items for all subsets.xlsx` 的 `NPSNPZMVRR` 表：`condition`、`disambPositionAmb/Unamb`（消歧词位置）、歧义句与无歧义句、两选项 wh 问句、`Answer`、`Ambiguity targeted?`；SI 目录下有合理性、cloze、动词偏好常模 |
| Čeháková'25 | 本地已缓存并审计（`results/D0-Cehakova2025-source-audit.json`，映射 0=Yes、1=No） | 24 NPZ + 24 MVRR × 8 条件，两个区域的正误问句 |
| Jurayj components | 本地已缓存（注意 P05 的拼写和配价问题） | 只在审计后用作同序控制 |

**统一 schema**（在 `scripts/data.py` 已有 schema 的基础上扩展）：`item_id, source, construction, pair_id, condition (gp/control), control_type, sentence, question, question_format (yn/2opt), options, gold, question_target (initial/final/other), disamb_word_index, amb_span, step5_*, genuine`。

**真实错误条目的定义：** GP 定向问句所问的命题，在最终解析下被 Step5 判为"矛盾"（而且对照句同理）。判为"不一定"的条目单独分析，这本身就是一项测量结果（参见 `results/D0-Amouyal-released-item-type-audit.json`）。

**规模：** 行为部分约 300 组以上（领域常规是每构式 24–100 组）；机制部分用 E57 扩到每构式 300–1000 条（对齐 Zeng 的 4,090 对、Tang 每种行为 300 条）。

### 4.2 Step5 标注协议（唯一标注者；便宜，所以每项做两遍）

- **端点：** Step Plan Messages（见 DATA_PLAN），模型 `step-5-preview`，key 只放本地私有配置，总并发 ≤8，不走代理。
- **任务：**
  - T1：命题在最终解析下的状态（蕴含 / 矛盾 / 不一定），附置信度；
  - T2：消歧词索引与歧义区跨度（由程序核对该词确实在句中）；
  - T3：语法与自然度；
  - T4：复述判定（GP 误读 / 正确解读 / 其他）；
  - T5：模板扩展条目审计。
- **批大小 ≤5 项/请求。** E51 每批 24 项，192 批里只有 39 批完整，这是 P12 的教训。输出用严格 JSON，回显 `item_id` 和输入的 sha256；`max_tokens` 给足。
- **校验与重试：** 检查 schema、覆盖率、哈希；失败项单独重试，最多 2 次；失败永远不算通过；保存所有请求和响应。
- **每项两遍：** T1 和 T4 各做两遍独立标注（打乱顺序、分不同批）；不一致的项做第三遍（要求写出推理）后裁决；报告一致率。
- **T1 提示骨架：**

```
You will see a sentence and a yes/no question about it.
Consider ONLY the globally correct (final) grammatical parse of the sentence.
Label the proposition asked by the question as one of:
ENTAILED / CONTRADICTED / NEITHER (compatible but not stated).
Return JSON: {"item_id":..., "sentence_sha256":..., "label":..., "confidence":0-1, "note":"<=20 words"}
```

## 5. 资源与工程

- **硬件：** 8 张 H20（96GB）在同一节点。每个模型、每个条件做成独立单卡分片；70B 用 TP=2 或 FP8。
- **软件：** 打分、修补、探针用 transformers（修补和 oracle 需要 eager attention 和自定义 4D mask）；生成用 vLLM；复用已有 venv。下载照旧不走代理，逐文件核对哈希。
- **复现记录：** 固定模型 revision 和 seed，greedy；记录 GPU 时、配置、哈希。原始数据放 `/data1/xiangding/work/incremental-interpretation-revision/`；git 只放代码、实验卡和小型汇总。
- **Ettin 的读数：** 这些模型只有 ≤1B，不适合用问答；改用两个改写句的（伪）对数似然比较，或用角色探针。

## 6. 护栏（防止重复 51 个实验的失败）

1. **漂移检查：** 每张实验卡都要写明它与"先前解释的修订"有什么关系（第一阶段指 GP 类结构）。如果一个问题不提这一点也能说清楚，说明已经漂移，要停下来请人审。
2. **广度：** 任何主张都需要至少 3 个模型族、至少 2 个构式；禁止单模型连锁实验；Qwen3-8B 不能作为唯一模型。
3. **局部追问上限：** 对同一个局部异常，连续追问不超过 2 次，之后必须更新假说表，并在日志里回答"如果为真，审稿人会关心吗"。
4. **数据：** 以已发表条目为主；构造只用程序可验证的模板，再加 Step5 审计；禁止再在旧的 24 句模板上做扰动。
5. **读数：** 主读数用正确率或正确解读的概率；bits 的差中差只作次要读数。
6. **预注册：** 先写实验卡（`python3 tools/process/new.py experiment incremental-interpretation-revision <slug>`），允许根据结果灵活设计下一步，但 POST-HOC 分析要如实标注。
7. **请人审的时点：**
   - D0-v2 标注完成（真实条目集合与测量发现）；
   - E52 地图完成；
   - 第一批机制结果出来；
   - 任何假说准备升为主线叙事时；
   - 连续 3 个实验假说表都没有变化时。
   **不要自己写"无需人决定"。**
8. **每块结束时在日志写：** 当前最好的故事（3 句话）、什么结果会推翻它、下一步最高信息量的实验。

## 7. 已知的坑

- 提问顺序可以造成 ±60pp 的交互（E03/E07）。标签映射和 Yes 倾向会主导小模型（E05、Hanna 的结论）。1.7B 级模型在对照上就接近地板（E04）。
- Qwen3-8B 在反身 Subj/Obj 上几乎没有 GP 差距，在 RR 上有。不要据单一模型下结论。
- 词首空格会影响词概率的计算（2406.10851），算 surprisal 时要用正确的词边界方法。
- 已发表数据也有错误：tomato/tomatoes、road/floor、had rode、burglers（P05）。先审再用。
- 不要把条件字符串的概率当成世界信念，也不要把问答读数和预测读数当成同一个量（Hu & Levy 2023，见 FIELD_MAP）。

## 8. 汇报

每次会话按 `AGENTS.md` §4 写日志：做了什么（实验卡 ID）→ 数字与 CI → 哪条主张升级或降级 → 下一步 → 需要人决定什么。主张登记在 [CLAIMS](CLAIMS.md) 的 C06–C09；idea 记在 [I02](ideas/I02-garden-path-misreading-attribution.md)。
