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
