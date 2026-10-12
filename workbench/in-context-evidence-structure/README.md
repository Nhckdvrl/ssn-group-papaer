# In-Context Evidence Structure（ICES）

**2026-10-12当前认识（E131全链完成）：** Source条件读取作用于历史形成的证据；共享输出改变其它来源的关联如何进入本来源证据。冻结形成预测、原生操作、固定词关联与整体功能政策已接成证据链。E122双方面独立确认中，选择性答案形成政策四模型平均收益2.8–7.4点，全部来源形成隔离更差；query-only与一致/冲突情形有不同后果。见[当前综合](RESEARCH_SYNTHESIS_2026-10-10.md)、[机制概览](results/figs/fig_source_evidence_overview.png)、[英文主文](PAPER_DRAFT.md)、[技术附录](PAPER_APPENDIX.md)。
## 状态
- **2026-10-12整篇对齐：** E120/E121/E122各四模型16→32完成；主文围绕三项认识重组，284数值呈现与原始证据独立核对。C21–23有界L3、C24有界L2；C22/23升级基于受控与真实SST直接实验、混杂审计和独立复算。E123四模型16→32完成，真实共享输出平均+7.32/+5.37/+9.47/+7.42点，两Actor均正；far完整输出错误、词先验和headroom保留，22,824项独立复算封版；[最终主文审阅](results/e123/manuscript_claim_audit_2026-10-12.md)核304个新数值呈现，未发现保留三项主张必须补实验的缺项。
- **E124继续推进：** 公共无标签身份在私有监督独立时的阶段反事实三模型16→32完成；Qwen形成身份特异+4.59[2.73,6.64]pp，Mistral负/Llama未定。见[完整结果](results/e124/report.md)/[独立11742项复算](results/e124/independent_review_2026-10-12.md)。进一步回到“哪些信息应共享”的自然问题；E125公共Source–输出词关系三模型16→32已完成：形成期特异+26.66/+7.71/+8.30pp，直接query期三项未定；错误对应表也有益，不能以字面表路由解释。私人监督历史形成隔离、joint query仍读两缓存，Qwen候选功能代价与M/L来源非对称保留。E126等价表缓存组合已确认，E126在public事实/private监督/词集/global位置全部相同时，共同order形成的Source缓存联合使用优于混合：Q/M/L +23.49[20.80,26.07]/+10.40[7.96,13.04]/+5.42[4.00,6.79]pp，private source-only仍强；主要词空间使用，candidate效应小。它补充公共关系形成如何支持独立规则部署，但不识别ID或latent非加性。Q/M两个coherent order有差、margin点负CI0、M A joint低全部保留。 E127四checkpoint16→32完整确认，同词相反约定primary +8.89/+5.86/+.78/+9.38pp、Source条件margin均正；小L/部分联合能力全部保留。主文§6.5整合机制链，E128全部完成，14B输入标准兼容+2.93[.59,5.47]pp但joint约52%，其余平均CI触/跨0；四T小正。E129两checkpoint16→32亦完成，确认两个标准功能primary CI0，single usable/小响应保留；仅F0形成Cue范围，不推断无native标准信息。下一步先全结果与近邻审阅历史共享如何支持Source条件信号，不扫head/layer。
- **状态：** ACTIVE-EXPLORE（2026-10-08 人决定恢复，E39–E48 已开展；此前 2026-10-06 PAUSED 为历史记录）。这是正式研究排程；不意味着别的研究方向停止。
- **当前综合判断（2026-10-12）：** 先读[综合](RESEARCH_SYNTHESIS_2026-10-10.md)前言和最新科学问题更新、[整篇对齐](PAPER_ALIGNMENT_2026-10-12.md)、[主文证据审计](results/e122/manuscript_claim_audit_2026-10-12.md)。早期E115–119与本轮E120–122分别封版；标题可修改，正式candidate状态未改。历史摘要如下，不将当时下一步重复执行。
- **E81确认：** 64新contexts，同实际码carrier m/pi下，改变其它token的whole-query读取使Tag准确率+13.3[9.4,17.2]点；固定m/kind翻Source分配使Prefix−11.3[−15.2,−7.8]点。C20 L1。旧Source ranking仅测输出contrast符号，不能直接当内部选择；公共偏移也可减少平均mass。下一步是解释已有因果区别，不扫新配置。
- **E82/E83：** Label读取重放独立+7.8[3.9,11.7]点，末位可转移其主要收益；原生Source影响仍按C16经整个query。冻结旧native注意力拟合的关系reader在64新context增加Source contrast .376[.358,.393]nats，预算/位置模型无益；逐context预测相关仅.252，非完整解释。Source与code在自然query共线，E84只检验这个具体解释，不开新任务。
- **E84/E85：** code代理更准确预测布局Label读取变化，但native两Cue都用；NameK交换独立确认使field反转/code保正，LabelKV改变两者。冻结联合干预四项均值预测误差.007–.036nats，形成有限依赖/组合解释，不称两个独立Source模块或完整算法。详见综合§11–12。
- **E86与最新纠偏：** 16-context pilot中码与标签直接相关时，alias gap增强14.46/15.89nats，严重超出旧模型外推。结果保存，64-context确认未启动；先读完整机制论证、回到自然多规则问题，避免局部控制自行繁殖。详见综合§13。
- **最新研究重构：** 不扩实验矩阵。输入过滤/条件读出/示例检索未必是互斥机制，整段状态交换也不识别所携带信息的功能。综合§14已逐项对照旧证据和原论文；优先明确Source地址与criterion含义的不同预测。E87仅未实施候选记录，无科学脚本/运行。
- **E88实际推进：** 保留recipient示例、input前同姓名来源字段K/V移植，24 pilot→32新措辞确认；隐式criterion迁移−.00084[−.01307,.01154]nats，显式+.18225[.14904,.21662]；两者差+.18309[.15328,.21541]。这是接口功能的有界分离，raw discordant accuracy约51%，不宣称完整规则/纯地址已证明。详见综合§15与卡。
- **E89诊断已完成：** 原生chat初版有请求类型歧义，明确请求后续完全部178截断回答、逐项核对最终结论；默认discordant accuracy56.25%[52.34,60.94]，标准识别50%。显式识别不跨请求稳定，未建立“知道标准但不会使用”。不继续格式/位置矩阵；候选下一问题是规则形成中的合法跨Source信息传播，定位与竞争解释见综合§15.6。
- **E90最新：** 从强E56基线检验Source形成/读取。24→48的统一正方向未确认；另冻结32新contexts确认query仅可读A时，B改rule仍改变A的17.6%[12.1,23.8]答案，规则效应幅度.734[.474,1.083]nats。单来源模块收益独立确认61.7%→89.3%。来源位置选择、信息依赖与准确率必须分开；结束mask矩阵，回到共享Task特征与私有输出映射的解释。见综合§16/卡。
- **E92/E93：** 强Qwen3.5-27B thinking同材料native63/64合规正确、余1内容正确但格式未解析；4context诊断不作普遍结论。E93已完成8B：私人B偏好仍改变A约16–20%答案，oracle亦弱；strong direct原子98–100%而A mixed仍约50%，thinking120/128；E94已完成：来源整字段可转B函数98.4%，标准运输384条0答案改变；结束此字段矩阵，检验怎样共享标准、保留当前来源偏好；不再只要求强模型持续失败。见综合§18。
- **E91最新：** 24→48确认，query禁读B、A原始证据和输出词不变时，分开B标签使rule影响幅度.683→.193nats；只换A Key也下降.228[.095,.361]，V-only下降.248[.100,.406]。标签身份影响来源内证据的形成与读取，纯直接foreign词读出不足以解释全部；不称新QK/V组件，见综合§17。A-only准确率差CI跨0，C16/C20仍L1。
- **E95–E97最新：** 匿名证据相同而来源分组决定标准；thinking criterion16/16、私人mixed19/32。自推criterion文字使Own-only mixed87.5%且保留私人偏好；E97带新review/yes-no的标准问题160/160。结束格式控制，见综合§19–21。
- **E98/E99最新：** E98轨迹运输未过阳性，停止该接口；E99独立n8标准64/64、Own256/256(128unique)，native mixed83.6%[68.8,96.1]，原生也已较强。E100行为候选未运行；E101已完成512交换，511最终判断不变；E102字段交换主要重定位recipient B；E103整函数KV模型95.3%，未分出C/P通道；E104跨Actor只换Rec有部分criterion作用（opposite mixed65.6% vs50%），后续推断矩阵未运行。见综合§22–27。
- **E105/E106/E107：** 标准推断16/16，但Rec after直接评分有EOS与有限criterion作用；E106独立32ctx确认，自己的label KV承载历史B-rule依赖（替换减少.429[.250,.632]nats），评论内容中介弱。E107完成480交叉＋4self，Own KV因果参与，mixed after56.25%、增益CI触零；结束此接口扩展。综合§28–29正面对齐近邻，不把局部接口或已有分工称最终novelty。
- **当前机制进展（E108–E112）：** 历史B答案K→A label形成的namespace解释在Qwen/Mistral32新ctx各自确认，冻结逐query rule预测r=.969/.966；Qwen第二任务亦保持，C21有界L3。固定答案词的情绪配对在新词/句式确认，答案V传递部分关联（对照差.618[.446,.813]nats），此为当时C22单模型L2范围；E113随后直接确认家族扩展。独立318项复算通过；E110长评论控制不足与E111残差完整保留。研究对象回到来源特定证据怎样形成和使用，不继续字段/头搜索。
- **最新完整机制链（E113/E114）：** 固定label关联传递在Mistral32新词句确认.404[.313,.499]nats，C22两家族L2。全Source原生判断中形成条件作用Qwen2.098/Mistral1.238nats，signed缓存交互.775[.113,1.440]/.321[.187,.454]；历史答案KV近似预测原生label反事实r=.899/.930、.959/.968。C23有界L2；559项独立复算与两家族token流重建通过。本轮5批/36,736评分/.353 GPU·时，有限核心实验已完成；native两家族/单任务，保留残差和真实应用有限后果。
- **E115–E119确认：** Llama native形成.947[.740,1.158]nats；E116三家族MHS真实文本局部作用确认、single私人能力仍弱。E118独立criterion×code全响应；14B native匹配方面选择性均正/rotation .410[.330,.493]，query全程禁读B仍.190[.073,.310]。local label/历史答案边仅解释部分，负/小正方向完整保留；E119 namespace预测r .934/.927、signed交互负。见综合§33–35，三家族/更大同族不靠模型数自动敲定novelty。
- **2026-10-08/09 进展：** 真实数据上的后果与机制（C13，E46–E49）：多人带名字的样例混在同一上下文时，LLM 只保留每人标注倾向的 35–58%（2 个真实数据集、8 模型、4 家族）；每人独立的标签词恢复到单人水平；读标签头把另一人的标签读进答案，换词后在读出层面分隔（E48）。顺序 / 格式敏感线（E40–E45）已止损关闭。见 `PAPER_SHAPE.md` 末节。
- **2026-10-10 继续探索（人授权）：** E58–E64完成，复盘见 [`REVIEW_2026-10-10.md`](REVIEW_2026-10-10.md)。来源影响有native因果路径；Qwen的label读取很大部分发生在答案前query位置，Mistral主要在末位，不能再写“默认完全不用来源”。C14–C16均L1，尚无完整机制选择理论。10-09整理保留为历史记录。
- **E65/E66更新：** query接力有模型边界（Qwen的Label标记／Mistral的来源字段）；删direct-label无稳定accuracy修复。input前source缓存对single/mixed均失败，已见input的缓存保留logit但准确率收益有限，不能包装成新组合瓶颈。各卡与复盘已记负结果，C16仍L1。
- **E67–E70更新：** 同信息code位置改变Qwen的来源排序；prefix K的历史作用可在完全禁读label后保留。独立冻结公共key偏移将accuracy从0.543恢复至0.602，但来源排序0.828仍低于原生0.938；预测恢复不等于binding恢复。C17–C19均L1，bf16数值失败已作废，详见复盘§8。
- **E71更新：** 相同namespace下，关系码×位置的accuracy交互独立确认+10.9点；旧冻结frame新身份迁移35%[23.1,47.7]/accuracy+3.1点[0.8,5.5]，是正的部分迁移，未达到原预设MIE，不能说没有可迁移结构。
- **E72–E75更新：** 短direct预算与Markdown漏判不能证明binding失败。48次同轨迹前缀核对全一致；27B thinking普通多来源pilot全对，8B native Source双射补全亦全对（18contexts），independent未完成三分之一，不称能力缺失。E74即时缺失组合32–36%，方向CI跨0；详见复盘§10。
- **E76/E77更新：** Source方向响应可复现，但E76中点与加性任务允许Source均值解释，撤回完整函数组合解释；新数字accuracy73.4%未过门槛。E77相同Source标签频率/多个Input下，显式规则全对，而从示例推断时连Single identity也弱；追函数识别、全局偏好与实际调用，不直接称Source特有缺陷。详见复盘§11。
- **E78/E79更新：** 定义顺序使mixed subtract插值96.1%→25.0%；共享词典任务lookup95–99%，但direct subtract组合仅15.6–21.9%，不作可靠知道却不用/provenance机制归因。两者作为诊断与解释边界保留；不优先追新的原生/算术门槛。详见复盘§12–13及综合总结。
- **主 idea：** [`ideas/I04-output-indexed-evidence.md`](ideas/I04-output-indexed-evidence.md)
- **目标会议：** ICML / ICLR（ICL 理论与机制叙事）；备选 ACL / EMNLP（标签语义、标注者视角、非平稳 NLP 场景叙事）。
- **证据账本：** [`CLAIMS.md`](CLAIMS.md)　**实验索引：** [`experiments/INDEX.md`](experiments/INDEX.md)　**论文形态卡：** [`PAPER_SHAPE.md`](PAPER_SHAPE.md)　**日志：** [`logs/`](logs/)
- **territory 卡：** [T16](../../search/our-taste/TERRITORY_IN_CONTEXT_EVIDENCE_STRUCTURE_2026-10-05.md)　**知识库：** [`library/themes/in-context-evidence-structure/`](../../library/themes/in-context-evidence-structure/)（FIELD_MAP、KEY_PAPERS）

