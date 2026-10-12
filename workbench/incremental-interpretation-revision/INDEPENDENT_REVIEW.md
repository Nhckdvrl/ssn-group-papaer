# 独立科学审查与方向决定：Incremental Interpretation & Revision

审查日期：2026-10-12。审查者：Claude Fable 5.1（独立于前两轮执行agent与10月12日审计agent）。本轮只做分析：读取全部实验卡、登记文件、知识库与外置原始资产，做CPU复算；没有任何新实验、模型推理、标注API、模型下载或旧流水线启动；没有覆盖任何原始结果；没有改动正式登记状态。

---

## 0. 判断（先说结论）

**这个workbench值得继续，但必须重构：研究对象要从“评分/credit/目标问答”收回到一个已经在我们数据里成立、有人类锚点、而且近邻没有占住的现象上。**

**我们实际得到了什么。** 两轮103张卡之后，真正站得住、且重要的只有一件事，而且它已经在E82–E90的原始输出里，只是被前任当作“17条反身关系”的局部细节跳过了：

> 在公开的人类garden-path材料上，2026年最强的开放模型读完整句后，能够**拒绝误读命题**（“Did the staff appoint someone?”→No），却几乎**不能断言替代依赖**（“Did someone send the file to the suspect?”、“Did the protester hide himself?”→Yes），而同一模型在无歧义对照句上能断言它。给出显式句法框架提示后，Gemma能补出替代依赖，Qwen完全不能。

用E87原始输出（POST-HOC，本人重算，strict源支持规则，GP句，按Gold分层）：

| 族 | MVRR 替代依赖（Gold Yes，16题×2映射） GP / 对照 | NPZ 反身替代依赖（17题×2） GP / 对照 | MVRR 误读命题（Gold No，41题×2）GP |
|---|---|---|---|
| Qwen3.8-27B | 0.0% / 81.2% | 0.0% / 41.2% | 81.7% |
| Gemma4-31B-it | 12.5% / 90.6%（下界，含未解析） | 0.0% / 70.6% | 58.5%（下界） |
| Ministral3-14B | 6.2% / 31.2% | 0.0% / 8.8% | 93.9% |

E89（同一批题，显式框架提示“the verb *sent* is a passive past participle in a relative clause”）：MVRR替代依赖 Gemma EARLY 26/32、LATE 23/32；Qwen EARLY 0/32、LATE 1/32；Ministral 0/32。NPZ反身：Gemma 0→100%/73.5%，Qwen/Min 仍0。E90把同样信息只经源句隐状态传递：Gemma NPZ 0→5.9%。

人类锚点：Ceháková & Chromý 2025（同一批英文材料）报告GP条件下替代依赖问句（AMBCOR）约50%、后半句正确关系（DISCOR）约90%。模型是0–12%对90%以上。

**这是什么。** 心理语言学里“partial reanalysis / good-enough”争论的核心（Slattery 2013：新结构已建成、旧义残留；Huang & Ferreira 2021、Ceháková 2023/2025：替代结构根本没建成）在LLM上有一个干净、可测、跨族的版本：**撤回不等于重建**。更强的部分是E89：对Qwen而言，显式告诉它正确的句法框架也不能让它把框架变成命题。这把“模型知道结构但不用”（Hanna & Mueller 2025的probe/QA分离）推进为“模型被告知结构也不构建依赖”，是一个可以追因果的具体对象。

**为什么值得兴奋。** 它改变Amouyal 2025/2026对“GP对LLM特别难”的猜想（要从记忆里丢弃错误解释）：瓶颈不在丢弃，而在重建；它解释为什么thinking对GP帮助最小（Amouyal 2026）；它给出一个可验证的预测：凡是要求断言替代依赖的题都难，凡是只要求拒绝误读的题随指令就能好；它给方法留一个具体入口（论元框架重实例化），而不是“再读一遍”。

**我们没有得到什么。** (1) 没有一个可以写成论文的机制解释：为什么Gemma能用框架提示而Qwen不能；源状态patch（E55/E64）改变的是误读题而不是替代依赖题。(2) I07（自监督重建credit继承误读）与I08（目标问句提高任务分却损伤解释）都不构成合格idea：I07所依赖的候选池里多数源根本没有正确候选（E107：Qwen 400个候选中260个是初始误读、110个明确正确，但按源看多数源8/8全错），而且NPS的“误读”标签被两句复述格式污染；I08在当前三族只在Qwen成立。(3) 前任把Ministral在strict规则下“initial 84.55%正确”当作撤回证据，这是No偏置伪影（见§4.3），E82–E90、E96–E107里所有含Ministral的三族叙事都要重读。

**方向决定。** 重构为一条主线：**替代依赖的建立（reconstruction）为何在撤回（retraction）之后失败，什么信息能让它成立。** 自然对象是公开的Ceháková 2025 / Christianson 2001 / SAP材料中带替代依赖问句的GP句，读数是实际作答与自由复述，操作是显式框架信息、控制句状态移植、以及“知道结构/用结构”的分离测量。I07、I08建议PARKED（由人决定），E108不执行。详见§8–§9。

---

## 1. 审查范围：什么是全量核验，什么是抽查

