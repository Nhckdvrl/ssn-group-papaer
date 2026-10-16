# 文献总表：领域地图、阅读深度、近邻占有和下一步检查点

**2026-10-15**。此表是导航与防止重复劳动的主目录；不是谁最新谁第一的排行榜。核心15篇有单篇理解卡，其他作为筛读/待精读队列。卡片里“idea来源”只有显式作者材料才当事实。

## A. 当前15份独立论文阅读卡

| 类别 | 论文 / 年份 | 阅读范围 | 和我们最关键的相邻点 | 本地深读卡 |
|---|---|---|---|---|
| 经典形成 | Olsson et al. 2022, In-context Learning and Induction Heads | 经典机制与形成论证 | IH并非所有复杂ICL的同义词 | [OLSSON](papers/OLSSON_2022.md) |
| 训练期因果 | Singh et al. ICML 2024, What Needs to Go Right for an Induction Head? | 正文训练clamping、many-to-many与附录D | 多头形成和训练期中介已有人深入研究 | [SINGH](papers/SINGH_2024.md) |
| 多任务复用 | Merullo et al. ICLR 2024, Circuit Component Reuse Across Tasks | 正文路径干预、附录I/J/K | IOI↔CO复用及XL头不重合而role相似已存在 | [MERULLO](papers/MERULLO_2024.md) |
| 训练/规模 | Tigges et al. NeurIPS 2024, LLM Circuit Analyses Are Consistent Across Training and Scale | 正文核心现象/实验 | 算法类似、组件换人是强近邻 | [TIGGES](papers/TIGGES_2024.md) |
| 数据套件 | Magnusson et al. ICML 2025, DataDecide | 官方论文+本地使用审计 | 初始化×语料交叉源；本地1B有6个标签错误 | [DATADECIDE](papers/DATADECIDE_2025.md) |
| ICL机制 | Yin & Steinhardt ICML 2025, Which Attention Heads Matter for ICL? | 正文对照/发展假说、结合E01代码审计 | IH→FV发展是speculation非必要性因果结论 | [YIN](papers/YIN_2025.md) |
| 对应维度 | Trott 2025, Toward a Theory of Generalizability... | 概念框架、1-back实验 | relational/configurational普适性术语已有 | [TROTT](papers/TROTT_2025.md) |
| 模块解耦 | Dong et al. 2025, Is Random Attention Sufficient for Sequence Modeling? | Frozen-QK概念与核心实验 | Head本身参数固定但输入表示学习能改变功能 | [FROZEN_QK](papers/FROZEN_QK_2025.md) |
| 数据归因 | Chen, Luo & Pan ICML 2026, Mechanistic Data Attribution | 正文实验与附录F.2.2/G/K区分 | 定向数据变IH、多头接手已见F.2.2 | [MDA](papers/MDA_2026.md) |
| 跨训练稳定性 | Bali et al. arXiv 2026, Quantifying LLM Attention-Head Stability | §3方法、§4多个因素/ablation | best-match稳定性、优化器和功能重要性已有 | [BALI](papers/BALI_2026.md) |
| 跨模型定位 | Shao et al. arXiv 2026, Differentiable Faithfulness Alignment | 训练信号、六任务和留一任务 | 学映射+跨任务已有；问目标标注预算/路径预测 | [DFA](papers/DFA_2026.md) |
| 测量学 | Méloux et al. ICML 2026, MI as Statistical Estimation | 方差与离散抽取 | rank/统计不稳已有系统测量 | [MELOUX](papers/MELoux_2026.md) |
| 非唯一性 | Chen et al. ICML 2026, All Circuits Lead to Rome | 忠实性与多个稀疏电路 | faithful subcircuit不保证唯一解释 | [ALL_CIRCUITS](papers/ALL_CIRCUITS_2026.md) |
| 条件与粒度 | Bayat Makou et al. arXiv 2026, Many Circuits, One Mechanism | 75电路与条件间比较 | 电路图差异可不对应计算机制差异 | [MANY_CIRCUITS](papers/MANY_CIRCUITS_2026.md) |
| 抽取定义 | Sheng & Fu arXiv 2026, Circuit Claims Depend on What Is Extracted... | 抽取对象与比较层次 | 功能图相似性本身依赖粒度/抽取方法 | [SHENG](papers/SHENG_2026.md) |
| 重学 / 可逆性 | UNDO 2025；Siddiqui 2025；Deeb & Roger 2024；Jain 2024；Guo 2024 | 正文精读（10-17） | 遗忘普遍可逆；加噪 + 蒸馏抗重学（无机制）；Guo：改写入端 MLP 比改抽取头更难重学（组件层面最近邻） | [UNDO](papers/UNDO_LEE_2025.md) · [SIDDIQUI](papers/SIDDIQUI_2025.md) · [DEEB](papers/DEEB_ROGER_2024.md) · [JAIN](papers/JAIN_2024.md) · [GUO](papers/GUO_MECH_UNLEARNING_2024.md) · [总览](papers/RELEARNING_REVERSIBILITY_2024_2026.md) |
| 自修复 / 可塑性 | Rushing & Nanda ICML 2024；arXiv 2606.24752 | 正文精读（10-17） | 推理时 previous-token / induction 头不自修复；可塑性丧失有现象无机制、未测重置 | [RUSHING](papers/RUSHING_NANDA_2024.md) · [PLASTICITY](papers/PLASTICITY_SCALE_2026.md) |

