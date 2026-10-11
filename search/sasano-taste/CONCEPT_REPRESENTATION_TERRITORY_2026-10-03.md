# Territory：模型怎样组织概念与知识

2026-10-03，Sasano-first候选；尚未开workbench。主会校准以ICLR/ICML/NeurIPS为主，语言理解证据可面向ACL/EMNLP。

**自然问题：模型知道很多事实，它用什么方式把这些事实组织成“同一类东西”“具有某种性质”“符合某组规则”？这种组织什么时候支持实际判断？** 这里研究类别、属性、概念组合与任务所需的表示单位。与上下文binding候选的区别是：后者着重一次输入里的具体人/物/关系及更新，本领域着重概念结构、抽象层次及来源。两者相邻，可以择一驻留，不建议同时新开两线。

## 热度卡

`density 'concept geometry|hierarchical concept|concept representation|belief state geometry|lattice representation'`：ICLR2026接收10/19、ICML2026为5、NeurIPS2025为3。人工抽查含医疗、身份、视觉等误命中，19分母很小；**53%不能当本领域接受概率**。`shapes`有分数accepted14，method64%、finding43%、benchmark50%，多标签重叠。该具体谱系规模可读、问题持续，但泛表征/SAE领域并不冷门。

## 谱系与近期论文

| 链条 | 改变的前提与我们应学的动作 |
|---|---|
| Linear Representation Hypothesis → [Categorical/Hierarchical Geometry，ICLR2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/be7430d22a4dae8516894e32f2fcc6db-Abstract-Conference.html) → [Lattice，ICLR2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/208853db0e806d03f6be769a3fae1ecd-Abstract-Conference.html) | 从二元属性方向，到类别与层级，再到概念交并和共享属性；没有停在一张聚类图 |
| 分布语义/word2vec → [Hierarchical Concept Geometry from Word Co-occurrence，2026](https://arxiv.org/abs/2605.23821) | 新论文从词共现预测层级几何，提醒不要把几何形状直接解释成专门的推理功能；NeurIPS2026目录已见，main未核 |
| Othello/chess表示 → [Structured World Models，2026](https://arxiv.org/abs/2605.18847) | Sudoku表示按行/列/宫约束组织，显示研究者选的分析单位可能不是模型使用的单位；目录收录，main未核 |
| [Belief State Geometry，NeurIPS2024](https://papers.nips.cc/paper/2024/file/8936fa1691764912d9519e1b5673ea66-Paper-Conference.pdf) → [LLMs Develop Belief State Geometry In-Context，2026-09](https://arxiv.org/abs/2609.17376) | 从专门训练的小模型到冻结开放LLM；最新版已有替代解释、patching/steering，不能再把“probe不等于使用”当新发现 |
| 人类概念特征norms → [Grounding Gap，2026](https://arxiv.org/abs/2605.08837) | 概念属性的生成与评分需要区分；不是只有WordNet树可作为理解标准。目录收录；行为范式与内部表示仍是不同证据 |

前两条是更贴近当前用户/Sasano的主入口；Sudoku/HMM是解释方法与任务表示的邻接参照，不要求把论文限定成一个小谜题，也不转向时间序列预测应用。

## 立足点卡

**推荐先复现ICLR2025的公开概念层级分析。** [官方仓库](https://github.com/KihoPark/LLM_Categorical_Hierarchical_Representations)有Gemma2B/Llama3-8B、WordNet数据生成、noun/verb分析、intervention与几何度量对照；基础模型冻结，向量缓存后可反复分析。`animals.json`/`plants.json`为既有GPT4生成词集，不能称纯人工数据，也无需重付API生成。需核token覆盖、词形处理和度量变换，不能直接把所有词的平均向量当概念。

第二个现成分析系统是[Sudoku代码](https://github.com/kameronton/sudoku-residual)及[数据/checkpoint](https://huggingface.co/datasets/residual-sudoku-dataset/residual-sudoku-dataset)。作者明确推荐用现成权重复现；大activation文件需要本地重建，JAX/Python依赖需适配。它是单任务受控窗口，不能单独支持通用LLM概念结论。

Lattice正文声明代码放supplement，本轮未取得独立完整repo；词共现论文代码仍是待发布表述；新belief论文代码未定位。因此不承诺三篇最新paper全部可立即复现。最新结果负责约束定位，成熟parent提供启动资产。

## 形态卡与压力

可行论文形态：**概念结构的可检验解释与边界**；**既有表征测量的重新归因且预测行为后果**；**对任务有效的表示单位/读出方法**。不以“更像人”“图好看”“某probe分更高”独立充当结果。

| 压力 | 来源 | 研究动作与已知ownership |
|---|---|---|
| 同一几何可有不同生成解释 | 共现2026与hierarchical2025 | 让统计解释和功能解释给出不同可检验预测；“共现可以解释层级”已拥有 |
| 概念不能总用一个二元反义轴描述 | hierarchical2025、Lattice2026 | 类别、属性、交并的共同测量；不能重新命名现有理论 |
| 评价所谓gold可能来自另一个LLM | Lattice §4.1用GPT4o属性矩阵 | 人工标准/公开norms/模型标注分开，检查结论依赖什么 |
| 读出单位选择会改变是否看见结构 | Sudoku §3 | 多层级状态标签与行为干预；cell对substructure已有答案 |
| 解码阈值变化可伪装成知识丢失 | Sudoku跨step probe附录 | 区分AUC、校准、整体可用性，而非只报固定阈值accuracy |
| 因果可用性要求排除输出分布代理 | belief2026 | 原作者已检验NTP/logNTP等替代项；进一步工作须有新对象或改变结论的条件 |
| 人的概念“常想到什么”与“承认什么性质”不同 | Grounding Gap | 任务/人群/解释来源审计；其具体gap不再当我们的新意 |

## 成本、分工与证据门槛

先复现一张原图/一个intervention → 缓存必要embedding与provenance → 做原论文已有强对照 → 寻找真实不稳定、失败或解释分歧 → 更新定位 → 人审研究动作。大规模Wikipedia重预处理并非最先必要；向量分析能吃到CPU并行，算力优势在重复测量而非联合预训练。

与现有mechanism-population线共享测量工具，但不能再复述其跨run机制迁移/语料仲裁主张；与组内knowing/using也要区分。10接收+5同邻域高分拒稿与评审核查尚未齐备，本轮作为有成熟资产的领域候选，不当成已完成正式驻留交接。