| 对象 | 覆盖方式 | 范围 |
|---|---|---|
| 103张实验卡 | 全部卡经EXPLORATION_RECORD、CLAIMS作废记录、PAIN_LOG逐卡对照；**逐字通读**的卡：E52、E55、E59、E64（设置部分）、E67、E82、E85、E87、E89、E90、E93、E96、E98、E99、E101、E102、E103、E107（18张）；其余85张按记录表与主张账本核对结论边界，未逐字读 | 全量对照 + 18张深读 |
| 登记/综合文件 | README、AGENTS、ROUTE、EXECUTION_BRIEF、AUDIT_2026-10-12、CLAIMS、PAIN_LOG、EXPLORATION_RECORD、EXPLORATION_SUMMARY、REASSESSMENT_2026-10-07_2355、ideas I02–I08、logs/2026-10-12、knowledge/RESEARCH_SYNTHESIS、00_STATE_OF_THE_FIELD、PRIMARY_SOURCE_REVIEW、topics/05、lee2026/amouyal-2026卡 | 全文 |
| 原始数据（外置 `/data1/xiangding/work/incremental-interpretation-revision/`） | E82/data-v1.jsonl（892QA全量结构核对）；E87 全部18192条实际输出按Gold/构式/目标重算；E89 全部9408条中MVRR替代依赖子集重算；E93 全部10464条前向有效性计数；E107 packets/assignments/complete-map-v2/step5 annotated 全量结构核对、类别分布重算、9个源×8候选逐条手读；E52 D0最终资格摘要、native-fp32图三族NEITHER gap读取 | 程序全量 + 手读抽样 |
| 代码 | E82 `current_open_baseline.py` 提示词；E107分析代码仅读文件结构，未逐行审 | 抽查 |
| 文献 | 本地知识库卡 + 本轮10次web检索（Amouyal 2025/2026、Hanna & Mueller 2025、Lee & Shin 2026、Ceháková 2025、Paape 2026、Zhou/Stanojević/Hale 2026、Emura & Sugawara ACL 2026、Prakash ICLR 2026、CASTLE、ABBEL及其2026后继） | 摘要/主文级核对，非全文重读 |

未做：E00–E51的原始概率CSV未复算；E55/E64 patch地图未复算；E96/E101–E106的LP分解未复算；E53的6244条标注未抽读；E107条件对的逐源符号一致性因文件只存面板未能复算。

---

## 2. 核心证据链（影响方向的结果，附路径）

### 2.1 数据的真实含义：原No多数是“未断言”，替代依赖题才是修订测验

`results/D0-final-qualified-summary.json`（1732题，1284题进入标注，Step-5两遍一致率.892 [.872,.911]，237簇）：Gold No的644题中，字面CONTRADICTED只有9题，NEITHER 616题；两侧都矛盾的“genuine pair”全库只有NPS 2对。原Amouyal式问句（“Did the man hunt the deer?”）要求的No是“文本不蕴含”，不是“文本否定”。这一点Christianson 2001 pp.371–372本来就承认（见knowledge/christianson2001卡）。

同一资格表里**存在**真正的修订测验：`grounded_gold = Yes` 的initial题。E82 cohort（892QA/356源）中：NPZ 17题（Ceháková 2025反身/互指，“Did the protester hide himself?”）、MVRR 16题（Ceháková 2025双宾语被动，“Did someone send the file to the suspect?”；SAP 1题）。这33题是全部实验里唯一直接问“替代依赖建立了没有”的题。它们在E82卡里只被写成一句“17个反身/互指初始关系三族几乎全错”。

### 2.2 当前模型实际作答（E87原始输出，本人重算）

路径：`E87/runs-v1/<model>/<shard>/predictions.jsonl`，字段 `known_correct`（v1字面解析；Gemma的A/B输出在v1记UNKNOWN，v2事后按选项语义解析全部明确，故Gemma行是下界）。strict规则原文（`E82/runs-v1/Qwen3.8-27B/0/current_open_baseline.py:15`）：

```
Answer Yes only if the sentence explicitly entails a yes answer to the question.
Answer No if that answer is unasserted or contradicted. A plausible or merely
compatible extra event is insufficient for Yes.
```

| 族 | 构式/目标/Gold | GP正确% (n) | 对照正确% (n) |
|---|---|---|---|
| Qwen | MVRR initial Yes | 0.0 (32) | 81.2 (32) |
| Qwen | MVRR initial No | 81.7 (82) | 100 (82) |
| Qwen | NPZ initial Yes | 0.0 (34) | 41.2 (34) |
| Qwen | NPZ initial No | 42.9 (184) | 90.2 (184) |
| Qwen | NPZ final Yes | 57.4 (176) | — |
| Gemma | MVRR initial Yes | 12.5 (32, 18未解析) | 90.6 (32) |
| Gemma | MVRR initial No | 58.5 (82, 28未解析) | 64.6 (82, 29未解析) |
| Gemma | NPZ initial Yes | 0.0 (34) | 70.6 (34) |
| Gemma | NPZ initial No | 69.0 (184, 11未解析) | 52.2 (184, 73未解析) |
| Ministral | MVRR initial Yes | 6.2 (32) | 31.2 (32) |
| Ministral | MVRR initial No | 93.9 (82) | 98.8 (82) |
| Ministral | NPZ initial Yes | 0.0 (34) | 8.8 (34) |
| Ministral | NPZ initial No | 91.8 (184) | 96.2 (184) |
| Ministral | NPZ final Yes | 13.6 (176) | — |

读法：
- **Qwen/Gemma在MVRR上是干净的GP特异替代依赖失败**：对照句“The suspect who was sent the file…”下81–91%能答Yes，GP句下0–12.5%。误读命题（Gold No）GP下58–82%能拒绝。
- **NPZ反身题对Qwen/Ministral部分是词义问题而非GP问题**：对照“While the protester hid, …”下Qwen只有41%、Ministral 8.8%承认“hide himself”。只有Gemma（70.6%）把它当GP特异现象是干净的。
- **Ministral在strict规则下是No机器**：主句事实“Did the memo near completion?”（Gold Yes，176任务）strict下只24个Yes、RECOVER下15个Yes、PLAIN下100个Yes。E82卡报告的“Ministral initial 84.55%正确、final 28.09%”不是“撤回了旧关系但没建立新关系”，而是规则措辞诱发的否定偏置。E82–E90、E95–E107中Ministral的strict/RECOVER读数不能作能力证据（E89/E90/E98对Min的“0恢复”“无收益”同样受此污染）。