## 1. 研究问题
**起点（T16）：** 冻结 LLM 能不能判断上下文里的反例是“噪声”还是“规则变了”，并据此调整证据的汇总方式？
**测量工具：** exact 层级 Bayes oracle（联合推断变化率 λ 与噪声率 ε）在指定生成模型与先验下给出一个**方向相反**的预测——在后缀反例之前加零散噪声，该oracle应**更不**相信后缀；而正权重的可加汇总会**更**相信。配合成簇检验（同样数量的反例，连成一串 vs 零散）与新旧对调检验（A→B vs B→A）。它不是所有ICL prompt唯一合理的规范假设。

**收敛后的问题：** 模型在什么情况下能追踪变化、在什么情况下把新旧证据混在一起——以及为什么。
**当前机制问题：** 多套规则共存时，来源特定证据怎样形成并用于新输入？来源cue影响读取，同时输出命名与历史关联影响被读取的证据。Tag/prefix等变量服务于这个问题，不自行成为题目。

## 2. 核心 idea（I04）
> **I04原始候选解释：In-context learner 按“输出”存放输入-输出证据。** 某个输出得到的支持，来自带这个输出的 demo 的、按输入相似度加权的汇总；这份汇总在时间与上下文上可交换。
> 因此：**改变“用哪些输出”的变化看得见**（标签流、格式、输出语言、换了新词的新 regime），**把已有输出重新分配给不同输入的变化看不见**（concept drift、因人而异的映射），而且新旧输出标签越相似，证据混得越多。