**阅读范围诚实标记**：这些卡主要来自相关正文/特定附录的核读与当前workbench实验对照，未对15篇逐一完成全附录证明、软件逐函数审计或本地复现。使用“精读卡”是指带实验逻辑与批判性边界的独立阅读资产，不是上述深度均已完成。

## B. 次层最值得追的论文和原文入口

| 领域缺口 | 论文及原文 | 当前深度 | 下一次精读应该追什么 |
|---|---|---|---|
| IH何时形成 | [Aoyama et al. ICML 2026, Predicting the Emergence of Induction Heads](https://proceedings.mlr.press/v306/aoyama26a.html) | 会议摘要/原知识地图筛读 | 数据bigram统计、batch/context变化怎样预测形成；对E46/E62的最近边界 |
| FV计算机制 | [Todd et al. ICLR 2024, Function Vectors](https://arxiv.org/abs/2310.15213) | 原知识地图重点摘要/背景 | task vector对few-shot有何因果操纵，怎样定义可靠FV |
| 更复杂ICL | [Minegishi et al. ICML 2025, Beyond Induction Heads](https://proceedings.mlr.press/v267/minegishi25a.html) | 原知识地图摘要/背景 | 多阶段电路机制与IH→FV发展必要性的距离 |
| 层级共同原因 | [Rohweder et al. 2026, Hierarchical Latent Structures...](https://arxiv.org/html/2603.06592) | 关键假说/原知识地图筛读 | IH/FV共同来自数据层级的竞争解释 |
| FV跨格式边界 | [Opielka et al. ICLR 2026, Causality ≠ Invariance](https://proceedings.iclr.cc/paper_files/paper/2026/hash/86b3697c4eb7792c951831636bfdacd5-Abstract-Conference.html) | 摘要/背景 | 不能把任务向量在一个格式的因果效果推成抽象语义 |
| 训练数据/算法 | [Kawata et al. NeurIPS 2025, From Shortcut to Induction Head](https://proceedings.neurips.cc/paper_files/paper/2025/hash/6499b639e8a4b5c9a780d9b88c09722f-Abstract-Conference.html) | 核心问题筛读 | 数据多样性导致不同计算策略已被怎样识别 |
| 模型机制可推广性 | [Sun ACL 2025, Circuit Stability Characterizes Language Model Generalization](https://aclanthology.org/2025.acl-long.442/) | 原知识地图摘要 | 电路稳定性和OOD泛化已有哪种预测指标 |
| 因果抽象 | [Geiger et al. JMLR 2025, Causal Abstraction](https://www.jmlr.org/papers/v26/23-0058.html) | 方法背景 | 路径对应能否转成真正的因果中间变量映射 |
| 发育阶段 | Hoogland et al. TMLR 2025, Loss Landscape Degeneracy and Stagewise Development | 正文 | 小模型阶段与头分化，未解释谁专业化 | [HOOGLAND](papers/HOOGLAND_2025.md) |
| 头分化 | Wang et al. ICLR 2025, Refined LLC | 正文前半 | 头按发育曲线分型、multigram 跨层迁移 | [WANG_RLLC](papers/WANG_RLLC_2025.md) |
| 训练中干预结构 | Chen, …, Saphra ICLR 2024, Sudden Drops in the Loss | 正文与附录A–C | 抑制 / 放开 SAS 判前提与竞争；相变中干预最糟 | [CHEN_SAPHRA](papers/CHEN_SAPHRA_2024.md) |
| 暂时性与竞合 | Singh et al. 2023；Singh et al. 2025 Strategy Coopetition | 2023摘要；2025正文 | 能力起落由组件角色转换驱动（合成） | [SINGH_TRANSIENCE](papers/SINGH_TRANSIENCE_2023_2025.md) |
| 自然预训练发育 | Dahiya & Blondin 2026, Copying Before Suppression | 正文前半 | IOI 下探由复制头早于抑制头发育造成，未解释顺序 | [DAHIYA](papers/DAHIYA_2026.md) |
| 种子与涌现 | Zhao, …, Saphra 2026, Random Scaling of Emergent Capabilities | 正文 | 合成 / 模拟设置中能力双峰，无机制 | [ZHAO_SAPHRA](papers/ZHAO_SAPHRA_2026.md) |
| 种子与涌现 | Baherwani, …, Izmailov 2026, Emergent Capabilities Arise Randomly… | Pythia部分与摘要 | 初级能力随机时间出现，注意力模式突变 | [BAHERWANI](papers/BAHERWANI_2026.md) |
| 删除学习信号 | Şahin, …, Mueller 2026, In-Context Learning Without Copying | 正文 | 去掉 induction 可预测的损失后抽象 ICL 仍在 | [SAHIN_HAPAX](papers/SAHIN_HAPAX_2025.md) |
| 跨模型评测 | [MIB ICML 2025](https://proceedings.mlr.press/v267/mueller25a.html) | 基准背景 | 从图保真度到下游中介干预需要增补哪些读数 |
| 训练后组件 | [Prakash et al. ICLR 2024, Fine-Tuning Enhances Existing Mechanisms](https://arxiv.org/html/2402.14811) | 原知识地图相关章节 | E81的lineage稳定已被解释到哪里 |
| 训练后边变化 | [Wang et al. 2025, Towards Understanding Fine-Tuning Mechanisms via Circuit Analysis](https://arxiv.org/html/2502.11812) | 原知识地图相关章节 | 节点复用和关系边改写是否能区分 |
| 机制泛化最新 | [Can Circuit Alignment Predict OOD Generalization? 2026](https://arxiv.org/abs/2609.31996) | 摘要筛读；主要为视觉域 | 相似性可预测真实OOD结果还是只反映训练相关 |
| Early symmetry breaking | [Silverstein et al. 2026, Symmetry Breaking in Transformers](https://arxiv.org/html/2601.22257) | 设定背景 | 旋转/参数化对称不等于head permutation，先核对群 |
| 大规模梯度机制 | [Conmy et al. 2023, Towards Automated Circuit Discovery](https://arxiv.org/abs/2304.14997) | 方法背景 | edge/node抽取选择对我们的实际路径比较意味着什么 |

## C. 立刻值得从摘要升级到正文/代码的顺序

1. **Merullo作者代码 + Appendix J/K**，重现定义和下游路径而非仅以文中结论为背景；我们已读相应原文，代码级复现未做。
2. **MDA附录F.2.2及关键数据干预代码**，避免误以为多头接手未被做过；全文相关章节已核对，代码未审计。
3. **DFA目标函数与target-only信息预算**，检验source提供的额外信息是否真有意义；相关实验已阅读，需未来可重复的基线测试。
4. **Méloux + All Circuits + Many Circuits**，先解决因果估计对象和非唯一性，再讨论映射失败。
5. 如转向发展机制，再深读Aoyama、Minegishi、Rohweder和Singh，别把三个不同方向混在一起。

## D. 版本与声称novelty的纪律

同一论文arXiv更新或大会版本可能有新增附录；引用特定结果须附具体版本与位置。对于NeurIPS 2026等新论文，不能把检索到标题就写成“精读”，也不能没有确认主会轨道就标accepted。已发表、预印本与未知会议状态应分别标记。

已有的总体筛读/领域背景文件：[2026-10-15 文献地图](2026-10-15-literature-map.md)。领域核心主张与研究问题见[FIELD_GUIDE](FIELD_GUIDE.md)和[CONFLICT_MAP](syntheses/CONFLICT_MAP.md)。