### 2.3 显式框架信息的作用（E89/E90，本人重算MVRR子集）

路径：`E89/data-v1.jsonl` 字段 `frame_hint`；`E89/runs-v1/*/predictions.jsonl`。MVRR替代依赖16题×2映射：

| 族 | EARLY（S前） Yes/32 | LATE（S后） Yes/32 |
|---|---|---|
| Qwen | 0 | 1 |
| Gemma | 26 | 23 |
| Ministral | 0 | 0 |

同卡NPZ反身17组：Gemma 0→100%/73.5%，Qwen/Min 0。E90只经源bank传递：Gemma NPZ 0→5.9% [0,17.6]，MVRR final Yes +29.2 [12.5,45.9]pp。

读法：Gemma能把“这个动词是被动分词/不及物”编译成替代命题；Qwen被明确告知结构仍不断言该命题，而它在对照句上能断言。这是“知道结构”与“建立依赖”之间可操作的分离，比Hanna & Mueller的“特征可读但QA不复用”更直接，因为这里结构是外给的、明确的。E89是oracle提示，不是native机制证据；但它把问题钉在了“框架→命题的实例化”这一步。

### 2.4 因果入口（E55/E64，卡片数字，未复算）

旧三族（Qwen3-8B/Gemma3-12B/Llama3.1-8B）。E55：前1/4层歧义区整残差替换（cue→GP）对MVRR initial/words/same-gold的GP收益Q/G/L 48.33 [25,71.67] / 36.67 [16.67,56.67] / 26.11 [10,45] pp，反向损伤−54.44/−33.89/−25.56，15簇。E64：TARGET_BANK−CONTEXT_BANK MVRR initial Q43.33 [20,66.67] / G19.44 [0,38.89] / L18.33 [5,35]，15簇；角色表达共同恢复弱。这些“initial”题以Gold No为主（E64资格MVRR19源），所以它证明的是**误读命题的拒绝**可以被歧义词状态因果改变，没有证明替代依赖可以被改变。这是前任没有分开的两件事。

### 2.5 目标问句（E67/E99旧三族forced-choice；E98当前三族actual）

E99：同源“QA正确且自由复述明确误读”联合增加Q17.23 [11.58,22.88] / G12.43 [7.34,17.80] / L29.94 [23.73,36.16] pp（`results`外置map 6f29db1…）。E98当前三族1800实际输出：GP QA收益Q+2.08 [−4.17,8.33] / G+3.13 [−4.17,10.42] / Min 0；联合损伤只有Q +20.83 [10.42,33.33]。结论：旧协议下的现象真实，但当前模型不普遍；且Ministral行受§2.2偏置影响。I08不是合格idea。

### 2.6 重建credit链（E91–E107）

E96三族fidelity alignment +.444/+.500/+.500（固定P换GP→cue目标）；E101 prefix三族负、suffix Q/Min正；E102 T2后缀oracle全50源选择收益Q+10.42 / G+8.33(CI含0) / Min+21.88 pp；E103同原源8候选池suffix−whole原角色Q+2.08 / G+6.25 / Min+8.33（仅Min CI正）；E107关键依赖维度：Q+6.25 [−2.08,16.67] / G 0 / Min+4.17 [−4.17,12.5]。

本人核对E107原始包（`E107/critical-dependency-commitment-map-v2.json` records，`packets-v1.jsonl`，9个源×8候选手读）：
- 候选类别分布（ALL/50源/400候选）：Qwen INITIAL 260、EXPLICIT 110、UNBOUND 24、IMPLICIT 6；Gemma INITIAL 189、EXPLICIT 127、IMPLICIT 22、UNBOUND 62；Ministral INITIAL 218、EXPLICIT 104、UNBOUND 62。
- 手读的9个源中7个源三族8/8候选全是同一误读（如“The professor awarded the grant gained more attention…”→“1. The professor awarded the grant. 2. The grant gained more attention…”）。**候选池里根本没有正确解释**时，评分器选不选都无意义；I07的“credit抵消修订证据”只能在14/50（Q）、13/50（Min）有可比候选的源上定义。
- NPS的“INITIAL_MISREADING”标签被格式污染：“The chef remembered the recipe required two hours of cooking.”→“1. The chef remembered the recipe. 2. The recipe required two hours of cooking.”被标INITIAL。Amouyal式“改写成两个短句”指令本身就要求拆掉that补语；这种输出是指令的自然结果，不是误读证据。NPS占50源中的25个。
- E93（25.7 GPU·h）前向DIRECT三族1744/1744全部cap（64 token上限下模型开始写推理）；COT Qwen 717有效/1027 cap，Gemma 0有效/1744 cap，Ministral 1有效。路径`E93/runs-v1/*/predictions.jsonl`，字段`capped/valid`。这是接口失败，不是任何能力读数。

结论：I07的三条机制竞争（grader误读 / 生产偏好 / inverse目标缺prior）在现有证据下无法区分，而且上游有更大的问题（候选池无正确解释、格式污染、Ministral偏置）。ABBEL/TRLM/LEDOM/IW-OPD已拥有inverse feedback与前后缀credit的一般形式。**I07不值得优先投入。**

### 2.7 第一轮（E00–E51）留下什么

E29（移除完整GP源句后，角色事实的“scope迁移”仍在：同actor 61.25 [52.07,70.07]pp、换actor 10.97 [4.81,18.79]）、E43/E44（普通场景不支持普遍反向）已经说明E13–E51研究的是Qwen3-8B续写概率对人工语篇框架的响应，与GP修订无关。P14已指出：28个实验复用同一批24句、单模型。这一轮的可保留价值只有测量教训（极性、顺序、选项、No含义），没有现象。C03–C05是协议事实，不是发现。