原候选机制（Qwen3-8B、Qwen2.5-7B）：一族晚层“读标签”注意力头从答案位置读取 demo 的标签词，按内容相似度选择、不看位置；旧 demo 的标签位置因因果掩码不可改写，新 demo 也不写入“变了”的信号；可交换汇总是这条直接读取路径的有效描述，完整query程序的充分解释已受E59–E64限制。

**解释边界（2026-10-10）：** 上述末位通路参与计算，但不是整个程序的充分解释。E59/E64检出来源名字K→query内部消息→答案的参与；source差分可跨标签迁移，但不等于完整绑定已可部署。当前追问：来源条件化在query的哪些位置形成、不同模型为何在不同阶段读取label，以及末位读取何时保留或稀释已经形成的条件规则。E64尚未证明最后一种“稀释”假说。

## 3. 证据（按主张组织；数字与 CI 见 CLAIMS 与实验卡）
| 主张 | 关键数字 | 实验 | 等级* |
|---|---|---|---|
| 输出侧变化被规范追踪 | 标签流噪声检验 13/13 模型为负；E22 格式通道 16/16；全局变换（±k、大小写↔反转）到 32B 更强 | E05/E06/E11/E16/E22 | L2 |
| 条件结构被可交换汇总 | 13 模型（0.6B–32B）噪声方向错；thinking、指令、T=64、时间戳、K=4/6、任务切换都不改变；与 set oracle r≈0.98 | E02a/E03/E07–E09/E16/E23/E25/E27 | L2 |
| 看最近邻，不看最近期 | 预测跟随“query 像哪一半 demo”，两种顺序对称（32B 差 ≤0.04） | E04/E21 | L2 |
| 同一答案内：察觉变化但不重置 | 大写标记时格式规范、映射平坦；删除影响：格式通道旧 demo 支持度为负 8/8，映射通道为正 16/16 | E22/E26 | L2 |
| 时间结构只在“偏向新输出”的成分上 | 不均衡翻转：条件成分噪声方向错 12/12（6 模型）；少数类 query 被拉错 | E28/E29 | L2 |
| 证据按输出身份分开 | 分隔阶梯：不同输出词 0.00 ≪ 输入领域 0.36–0.49 < 上下文标签 0.51–0.91 < 时间（完全合并） | E24/E30/E31/E35 | L2 |
| 泄漏 ∝ 标签语义相似度 | 14 套标签词，ρ=0.75–0.96（5 模型 × 2 任务） | E33 | L2 |
| 输出命名作用于本Source证据形成 | 历史答案K冻结重建r=.969(Qwen)/.966(Mistral)，Qwen第二任务r=.907；独立校对通过 | E109/E111/E112，C21 | 有界L3 |
| 固定输出词仍可传递关联 | 受控情绪与真实SST直接确认；SST答案KV绝对超额四模型正，signed方向不统一；仅部分路径 | E111/E113/E121，C22 | 有界L3 |
| 形成与正常读取共同作用 | 全Source读取时作用保持，A/B历史背景交互有模型差异；受控及SST直接测得 | E114/E115/E119/E121，C23 | 有界L3 |
| 建设性修复：新 regime 换新词 | concept drift 变得可追踪，11/12 格（含 1.7B/2B） | E32 | L2 |
| 机制：读标签头 + 不可改写的锚点 | 逐头分解重建 r=0.9997；注意力：同类 ×2–69 ≫ 标注者 ×1.5–2.6 ≫ 位置 ≈0；因果修补：方向错误的噪声效应 = 晚层直接读噪声锚点 | E36/E37/E38 | L2 |
| 为什么（训练统计） | toy：任务同质数据复现解离，易变数据推不动；LoRA 只得到近因 | E12/E18 | L1 |

