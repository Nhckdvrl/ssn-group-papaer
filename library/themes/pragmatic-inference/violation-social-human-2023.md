# Pragmatic violations affect social inferences about the speaker（Glossa Psycholinguistics 2023）

[作者公开全文](https://www.langcoglab.com/_files/ugd/7cb05b_a7a6b8309d2f44c1bee5fedacd66d66e.pdf) · [OSF素材/Rev数据/R](https://osf.io/f3phz)。41页论文正文§1–8、方法/结果/讨论/局限及部分参考文献已读；PDF图像未独立审。E62已读全部三套材料规格、fillers和原R核心分析；只复算描述均值，未复现lmer/p值，未执行原Ibex UI。

- **论文形态 / 背景压力：** 理论＋受控人类实验。Grice路线主要解释句子的描述信息；社会语言学常解释声音/形式携带的人物属性。把日常“违背交谈期待”的选择作为二者交会处，不要求说者有意传达人格。
- **idea来源（DOCUMENTED）：** 先确认相关性/信息量违规的社会成本；这个效果无法区分违规本身与故意不合作，因而第二实验改变有无相关知识；第二实验不能区分各种不愿合作的理由，第三实验加入自我导向的转题理由。后续问题从前实验的解释歧义自然长出，非追加benchmark。
- **最近邻距离：** Fairchild/Papafragou2018、Fairchild/Mathis/Papafragou2020已有native/non-native及under-informativeness的社会成本；Fiske等已有Warmth/Competence；politeness已有非字面表达的关系含义；本文改变的是一般相关性违规、解释理由与瞬时/持久特质一起测。Social Meaning LLM2026有precision效应强度/理论prompt；不能claim首次社会语用测量或首次动机影响评价。
- **设计：** 三实验同16场景，每个2×2，Latin-square每人每场景一版本。E1 relevance×informativeness；E2全部irrelevant，知识自述inability/unwillingness×informativeness；E3全部irrelevant/knowledgeable，self-oriented preamble有/无×informativeness。四问题分别knowledgeable-in-conversation、considerate-in-conversation、competent-as-person、likable-as-person，1–7。300 recruited，公开Rev retained86/93/83人，1376/1488/1328行。不是48独立场景。
- **发现与边界：** 原人类发现相关性成本大、信息量效应从属于相关性；inability减轻Warmth与durable competence处罚，但不是全部trait；self-centered preamble主要改善competence。知识自述是观测证据，不是说者真实内心的verifier。无差异不等于严格等效，latent chain未做因果中介。
- **源质量：** E2第15项缺reason分隔符、第16项缺信息量括号；E3第3项extra brace、第16项缺信息量括号；跨实验部分词串不同。原Rev少量描述均值与论文不同，保留两版，不把原R显著性判错。不能悄悄“修正”素材然后挂原human norm。
- **可迁移动作 / 我们的问题：** 将事实/知识声明读取与它引起的局部动机、跨到持久人格的推断分开测；同一实际不相关回答，证据应怎样改变评价？能读对知识声明但不正确传播其含义，是值得测的候选解释，当前没有模型finding。需更多自然现象和足够独立材料，而不是“某个模型某句话有错”。
- **规模/训练解释：** 小模型入口失败先隔离；同族stage只能说明检查点差异，不能单因果归训练目标。只有语义阳性对照成立且跨现象条件关系稳定，才考虑能力–policy解释。人类理论已经拥有机制叙事，迁移到LLM本身不是完整顶会增量。
