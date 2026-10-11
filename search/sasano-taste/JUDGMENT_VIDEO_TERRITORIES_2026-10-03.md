# 人类判断、视频理解与视觉知觉：三个可驻留领域

核查：2026-10-03。这是 SEARCH 文献与资产核查，不是实验结果；未建 workbench、未改 ACTIVE 状态。精读记录见 [论文卡](../../library/themes/unified-multimodal/JUDGMENT_VIDEO_PAPER_CARDS_2026-10-03.md)。主线仍为 real-time causalization，探索线仍为 mechanism population。

**按用户最新纠正，先看导师关心的自然问题与可解释的发现，再结合个人兴趣：§3 视觉表征作为跨DL参考；§2 视频依导师匹配暂非首推；§1 人类语言分歧作为方法参考和交互研究桥梁。** 三者都是已核资产的领域材料，不意味着必须从中开线。接下来应优先补最新主会的模型理解、概念表征与抽象结构，避免困在传统语言学或视频评测。当前没有任何“会出现反常”“更容易中”的实验依据；以下保留原节号以便追踪核查。

## 0. 对附件上一轮的纠偏

- A/B 的引文基本存在：[Japanese Quiz](https://arxiv.org/abs/2511.12300)、[ACL2026 NLI](https://aclanthology.org/2026.acl-long.752/)、[Wavelength](https://aclanthology.org/2025.emnlp-main.1008/)均核到原来源。应撤掉五星、95% inference、容易出异常等无预算/实测依据的判断。
- “Human–Model Behavioral Geometry”同时装入知识难度、语义歧义、价值分歧、解释风格，缺少共同实验对象。这里把 A/B 收束到**有重复人类标注的语言理解与决策**；不把人的分歧全部称为错误，也不把采样温度等同于人群多样性。
- “均值好、分布不同”已有直接 ownership：Wavelength；“ensemble接近人类标签分布但解释更同质”已有 ACL2026 NLI。它们是要复现的起点，不能作为我们的预期 novelty。
- [non-verbal ACL2026](https://aclanthology.org/2026.acl-long.2101/)研究以文字描述的沉默/表情/动作，**不是把真实视频或音频换入模型**。其最高约60百分点差不能直接用来论证视频感知失败。其数据也不等于自然对话的总体分布。
- 语用共同任务与反馈是有价值的桥梁，Wavelength具备公开人类实验和本地模型入口；本 memo 不另开泛“隐含意义”领域，与互动 agent 检索合并。

## 1. 人类语言分歧与标注行为（桥梁备选）

**自然母问题：同一句话，几个人给出不同解释时，模型究竟保留了哪些合理差异、又把哪些差异当成了错误？** 应用是文本标注、语言理解、个性化交互；意义不依赖某个模型的排行榜。起点限定 NLI/释义判断，再依据真实测量扩到语用，避免一开始包揽道德、医学、政治等相异构念。

### 热度卡

执行 `density 'human label variation|annotator disagreement|human disagreement'`：EMNLP2024 1、ACL2025 3、NAACL2025 1、EMNLP2025 5、ACL2026 3；ICML2025 1、ICML2026 2、NeurIPS2025 1。ICLR2025 0/1、ICLR2026 0/2，样本太少，不可推接受概率。较宽的 `human.*difficult` 会大量捞入不相关视觉任务，不能拿来证明本领域拥挤。

`shapes` 精确切片只有2篇 rejected、1篇 withdrawn，没有足够 accepted；无法给可靠形态比例。2026新增 CAPO、IDRR、multimodal HLV、formal-semantic decomposition 等预印本；没有时间完整的 arXiv 分母，**月度增长率未核对**。这是一条活跃的 NLP 方法/测量线，不是空白，但无需与旗舰模型预训练竞争。

### 谱系卡

| parent → successor | 压力与改变的前提 | 当前入口与边界 |
|---|---|---|
| 多数票NLI → [ChaosNLI](https://github.com/easonnie/ChaosNLI) → [ACL2026模型label/explanation variation](https://aclanthology.org/2026.acl-long.752/) | 单一gold无法描述人的分歧；从accuracy改为分布和解释 | 官方100人/题分布与JSD/KL脚本；不能因此说每种少数意见均合理 |
| [VariErr](https://github.com/mainlp/VariErr-NLI) → [LiTEx](https://github.com/mainlp/LiTEx) → [CAPO](https://arxiv.org/abs/2605.28802) | 区分标错、不同解释、稳定个人风格 | LiTEx代码/标注存在；CAPO论文说开源，但核查时仓库仅README/LICENSE，不作为首跑基线 |
| annotator aggregation → [NUTMEG](https://aclanthology.org/2025.emnlp-main.144/) | 不把所有分歧当噪声，也不把所有噪声当多样性 | Bayesian aggregation作统计对照；不需要大模型训练才能审计标签 |
| 语用选择题 → [Wavelength](https://github.com/linlu-qiu/wavelength-eval) | 单一答案不足以刻画连续概念理解 | 100题×40人类guess，开放本地logit/RSA实现；单轮且人群固定 |

### 形态卡与近邻 ownership

可行形态：**构念分解+人类数据测量**；**可靠分歧识别/保留方法**；**有后果的评测修正**。不是“更多模型跑一遍ChaosNLI”。

最近邻明确拥有：

| 近邻 | 已有claim/证据 | 我们仍需由驻留确立的距离 |
|---|---|---|
| ACL2026 Label and Explanation Variation | 跨模型采样与人类NLI分布/解释比较 | 不能再仅宣称模型不似人；需解释具体误归因或判断后果 |
| EMNLP2025 LiTEx | 相同标签内部仍有不同语言学解释 | 仅解释taxonomy换模型不足；要证实某类差异改变决策 |
| CAPO，作者在arXiv注明EMNLP2026 Main接收 | 重复行为可辨识；ICL/SFT/DPO模拟特定标注者 | “个人差异存在且可学习”已占；需要外部有效性/可识别性等实质变化 |
| [IDRR 2026预印本](https://arxiv.org/abs/2602.22723) | 个人模型在歧义高时不稳定 | 不把一个人一次选择当稳定身份；需重复判断或明确可识别边界 |
| [MLLM HLV 2026预印本](https://arxiv.org/abs/2603.19744) | 共识/分歧子集上的规模结论不同 | “更大不总更像人”已有，不能照搬到另一benchmark |
| [Formal structure 2026预印本](https://arxiv.org/abs/2607.15870) | formal profile的组效应与个体预测上限不同 | entropy相关性本身不足；要检验解释类别、干预或实际决定 |

### 立足点卡

1. **先跑成熟人类数据和官方统计脚本**：ChaosNLI的4,645题每题100个标签；官方提供旧模型预测与JSD/KL结果，可先在CPU复核，之后换本地开放模型作系统基线。[代码与数字](https://github.com/easonnie/ChaosNLI)
2. **强现代开放模型入口**：Wavelength官方支持Qwen3/Gemma3/Llama3及直接logit、CoT、RSA。先固定一个能在单卡运行的模型和官方完整100题，复核其主图数值，再增加同家族与跨家族；不要从第一轮就全笛卡尔积铺开。[实现](https://github.com/linlu-qiu/wavelength-eval)
3. LiTEx/VariErr补充解释与标错分析。CAPO不是当前可直接运行的完整仓库；所有声称“公开”都须区分论文承诺、仓库文件和实际下载验证。
4. 资源形态：文本与缓存logit，独立单卡；无需付费API。少量解释人工复核不可被模型judge悄悄替代。统计不确定性按item/annotator层次重采样，采样次数不冒充人类人数。

### 压力清单（来源是压力，不是预注册结果）

| 压力 | 出处 | 可形成的工作形态 |
|---|---|---|
| 真实分歧与标错混在一起 | VariErr、NUTMEG | 构念测量/标注协议 |
| 相同标签掩盖不同理由 | LiTEx | 解释分类与决策后果 |
| 模型输出总体分布近人，item-level关系仍异 | ACL2026 NLI | 分布保留的有效性分析 |
| 个体风格受输入内容干扰 | CAPO §3 | 检验测量单位，避免单item拟人推断 |
| 不同任务对“稳定个体”的证据相异 | CAPO与IDRR | 可识别性/跨任务复核，而非预设冲突 |
| 高共识结果掩盖高歧义行为 | MLLM HLV | 评测修正+下游后果 |

**D1–D6顺序**：官方预测复算 → 本地开放模型复现 → human-data schema与item provenance → 分歧/错误/重复性测量 → 更新近邻 → 再决定是研究标注方法、交互中的解释差异还是评测。不先许诺 post-training 会“洗掉差异”。

## 2. 视频中的证据使用与社会解释

**自然母问题：看一段互动，模型根据哪些实际线索判断人物在做什么、为什么这样做；线索不够时能否区分看见的事实与合理猜测？** 对数字人/NPC的价值是理解互动，不等同于生成一个数字人。与当前主线不同：这里研究冻结视频理解器，既不训练world model，也不研究causalization阶段损失。

### 热度卡

`density 'video' 'social|narrative|theory.of.mind|human.*reason'`：CVPR2025 30、ICCV2025 30、NeurIPS2025 32、ACL2026 8、ICML2026 24；ICLR2026 35/121（29%，全会27%）。该宽切片还含生成/叙事，不可当纯social understanding篇数。`shapes`的ICLR接收48篇：method90%、benchmark75%、finding15%；关键词可多选，不能视为互斥贡献比例。

它比“低热度”强很多，且benchmark密集。推荐的理由是数据/基线可用和自然问题持久，**不是已经证明竞争少**。新增 [SocialReasonBench](https://arxiv.org/abs/2608.30716)、[Cultural Moment Benchmark](https://arxiv.org/abs/2608.23065)继续占据反事实/文化/模态分解。

### 谱系卡

| 谱系 | 前提变化 | 入口 |
|---|---|---|
| Social-IQ → [Social Genome](https://aclanthology.org/2025.emnlp-main.1264/) | 不只看答对，要看证据来自视觉/语言/声音/外部知识 | 272视频、1,486人类trace；公开视频下载有失效/I/O风险 |
| Video-MME/MVBench → [Video-TT](https://openaccess.thecvf.com/content/ICCV2025/html/Zhang_Towards_Video_Thinking_Test_A_Holistic_Benchmark_for_Advanced_Video_ICCV_2025_paper.html) | 分开没采到关键帧与已有帧仍理解失败 | 全部短于65s，固定80帧可回答；评测代码沿用lmms-eval |
| 静态ToM → [MoMentS](https://arxiv.org/abs/2507.04415) → [Read the Room](https://github.com/LiXingNiu/Read-the-Room) | 上下文/模态与连续心理状态 | 前者开放数据；后者R3-Bench/FDT数据有链接，但代码库仅README，不能算完整训练基线 |
| 线性影视叙事 → [SocialReasonBench](https://arxiv.org/abs/2608.30716) | 使用游戏实际分支提供可核验反事实 | 六选一、脚本/flowchart ground truth；游戏常识污染与发布权限仍要核对 |

### 形态卡与定位

可行形态：**自然任务中的证据失效+最小修复**；**跨模态可归因测量**；**具有实际后果的评测协议**。泛“模型看不懂人”已不是增量。

| 近邻 | 已有ownership | 驻留时要回答的距离 |
|---|---|---|
| Video-TT | 固定可回答帧、自然误导问题、强人机差距 | 仅加模型或改prompt无实质增量；需要具体证据依赖与后果 |
| Social Genome | 逐步trace及视觉/声音/知识grounding | 不能重做“回答对但理由不grounded”；需可干预的条件/机制 |
| MoMentS | full/focused context与模态消融 | 再发现“更多上下文不一定好”压缩风险高 |
| Read the Room（作者库注明ICLR2026） | 心理—物理因果链、数据+微调 | 泛social CoT训练不适合抢；先看冻结baseline真实困难 |
| SocialReasonBench（预印本） | Detroit分支、反事实及干扰项分类 | 换游戏不足；game script ground truth不同于人类社会真值 |

### 立足点卡

- **首跑**：Video-TT官方数据的多选split+Qwen2.5-VL-7B/LLaVA-Video-7B开放weights，固定80帧。官方Qwen2.5-VL-7B MC=39.9%、primary=20.9%；二者不可混用。MC无judge；完整open-ended复现用官方Qwen2.5-72B评分器，开销与judge误差都计入，不可称完全免judge。[论文表1](https://arxiv.org/html/2507.15028v1)、[数据](https://huggingface.co/datasets/lmms-eval/video-tt)
- 视频一次本地下载并做定长帧缓存；同checkpoint连续跑condition，节点之间不共享随机读。7B×80帧也必须实测显存，不能用参数量替代预算。8张卡可以分模型/条件，但先做单卡端到端读盘与生成profile。
- 社会证据系统采用Social Genome的公开trace补充；其官方全量下载说明约60GB、有`--no_frames`约30GB，不能假设网络瞬时可用。[作者代码](https://github.com/CMU-MultiComp-Lab/social-genome)
- 后续小训练只在明确痛点后做adapter/读数校准；不开几十小时全长影片训练，不依赖持续商业API。

### 压力清单

| 压力 | 出处 | 形态 |
|---|---|---|
| 没看见与看见但误解混杂 | Video-TT §1/§3 | 控制输入的归因测量 |
| 视频事实与问句暗示竞争 | Video-TT五类问题 | 真实交互可靠性+修复 |
| 模型理由涉及未呈现的外部知识 | Social Genome | 证据归属/干预 |
| 长上下文改变模态利用，非单调收益 | MoMentS §5/附录 | 上下文选择与信息可用性 |
| 游戏状态可核验但隐藏状态不一定由输入可推断 | SocialReasonBench §3 | 可回答性审计；不是声称其全数据有问题 |
| 文化知识、识别与定位可能有不同瓶颈 | Cultural Moment Benchmark | 细分测量与迁移界限 |

**D1–D6**：固定官方split/帧复现 → 同视频缓存/版本化 → 记录读取/评分/解码痛点 → question-only、固定视觉、caption-only及一句指令恢复等标准测量 → 再选真实异常。保留成功案例和无差异结果，不能反复筛出“不会社会推理”的小切片。

## 3. 人类视觉相似性与模型表征（本轮新增 DL 备选）

**自然母问题：人觉得两幅图、两个动作“像”，究竟像在哪里；视觉模型保存的相似关系能否支持我们实际要做的比较、检索和理解？** 这里有明确人类实验、强开放encoder和真实下游，不需要先依赖语言prompt判断。物体、场景、姿态、关系、社会动作构成相邻但不同层次；先驻留公开静态资产，再决定是否延伸视频，不直接把所有模态揉成geometry大口袋。

### 热度卡

`density 'perceptual similarity|human.*similarity|behavioral alignment'`：NeurIPS2024 9、NeurIPS2025 21、CVPR2025 8、ICCV2025 11、ICML2026 8；ICLR2026 14/80=18%（全会27%）。宽切片混入语言/音频，故只是地图。`shapes`接收24篇中method67%、finding33%、benchmark62%；不据此判“分析论文能中”。

最新 [NeurIPS2026官方Downloads](https://neurips.cc/Downloads/2026)收录 BGS、Cosine is Human、What Sketches Tell Us about LVLMs 等标题；**本轮未取得单篇track/最终PDF，标目录收录而非声称Main接收**。BGS已有[2026年5月v2全文](https://arxiv.org/abs/2510.01502)。总体不是无大厂参与：AligNet有DeepMind；但公开模型的独立测量并不要求复制其预训练规模。

### 谱系卡

| 谱系 | 前提变化 | 当前开源基线 |
|---|---|---|
| pixel/LPIPS → [DreamSim](https://github.com/ssundaram21/dreamsim) | 低级失真距离不能代表布局、姿态、主体等中层相似性 | ensemble及单分支weights、NIGHTS、人票与完整eval |
| DreamSim指标 → [NeurIPS2024 perceptual alignment](https://proceedings.neurips.cc/paper_files/paper/2024/hash/63ba665e01f39233674426ba36d6e177-Abstract-Conference.html) | 改善人类相似性是否改变任务表征 | 已发布aligned与base，不必重新训练 |
| THINGS → [AligNet/Levels](https://github.com/google-deepmind/alignet) | 单一抽象层次不能代表多层概念结构 | 8种模型，各base/alignet/untransformed；Levels为人类评测，AligNet为模型伪标签，二者勿混 |
| [dynamic social vision（ICLR2025正式论文）](https://proceedings.iclr.cc/paper_files/paper/2025/file/b1bdb0f22c9748203c62f29aa297ac57-Paper-Conference.pdf) → [BGS](https://arxiv.org/abs/2510.01502) | 从静态物体到短动态互动，轻量人类监督改变关系结构 | 代码在，但视频与DeepJuice需联系作者；**非首个直接可跑入口** |

### 形态卡与ownership

可行形态：**成熟人类知觉范式+可复现的模型科学**；**表征几何改变的具体任务后果**；**小规模监督或training-free读出修复**。它比“内部特征奇怪”更自然，但只报告CKA/RSA差异仍不足以推出模型有人的概念。

| 近邻 | 已有内容 | 我们不能重复的headline |
|---|---|---|
| DreamSim | 人类中层相似性可改善感知距离 | 简单换encoder刷新NIGHTS |
| NeurIPS2024 perceptual alignment | 多下游收益与分类损失，patch/CLS、标签来源消融 | “人类监督可帮助一般视觉任务” |
| Nature2025 AligNet | 跨抽象层次对齐、公开训练后checkpoint | “层次不同/可以轻量对齐” |
| [Fine/coarse correspondence 2025](https://arxiv.org/abs/2505.16419) | 细/粗粒度比较，语言监督作用 | 只有另一种相似度/聚类metric |
| BGS | 短社会视频人类监督、文本蒸馏对照、OOD/任务保持 | “视觉模型不像人，但少量LoRA可变好” |
| Cosine is Human（NeurIPS2026目录） | 标题提示感知相似性可复现上限 | 未读全文，保留为优先ownership缺口，不能宣称已避开 |

### 立足点卡：已核到可下载入口

- DreamSim官方库有真实训练/评测/特征脚本及weights自动下载。可用冻结模型缓存embedding，再独立CPU统计。官方NIGHTS test：ensemble96.2%，DINO单分支94.8%，DINOv2单分支95.0%；这些是高度共识子集的成绩，不是“人类知觉总体已解决”。
- NIGHTS正式集20,019 triplets，完整解压58GB；100k未筛集289GB。先缓存官方test/小分片并保证固定抽样，**不用先复制289GB到所有节点**。本轮只核资源，未下载大数据、未跑模型。[数据说明](https://github.com/ssundaram21/dreamsim/tree/main/dataset)
- 本轮实际读取[JND CSV](https://data.csail.mit.edu/nights/jnd_votes.csv)与[未筛票CSV](https://data.csail.mit.edu/nights/nights_unfiltered/nights_raw.csv)开头并确认HTTP200（分别约201KB、16MB）；后者含左右票率/票数/图像路径。图片zip未完整下载验证。
- 官方`download_dataset.sh`含作者硬编码`/home/fus/data/`；复现必须修为任务专用缓存路径，不能盲跑。模型输入224×224，单卡feature extraction比长视频理解更适合弱I/O。
- AligNet发布[8模型×3版本下载索引](https://storage.googleapis.com/alignet/models/index.html)，本轮HTTP200确认。冻结比较可起步；不先训练10M伪标签或下载约150GB ImageNet。THINGS官方[代码](https://github.com/ViCCo-Group/THINGS-data)在，OSF/Levels数据页本轮抓取失败，不能说所有原始人票/图片已下载验证。
- BGS作者报告单A100一次ViT-B LoRA约2.5 GPU小时、整套约130 GPU小时，**不是我们的实测**；两项外部依赖（许可视频、未发布DeepJuice）使其暂不能当最先复现的系统。[代码说明](https://github.com/garciakathy/bgs-finetuning)

### 压力清单

| 压力 | 来源 | 可以做的研究动作 |
|---|---|---|
| 相似性随抽象层次变化 | AligNet/Levels | 区分对象层次，验证具体任务后果 |
| 感知收益伴随部分分类任务退化 | NeurIPS2024 alignment | 复现trade-off，再查损失了什么关系 |
| 只保留一致人票使人群变窄 | NIGHTS正式集与未筛集 | 人类噪声/合理分歧的测量审计 |
| 合成刺激与自然图像不等价 | NIGHTS数据局限、THINGS | 跨来源复核，不用新模型分数代替解释 |
| 文本caption可承载人的高阶比较 | BGS、AligNet | 视觉信息/语言标签/读出的分解与干预 |
| 语义几何与低层视觉相似性不是同一读数 | DreamSim与Fine/coarse correspondence | 读数有效性、对检索/选择的后果 |
| 公开代码仍缺私有依赖 | BGS README | 资产可行性修复；不是科学结果 |

**D1–D6**：DreamSim公开checkpoint+官方test复现 → 固定缓存与人票provenance → base/aligned/不同标签来源测量 → 人类分歧/刺激来源/任务指标的标准图谱 → 补NeurIPS2026 ownership → 再判断需要表征读出、微调还是新测量。不预设“对齐越强越不好”或“去掉语言监督更像人”。

## 4. 接收形态与near-miss校准：数量不足不硬凑

以下10篇构成跨三个领域的已接收参照，不能冒充每个领域都已深读10篇。数字仅在上文已核原文处使用；其余为语料标题/摘要级，未逐篇审稿核验。

| 论文 | 状态依据 | 形态与证据 |
|---|---|---|
| Label and Explanation Variation | ACL2026主会原页 | 分布+解释，多模型采样 |
| LiTEx | EMNLP2025主会原页/作者代码 | 解释taxonomy+人类多标注 |
| NUTMEG | EMNLP2025主会原页 | Bayesian方法+合成/真实标注 |
| On the Same Wavelength | EMNLP2025主会全文 | 人类任务+开放模型+RSA |
| Social Genome | EMNLP2025主会全文 | 细粒度人类证据trace |
| Video-TT | ICCV2025 CVF全文 | 控制帧+人机比较+自然误导 |
| Read the Room | 作者正式引用ICLR2026，语料Poster5.5 | benchmark+训练集+方法，完整复现资产待补 |
| When Does Perceptual Alignment Benefit… | NeurIPS2024主会官网 | 多encoder、多下游、对齐方式消融 |
| Modeling dynamic social vision highlights gaps… | ICLR2025正式proceedings已核；语料Poster7.0 | 已接收校准；全文未精读 |
| Diverging Preferences | ICML2025语料Poster；ICLR2025曾拒5.5 | 分类真实分歧+reward/judge后果；不得把拒稿当永久判决 |

相关 near-miss：ICLR2025 Diverging Preferences 5.5（后ICML接收）；ICLR2026 Aligning Video Models…4.0（BGS旧题名，后大修）；ICLR2025 Can LVLMs Describe Videos like Humans? 5.0；ICLR2026 SHREC 5.2；ICLR2025 Vinoground 5.75。**没有核到五篇高度同切片且高分的拒稿及完整评审原因**；不得用更远的图像生成/语音拒稿凑数，也不根据均分编造拒稿原因。

## 5. 搜索覆盖与缺口

已运行三个territory的`density`/`nearest`/`shapes`，另跑语用切片。旧corpus不覆盖NeurIPS2026；其结果不与最新目录直接相加。[PaperNotes](https://papernotes.org/)作发现入口，状态回原站；[Awesome Multimodal Modeling](https://github.com/OpenEnvision/Awesome-Multimodal-Modeling)和[DailyArXiv](https://github.com/zachysun/DailyArXiv)已检查，后者2026-10-02更新且每关键词仅保留100条，因此不能据当前快照推月度增长。

本轮推进的是SEARCH领域定位，无已有workbench C/I/P升级。没有做GPU实验、没有置信区间属于本仓库结果；所有论文数值是作者报告。下一人审要选的是愿意长期研究的自然对象，不是最喜欢的预期反常。