\*等级见 CLAIMS；旧主张在独立校对前不自动升级。**校对备注：** C21/C22另一个会话先从原始记录复算318项数字并审查采样/缓存，实现通过；C21只在实际3个model/task组合记L3，C22不随之泛化。K-only仅该边不直接替换V，后继状态自然演化；高重建不证明唯一/必要通路。

关键图（`results/figs/`）：
- `fig_marked_drift.png`：格式跟随变化、映射不跟（E22）
- `fig_nearest_not_newest.png`：看最近邻不看最近期（E21）
- `fig_structure_selectivity.png` / `fig_regime_map.png`：跨任务 × 模型地图
- `fig_label_similarity_leakage.png`：泄漏 vs 标签语义相似度（E33）

## 4. 被实验否定的解释
表层 vs 潜在（E11b）· 单条 demo 可识别 regime（E13）· “可复制标签”（condarith）· 任务识别 vs 任务学习（E27）· 时间写进内容（E23）· 输入侧标签分流（E24）· 主效应来自相邻 token 统计（E34）· 映射与主效应由两组头承载（E36）· 新锚点是运行滤波器（E37）· “Label:” 预测位置存放运行估计（E38b）· 游程头 = 边缘通道（E28b）。详见 I04 §5 与 CLAIMS 作废记录。