---

## 3. 103张卡的覆盖审查

分组说明：范围=该卡实际完成的科学范围；有效=读数是否承载它声称的意义；保留=可保留的结论；越界=我认为超出数据的解释或后续被推翻的叙事。数值引自各卡/记录表（“卡”）或本人重算（“算”）。

### 3.1 E00–E12 基线与读数（Qwen3-8B/1.7B，Amouyal/SAP公开题）

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| E00 | 16-prefix复现；pooled −2.81 [−11.50,5.89]pp（卡） | 工具级 | 原协议对顺序极敏感 | 无 |
| E01 | PARTIAL；565/626变体审计 | 部分 | NP指称与“未断言≠假”混杂 | 旧role下降不能叫digging-in |
| E03 | FP32顺序交互+66.67 [49.28,84.06]pp | 协议事实 | BF16不是反转原因 | 无 |
| E04 | 1.7B方向+19.84 [14.04,25.82] | 方向复现 | nonGP lingering 30.71%说明仪器不干净 | 无 |
| E05 | 标签/断言语义校准 | 工具 | 换标签不除顺序效应 | 无 |
| E06 | attachment/event读数 | 工具 | GP主语角色0–5.8% | object-No高分不是恢复（卡已注明） |
| E07 | 原生边界迁移+60.87 [44.93,76.81] | 协议事实 | C03 | 不归内部parse（卡已注明） |
| E08 | 前/后focus交互CI跨0 | 测量 | 后置focus对GP/nonGP都+22pp | 无 |
| E09 | SAP自然题1152任务 | 测量 | cue有效、mapping强 | 无 |
| E10 | 问题/选项位置 | 测量 | 大差可由cue下降造成 | 无 |
| E11 | PARTIAL n3 | 弱 | 无歧义extension也降 | 结论范围已限制 |
| E12 | surprisal与QA分开；+1.47 [.47,2.52]bits | 测量 | cue facilitation主导 | 无 |

这一组是必要的仪器建设，但用了一天半去修一个最终被抛弃的协议（见§7）。

### 3.2 E13–E24 自然后文、事件、患者（Qwen3-8B续写log-prob，7–12 family）

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| E13 | Slattery后文，无诊断Q；−.031 [−.255,.211]bits | 测量 | 无普遍后文代价 | 无 |
| E14/E15 | 7 episodic；−2.61 [−3.78,−1.09] / 固定continued −1.97 | 测量 | 混合续写响应 | 不是患者特异旧绑定 |
| E16 | 桥交互+2.11 [1.17,3.14] | 测量 | 排除一般self/reciprocal抑制 | 实体曝光/词汇关联未排 |
| E17 | 关系+7.82 vs 中性−.98 | 测量 | 限制entity-only | 谓词检索竞争 |
| E18 | faithful9释义+1.44 [.90,1.91] | 测量 | 非exact verb echo | 未证明语义状态 |
| E19/E20 | 晚到角色事实；7/7 R负 −3.40 [−4.28,−2.44] | 测量 | 角色事实有效 | 不等于旧关联删除 |
| E21/E22 | named/generic；+3.06 [2.03,4.38]；POST-HOC主要cue | 测量 | C04局部 | 不是named更好修复 |
| E23 | 224实际续写；明确矛盾10→6 | **弱**：48 token cap、unknown 84/88 | 功能错误不稳 | 不升false belief |
| E24 | 12 family −.795 [−1.210,−.394] | 测量 | 跨source概率结构 | 不追认E23 |

### 3.3 E25–E42 范围、迁移、历史、实际用途（同上，人工frame）

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| E25–E28 | scope/actor/三态 | 测量 | 迁移不限旧event；U判断随label波动 | 不是world scope错误 |
| **E29** | 移除整句GP源，效应仍在（同actor 61.25 [52.07,70.07]pp） | 测量 | **GP不是必要条件** | 此后E30–E51已离开修订问题，却沿原名继续（关键节点） |
| E30–E33 | 边界/谓词/顺序/释义 | 测量 | 谓词依赖结构；表述匹配 | 不是普遍反向 |
| E34/E35 | 撤回report vs 假设；一句恢复+14.58 | 测量 | 冲突old-source native 54.17% | 不是成功修订后残留 |
| E36–E38 | 肯定/时间角色/独立选择 | 测量 | 624时间角色短语全对 | 新who题“0%”是审计失效，非错误率 |
| E39–E42 | 两名字/plain role/availability/native续写 | 测量 | old控制仅J/native成立 | 人工frame |

### 3.4 E43–E51 自然迁移与格式

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| **E43/E44** | 最小普通事实 / 平衡场景 | 测量 | **普通语言反转不成立**；native 96/96、576正确 | 反证正确，但此后仍缩回人工frame三张卡 |
| E45–E48 | 名字替换/析因/身份断言/表达交叉 | 测量 | 表达匹配效应；identity效应含一般提及 | 已是屎上雕花 |
| E49/E50 | 实际复述格式：列表joint 41.41% vs anchored 98.05% | 测量 | 输出格式支配“联合角色使用” | 不是角色能力失败 |
| E51 | PARTIAL；Step批39/192完整 | 无效 | 无 | 用户暂停 |

