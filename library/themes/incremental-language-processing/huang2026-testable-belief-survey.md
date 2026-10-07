# From Memory to Testable Belief: A Survey of LLM Agents（2026-09作者预印本，接收未核对）

`[证据级别：主文精读＋指定附录]` [作者仓库](https://github.com/jiminHuang/belief-state-survey)，固定revision62366ecf9c948f1fe26a8988b1578e472e5fbad1。SSRN7493158的较早题名是From Memory to Belief，不能混为同一PDF版本；本文48页、SHA422d764befbe4607255861a287b989e0a397417ffc87346330d1578b81b78e20。

1. **论文形态：** 跨子领域综述／构念及测量对齐。
2. **背景与压力：** memory、uncertainty、agent RL各有指标，少在同一系统测同一状态。作者按state/revision/test及来源重排517篇（182同行评审、335预印本），区分结果、交互/记忆操作和状态本身的credit。
3. **改变的前提：** 历史记录不自动是可反驳的假说，答案正确不足以测状态及其使用。严格的written-belief own-observation训练定义只有ReBel/ABBEL；包含world model等宽定义为13，不是只有两项研究过环境预测。
4. **idea来源（RECONSTRUCTED）：** 分别覆盖存什么、reward在哪、confidence多少的旧综述→将信念写入、更新、测试的职责统一成可核对字段→用credit对象与test来源的交叉找缺口。相对16邻综述靠研究对象和计数对齐，不靠宣称空白。
5. **最近邻距离：** memory综述、post-training credit综述、uncertainty综述、Cai/Tang2026单域Bayes-filter综述；只前四格组合不能独占“可测试信念”理论。本文是领域画像，不是新训练方法或因果失败定位。
6. **方法／证据：** 已读Main§1–11＋limitations pp1–9全部，AppA pp34–36全（查询/筛选/五六轮/九月更新/敏感性），AppB/C Tables12–16 pp37–38全部；图4/Table4 p6、Table6 p8视觉核对。References pp9–34未逐篇核对，Table17–26 pp39–48的517篇表及代码未全读，不能计作我们又读517篇。
7. **短板与质量判别：** 23→34query、规则排除短摘要/至少2关键词、引用树按score固定抽样，缺失仍可能由词表/抽样造成。LLM筛选编码，作者称逐字段人工校对518篇（最终517），99.8%是内部校对不是独立间人一致。没有重跑方法，headline数字来自各论文，不能跨protocol当共同机制。只两篇own-obs credit都预印本；同行评审子集该格0，不能当普适不存在。
8. **对概括的思考：** “state而非reasoning”“belief-action gap必须训练”“只有latent GT能测belief”等是作者观点，综述列例并不能穷尽因果/方法；有预测可评分并不必知道每项latent真值。Section3的belief定义要求testability及uncertainty，缺一项按此不算并非领域唯一构念。Insight2“none routes to claim”需与AppendixTable13 memory-row/claim方法的粒度区别，不能照抄为没有细粒度修订。
9. **可迁移动作与I06：** 分清被更新的对象、signal如何到它、修订后的新用途；GP不是显式长期belief，不能把原QA当known latent state。我们的增量若只有“修了答案没修状态”仍薄。值得挖的是依赖解除后论元重新实例化的具体遗漏规律，及Q未知源影响是否改变未指定关系；E90是这一核心区分。不是因为本文已有state研究而关线，也不把未peer-reviewed的缺口直接当题。