## 5. 最近邻（完整定位见 I04 §6）
Wang et al. EMNLP'23（标签词锚点，机制层最近邻）· Kossen et al. ICLR'24 · Falck et al. ICML'24 · Zhao et al. ICML'21 · Xiong et al. ICML'25（任务叠加；正式记录已校正）· Dudley ICML'26 / Qin ICLR'26（训练模型的变化检测）· Cho et al. ICLR'25 / Yang-Cho-Inoue ICLR'26（检索电路、TR/TL 头）。
**最危险的压缩：** “ICL = kNN + 标签偏置”——回应见 I04 §6。

## 6. 下一步（按信息量排序，非日程）
1. 以“多个来源共享输出时，来源特定证据怎样形成并被使用”为主问题，围绕C21/C22/C23、E90/E91及原生Source读取证据组织论文候选；不把一般上下文化或QK/V改名成新发现。候选形态见PAPER_SHAPE当前段。
2. E120–122已完成原生操作、自然功能与双来源整体政策检验；E123自然政策/namespace竞争已完成，将所有功能代价、完整条件与独立复核纳入主文/附录；[最终整篇主张审阅](results/e123/manuscript_claim_audit_2026-10-12.md)与可复现交付已完成。以科学预测与认识增量评估这一轮，不自动追加头/层控制；正式candidate状态由人判断。
3. **人要求的工作习惯：** 每完成一组相关实验，回到研究问题、原文和已有结果检查：实际回答了什么，是否跑偏，替代解释还剩什么，增量与novelty在哪里；据此改变下一动作。不是每个控制失败就压缩主张，也不靠多写卡片代替判断。