### 3.5 E52/E53/E59 重置后的广面

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| **E52** | 1732QA/309对/14模型/5族；NEITHER gap 24.03 [21.60,26.56]pp（226簇）；R1重读reduction −1.22 [−2.76,.39] | 测量，仪器审计极重 | 原No多为未断言；重读无选择性修复；旧三族FP32 NEITHER gap Qwen8 .358 [.299,.420]、Gemma12 .410 [.347,.473]、Llama8 .108 [.081,.136] | 卡片超过2/3篇幅是仪器自审；科学读数只占末尾 |
| E53 | PARTIAL；6244/6247双遍，role-v2未封版 | 部分 | 无终图 | 不能混入新角色证据 |
| **E59** | 明确源支持G2，1014QA/507对；MVRR gap Q63.79 [49.14,77.61] / G58.62 [43.10,74.14] / L37.07 [18.97,54.31]，29簇 | 测量 | 语义澄清不除缺陷 | 未分Gold Yes/No层：gap里混着“拒绝误读”与“断言替代”两件事 |

### 3.6 E54/E55/E60/E63/E64 可见性与源状态干预（旧三族）

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| E54 | 问句前非因果可见性 | 测量 | 无三族选择性修复 | null不排除架构机制（卡已注明） |
| **E55** | 4层×3位置×双向整残差替换；MVRR前1/4层歧义区48.33/36.67/26.11pp | 因果测量 | 源状态因果影响误读题 | 整残差不是语法变量（卡已注明）；**没有在替代依赖题上分层** |
| E60 | 消费深度切断 | 测量 | 早晚不同但伴损伤 | I05落空 |
| E63/E64 | 跨用途、source bank分解；TARGET−CONTEXT 43.33/19.44/18.33 | 因果测量 | C09限定L1 | 角色表达不共同恢复 |

### 3.7 E65–E75 目标与共同关系

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| E65/E66/E68 | 提前目标、经源/只在readout | 测量 | 目标收益不经源传递 | initial/final≠撤回/建立（P16） |
| **E67** | 3204自由输出，3033 packet双盲 | 测量 | 旧三族INITIAL目标↑明确误读 | forced-choice QA |
| E69 | 合理性 | 测量 | 一般合理性效应已有owner | 无 |
| E70 | 原子脚印；initial正断言+40/+60/+90 | 测量 | 局部断言恢复 | 8项语义更正传播 |
| E71–E75 | 正确前缀/联合/首答案/双版本/跨源 | 测量 | 均无三族共同恢复 | 五张卡是同一局部网格 |

### 3.8 E76–E84 草稿、输入可靠性、逆向、K/V

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| E76–E79 | 草稿→QA、Source移除、强模型草稿、P1 vs Source | 测量 | 无共同恢复；E79 MVRR Q+40.96 | 方法动作围绕同一读数 |
| E80 | TRUST/NOISY | 测量 | 输入信任不解释 | 无 |
| E81 | 逆向逐词Source | 测量 | NPVP final↑伴损伤 | 无 |
| E83 | LATE−WHOLE +59.06/+57.61/+31.88 | 条件评分 | 已给候选下的评分 | 不是native恢复 |
| E84 | K/V分解 | 测量 | V更多变化 | 无relation-specific变量 |

### 3.9 E82/E85–E90 当前三族、词义、框架（**本轮主要重读**）

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| **E82** | 当前三族21408条件；NPZ Min initial 84.55 / final 28.09 | **部分无效**：Ministral strict下No偏置（§2.2） | 真实错误仍在 | “Ministral initial已对、final错”是伪影 |
| E85 | Blott 2020词义48框架；歧义gap 38.54/29.17/30.21 | 测量 | 词义也难 | 与结构QA不可等量 |
| E86 | 接受 vs 理解 | 测量 | 输入拒绝不足解释 | 无 |
| **E87** | 18192实际输出；v2解析全明确 | 测量 | 实际≈强制选择 | **分层数据里已含本审查的核心现象，卡未写出** |
| E88 | verb/noun lookahead | 测量 | NOUN>VERB | 无 |
| **E89** | 9408实际；Gemma NPZ 0→100/73.5，MVRR 10→80/70；Q/Min 0 | 测量（oracle） | **显式框架对Gemma充分、对Qwen不充分** | 不是native valence证据 |
| **E90** | 源bank传递；Gemma NPZ 0→5.9 | 测量 | 源状态不携带框架 | bank不覆盖全部信息 |

### 3.10 E91–E108 观察重建credit（I07链）

| 卡 | 范围 | 有效 | 保留 | 越界/问题 |
|---|---|---|---|---|
| E91/E92 | reward vs 语义；G-grader/Q-gen −7.093 [−14.201,−.771]；E92 +.278/.222/.222 | 测量 | 表达影响credit | 未训练类比 |
| **E93** | 10464前向全cap（§2.6） | **无效** | 无 | 25.7 GPU·h执行失误 |
| E94 | ReBel 426 trace CPU | 描述 | parser问题 | 无 |
| E95 | Min 95.45% Tie，Q/G不全 | **接口不可用** | 无 | 不是0能力 |
| E96 | fidelity alignment +.444/+.500/+.500 | 测量 | 表达影响self-grader | 不是理解完好 |
| E97 | 仅Min完整，UPDATE 8.11% | 部分 | 无 | Q/G UNAVAILABLE |
| E98 | 当前三族1800实际（§2.5） | 测量 | 只有Qwen联合+20.83 | I08不普遍 |
| E99 | 旧三族POST-HOC联合 | 测量 | 旧协议现象 | forced-choice |
| E100 | 528/1200执行 | 部分 | 无 | 672未执行 |
| E101/E102 | prefix负/suffix正；T2 oracle +10.42/8.33/21.88 | 代数分解 | credit竞争存在 | 候选含cue来源；oracle位置 |
| E103 | 同源8候选；suffix−whole仅Min CI正 | 测量 | 多数源无好候选 | 角色类别≠完整意义 |
| E104 | Belief-R then-cut；UPDATE −12.72/−25.12 | 操作未对齐 | 无 | 无 |
| E105/E106 | 预算1→8 Q+13.54 [5.21,22.92]；自动规则无修复 | 测量 | 反对“搜索更错” | 无 |
| **E107** | 243/243双遍、76.54%一致；明确依赖收益Q+6.25/G0/Min+4.17 | 测量，**NPS标签受格式污染（§2.6）** | 原角色收益≠意义修复 | Min行受No偏置影响 |
| E108 | 未执行 | — | — | 不自动继承 |

