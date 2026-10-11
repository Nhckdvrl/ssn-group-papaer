# 视觉知觉、视频证据与人类判断：论文卡

核查日期：2026-10-03。SEARCH 阶段；所有数字为作者报告，未在本仓库复现。按用户最新纠正，先看导师偏好与自然问题，再结合兴趣：视觉知觉提供跨DL表征参考，视频暂非首推，语言分歧保留为测量方法与交互研究桥梁。领域提议、资源审计与接收形态见 [territory memo](../../../search/sasano-taste/JUDGMENT_VIDEO_TERRITORIES_2026-10-03.md)。

阅读边界：下列五篇均读正文方法、结果与局限；Video-TT、BGS、CAPO另核相关附录。不是“所有参考文献均全文精读”。idea 来源的 DOCUMENTED 只代表作者公开叙述；RECONSTRUCTED 是我们的研究逻辑重建，不声称知道作者实际灵感过程。

## 1. When Does Perceptual Alignment Benefit Vision Representations?（NeurIPS 2024 Main）`[全文 / 代码README]`

[正式接收页](https://proceedings.neurips.cc/paper_files/paper/2024/hash/63ba665e01f39233674426ba36d6e177-Abstract-Conference.html) · [全文](https://arxiv.org/html/2410.10817v1) · [代码与模型](https://github.com/ssundaram21/dreamsim)

1. **形态**：构念测量＋方法消融＋多任务迁移。它的贡献单位是“什么样的人类相似性，在什么任务中有用”，并非只把一个感知指标做得更准。
2. **背景压力**：DreamSim 已把人类中层相似性变成可训练距离；此前较少系统检验这种监督到底改变了哪些任务能力。分类、计数、实例检索并不要求同一种不变性。
3. **改变的前提**：从“和人更一致应普遍更好”转向按监督层次、token类型和下游任务检验收益。不是把人类相似性当通用真值。
4. **idea 来源**：DOCUMENTED：引言与§5从已有感知对齐的成功提出迁移范围问题。RECONSTRUCTED：在一个成熟方法后，先把其通常被合并的“好表征”拆成具体用途；这个动作适合我们，而“对齐有trade-off”本身已被占据。
5. **最近邻距离**：LPIPS/BAPPS研究局部失真；DreamSim/NIGHTS研究中层图像相似性；THINGS强调跨概念odd-one-out；DINOv2提供强通用表征。本文把这些监督来源放入相同训练/任务协议，增量在可比实验与下游后果，不在提出新的相似性定义。
6. **方法与证据**：对CLIP、DINO、DINOv2、SynCLR等做LoRA感知对齐；比较image-level与patch-level监督。用等规模BAPPS、THINGS及ImageNet构造对照。正文报告计数36种比较中35种改善，但标准自然图像分类不普遍改善；RAG结果以5个随机种子给置信区间。不要把这些比较当36个独立数据集。
7. **局限**：监督来源同时改变刺激分布与相似性层次，不能直接由消融推出唯一心理机制。下游探针可读出某信息，不等于模型实际采用同一种视觉策略。本文公开的机制解释是待检验假设。
8. **可迁移动作（我们的推论）**：先拿同架构base/aligned检查指标变化是否对应可理解的检索邻居变化，再要求这种变化影响一个实际选择；否则仅有embedding散点图不足以构成主要主张。
9. **对我们**：checkpoint、评测代码和NIGHTS入口成熟，冻结特征允许独立单卡提取＋CPU统计；完整数据58GB，先小分片与官方test。若驻留，先复核baseline，不能再把“人的监督有益但非万能”当新headline。

## 2. Behavioral Geometric Supervision Aligns Video Foundation Models with Human Social Perception（2026 v2；NeurIPS 2026目录收录，track未核）`[全文 / 附录 / 代码README]`

[版本与全文](https://arxiv.org/abs/2510.01502) · [v2 HTML](https://arxiv.org/html/2510.01502v2) · [代码](https://github.com/garciakathy/bgs-finetuning) · [官方目录](https://neurips.cc/Downloads/2026)

1. **形态**：人类行为监督＋轻量方法＋域外/任务保持验证。旧题名“Aligning Video Models…”在本地ICLR2026语料为reject、均分4.0；v2大幅增加实验，不能沿用旧评审判最终工作。
2. **背景压力**：静态人类相似性对齐有效，但动态社会判断还涉及关系与动作。更大、更强的视频模型并未自动复制人的比较结构。
3. **改变的前提**：社会知觉的不足未必只能靠更大预训练补齐；可用人的局部triplet判断与全局关系结构提供少量针对性监督。
4. **idea 来源**：DOCUMENTED：作者把静态行为对齐与其先前dynamic-social模型测量结合。RECONSTRUCTED：先确认现有表征的“缺了哪种关系”，再设计监督粒度，比从一个损失函数出发找用途更适合我们。这里的RSA是representational similarity analysis，与Wavelength的rational speech acts不同。
5. **最近邻距离**：DreamSim提供静态triplet对齐；VICE/AligNet使用人类概念结构；[Modeling dynamic social vision（ICLR2025）](https://proceedings.iclr.cc/paper_files/paper/2025/file/b1bdb0f22c9748203c62f29aa297ac57-Paper-Conference.pdf)主要测量模型与人的差距；caption表征给文本基线。BGS的增量是视频表征的行为监督、局部/全局组合与泛化验证，而非首次发现视觉模型不像人。
6. **方法与证据**：250段3秒视频，49,484个人类odd-one-out判断，245位参与者；按刺激划200/50 train/test。LoRA结合triplet和RSA；V-JEPA-2.1 distilled的平方Spearman读数约.058→.165，MPNet约.134；指标不是准确率。测试pair有缺测，noise ceiling按作者协议估计。报告单A100一次训练约2.5GPU小时、全工作约130GPU小时；非我方实测。
7. **局限**：单一视频域、特定人群、合并共识与稀疏关系。attention rollout是辅助图，不能单独证明因果机制。v1/v2与主表/paired-bootstrap的数值协议不同，不混用。
8. **可迁移动作（我们的推论）**：把“保留人的哪些关系”落到不同任务读数；比较caption、冻结视觉、轻量读出后再讨论训练。若文本胜过视觉，先检查文字标注额外提供了什么信息，不直接推导语言优于感知。
9. **对我们**：计算量看似合适，但代码依赖尚未发布的DeepJuice，视频需按许可联系作者；当前不能当立即可跑baseline。可先在DreamSim资产驻留，BGS用于视频延伸与ownership校准，不把联系作者的成功当既成事实。

## 3. Towards Video Thinking Test: A Holistic Benchmark for Advanced Video Reasoning and Understanding（ICCV 2025 Main）`[全文 / 表格 / 数据入口]`

[CVF正式论文](https://openaccess.thecvf.com/content/ICCV2025/html/Zhang_Towards_Video_Thinking_Test_A_Holistic_Benchmark_for_Advanced_Video_ICCV_2025_paper.html) · [全文](https://arxiv.org/html/2507.15028v1) · [数据](https://huggingface.co/datasets/lmms-eval/video-tt)

1. **形态**：benchmark＋混杂控制＋自然误导测量。其好处是提供可回答、可缓存的视频任务系统；不能因其benchmark形态就只考虑再做一个benchmark。
2. **背景压力**：长视频评测中，答错可能源于没有采到关键帧，也可能是采到了却不能整合。单个分数无法区分。
3. **改变的前提**：先把人类可回答的输入固定，再检验视频理解；同时区分原问题、改写、正确/错误暗示与多选形式。
4. **idea 来源**：DOCUMENTED：作者显式提出“看到了但不能理解”的测量需求，并用短视频与固定帧设计减少采样混杂。RECONSTRUCTED：强benchmark之后的可迁移价值是建立可靠输入控制，而不是预设所有剩余误差都属于reasoning。
5. **最近邻距离**：Video-MME与MVBench提供广视频测评；FunQA偏向有趣/反常片段；TemporalBench聚焦时间细节；Video-TT结合视觉和叙事复杂度并构造同题多形式。相邻Social Genome进一步提供证据trace；两者适合互补，但不能视为同一个数据协议。
6. **方法与主表**：1,000段短于65秒的视频、5,000道五种形式问题；80帧由人类验证可回答。Qwen2.5-VL-7B primary20.9%、MC39.9%；LLaVA-Video-7B primary21.4%、MC41.8%；人类primary84.3%、MC87.5%。open-ended采用Qwen2.5-72B评分，多选可精确计分。RB分母为primary正确题，不等同整体accuracy。
7. **局限**：选题用模型失败过滤，含对已有模型的选择偏差；人工删掉不一致问题会收窄自然歧义。80帧并不控制每个VLM的编码分辨率/视频token预算；文本judge也有额外误差。视频不使用音频，不能推出完整多模态社会认知结论。
8. **可迁移动作（我们的推论）**：先在同一视频固定帧下确认答案依赖哪些证据；与question-only、caption-only、同帧不同问法和一句指令恢复比较。只有存在稳定后果，才考虑信息选择或最小修复。
9. **对我们**：首跑官方多选split和本地7B可绕开大judge费用；80帧显存与解码I/O仍要实测。多卡优势是模型/条件独立运行、反复复核；不要起步就下载多份视频或全组合跑所有模型。

## 4. On the Same Wavelength: Evaluating Pragmatic Communication in LLMs（EMNLP 2025 Main）`[全文 / 附录 / 代码README]`

[正式论文](https://aclanthology.org/2025.emnlp-main.1008/) · [PDF](https://aclanthology.org/2025.emnlp-main.1008.pdf) · [代码](https://github.com/linlu-qiu/wavelength-eval)

1. **形态**：自然沟通游戏＋连续人类判断＋计算语用基线；这里只作互动agent的桥梁，纯语用不列用户首选主体。
2. **背景压力**：语用选择题通常要求单一正确答案，但听者对同一线索的理解可能是连续且合理多样的；“选对”无法覆盖沟通目标。
3. **改变的前提**：同时观察说者与听者、均值与分布，并与真实人类比较，而不是只让LM judge评另一LM的自然度。
4. **idea 来源**：DOCUMENTED：作者取Wavelength游戏的连续概念尺度，将其改为受控单轮沟通，并引入RSA。RECONSTRUCTED：有自然成功条件的小游戏把抽象“理解”变成可测量操作；相比先写一个心理能力标签，更容易驻留并发现真实系统问题。
5. **最近邻距离**：Hu等的语用选择题覆盖多现象；Lipkin等已有连续graded判断；Tsvilodub等与Spinoso-DiPiano等使用RSA理解；Jian/Narayanaswamy等使用指称游戏生成。本文把连续双角色任务、人群分布与开放模型放进同一协议。上述邻居按本文related work定位，未全部独立精读。
6. **方法与证据**：50组概念对、每组2个目标，共100题；708名参与者，每道comprehension题40次人类猜测。本地Llama/Gemma/Qwen与API模型比较direct logits、CoT和RSA。较强模型能追随人的中心趋势，但分布更窄；RSA尤其帮助production。这个headline已有ownership。
7. **局限**：单轮、刺激少、参与者地域与语言集中；与真实游戏中认识伙伴/持续适应不同。production最终需要人类判断，不能把“文本任务”自动视为零人工成本。
8. **可迁移动作（我们的推论）**：把模拟多样性与实际伙伴可预测性分开；温度采样不是人群。若延伸互动任务，要看伙伴反馈改变了什么以及是否提高共同目标完成率，而非只让分布更像现有样本。
9. **对我们**：公开数据、模型backend、缓存与RSA实现可从training-free起步；先复现100题及official指标，再决定是否进入持续互动。不要未经测量就宣称训练抹平个性或RL是必要后续。

## 5. CAPO（2026预印本；作者arXiv记录注明EMNLP 2026 Main接收）`[全文 / 方法附录 / 代码目录]`

[版本与接收声明](https://arxiv.org/abs/2605.28802) · [v2全文](https://arxiv.org/html/2605.28802v2) · [代码仓库](https://github.com/mainlp/CAPO)

1. **形态**：先建立行为可识别性，再做个体解释模拟；是测量＋方法论文。接收根据作者声明，尚未用正式Anthology页交叉核验。
2. **背景压力**：多标注研究知道人会分歧，但单个解释同时受输入内容与个人习惯影响。无法辨识稳定行为，就不能把一次回复叫“这个人的推理方式”。
3. **改变的前提**：测量单位从单item解释改为多item的行为组；输入内容残差化后再检验个人信号，然后训练模拟。
4. **idea 来源**：DOCUMENTED：论文先验证标注者特征可区分，再比较prompt、ICL、SFT及对比偏好学习。RECONSTRUCTED：先证明所要模仿的对象可识别，再选择优化目标。这是研究顺序上的可迁移价值，不是建议我们继续做传统NLI。
5. **最近邻距离**：VariErr提供分歧与误标；LiTEx细分相同标签下的解释；Value Profiles用文本profile表达差异；常规DPO提供偏好目标。CAPO把“同题其他合理标注者解释”用于区分目标标注者，并用group-level读数测量；与IDRR的个体不稳定结果须按任务和重复证据比较，不能只看标题判矛盾。
6. **方法与证据**：VariErr-NLI、R2释义两任务，分别4标注者，500题划300/100/100；Qwen3-4B与Llama3.2-3B。个体识别随group规模增加改善。Qwen在NLI中SFT→CAPO的label读数.638→.627、ImiScore .859→.888，说明模拟分数和任务正确率可不同向；不声称所有指标改善。
7. **局限**：少量固定标注者，样本外人群与跨任务身份未充分验证。分类器可能利用表面风格；解释可辨识也不等于忠实复现人的内部思考。ICL50例和微调成本不能与零示例条件混比。
8. **可迁移动作（我们的推论）**：把伙伴的稳定习惯、当前任务内容、随机误差拆开；在交互agent研究中也先问伙伴适应目标是否存在，再选择记忆或训练算法。
9. **对我们**：核查时仓库仅README/LICENSE，不能算完整可复现baseline。可先借公开VariErr/LiTEx做统计验证；该领域因用户偏好降为桥梁，不以“低算力”覆盖兴趣不匹配。

## 6. 补充资产与最新ownership（没有冒充全文精读）

| 来源 | 本轮证据级别 | 用途与限制 |
|---|---|---|
| [DreamSim/NIGHTS](https://github.com/ssundaram21/dreamsim) | README、脚本、CSV端点 | weights/eval齐；20,019 triplets；正式集58GB、100k未筛289GB；先核test下载与缓存，不盲跑硬编码作者目录 |
| [AligNet](https://github.com/google-deepmind/alignet)、[Nature2025论文](https://www.nature.com/articles/s41586-025-09631-6) | 原文摘要/资源说明、下载索引 | 8模型×base/alignet/untransformed可冻结比较；10M训练triplets为模型伪标签，不能称10M真实人类判断 |
| [Label and Explanation Variation](https://aclanthology.org/2026.acl-long.752/) | 主会原页/摘要 | 已有模型标签分布与解释同质性的ownership；PDF本轮受抓取限制，未标精读 |
| [Social Genome](https://aclanthology.org/2025.emnlp-main.1264/)、[代码](https://github.com/CMU-MultiComp-Lab/social-genome) | 原文方法摘要、README | 272视频、1,486人类trace；下载/解码成本明显，先确认公开视频仍可获取 |
| [SocialReasonBench](https://arxiv.org/abs/2608.30716) | 正文方法与局限 | Detroit游戏分支可核验反事实；评测是离线QA，不是交互agent；玩家多数选择不是道德真值 |
| Cosine is Human / What Sketches Tell Us about LVLMs | NeurIPS2026官方目录标题 | 留为最新ownership缺口；没有PDF不得由标题推导结论 |

后续进入任一领域前还需补：最新目录论文全文、选定baseline完整小样本下载与单卡profile、与具体研究对象对应的近邻表。上述缺口不自动关闭领域，也不由本卡替人决定是否开线。