## 7. 目录
| 路径 | 内容 |
|---|---|
| `ideas/` | I04（主 idea）、I01（早期版本） |
| `experiments/` | E00–E123 实验卡（E80未运行；E86仅pilot；E87候选未实施；跑前卡与POST-HOC分开）；`INDEX.md` 为总索引 |
| `CLAIMS.md` | 主张账本 C00–C24、混杂审计、作废记录 |
| `PAPER_SHAPE.md` | 论文形态卡（I04 版）；`PAPER_DRAFT.md` 为当前英文论证；`PAPER_OUTLINE.md` 为 10-05 旧版历史提纲 |
| `DATA_PLAN.md` | 数据方案与实际使用的数据 |
| `PAIN_LOG.md` | 痛点与工程坑 |
| `scripts/` | 数据构造、打分、分析、机制脚本；见 [`scripts/README.md`](scripts/README.md) |
| `results/` | git 里只有汇总表（csv/json）与图；逐条打分 `*.jsonl` 与大数组只在本地 |
| `logs/` | 每日日志 `YYYY-MM-DD.md`（训练/进程日志只在本地） |

## 8. 复现与资产
- **环境：** `/home/xiang/miniconda3/envs/verl-clean`（transformers 4.57）；Qwen3.5 / Nemotron-H 用 `openslime` + `scripts/vendor`（tf 5.12，不进 git）。
- **数据：** `data/*/rows.jsonl` 由 `scripts/build_*.py` 以固定种子重建（不进 git）。自然数据集直接下载使用：SetFit/sst5、fancyzhx/ag_news、CogComp/trec、Yelp/yelp_review_full、Todd et al. FV 任务（`data/fv_tasks/`）。nonce 词库经 StepFun step-5（Step Plan 接口）逐条审计：`data/lexicon.json`（标签词 84、属性名 26）。DICES-350 原始 csv 在 `data/dices/`（未使用于结论）。
- **打分：** `scripts/run_lm.py`（左填充 + 显式 position_ids + 精确多 token log-prob）；多机排队 `scripts/run_queue2.sh HOST GPU "DATA:MODEL ..." BS`、即时启动 `scripts/launch.sh`。
- **只在本地（不进 git，NFS `/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure/`）：** 逐条 LM 打分 `results/*/*.jsonl`（约 570MB，可用 `run_lm.py` 按卡重跑）、训练/进程日志 `logs/*.log`、机制数组 `results/mech/*.npz`（逐头 DLA、锚点 value、注意力；可用 `scripts/mech_*.py` 重建）、注意力探针 `results/*/attn_*.npz`、LoRA/toy 权重 `/tmp/xiang_*`（fvcrc13 本地）。
- **算力备注：** fvcrc10/13/20 的空卡；NFS 约 40 MB/s，32B 模型首次加载需 ~25 分钟；同一张卡上的任务只放一条队列（两条队列会在交接时撞车导致 OOM）。
- **E67–E70资产：** `results/e67_e70_summary.json`、各有效`analysis/run.json`与汇总图入git；原始JSONL、token布局、`results/e70/frozen_frame/frame.npy`留上述NFS路径。冻结偏移按E70卡无query提取重建；bf16作废控制记录保留。科学确认使用独立seed/词库/label，E70为float32。
- **E71–E77资产：** 各卡脚本、小`run/analysis/control/format_audit/prefix_audit/scoring_audit.json`、摘要与图入git；原始生成token/text、contexts、prompts、behavior JSONL在`results/e71/`至`e77/`上述NFS路径，不进git。E72 27B用本地`/tmp/ices_models/Qwen3.8-27B`，HF revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`，conda openslime＋vendor tf5.12.1；text-only语言权重完整，无MTP。按卡固定seed、所有contexts与失败保留。
- **E65/E66资产：** `results/e65_e66_summary.json`、各有效`analysis/run.json`与E65图入git；逐query原始JSONL及token布局留NFS。E66 bf16作废输出/控制记录保留，float32有效版本按卡重建。
- **E58–E64资产：** `results/e58/`、`e59/`中的`*.npy`锚点状态与各卡`contexts.jsonl/behavior.jsonl`留在上述NFS路径，不进git；代码与固定种子可重建。小汇总`results/e58_e64_summary.json`与`analysis.json`入git。Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`；Mistral-7B-v0.3 `caa1feb0e54d415e2df31207e5f4e273e33509b1`；节点NVMe `/tmp/ices_models/`由对应HF缓存snapshot复制。环境仍为conda `verl-clean`（torch2.8.0/cu128、transformers4.57.6）。