---

## 4. 数据与读数是否承载了声称的意义

### 4.1 四种“No”的混淆
原Amouyal No（未必）、源支持No（未断言）、字面矛盾No、世界否定No。D0把它们分开了，这是前任真正做对的事。但分开之后，前任仍用混合的“initial正确率”做主读数（E59 gap、E65–E68目标收益、E82 initial），而没有把Gold Yes的替代依赖题当作主对象。**替代依赖题是整个库里唯一不受“No约定”困扰的修订测验**，因为它要求的是肯定断言。

### 4.2 initial/final 不是撤回/建立
P16已记录：INITIAL目标里NPZ 17 Yes、MVRR 16 Yes；FINAL里MVRR 19 No。E65–E75的“initial收益”把拒绝误读和断言替代混在一起。本审查§2.2的分层表就是把它们拆开后的样子。

### 4.3 Ministral的No偏置
strict规则下NPZ主句事实（Gold Yes）只13.6%正确，PLAIN下57%。任何用strict/RECOVER规则比较三族的卡（E82、E85–E90、E96–E107）都把Ministral当成了一个会“撤回旧关系”的模型。它只是在说No。前任记录了“Min控制弱单列”，但没有把它上升为“Min的strict读数不可用”，继续把Min列在三族主图里，还用Min的E103 +8.33、E107 −14.58/+10.42讲故事。

### 4.4 NPZ反身题对Qwen/Ministral的词义成分
对照句“While the protester hid, the mother…”下Qwen 41%、Min 8.8%承认“hide himself”。这不是GP。Gemma 70.6%是可用的。未来NPZ替代依赖测验要先用对照句筛出模型接受的反身词义，或改用Christianson 2001的RAT材料并报告对照基线。

### 4.5 两句复述格式对NPS的污染
Amouyal“rewrite as two shorter sentences”指令对NPS必然拆掉that补语。E53/E67/E96/E103/E107里NPS的“GP_MISREADING/INITIAL_MISREADING”相当部分是格式产物。NPS占E96–E107源的一半（25/50），占E67的36/178簇。涉及NPS的自由复述结论需要重标或改任务（例如要求“用一句完整句改写”或直接问替代依赖）。

### 4.6 E107标注本身
Step-5双遍一致76.54%，57裁决，是同一模型两次调用的一致性。我手读的9源×8候选中，MVRR/NPZ的INITIAL标签看起来正确；NPS按§4.5应改。“something”类UNBOUND判定合理。

---

## 5. 机制竞争图

对象：GP句读完后，替代依赖（被动双宾语/反身）为何不被断言。

| 解释 | 支持 | 反对/不可辨 |
|---|---|---|
| A 替代依赖没有形成（重建失败） | E87：GP 0–12% vs 对照81–91%（Q/G MVRR）；E89 Qwen被告知框架仍0；E107候选池多数源8/8误读 | E55/E64只在误读题上有因果证据 |
| B 形成了但读出/用途条件化（知道不用） | E55/E64源状态因果影响误读题；E89 Gemma给框架即可用 | Qwen给框架也不用，说明对Qwen不是“有而不用” |
| C 输出合同/问句语义 | NPZ反身对Q/Min对照也低（§4.4）；NPS复述格式（§4.5）；Min No偏置（§4.3） | MVRR双宾语对照81–91%说明Q/G接受问句语义 |
| D 评分/选择错配（I07） | E101/E102条件对有前后缀竞争 | 池里无正确候选；NPS污染；ABBEL/TRLM已有一般形式 |
| E 一般信息干扰/提示策略 | E89 EARLY>LATE、cue损伤 | 不解释Gemma/Qwen的框架可用性差异 |

现有证据最支持：**A为主，且A的失败在族间不同——Gemma的失败可被显式框架修复（缺的是触发），Qwen的失败不能（缺的是把框架实例化为命题的计算）**。B只在误读题上有证据。C是必须先清掉的伪影。D依赖A的上游。不可辨：A在Qwen身上是“词汇框架知识缺失”还是“在GP上下文里不能应用框架”；需要§9的实验。

---

## 6. 近邻定位

