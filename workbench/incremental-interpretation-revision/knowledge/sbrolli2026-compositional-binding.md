# Beyond Bag-of-Words: Diagnosing Compositional Binding Failures in Vision-Language Models（NeurIPS2026，presentation/评分未核对）

`[证据级别：主文精读＋指定附录，作者v2]` [arXiv2602.02043v2](https://arxiv.org/abs/2602.02043v2)，2026-09-25。官方9094接收题名中核对Sbrolli/Yamasaki/Matteucci、event139620；OpenReview最终稿不可访问。已读Main§1–7 pp1–10全部、AppA8–12 pp19–21，Tables2–11 p7–9视觉核对；A1–7及代码未全读，不称完整附录。

1. **论文形态：** benchmark＋失败分解＋针对训练。
2. **背景与压力：** VLM交换型组合测试上表现较好，仍可能不会属性与对象/关系与参照对象绑定。Auto-Comp生成四类概念、Minimal/Contextual两版本，评测25余模型；候选由Swap改为包含重复对象/颜色的Confusion。
3. **改变的前提：** 正确拒绝交换描述不等于完整绑定。所测是caption候选打分，不是模型自由答题。
4. **idea来源（RECONSTRUCTED）：** 一类负例接近天花板→改变错误候选的生成规则→把“只要词袋相同就难”拆为另一个绑定压力→用定向训练测试余下缺陷。推测依据是论证结构，不冒充作者发现经历。
5. **与近邻距离：** SugarCrepe等hard-negative、Winoground、ARO、CREPE已拥有组合/属性交换主题；本文增量为可批量的概念配对、重复元素候选与背景复杂度。不是找空白，靠更能区分失败的测量对象形成叙事。
6. **方法与基线：** 四类、2/3对象，生图与过滤；Swap/Confusion及针对负例训练。主图显示一类绑定改善后仍有另一类错误。generative model按caption token log-likelihood求和，不是实际回答；参数/训练配方及候选数需一起解释。
7. **证据边界：** PDF SHA4188a3236560ddaea41756f97a9b421d3a4069b5e0133765b77a74228f620ee8，外置`papers/reassessment-2026-10-07/sbrolli2026-binding-v2.pdf`。Swap候选2/6，Confusion属性16/729、关系4/108；纯accuracy差混有难度/候选数量变化。人类/盲基线N3只抽50候选，Appchance2%与主全729的.14%并非同protocol。Minimal/Context同时改图和caption，不独占视觉clutter解释。各模态经筛选后不保证逐概念配对。
8. **需代码核对的短板：** N^(2N)−1枚举是否剔除整体重排后的等价真描述未核对；不能仅凭公式宣告数据有错。Table2 ShapeN2保留数与Table3比例不一致未解释；正文“all>94%”与Table11 ShapeContext93/92%不符。主文Table8称相对Swap-only，AppA9/10称相对pretrained，增量分母未统一；N2 Swap的唯一negative重复方式未核对。
9. **对我们：** 借从“拒绝一种错误”走向“完整重建”的对象变化，不照搬视觉benchmark与泛化结论。E88/E89可提出论元重建问题，但仅No改对或一个hint涨分尚未提供它的具体增量。下一应问正确frame能否形成可供新问题使用的源解释。保留弱/null族，先找探索idea，不要求一晚做完论文。