- **E78/E79资产：** `results/e78/qwen3_bridge/`、`results/e79/qwen3_codebook/`的原始context/behavior JSONL本地留存；小run/preflight/analysis、E79事后错误签名及`results/figs/e78_definition_order.{png,pdf}`入git。按实验卡/seed与同conda重建；不把coded词典任务当原始多标注分布。
- **E81资产：** `results/e81/qwen3_{discovery,confirmation}/`的小run/preflight/analysis与标POST-HOC的输出几何、`results/figs/e81_carrier_and_query.{png,pdf}`入git；contexts/behavior JSONL留上述NFS路径。同Qwen3-8B/conda，按E81卡seed81001/181001重建；源码hash与完整行数均核对。旧读数核对为`results/e70_e71_attention_audit_posthoc.json`。
- **E82/E83资产：** raw JSONL与E82 `native_features/*.npz`留上述NFS路径；小run/preflight/analysis与冻结reader metadata入git。唯一小数组`results/e83/frozen_reader/coefficients.npz`约152KB用于复现冻结预测，按`fit_e83_reader.py`从E82 seed82001重建。E82确认seed182001、E83验证seed183001，全部错误donor/contexts保留。
- **E84/E85资产：** 小run/preflight/analysis、冻结预测与独立验证、E85静态图入git；raw contexts/behavior JSONL留上述NFS路径。E84 seed84001/184001，E85 seed85001/185001；按卡脚本/同conda复现，科学引擎hash冻结。
- **E86资产：** 仅seed86001的16-context pilot，小run/preflight/analysis、冻结旧参数预测与图入git；raw在上述NFS的`results/e86/qwen3_discovery/`。按E86卡、同conda/Qwen3-8B重建；seed186001确认未运行。
- **E88/E89资产：** 小analysis/run/preflight、注明POST-HOC的内容审计、E88图入git；原始JSONL和生成token IDs留上述NFS的`results/e88/`、`results/e89/`。E88源hash522515d8…两阶段不变；E89版本/完整预算续完按各卡与run重建。Qwen3-8B/conda同上，实际合计约.466 GPU·时；没有新checkpoint。
- **E90资产：** 三批主实验与两批single的JSONL留本地`results/e90/`；小analysis/run/preflight/rule_sensitivity、冻结forecast和图入git；按卡seed/源码hash748c497f…/同conda重建。实际约.1793 GPU·时，Source隔离无layer/head搜索，无新训练。
- **E108–E112资产：** 原始contexts/behavior JSONL留本workbench绝对路径的`results/e108/`至`results/e112/`，大checkpoint不入git。Qwen3-8B在本机`/tmp/ices_models/Qwen3-8B`，Mistral base在fvcrc20 `/tmp/ices_models/Mistral-7B-v0.3`（revision caa1feb0…，3权重SHA核对见e112/model_identity_audit）。同conda、FP32/eager；各卡/run记录n/seed/脚本SHA。E111 validation用`--materials validation --n 32 --seed 111101`，E112确认`--n 32 --seed 112101`；复现写新out目录。小analysis/run/冻结预测/完整性及独立审计、核心图/绘图源码入git；无需下载新训练checkpoint。

- **E99/E101资产：** E99 raw生成、prompt与token IDs留本地`results/e99/qwen35_part*/`；E101标注输入`results/e101/annotations/`与原始32轨迹在上述E99目录，脚本保存原token前缀，不重新编码CoT。小标注/设计审计与后续run/analysis入git，高维activation与raw续写留`results/e101/`；同本地27B revision、openslime/vendor环境可复现。
- **E113/E114资产：** 原始contexts/behavior JSONL在上述NFS的`results/e113/`与`results/e114/`，小analysis/run/preflight/completeness、独立559项复算和两个PNG/PDF/数据及绘图源码入git。E113 seed113001/113101；E114 seed114001/114101/114201，确认`--materials validation`，按卡用同conda、FP32/eager、原model revision重建至新out。Mistral实际分块token流含固定额外空格，答案区域word＋3实际分隔token（B32senders；Qwen16）；不等于字面整串编码。没有新训练checkpoint。

- **E115–E119资产（2026-10-12）：** raw `results/e115/`至`e119/`的`contexts.jsonl/behavior.jsonl`留在`/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure/`共享资产路径，small analysis/run/rotation/audit与图入git；实验卡固定seed/revision/source hash可重建。Llama官方匹配分片审计在`results/e115/model_identity_audit.json`；14B official revision40c069824f4251a91eefaf281ebe4c544efd3e18及身份见`results/e119/model_identity.json`，远端缓存`/dev/shm/ices_models/Qwen3-14B`为易失副本，可从HF snapshot重建。使用conda verl-clean，实际Qwen3-8B/14B为post-trained（历史Base称呼纠正），无新训练。