| 近邻 | 版本 | 它拥有的claim | 我们的距离 | 压缩风险 |
|---|---|---|---|---|
| Amouyal, Meltzer-Asscher, Berant 2025（ACL main, long.403）/ 2026（ACL main, long.1040） | 正式 | GP对LLM特别难；人机难度排序相似；thinking对GP帮助最小；猜想“要丢弃错误解释” | 他们的题几乎都是误读命题（Gold No）；没有替代依赖题分层、没有对照句下的替代依赖基线、没有框架提示；我们的增量是把“难”拆成撤回/重建两步并指出瓶颈在重建 | 中：若只报“更多模型更多构式”则被压缩 |
| Ceháková & Chromý 2025（Discourse Processes 62(10)）| 正式 | 人类英文MVRR/RAT最终表征比预想更破碎，AMBCOR约50% | 人类锚点与材料来源；无LLM | 低 |
| Lee & Shin 2026（KJELL, 期刊）| 正式 | GPT-3.5/4复述显示partial reanalysis（24句） | 单族、无框架干预、无因果；我们跨族+替代依赖直接问+框架充分性分离 | 中：标题“LLM partial reanalysis”已被用过 |
| Hanna & Mueller 2025（NAACL main）| 正式 | Pythia/Gemma-2-2b双parse特征共存；QA不复用句法特征 | 他们是feature级、小模型、不给外部结构信息；我们是行为级、外给结构仍不构建依赖 | 中高：须把“外给框架仍失败”作为核心，否则是“知道不用”的换名 |
| Li et al. 2024（CogSci）| 正式 | 24句、GPT-2/LLaMA-2，lingering misinterpretation与attention | 旧模型、无替代依赖分层 | 低 |
| Paape, Linzen, Vasishth 2026（arXiv 2602.04489）| 预印本 | surprisal不够；人类reanalysis是独立过程 | 他们是阅读时间；我们是最终解释 | 低 |
| Zhou, Stanojević, Hale 2026（arXiv 2606.27206）| 预印本 | syntactic belief update解释GP阅读时间 | 同上 | 低 |
| Emura & Sugawara 2026（ACL main, long.552）| 正式 | 双任务资源限制使LLM转向合理性理解 | 无GP修订 | 低 |
| Prakash et al. 2026（ICLR）lookback；Gur-Arieh 2026 rebinding | 正式/预印本 | belief/entity绑定与更新的电路 | 可借方法（binding干预）；对象不同 | 低 |
| ABBEL 2026 / Beyond Memory 2610.01415 / Agent-BRACE / ReBel / TRLM / LEDOM / IW-OPD | 混合 | 内容重建reward、belief trapping、inverse feedback | I07的全部一般形式已被占 | **高**（I07） |
| Christianson 2001; Slattery 2013; Huang & Ferreira 2021; Patson 2009 | 正式 | 人类lingering/partial reanalysis理论 | 理论框架来源；我们提供LLM版本的“重建而非撤回”证据 | 中：需明确说明不是重跑人类实验 |

本轮新发现、知识库尚无卡的近邻：Paape 2026、Zhou/Stanojević/Hale 2026、Emura & Sugawara ACL 2026、Clark/Levy/Gibson 2026（noisy-channel GP回视，arXiv 2605.18563）、"Beyond Memory" 2610.01415、Gur-Arieh 2026 rebinding（2606.08644）、"Belief-reality separation" 2607.11945。均为摘要级核对。

---

## 7. 推进失误诊断（节点级）

时间线（git按日统计）：10-05 95次提交（E00–E33）、10-06 56次（E34–E52）、10-07 45次（E53–E89）、10-08 28次（E90–E108）。**四天103张卡**，平均每天25张。这个节奏本身就排除了“看结果、想假说、读论文、再设计”的循环。

| 节点 | 发生了什么 | 当时本应 |
|---|---|---|
| E00–E12（10-05上午） | 一天半修Amouyal协议的顺序/标签/精度 | E03确认顺序反转后即可停；协议是上游的，不是我们的问题 |
| E13→E29（10-05） | 从自然后文滑到人工事件frame的续写概率 | E13 null之后就应回到真实错误条目 |
| **E29（10-05）** | 证明效应不需要GP源 | 这是关线信号；却又做了E30–E51共22张 |
| E43/E44（10-06） | 反证普遍叙事 | 停；却继续E45–E51 |
| E52（10-06）| 正确的重置；但卡片2/3是仪器审计 | 广面本身正确；D0已发现“替代依赖题”存在，应即刻以它为主读数 |
| E59（10-07）| gap不分Gold层 | 分Yes/No层后现象当天就能看到 |
| E55/E64（10-07）| 在误读题上做patch | 应在替代依赖题上做 |
| E65–E81（10-07）| 17张卡围绕目标/草稿/mask | 低信息量，均无三族共同恢复，每张卡都在决策表上写“不继续网格”然后继续 |
| **E82/E87（10-07）** | 分层数据里已有核心现象；Ministral偏置未识别 | 读原始输出、按Gold分层、丢掉Min |
| **E89/E90（10-07/08）** | 得到最强结果（Gemma可用框架、Qwen不能） | 这是方向；却判为“无稳定规律”转向I07 |
| E91–E107（10-08）| 17张卡做reward代数，E93浪费25.7 GPU·h | I07在候选池无正确解释时无定义 |
| 10-08 09:00 | 资源到期，权重删除 | — |

共性：(1) 每张卡的“决策表”写得很好，但下一张卡几乎总是“上一张缺什么补什么”，而不是按决策表走；(2) “不升级、不认证novelty”的措辞纪律极严，掩盖了没有做科学判断的事实；(3) 把测量纠错当成进展；(4) 读论文很多（86篇主文），但没有一篇改变了实验选择；(5) 用户在10-06、10-07晚两次要求“先找值得追的idea”，agent两次都用新的局部链回应。

用户的要求是否被落实：广面（是，E52）、真实错误（部分，但Min伪影）、多族（是）、自由用途（是，但格式污染）、避免防御性控制（否，E45–E51、E71–E81）、先找idea（否）。

---

## 8. 方向决定

### 8.1 是否继续
继续。理由不是沉没成本，而是：(a) 数据资产（D0资格表、892QA cohort、E87/E89全部实际输出、三族runtime配置）已经能支撑§0的现象而不需新标注；(b) 现象大（70–90pp）、干净（对照句内基线）、有人类锚点、跨两个强族；(c) 近邻只占了“难”和“partial reanalysis存在”，没有占“撤回与重建分离、显式结构对重建不充分”。

