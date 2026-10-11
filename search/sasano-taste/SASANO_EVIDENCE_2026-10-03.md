# Sasano 品味与组内边界：2026-10-03 证据复核

本次推进的是用户要求的领域搜索校准，不是某条 workbench 的实验证据升级。未开线、未改状态、未运行 GPU 实验。仓库基准为 README、workbench 登记表、RESOURCES 与当前 sasano-taste README；archive 只作为历史证据，旧版“方法只能后置”等规则不覆盖当前 v4。

**本轮新增人类品味输入：** 先以 Sasano 的问题/结果形状筛选，再结合用户可能喜欢的题材；允许模型理解、表征、可解释性、推理与Agent，不依据游戏/视频兴趣把它们排前。用户明确估计导师不会支持视频，因此视频移出首推。组内语言学论文只校准研究范式，不能据此把传统语言学排成首推。横向 follow 排除时间序列、图算法；以下建议不代表新开 workbench，最终排序见[本轮领域比较](TERRITORY_SHORTLIST_2026-10-03.md)。

## 1. 先纠正附件中会影响选题的三件事

1. **不能把 Sasano 概括成不喜欢 Agent 或可解释性。** 在 2026-04-14 的 `r_xiang`，他直接帮忙整理了检索型 agent 在敌对输入下的行为与安全性研究计划，但同时说当时学修计划的内容不必过分看重。它能反证“Agent 一律不合口味”，不能当成某个 agent 选题已获科学认可。[原消息](https://fvcrc.slack.com/archives/C0ASG6BEE1H/p1776134954868809)
2. **附件对 Knowing vs Using 的背书漏掉了同日后续。** 9 月 14 日 11:20，他觉得 real/imagined 工作的第三项 finding 最意外，并要求 RQ 与 finding 一一对应；12:39 学生补充“内部编码信息却输出相反”已有先例；14:04 他立即回复，这样就难以强主张。应完整读这三步，不能只摘“有趣”一句。[兴趣与叙事要求](https://fvcrc.slack.com/archives/C0ATPT9P8SV/p1789356019464609) · [后续定位约束](https://fvcrc.slack.com/archives/C0ATPT9P8SV/p1789365861632809)
3. **Human–Model Behavioral Geometry 与 Pragmatics 都有组内邻居。** `r_tanaka` 已比较人类与模型的回答分布、熵、Wasserstein 距离；`r_yano` 已讨论相同动词/相近表面结构下不同事件类型与隐含参与者。它们仍是可驻留领域，但不应标成低重叠空地，需按科学对象划边界。[Tanaka 的测量修正](https://fvcrc.slack.com/archives/C050CEX2J82/p1760937331975549) · [Yano 的自然对比例子](https://fvcrc.slack.com/archives/C03BT3F495Y/p1773583906534489)

## 2. 本人评论与我们的推断分开

| 证据 | 直接确认了什么 | 可以据此推断什么；不能推断什么 |
|---|---|---|
| `r_hamdi`，2026-07-08：[原 thread](https://fvcrc.slack.com/archives/C0ATPT9P8SV/p1783402245660699) | 学生得到与预测相反的结果后，他仍说有意思，并建议从 obituary 扩到政治/体育文章与真实人物共现等自然语境 | 重视结果对预期的修正、自然变体与边界；不是要求每篇都必须出现反常，更不是预先构造反常 |
| `r_hamdi`，2026-06-28：[原评论](https://fvcrc.slack.com/archives/C0ATPT9P8SV/p1782624771444119) | 输出相似而内部不同可以有趣，但可能只够 discussion | 内部差异不是独立 headline 的保证；可解释性应服务明确外部问题 |
| `r_hamdi`，2026-06-28：[另一评论](https://fvcrc.slack.com/archives/C0ATPT9P8SV/p1782624233200559) | 建议 manifold steering 对比线性、局部分段线性、spline，并定位非线性来自哪些 layer/parameter | 并不排斥方法、机制与干预；要求读数能分辨真正增量 |
| `r_hamdi`，2026-09-14 / 18：[RQ/finding](https://fvcrc.slack.com/archives/C0ATPT9P8SV/p1789356019464609) · [读者负担](https://fvcrc.slack.com/archives/C0ATPT9P8SV/p1789746607243569) | 普通审稿人要很快理解工作及其有趣之处；RQ/finding 应对齐 | 清楚自然的入口应先于机制术语；不能用大量实验掩盖主旨不清 |
| `r_tanaka`，2026-01-17：[原评论](https://fvcrc.slack.com/archives/C050CEX2J82/p1768662590500549) | 已开始知道发生什么，但为何发生仍不清楚；弄明白会更有意思 | “模型与人不同”通常只是驻留开端，需要能区别解释的后续测量 |
| `r_tanaka`，2025-12-29：[原评论](https://fvcrc.slack.com/archives/C050CEX2J82/p1766984523879379) | 即使不如预期，也只能据实写结果，不要求所有结果都有趣 | 不筛结果；这是观察纪律，不是要求所有无效切片都扩成 paper |
| `r_kisako`，2026-04-11：[量化建议](https://fvcrc.slack.com/archives/C06T0TCPJSG/p1775837696705759) · 05-11：[任务异质性](https://fvcrc.slack.com/archives/C06T0TCPJSG/p1778497728371079) | 异常可能来自量化实现；建议等频分箱；一贯趋势出现后仍追问 retrieval 的异常 | 先修强 baseline，再解释差异；小方法不是禁止项，也无需一开始训练大模型 |
| `r_guo`，2025-08-21：[原评论](https://fvcrc.slack.com/archives/C08MPLKALSF/p1755754821976589) · 2026-03-27：[定位](https://fvcrc.slack.com/archives/C08MPLKALSF/p1774596827005219) | 与英文 pivot 预期不相关也可能有趣；标题要让人看出与已有工作的区别 | 负相关/零相关可以是出发点，但换更新模型并不足够形成增量 |
| `r_kurauchi`，2026-08-02：[原评论](https://fvcrc.slack.com/archives/C08PS660124/p1785664123315619) | LLM 的价值在于适配听者年龄、知识和兴趣；有限汉字覆盖本身不足以超过字典；自动评估和人评角色需说清 | 对数字人/游戏 NPC 可借鉴“沟通对方是否实际理解”，而不是角色口吻是否像；这是我们的研究转译，并非他明确批准 NPC |
| `r_utami`，2026-05-25：[讨论建议](https://fvcrc.slack.com/archives/C07QNJ8053J/p1779672964264889) | 单一 rewriter 统一处理全部文本与真实使用方式不同，不能混同 | 真实行为与受控干预需要相互校验；不能把统一改写的效应直接当现实总体效应 |

**本次最可靠的归纳：** 他并非只接受纯语言学、只接受无训练、或不接受 agent；他更在意研究对象自然、增量说得清、测量可信、结果对普通读者有信息量。用户关于“不喜欢追热点/小模型 benchmark 刷分”的直接经验继续有效，但本轮公开 Slack 样本没有独立重现那次口头判断，故不伪造其逐字来源。

## 3. 组内题材与可复用资产边界

| 对象 | 已核对的相邻工作 | 对新 territory 的影响 |
|---|---|---|
| 人与模型的意见、分歧、分布 | `r_tanaka`：WVS/SmartNews、距离/熵、拒答比例修正 | 社会调查分布复刻需先对齐组内；对话中理解/协作/误解修复不是同一对象，可作为邻接方向 |
| 随机选择、多样性、内部知识与输出 | `r_hamdi`：random choice、real/imagined、内部干预 | 不要把 generic knowing-doing 或 random-choice diversity 直接包装为全新主线；先定自然任务及 consequence |
| 语义 frame、隐含参与者 | `r_yano`；公开 FrameEOL 系谱；`r_guo` 最新可见消息在做标注手册与元话语参照功能 | broad pragmatics 要进一步分 common ground、听者模型、修复等；不能默认所有隐含意义均无人做 |
| 面向听者的表达适配 | `r_kurauchi`：汉字解释的听者适配与人评 | 可以作为研究方法和评估经验，直接复做“为儿童生成汉字解释”重叠很高 |
| 写作同质化、母语痕迹 | Utami 的 [v4](https://arxiv.org/abs/2604.08568v4)，作者标注 EMNLP 2026 Main | 这是直接的组内 claim ownership；“Human Variation”若只做改写后的语言多样性会重叠，需要区分行为对象 |
| embedding 冗余与压缩 | Kisako/Tsukagoshi/Sasano 的 [联合压缩](https://arxiv.org/abs/2606.01074) | 适合学如何从已有测量长出小方法；不建议直接复制为自己的独立线 |
| cross-lingual / form–meaning | 仓库 `cross-lingual-acquisition-regimes` 为 PAUSED，保留丰富测量与 baseline 修复授权；组内也有跨语言同形词资产 | 如用户选这一域，优先复用并重构旧资产，不能由 agent 恢复状态 |

Pragmatics 的推荐边界不应是“所有隐含意思”。更适合驻留的是一类持续发生的自然活动，例如**参与者如何建立共同理解、发现误解、澄清和修复**：它能连接协作游戏、NPC/数字人与 agent，且不必从 RL 或训练开始。这是研究建议，不是已经完成近邻审计或已发现异常。

## 4. 三个公开论文样例如何改变我们的找题动作

详细论文卡见 [组内研究形态卡](../../library/themes/research-craft/SASANO_GROUP_PAPER_CARDS_2026-10-03.md)。这里只保留对搜索的作用：

- **Utami 的新版本尤其重要。** [v4](https://arxiv.org/abs/2604.08568v4) 与检索常返回的 *Can We Still Hear the Accent?* 旧版题目、叙事不同。最新主旨是母语痕迹变淡并非 LLM 突然造成，较大变化早已出现在神经翻译阶段；控制改写显示仍可进一步变淡。我们要学的是“把已有直觉放回更长历史中检验”，不是照搬“LLM 让人同质化”的标题。
- **Kisako 的联合压缩**并非从空白开始，而是将两个成熟操作放到同一预算轴上，找任务之间的规律与异常。适合卡多弱互联：同一批 embedding 可缓存，CPU 后处理反复测量。它也说明 training-free 不是 zero-cost，校准、任务训练的轻量 classifier、数据缓存均须计入。
- **To Drop or Not to Drop?** 把“信息是否可恢复”与“人是否自然愿意省略”分开，再采集理由。训练强 baseline 并不是本文目的，论文明确指出 supervised BERT 强于 zero-shot LLM 不能本身作为意外结果。应学“自然选择 → 理由标注 → 对照”，不能把更大模型的低分当机制结论。

## 5. 搜索阶段可执行的品味校准

1. 先选真实活动与现成数据，再复现强开源 baseline；先不承诺异常是哪一个。
2. 至少保留“不同结果分别会改变什么理解”；不要把预期写成发现。
3. 用户资源支持独立单卡/单节点的条件、模型、seed 并行；人评、CPU 模拟器、数据下载与 evaluator 可能成为瓶颈，不把十几张卡自动折算为线性吞吐。
4. training-free discovery 可以保留后续小训练；公开论文样例证明无需从零训大模型，但不证明每个题都无需训练。
5. 知道/使用差异、人与模型差异、自然/合成差异优先当测量维度；只有出现稳定、能排除最简单解释的结果，才考虑独立 headline。
6. 不以组内或外部邻居为自动关闭理由。先写“谁拥有哪条 claim、我们共用哪些资产、增量在哪”；由人决定分工或选线。

## 6. 访问边界与未核对项

- 已使用 Slack 插件的只读 public search 与 thread read；核对了 Sasano 的用户身份，并定向覆盖 `r_hamdi/r_kisako/r_tanaka/r_guo/r_kurauchi/r_yano/r_xiang/r_utami` 八个频道。先看近期消息，再检索研究相关内容；不是穷尽全频道历史。
- 未搜索 private/DM，未发消息，未下载 Slack 附件；不会把无检索命中解释为“没有此项研究”。不转存原始 Slack 对话，仅保留必要摘要与 permalink。
- Sasano 个人英文主页本轮返回 Internal Error；公开论文通过 ACL Anthology 作者页、论文全文和 arXiv 最新版本交叉核对。主页访问失败不影响上述消息/论文证据。
- 公开论文卡是 source-grounded 研究形态分析。DOCUMENTED 指作者明确写出的动机/变化，不意味着知道作者最初灵感的私人历史；RECONSTRUCTED 是我们的谱系重建。
- 本轮未运行数据、未复现任何公开论文数字；引用均为论文报告值。EMNLP 接收状态为 arXiv 作者声明，未独立查验会议 proceedings；Kisako 的最终会场状态未核对。
- 没有将 EACL 工作作为候选依据；Findings 文献仅作为已有近邻/组内资产，不是投稿目标。

## 7. 补充：从最新 NeurIPS 标题表横向 follow 的三个领域

检索源为主 agent 保存的 `/tmp/sasano-search-20261003/neurips2026-events.json`，来自 [NeurIPS 2026 官方下载目录](https://neurips.cc/Downloads/2026)。poster 独立页面本轮经 web/HTTP 均无法打开（HTTP 403），所以区分“目录确认”和“全文/作者站确认”。狭窄关键词的命中数只说明标题表的检索量，不可当作领域热度或录用率。

### A. 生成模型默认审美与风格个体差异

- **自然母问题：** 没有指定风格时，模型替用户做了哪些稳定的审美选择；不同模型是真的多样，还是在收敛到同一种画面？这连接视频、游戏美术和数字人，但研究对象是模型默认选择，不是训练更大 T2I 模型。
- **目录锚点：** *Characterizing the Aesthetic Defaults of Generative Image Models*；*Beyond a Single Score: An Audit of Aesthetic Evaluation in Text-to-Image Pipelines Across Subcultural Visual Languages*；*AesGI-Bench*。`aesthe` 在该目录命中 3 标题，仅是粗检索。
- **主源核验：** [LouvreSAE 项目站](https://louvresae.github.io/) 已给出 26 个生成器的语义受控审美 profile 和测量方法；不能把“模型有默认审美”再当我们的 novelty。可跟进的是 profile 的稳健性、特定用户/任务下的审美偏置、及哪些自然干预改变默认选择。
- **资产状态：** 项目站给出 [模型 collection](https://huggingface.co/collections/danielfein/louvresae) 和 [数据入口](https://hf.co/datasets/neurips-subm/anonymous)；模型 collection 已访问并确认列出 SAE checkpoint，数据页访问失败，Paper/Code 链接目前是占位。未验证文件体积、许可证与完整可下载性。资产核对后才可称 baseline-ready。
- **资源适配推断：** 缓存公开生成图/embedding 后可独立推理与重分析；需要保留人类审美分歧，不能全靠一个 aesthetic score。用现成 SAE 不必先重训，但图像资产的磁盘成本需实测。

### B. 模型的行为个体性、自我能力判断与可预测性

- **自然母问题：** 模型说“我擅长/不会”的时候，反映的是它自己的特长，还是所有模型共享的题目难度印象？长期合作时能不能认识某个具体伙伴的长短处？它直接连接大小模型协作与游戏搭档，但首先是测量问题。
- **主源：** [LLMs Show No Signs Of Individuated Metacognition](https://arxiv.org/abs/2605.24299) 在 20 模型、6 benchmark 中区分共享难度、模型阈值与真正的个体校准；推理模型可能在回答信心问题时偷偷解题。不能把相同 claim 换成小模型再做一遍。[Feedback Forensics](https://github.com/rdnfn/feedback-forensics) 提供公开工具和预标注数据，测量反馈鼓励的行为特征与模型表现出的特征。
- **资产/成本：** 前者正文和附录已读，作者报告约 $4,000 API / 18 万 calls；声称 cache 可重现，但本轮没找到可用 release 地址，故不推荐照搬开销。后者仓库已可访问；存在 AI annotator 依赖，先用预标注结果或本地校准，不能称完全无 API 成本。
- **可探索空间（推断）：** 模型个体差异是否跨任务、跨反馈、跨伙伴可迁移，以及失配对协作造成什么后果。先自然任务 baseline，再考虑游戏/NPC对象；与现有 mechanism-population-dynamics 的区别是行为个体性而非内部机制复现，仍需仓库分工。

### C. 视觉社会认知、自然错觉与可见证据

- **自然母问题：** 当视频中的人知道的东西与镜头呈现不同，模型错在没看清、没记住，还是没有分清各参与者获得了哪些证据？游戏、魔术视频、遮挡与视角切换提供自然对象；无需训练视频 foundation model。
- **目录线索：** *The Prestige: Benchmarking Cognitive Visual Reasoning using Magic Tricks*；*Perception, Not Reasoning, Limits Visual Theory of Mind*；*What Sketches Tell Us about LVLMs: Conventions, Grounding, and Localisation*。这些标题体现了视觉基础/认知构念之间的重新归因，但目录标题不能替代论文证据。
- **资产边界：** [ToM 作者主页](https://bmrayan.com/) 确认题目，但 paper/code/project 仍显示 soon；其余两篇本轮未找到可靠全文/仓库。暂列横向跟进，不升为立即可跑的优先项。
- **成熟邻接入口：** [MovieRecapsQA（CVPR 2026 原文）](https://openaccess.thecvf.com/content/CVPR2026/papers/Shaar_MovieRecapsQA_A_Multimodal_Open-Ended_Video_Question-Answering_Benchmark_CVPR_2026_paper.pdf) 报告视频与对话的理解瓶颈与人模型差异，可作为继续检查的入口，当前只核验摘要，尚不能给 baseline 配方。
- **定位压力：** generic perception-vs-reasoning 已有大量近邻，不应包装成冷门空白；需要具体自然活动、可控输入与对后果有解释力的读数。相比 A/B，此领域数据 I/O 和人工标注风险更高。