## 9. 决策记录
- **2026-10-05：** 注册为 PROPOSED（ownership audit 后选定 evidence-structure inference）。
- **2026-10-06：** 人决定 I04 为主 idea，先做机制；机制阶段完成第一轮（E36–E38）。
- **2026-10-06：** 人决定暂停推进，留作之后主推的 candidate；转去找新题。

- **2026-10-08：** 人决定恢复为 ACTIVE-EXPLORE；E39–E48 已开展，见当日日志及实验卡。此决定不构成永久关闭其他项目的依据。
- **2026-10-10：** 人要求停止不断追加解释条件，耐心总结全部进展与下一步并上传GitHub main。本次据此完成综合与记录；不改变ACTIVE/I04，不启动新实验，下一步聚焦已有E59–E71链条。

- **E120–E123资产与复现：** 四项共32批768contexts/388608评分，小run/preflight/analysis/audit、5组科学PNG/PDF和源码入git；raw JSONL在本workbench共享`results/e120/`至`e123/`。从[脚本说明](scripts/README.md)按冻结seed/revision重建，SST公共pinnedJSONL用`scripts/reproduce_sst.py --cache-dir <新路径>`下载/核SHA，原science不改；[portable审计](results/e123/portable_reproduction_audit.json)验证三Arrow和Llama32上下文byte-identical。conda/FP32/eager，无新训练checkpoint。

- **E124资产：** 6批144contexts/54144scores，raw contexts/behavior JSONL在上述NFS `results/e124/`；小analysis/run/preflight、独立审计、科学源和PNG/PDF入git。首评分前f9b9b31c/ea65caf59…，固定seed124001/124101，3checkpoint同revision/conda；portable SST入口支持e124且Llama32新名字contexts byte-identical，详见[脚本说明](scripts/README.md)。

- **E125资产：** 6批144ctx/72576scores，raw `results/e125/*/{contexts,behavior}.jsonl`只留NFS；小报告/metadata/独立审计与科学源码入git，75f756…/a0a79918首评分前freeze。复现入口支持e125且Llama32官方新别名contexts byte-identical。

- **E126资产：** 6批144ctx/49536scores；raw同NFS `results/e126/`，ad2c6f…/377de6c4前评分freeze；summary/metadata/audit/科学源和图入git，独立12462项max0。portable SST支持e126，Llama32 contexts byte-identical。

- **E127资产：** 8批192ctx/132096scores，raw同NFS `results/e127/`；cef7952…/4b8ee609前评分freeze，summary/8run/audit/两图入git，35528数值max1.78e−15。Q14原10ctx partial与0-score OOM留档、完整run计时1.950864GPU时单独记；portable Llama32 byte-identical。

- **E128/E129资产：** E128八批192ctx/130560scores，f0a014…/5e9549ed前评分freeze，独立38760数值max0；raw同NFS `results/e128/`，小report/summary/run/preflight/audit与图入git。E129 raw同`results/e129/`，四固定Llama/14B运行16/129001→32/129101，生成材料无需外部数据；完整多层pre-input Cue-only运输，所有raw/事故保留。复现入口见[脚本说明](scripts/README.md)，model pins和conda与E119/128相同。

- **E130/E131资产：** E130四批96ctx/104448scores完整；E13118/18阶段、480run-stagectx/245760scores独立核验，两个家族8→32/70B新材料三环均完成。原始JSONL与pin权重留共享results/e131和节点本地资产，不进git；完整analysis/run/小summary/独立审计与12点图入git。L70确认formation/native在10、function在13四卡单节点完成；未执行20迁移，其同30shard SHA资产仅准备/0科学评分。权重10路径/local2/moonshot/ices_xiang_models_20261012/Llama-3.1-70B、11/13的/tmp/ices_models/Llama-3.1-70B、Q32在20的/dev/shm/ices_models/Qwen3-32B；恢复方式与逐文件pins见results/e131/model_identity_*.json及download/helper记录。

- **可重建论文稿：** [完整PDF](results/paper/main.pdf)；科学正文/附录仍为PAPER_DRAFT.md/PAPER_APPENDIX.md，官方ACL样式原样，22项primary来源与构建命令见[paper/README](paper/README.md)。当前排版稿含全部旧证据，E131同链完成后继续整合；呈现审计不等于科学完成/接受判断。