### 8.2 重构什么
1. **研究对象**：从“修订”泛称改为“替代依赖的建立”。主读数是替代依赖题（Gold Yes）的实际作答，辅读数是误读题拒绝率与对照句基线；三者同报。
2. **材料**：只用已发布材料里带替代依赖问句的GP句（Ceháková 2025英文MVRR双宾语/RAT；Christianson 2001 RAT；SAP中可用项）。先用对照句过滤“模型接受的词义”（§4.4）。预计可用源60–100句，不造模板。
3. **模型**：Qwen3.8-27B与Gemma4-31B保留；Ministral在strict规则下作废，若要第三族，用PLAIN规则重测或换族。
4. **I07、I08**：建议PARKED，重开条件写在idea卡（由人改状态）。E108不执行。
5. **E91–E107**：作为历史测量保留；其NPS结论标注格式污染。
6. **知识库**：补§6新近邻卡；在EPISTEMIC_CORRECTIONS记录Ministral偏置、NPZ词义成分、NPS格式污染三条更正。

### 8.3 候选方向比较（选一个）

| 方向 | 自然对象 | 关键问题 | 与证据的连接 | 相对近邻增量 | 主要风险 |
|---|---|---|---|---|---|
| **R1 替代依赖建立（选）** | 公开GP句+替代依赖问句 | 撤回之后为何不重建；显式框架为何对Gemma充分、对Qwen不充分；什么信息/状态能让重建成立 | §2.2–2.4已有全部起点 | Amouyal只有“难”；Lee&Shin只有“partial存在”；Hanna只有“特征不复用”；我们给出两步分离+外给结构不充分+因果入口 | n≈33题（可扩到60–100）；Qwen失败可能是词汇框架知识而非GP计算 |
| R2 I07 credit抵消 | 同源候选池 | 重建reward是否惩罚正确修订 | 池无正确解释；NPS污染 | ABBEL/TRLM/LEDOM占一般形式 | 高压缩风险 |
| R3 I08 目标问句 | 提前问句 | 任务分↑解释↓ | 当前只Qwen | query-aware/false-presupposition已有 | 不普遍 |
| R4 源状态patch机制（C09延伸） | 歧义区残差 | 哪个状态承载误读 | E55/E64 | Hanna/Prakash方法重叠 | 只在误读题上成立，不触及重建 |

选R1。R4可作为R1的白盒分支（把patch放到替代依赖题上），不单独立线。

### 8.4 若证明成立，一句话RQ、insight、为何兴奋
- RQ：读完GP句后，LLM是否建立了与晚到证据一致的替代依赖，还是只撤回了误读？
- Insight：撤回与重建是两个计算；当前最强开放模型普遍能做前者、几乎不能做后者；显式句法框架能触发部分模型的重建，另一些模型即使被告知框架也不能把它实例化为命题。
- 兴奋点：它把“LLM在GP上像人一样错”改写成“LLM在GP上比人更彻底地不重建”（人50%，模型0–12%），指出thinking无效的原因，给出按谓词论元框架而不是按整句重读的修复入口。

### 8.5 什么证据会改变我的判断
- 若在对照句过滤后，扩充到60+源的替代依赖题上，Qwen/Gemma GP正确率升到对照的一半以上 → 现象是题目/词汇效应，R1降级。
- 若Qwen在“框架提示+对照句”上也不能断言替代依赖 → Qwen的失败是词汇框架知识，不是GP重建，R1缩到Gemma一族。
- 若把对照句的动词位置状态移植到GP句，替代依赖题恢复到对照水平 → 机制在动词论元框架，R1升级为机制论文。
- 若2026年出现直接测“replacement dependency”跨族的论文 → 重新定位。

---

## 9. 未来最核心的两个辨别动作（只设计）

**X1 替代依赖三读数 × 结构信息来源（行为，≤3 GPU·h）**
- 材料：Ceháková 2025英文全集 + Christianson 2001 RAT + SAP可用项，每源三题：误读命题（No）、替代依赖（Yes）、后半句事实（Yes）；GP与对照各一。对照句先过滤：只保留模型在对照上替代依赖≥75%的源。
- 条件：native；EARLY框架提示；“结构释义”提示（给出对照句形式“X who was V-ed Y”作为无关句子的语法示例，不含本句实体）；对照句。
- 读数：Qwen、Gemma（Min用PLAIN规则）实际作答；每源三题联合模式（拒绝∧断言、拒绝∧不断言、不拒绝）。
- 结果如何改变判断：若提示使Qwen在示例句上能断言、在GP句上仍不能 → 失败是“在GP上下文应用框架”，机制在上下文而非词汇；若示例句也不能 → 词汇框架知识；若Gemma三条件都高而Qwen都低 → 族差是能力而非触发。

**X2 动词位置状态移植到替代依赖题（白盒，≤2 GPU·h）**
- 复用E64的bank框架，但读数换成替代依赖题；donor是对照句（“who was sent”）在主动词token的各层残差；recipient是GP句同词位置。对照：移植到歧义名词位置；移植self。
- 结果如何改变判断：动词位置移植恢复替代依赖而名词位置不恢复 → 重建瓶颈在动词论元框架表示（I06的具体版本成立）；两者都不恢复而误读题恢复 → 替代依赖不在源状态里，在读出端；都恢复 → 整残差太粗，须细分。

不排日程、不占卡、不恢复模型。

---

## 10. 本轮对仓库的实际修改

- 新增本文件。
- `ROUTE.md`：加入指向本审查与拟议新主线的入口（不改正式状态）。
- `README.md`：当前入口表加入本审查。
- `knowledge/EPISTEMIC_CORRECTIONS.md`：追加三条测量更正（Ministral strict No偏置；NPZ反身题词义成分；NPS两句复述格式污染）。
- `ideas/I06`、`I07`、`I08`：各追加一段带日期的审查意见（建议，不改状态）。
- `logs/2026-10-12.md`：追加本轮记录。
- 复算脚本未入库；所有数字可由§2给出的路径与字段用十行Python重得。

未做：未改workbench登记表、未改C/I状态、未删除任何文件、未推送。
