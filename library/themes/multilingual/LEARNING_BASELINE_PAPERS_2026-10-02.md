# 有效学习与训练选择：本轮论文卡

本轮按用户指定的一手论文读取关键方法、主实验和相应附录；不冒称逐页复现。
各项 idea 来源为 DOCUMENTED（作者明确描述），距离与对我们的推论为 RECONSTRUCTED。
不以会议类型推断科学有效性；投稿仍遵守主会限定。不把近邻当自动否决器。

## MuBench（ACL 2026；全文关键方法与受控实验附录）

[一手全文](https://aclanthology.org/2026.findings-acl.794.pdf)，重点 Appendix D/E，Figure 8。

1. 形态：多语言测量 + 受控训练。
2. 压力：语言比例与 parallel dose 混在现有模型比较里。
3. 改变前提：固定500B token，改变EN/ZH比例及10B/40B平行替换。
4. 来源：DOCUMENTED，基准用于分析训练数据因素。
5. 距离：相比MONOWEB自然双语删除、JGP英语占优和TransWebEdu翻译内容，增加平衡/不平衡与dose证据，不纯粹隔离pairing。
6. 方法：1.2B scratch，翻译EN并COMET>.8过滤，等量移除两语mono以保预算；250K tokenizer。
7. 强弱：balanced中文HellaSwag45.99→48.14，对简单saturation预测反压力；质量/内容替换仍混杂，适配种子信息未核对。
8. 动作：预算守恒和多能力非对称比较，不靠跨论文参数量贴标签。
9. 对我们：撤回领先解释，而非宣布一般acquisition交互不存在；不复刻昂贵500B训练。

## LINK（arXiv 2605.23885v1；全文§3–6及模型规模附录）

[一手全文](https://arxiv.org/html/2605.23885v1)。

1. 形态：廉价数据方法 + 多规模验证。
2. 压力：目标语数据缺乏，完整翻译与额外阶段昂贵。
3. 前提：不需流畅codeswitch文本，词典共现可以提供信号。
4. 来源：DOCUMENTED，词汇替换预算与源语代价。
5. 距离：相比PreAlign初始化、False Friends token-ID控制和TransWebEdu全文翻译，是输入数据处理；非领域对照也已经存在。
6. 方法：137M–2.7B、8语，uniform/domain/non-domain；替换量和词典覆盖控制。
7. 强弱：非领域替换量95.5% vs领域4.5%，不能将胜出解释成同dose的领域无关性；真实低资源效果不均一。
8. 动作：一起测目标收益、英语损失与廉价竞争方法。
9. 对我们：词汇桥接/领域外迁移已是baseline；增量应是实际后续学习失败及可操作干预，不是重命名桥接。

## PreAlign（arXiv 2407.16222v3；复读§3–6与评测定义）

[一手全文](https://arxiv.org/html/2407.16222v3)。

1. 形态：训练时机方法 + 受控合成/真实语言。
2. 压力：自发对齐早期不足，后期再对齐可能错过学习。
3. 前提：早建立并持续维护词对应。
4. 来源：DOCUMENTED，初始化contrastive与input-only CS分拆。
5. 距离：相比联合mono、训练中CS和后训练对齐，控制时机；区别LM、英语任务微调后的XNLI迁移和新知识应用。
6. 方法：En-Clone与ZH/DE/AR/RU，150M/400M/1.3B；词对所有层contrastive+LM，维护CS5%。
7. 强弱：synthetic perfect-alignment上界与真实语言差异明确；知识triples简单，不能泛化所有reasoning。
8. 动作：先正常任务学习，分拆知识应用与已有能力调用。
9. 对我们：source task fine-tuning是标准有效baseline；“alignment时机/新知识迁移”本身不新。

## AdaXEval（arXiv 2510.12115v1；全文§2–5关键方法）

[一手预印本](https://arxiv.org/html/2510.12115v1)；版本限v1，非对其他版本或会议全文的等同核对。

1. 形态：训练覆盖绑定的测量 + domain adaptation分析。
2. 压力：通用评测与实际学习内容不匹配。
3. 前提：从同一双语领域语料构造记忆、改写、跨语应用测量。
4. 来源：DOCUMENTED，知识注入CK与不含评测新知识的桥接CT分离。
5. 距离：相比PreAlign简单人工facts、LINK词替换和MONOWEB预训练删除，研究真实医学适配。
6. 方法：llm-jp-3-13B，EN/JA，0.5B CK+0.5B CT，translation/romanization与领域对照。
7. 强弱：已有acquired/forgotten分析；mono0.5B与混合1B预算不完全相同；J-STAGE授权限制资产公开。
8. 动作：追踪新增与遗忘，不以平均净收益解释全部机制。
9. 对我们：分离桥接与新知识不是新idea；需要有实践后果的具体瓶颈，不直接搬医学生成probe。

## NiuTrans.LMT（arXiv 2511.07003v2；全文§2–5与资产介绍）

[一手全文](https://arxiv.org/html/2511.07003v2)。

1. 形态：真实训练失败 + 数据修复 + 系统。
2. 压力：多路parallel对称SFT后反向翻译下降。
3. 前提：多语监督的复用结构不总有利。
4. 来源：DOCUMENTED，从强baseline方向性退步出发。
5. 距离：相比普通CPT、多路平行训练和direction-aware模型方法，分析重复目标与数据结构并给数据级修复。
6. 方法：Qwen3 .6–8B、Llama3.1/Gemma2；disjoint replacement、reverse retention、语言数；SD默认5%，PMP辅助平行上下文。
7. 强弱：跨规模/家族与实际翻译后果；disjoint源不同，不能无条件当纯结构识别。
8. 动作：明确失败→关键解释→可用修复，不从陌生probe倒推重要性。
9. 对我们：学形成idea的过程，不把已知方向退化移植成新题；先恢复自己的学习baseline。

## 本轮定位与证据缺口

没有宣告新ownership或完整论文故事。E01补的是过去未建立的学习substrate。
venue corpus nearest 首次因缓存缺失失败，随后fetch/build重建65716条记录并完成查询。
主旨查询：`multilingual pretraining bilingual data downstream task learning cross lingual transfer adaptation`。
近邻包含MONOWEB、PreAlign、Cross-lingual In-Context Pre-training、Active Forgetting、ATLAS；
BM25分数仅检索距离，不是新颖性判断。缺失年度列表明确保留fetch的404记录，不声称全年完备。
Standard-vs-Split/ParaRater完整方法仍未取得，不能依摘要宣布空间穷尽。

## 本轮扩展近邻（非新主线）

**Active Forgetting，EMNLP2025**：[官方全文](https://aclanthology.org/2025.emnlp-main.120.pdf)，已读§3–6。
形态是语言适配的失败+预训练修复；DOCUMENTED来源是新语言tokenizer/embedding适配损害其他语言。
与PreAlign、普通vocab expansion和encoder active forgetting相比，改成decoder预训练时周期重置embedding，
再新增词表、冻transformer适配新embedding/LM head，最后English-only OpenOrca SFT。
它已把预训练选择接到后续学习与旧语言代价，不是只做静态几何。不能把“预训练影响learnability”当新主张。
方法不能直接作用于已训好checkpoint；我们的MONOWEB数据干预与它的参数初始化不同，增量需实际瓶颈与干预后果。
abstract说三个尺寸，但结果表含四个尺寸；种子和实现细节未完整核对，不由摘要补全。

**ATLAS，ICLR2026**：[官方全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/35c26a810471039b3427e524565cbef9-Paper-Conference.pdf)，已读§2–5与模型对象。
大规模controlled training支撑语言比例/重复/规模与迁移效益的预算选择。
其finetuning指从multilingual Unimax checkpoint继续单语言LM训练，不等同E01监督任务学习→跨语测试。
可迁移动作是将控制变量接到明确的训练选择；不要再把泛泛的resource correlation/scaling当C的贡献。
未逐页完成后半部分方法/附录阅读，不能冒称完整复现。

**Building Multilingual Bridges，2026-09预印本**：[一手全文](https://arxiv.org/html/2609.10445v1)，已读§2、§5.2–5.4、附录G开头，非全篇审计。
形态：Tiny Aya 3.35B的数据混合与泛化；DOCUMENTED来源是英语中心reasoning与目标语输出不一致。
方法：English reasoning、translated multilingual reasoning、multilingual non-reasoning三类监督；matched-step比例扫描，另比joint/sequential/merge。
距离与ownership：已有廉价non-reasoning监督促进未监督语言行为迁移的证据；这不是C的新主张。
强弱：真实可训练模型、held-out languages；matched steps不自动等于matched tokens/content，reasoning语言率不等于正确率。
动作：学习它把数据选择接到真实训练结果的过程；不据此把C转为reasoning-language新线。

**Leitner-Guided Memory Replay，NAACL2024**：[一手全文](https://aclanthology.org/2024.naacl-long.432.pdf)，已读§2–4及附录A.1/A.3。
形态：跨语言持续任务学习的失败+replay改进；DOCUMENTED来源是固定buffer如何保留有效旧样本。
方法：mBERT、四语言平衡顺序、MTOP/MultiATIS++/TyDiQA；正确/错误更新1–5技能等级，对比easy/hard/random/balanced。
ownership：学习难度驱动replay与遗忘/最终能力权衡已有方法；不是泛泛“桥接可复用”的空白。
强弱：多个任务和顺序，报告额外评估成本；单seed42，不能把语言顺序重复当参数seed重复。
动作：后续若研究可复用旧数据，需要区分保任务标签与保跨语言接口，而非只胜过无replay。

**XLDA，2019预印本**：[一手全文](https://arxiv.org/html/1905.11471v1)，已读§3–4.7。
形态：监督任务的翻译augmentation；DOCUMENTED来源是语言间监督与泛化不均衡。
方法：翻译premise/hypothesis中的一个输入，对比EN-only和同语言translated训练；mBERT与使用冻结BERT embedding的LSTM，不把后者说成全部从零。NLI/QA均有实验。
ownership：任务输入的跨语混合与同语言翻译不是同一个baseline；simple translated-task gain不是新贡献。
强弱：跨语言/任务及QA恢复span处理；greedy augmentor按validation选择，不等于无选择的多seed重复。
对E02：我们先在无标签CPT中控制内容覆盖/conditioning，再统一EN任务学习，不是XLDA本身；若发展成方法，仍须与有效translate-train/XLDA比较，不能只胜EN-only。

E02定位检索已运行：`reusable bilingual bridge same content cross lingual task learning translated data document isolation`。
最近包括Cross-lingual In-Context Pre-training、MONOWEB、Cross-Lingual Continued Instruction Tuning；检索分数不是ownership裁决。

## 持续探索补查：ParaRater公开实现（非论文全文）

[作者实现](https://github.com/aialt/pararater)，本次核对commit `a96a55b6790d5041a383d528420b646c5e17adc9` 的 `pararater.py` 参数、模型构造、inner loss、meta-gradient和训练循环。
实现以从config初始化的causal LM训练主模型、BERT标量rater加权每样本token平均NLL，通过validation LM loss对短inner-loop求meta-gradient来更新rater。
公开工具要求text parquet，不提供监督任务标签或后续任务适配循环；这不证明论文没做那些实验，完整两阶段过滤和主结果仍待全文核对。
作者[ParaCore资产](https://huggingface.co/datasets/pararater/paracore)说明Common Crawl英语经Qwen3-8B翻译，每语言约1B token。
DOCUMENTED来源：不只按一般质量选译料，而按目标语数据效益识别有价值的parallel；“选有用桥接”显然不是我们的空白。
RECONSTRUCTED距离：E02不训练rater，检查一次CPT的内容覆盖/conditioning如何影响后续统一任务学习；若以后提出选择方法，需要直接比较当前语言建模效益与后续学习效益，不能只说pairing有效。

Standard-vs-Split的forum、hash PDF及API本次再次受验证/403限制；搜索索引只取到匿名under-review摘要，不等同全文阅读或接收确认。作者博士论文公开入口也返回403。无精确方法证据就保留缺口；不将此作为自动关线理由。

## CrossIC-PT（EMNLP2025；已读§3–5、Appendix A与任务表）

[官方全文](https://aclanthology.org/2025.emnlp-main.1380.pdf)。DOCUMENTED来源是严格bitext域/量有限；改用同entity维基与检索语义相关文本提供上下文。分段串接EN→目标文档、SPLIT-aware窗口保完整；LoRA rank64/alpha128/dropout.05，一epoch；同源不串接Mix-PT与mono目标是重要对照。
它已经控制部分文本来源并比较随机配对、方向、语义检索，不能把“非精确翻译也可桥接”当我们的新idea。Appendix A是冻结的0/5/8-shot评测，不是后续统一任务学习；Qwen1.5B按validation LM loss选checkpoint。LEIA有三seed不代表所有对比三seed；p>0.1不能证明英语收益/遗忘等价。
RECONSTRUCTED距离：E02/E04操纵后续监督内容覆盖、文档条件连接，再测实际学习全曲线；只有带来不同训练选择，才可能有实质增量。不要把该距离本身写成贡献。跨语CPT方法发展时应比较同源Mix-PT/预算及有效监督augmentation，而非只比base。

## X-CIT（ACL2025；已读§3–5.1、训练与任务表）

[官方全文](https://aclanthology.org/2025.acl-long.1121.pdf)。DOCUMENTED来源是英语SFT具跨语能力但不稳定输出目标语言、普通mixed translate-train未利用对应；英语Alpaca52K先SFT，再10%目标监督与双轮目标→EN instruction/response→目标answer，另用SPL。它已有顺序/混合、移除mono/chat、CrossAlpaca与PLUG对照，不应将“先任务学习再维护语言接口”重命名为新idea。
五语言、Llama2-7B、不同模型/量扩展；三次10%抽样不等于三个预训练seed。相同epoch不等于相同实际样本/监督token，SPL额外8epoch结果须和主表区分。en_SFT某些知识答案标为English，年份任务高分不能自动说明目标语言语义调用；输出语言和准确率应分开。
RECONSTRUCTED距离：我们的当前干预是无标签CPT新覆盖/内容不重叠复用之后统一新任务学习，不是翻译监督双轮chat；若形成方法，应把有标签translate-train与桥接复用成本/收益一起比较，而不因控制更细就预写novelty。

## MT能否连接预训练与迁移（LREC-COLING2024）

[官方全文](https://aclanthology.org/2024.lrec-main.250.pdf)，已读§2–3与主结果表。
DOCUMENTED来源：翻译应提供跨语表示，但是否帮助后续任务学习并不明确。比较mBART与其公开MT继续训练版本，统一12层encoder、英语任务微调十epoch，再评估XGLUE八任务；mBART XNLI67.6，m2o65.9、o2m48.1、m2m60.2。
强弱：实际任务学习而非冻结probe；不是同内容/等预算随机干预，作者明确不处理遗忘。CKA未建立强性能联系；权重奇异值/输出separability解释是分析假设，不是被救援干预识别的机制。
ownership：“翻译更好不代表后续迁移更好”已有直接先例。RECONSTRUCTED距离：E04在同一causal LM起点分离内容覆盖与条件连接，完整源/目标学习曲线；该控制本身尚非论文贡献，也不能把encoder结果直接泛化到生成式LM。

## 成本与有效监督（2021预印本）

[一手全文](https://arxiv.org/html/2105.06813v2)，已读§3–5。
DOCUMENTED来源：transfer方法选择还受一次翻译成本、部署延迟影响；对比zero-shot/translate-train/translate-infer，QA、NLI与ranking。QA标记answer边界再译，约20%样本因边界丢失被删；QA翻译监督不及零样本，NLI/ranking则受益。
强弱：把实际成本接回任务选择；QA小测试集、任务/模型/内容差异，不是同信息量的预算因果控制。历史API/GPU价格不是当前报价。
动作：E04若有有效训练后果，再接同预算有效translate-train；必须报告目标答案恢复/丢失率，不能把译料监督失败误归为跨语言学习限制。“成本敏感的训练选择”本身已有ownership。

## EMMA-500 Llama3（arXiv2506.00469v2）

[一手全文](https://arxiv.org/html/2506.00469v2)，已读§2.2–3.3；不是全部附录审计。
DOCUMENTED来源：500语言CPT中是否加入双语数据；Llama3/3.1-8B公开Mono/Bi，十句pair拼文档并标语言。Mono419B token/25K步，Bi671B/40K步，warmup亦不同；不是等预算同文本pairing识别。
§3.3 Model Adaptability实际比较CPT相对base的静态基准变化，不是统一后续新任务学习曲线。双语收益随base/任务不同；不能重新贴成acquisition-saturation证据。
动作与距离：这是可扩到更强、多语released family的资产，不需复刻其800K GPU小时训练；但不应盲目把8B四模型全参数训练铺开。先由当前实际训练决策的有效后果决定扩展对象，再选择单卡可承载的适配与源语gate。无新ownership升级。

## AAdaM：cross-lingual TAPT先例（SemEval2024）

[官方全文](https://aclanthology.org/2024.semeval-1.114.pdf)，已读§3.1–3.4、主对照表与limitations。
DOCUMENTED来源：低资源STR标签不足和任务域失配；译SemRel/STS-B监督warmup，再原始标签学习，目标语无标签TAPT；MAD-X语言adapter固定、任务adapter学习后替换语言adapter迁移。它已研究TAPT/翻译augmentation/full vs adapter，不可将“新任务无标签文本有用”作为我们的新发现。
强弱：有效下游训练与多语对照，TAPT并非所有条件收益一致；用目标dev选source有真实zero-shot限制，作者明确承认。RECONSTRUCTED距离：E04控制same-origin conditioning和新内容/不重叠同域复用，若有后果还须分离一般TAPT与跨语言收益，不以控制更细自称novelty。

## Copy First, Translate Later（arXiv2604.17633v2）

[一手全文](https://arxiv.org/html/2604.17633v2)，本次已读§3–8及limitations；KEY_PAPERS已有登记，不是新检索出的无人区。
DOCUMENTED来源：终点分析难以解释跨语机制形成；九语1.7B scratch、185M-token间隔200 checkpoints，MultiBLiMP及125 concepts/72方向WLT；无定向parallel目标，但不证明随机web绝无自然双语。参数缩放/跨checkpoint层交换提供干预，最终bottom+top能提前调用中间层WLT机制。
边界：WLT最终32.1%，synonym覆盖/提示效应/未收敛与单family；phase边界是dataset-specific行为定义，ExPLAIND归因本身不是训练数据因果效果。不是源语任务训练后的新学习迁移，也不是parallel收益regime证明。
动作：将有用接口与内部机制拆开，但不要从当前有效QA学习退回弱WLT冻结终点寻小信号；若真实适配代价出现，再做对训练救援有信息量的部件干预，不单为画机制图。

## General Forgetting Mitigation Does Not Preserve MT-Specific IF（arXiv2609.28395v1）

[一手全文](https://arxiv.org/html/2609.28395v1)，已读§3–6、附录训练设置；2026-09-23预印本，接收状态未核对。
DOCUMENTED来源：MT适配后，通用保留指标能否代表翻译中的具体控制？1B筛选多类遗忘缓解，再在8B双向Arabic/Spanish MT检验formality/gender/length。EWC在通用指标保留强，但具体控制接近普通SFT；对应控制任务混合才有效，换训练prompt后收益不可靠。
边界：阶段间模型、方向与数据来源同时变化；方法筛选按目标MT+通用分数，不是我们的source-only protocol；formality仅matched hypotheses计算。不能把作者的anchor解释当成已识别电路机制。
RECONSTRUCTED距离：E06是QA学习后已有MT保持，干预方向不同；但“通用指标保留不保证接口保留”已有人直接研究。若E06失败，须有训练救援及实际预算后果，不能仅换任务发布同一句话。

## Conditions for Catastrophic Forgetting in Multilingual Translation（arXiv2510.19546v1）

[一手全文](https://arxiv.org/html/2510.19546v1)，已读§3–4设置与gain-forgetting；全文其余机制/附录尚未完整核对。MRL2025，不当作主会尺度证明。
DOCUMENTED来源：旧MT模型与LLM的遗忘报道不一致，比较模型规模、instruction interface、数据量及LoRA。117K与54M设置数据领域/语言也不同，另有大数据的subsample系列；seen pair/unseen source/unseen target分开，COMET辅以BLEU/LID。
边界：作者明确不同family不是纯架构控制；训练集规模变化不能全归因token量；主要任务仍是MT，不是QA学习后翻译保持。LoRA不自动保证保持、语言指令重要已有ownership，不是潜在新中心主张。

## Overcoming Catastrophic Forgetting in Zero-Shot Cross-Lingual Generation（EMNLP2022）

[一手全文](https://aclanthology.org/2022.emnlp-main.630.pdf)，已读§2–3及方法图，未冒称独立复现。
DOCUMENTED来源：英语摘要适配后非英语摘要输出退化；mT5多规模、full/prompt tuning、translate-train/test、监督参照；语言识别与学习曲线区分质量及错误输出语言。mix无标签mC4与factorized task/language prompts缓解，较强source学习也可能增加非英语退化。
边界：prompt tuning另有100K prefix-LM adaptation；target-language dev选择及各方法额外预训练成本不能忽略；中间适配不保证收益。RECONSTRUCTED距离：已有语言保持/新任务学习的实际训练问题与方法，E04/E06不以“首次研究adaptation”定位。我们的extractive QA输出负担较轻，不能外推到摘要，也不能以QA成功否定其观察。

## Domain adapted MT: What does catastrophic forgetting forget and why?（EMNLP2024）

[一手全文](https://aclanthology.org/2024.emnlp-main.704.pdf)，已读§2–4的操作性读数、数据控制及Minimal Mix-in。
DOCUMENTED来源：BLEU下降掩盖词汇替换，先定位正确词丢失及替代，再检查适配数据规模/长度/质量/词表覆盖。八domain、DE→EN/EN→JA，原模型各一个，固定20K更新；target词汇覆盖选择少量generic译对，多个domain接近大量随机replay的保持效果。
边界：相关性不等于所有数据特征独立识别；20K更新非等独立信息量；token forgetting定义刻意不奖励新获得正确词，不能当总能力分数。最小mix与随机mix的例数/信息量不同，非任意LLM任务适配的定理。
RECONSTRUCTED距离：E06整句照抄是具体可核对后果，但不能由此认定其原因就是copy技能过度泛化；目标词汇覆盖/语言输出偏置也是竞争解释。E07译料监督参照很重要：若仅补目标语任务与词汇即可恢复，不能把parallel correspondence写成必需；若不恢复，才值得设计同内容coupling训练干预。不在读数之前预设机制。

## Toward Robust Multilingual Adaptation / LiRA（ICML2026）

[官方会议论文](https://proceedings.mlr.press/v306/li26jh.html)，取得官方PDF，已读§3–5、附录C/D方法和参数扩容对照；未独立复现。arXiv v3与正式PDF的附录并非完全相同，以正式PDF为准。
DOCUMENTED来源：翻译噪声与双编码路径失配影响低资源检索/推理。Arca以翻译候选critic和actor选择配合feature anchoring；LaSR融合多语与英语编码，队列稳定排序/检索目标。正式PDF附表17有相同扩容但不加LiRA训练目标的对照，不能误称作者完全没有扩容对照。
边界：这是含译者/critic/编码器的模块化系统，不是同一个LM的训练数据删除及后续任务适配保持；理论是在语义参照和局部稳定假设下的误差界，不识别我们的学习因果量。原文§5.1称4卡服务器，附表9部分任务列8卡，执行规模需核实，不能直接照搬其预算。离线翻译复用与在线候选计算成本须分开。
RECONSTRUCTED距离：桥接与翻译噪声不是新概念，低资源适配也不是无人区。若P05发展，只能以可靠实际学习瓶颈、同内容训练干预和优于标准方法的决策后果定位；不能把静态跨语representation改善重命名为新故事。

## 本次定位边界（非科学判决）

venue corpus两次nearest已运行，返回MONOWEB/JGP、Domain adapted MT、LiRA和FOREVER，也有无关检索/视觉条目；BM25相似度不是ownership裁决。保持/桥接/译料监督的母问题已有强ownership，compression risk高。E04小终点差不作为贡献；P05是实际QA学习后的输出代价，尚需种子重复、保持干预和标准译监督/replay竞争方法。不能凭相关工作关闭领域，也不能先命名预期结果。

## FOREVER（ACL2026主会）

[官方全文](https://aclanthology.org/2026.acl-long.1144.pdf)，已读§2–3方法/实验及附录H训练设置，取得PDF；没有复现。
DOCUMENTED来源：固定训练step不代表相同模型变化，以实际LoRA参数更新范数累计model time触发旧任务replay；近期更新强度决定对上一任务快照的正则强度。0.6B–13B、三类CL benchmark、2%旧数据buffer及三个独立run，已有真正训练救援而非仅诊断。
边界：同架构/config/buffer不自动等更新或计算预算；每新任务10 epoch、每次触发额外旧任务2 epoch，比较时须报告触发数和实际replay token。对象为已监督旧任务，不是未监督预训练翻译接口，也未识别正确双语对应的必要性。
RECONSTRUCTED距离：通用自适应replay timing/intensity已有ownership；不能把P05后任意混合/replay命名为新方法。我们优先需要同内容/目标语言暴露的最小训练对照及标准方法成本参照，而不是先造复杂scheduler。

## Parameter Alignment Mitigates Catastrophic Forgetting in Multilingual Expert Language Models（arXiv2606.00284v1）

[一手全文](https://arxiv.org/html/2606.00284)，已读§2–4及附录A.2/A.3/A.5；接收状态未核对，没有复现。
DOCUMENTED来源：Gemma3-4B语言family CPT中获取语言与保持旧能力冲突，比较层冻结、L2-SP、训练后还原和模型混合；固定中层边界，插值干预检验不同能力的层级敏感性。理解与翻译的敏感层不一样，并给出实际部署取舍。
边界：dense25B与单family5B、学习率/early stopping不同，family策略间更可比较；single seed42，不能当普遍精确层级分工。FLORES统一post-truncation不复现原Gemma报告；作者也承认其协议边界。中层还原不等于删掉/恢复某项语义知识的唯一解释。
RECONSTRUCTED距离：能力分解与训练保持均有直接近邻。E10/E09须回答实际数据选择是否改善保持，不以任务名不同抢ownership；简单增加层还原小网格也不足以构成新idea。

## Exploring Two-Phase Continual Instruction Fine-tuning（ACL2026 Findings；仅近邻定位，不作为投稿目标）

[官方全文](https://aclanthology.org/2026.findings-acl.1595.pdf)，已读§3–5训练/数据及replay细节；附录预算尚未完整核对，没有复现。
DOCUMENTED来源：英文IFT后再多语IFT，希望同时保持英文和增加多语收益；阶段数据风格/内容相近时保持更好，另比较混合、生成replay、英文replay、层冻结与LoRA。生成replay使用第一阶段模型对第二阶段英文对应指令作答，5%/10%；不是简单随机复制旧数据。
边界：相似数据也同时改变任务/质量，DES/参数差与保持的关系不是独立操纵纯相似度的因果证据；声称约同step不等于逐语token/独立内容等预算。多类能力平均可能掩盖代价。
RECONSTRUCTED距离：时序与内容一致性已有ownership，E04重复语义内容的正收益即使出现也不是自动新发现。我们应比较明确预算下的实际学习和旧接口保持，并用同文本干预识别增量，而不是把correlation命名为新regime。
