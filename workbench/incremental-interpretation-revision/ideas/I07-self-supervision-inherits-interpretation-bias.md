# I07：自监督记忆奖励可能继承对观察的误解释（SEED，探索idea）

- **来源：** P20；E91/E92固定P的观察表达干预；ABBEL全文与selected code的内容credit定义。

**研究问题：** 当正确修订要求重新解释观察，自监督内容reward是否把评分模型的旧解释变成奖励标准，漏奖甚至反向惩罚正确记忆？先找有价值预测，不要求现在完成论文标准；不认证已证明一般机制。

**三句话叙事：** 新观测并不自动是可靠的“自动评分器”：模型还得解释它。若内容奖励直接基于同一语言模型的观测可重建性，正确的关系修订也可能得不到相应credit。应让reward识别语义关系的变化，而不是只识别原表达的可预测性；一旦建立具体失配机制，可发展解释稳健的belief credit。

**来源与已得证据：** E88–90提示拒绝旧依赖与重建正论元不总同步；P20/E91由ABBEL的内容reconstruction reward直接发展。E92固定原P和context，只换发表配对观察，已有共同Q Gold一致：Q-generator GP语义reward alignment提升三grader+.278[.056,.500]/+.222[.056,.444]/+.222[.056,.444]，反向cue→GP方向下降；另两generator效应弱，主要来自MVRR。实际1800评分/50发表pair/三构式，全族全侧保留，原子盲标全复用。E91/E92是未训练raw analogue，**不是作者RL训练被证伪**。方法的candidate selection、schema、额外compute都未确认，不叫完成稿。

**若为真为何值得兴奋：** 外部观察本来是自监督学习正确修订的锚，却可能被同一错误感知模型变成确认旧解释的信号。这会把GP的行为缺陷连接到agent memory训练的credit问题，给出内容reward该约束哪一种变化的实际机制与方法入口。它比“LLM偶尔误读”更有后果；如果只在这一小群MVRR/一个generator生效，范围仍不够，不能硬夸。

**近邻与compression risk：** ABBEL拥有观测reconstruction与belief内容监督；Agent-BRACE/CBM已有缺失、错误、stale belief rewards；ReBel已有基于观察的一致性credit（主文／关键附录已深读，非字面重建）；Kamoi/self-correction已有内部grader不可靠压力。MetaRAG已有同policy一致性reward＋最终correctness gate。一般“reward可能错”与一般“state不等于action”不新。拟增量是**正确替代关系的内容credit为何会随同注册语义的观察表达改变**，如何由解释/评分通道产生、能否在其它自然更新域预测与改善。

**当前最高信息量的下一核心：** E103从同一原GP观察自然采七个候选，加原greedy组成固定八候选池，比较WHOLE与原T2后缀oracle的实际选择忠实度。如果只有cue来源候选对有效而同原观察不能产生好候选，必须收紧；若池有好解释而WHOLE漏选、suffix恢复，才把评分分解推进到真实内容选择后果。社区Belief-R扩域已经E93/E97测过，仪器不可用与Min修订困难如实保存，不继续格式网格，不把未测到当0能力。

**机制仍有三个竞争解释（E93效应读取前）：** (1) grader沿用观察的误解释；(2) grader即使能识别含义，条件于正确belief的语言生产偏好仍可能更喜欢显式、无歧义表述，故原GP的逆向预测低分；(3) 新观察与正确更新不一一对应，inverse ranking本身缺必要prior／任务信息。E92只能说明观察表达参与credit，不能区分这三者。当前核心价值来自明确的“关系更新→训练信号”后果，不能把标题中的继承偏差当已证事实。MemTrain实体回填、MemoryRewardBench过程judge、CERL未来用途训练都有ownership；不凭它们的存在判死，也不把同类主题换名当新idea。

**语义校对补记：** E70八定点项更正已传播全E70/E91/E92，E91 G-grader/Q-generator同40语义源reward−7.093[−14.201,−.771]与正质量并存；E92主Q-generator alignment及CI保持，其它仍弱。旧数保留、更正不是人类独立Gold；后续用[更正摘要](../results/E70-posthoc-semantic-correction-summary.json)。E94真实观测参照CPU图有时间偏好，但主要新信息覆盖与当前parser实现问题，不把它改名为新合格idea，不继续修bug局部网格。

2026-10-08 E96首完整Min当下native同writer/grader新增实质边界：100自然P/200score/完整盲T1，固定P source目标消歧使semantic fidelity credit alignment+.500[.167,.833]，map48aa680d625c8cb1e8e59a8c6d9577ca6fb04c92f599b049e0a30f9db7ff50af（INTERIM）。E97 UPDATE actual仅8.1%，故不以“懂了只是credit错”讲故事，而问重建困难观察是否复制尚未撤回的解释。两族待测，尚SEED，不认定作者RL方法已失效。

**2026-10-08完整三族后的更具体机制种子：** [E101](../experiments/E101-disambiguation-region-reconstruction-credit.md)显示same-P/GP-target重建的前缀项三族皆负，消歧起后缀Q/Min明确正、G方向正但CI0；11/13/16条总分偏旧解释而后缀偏cue解释。[E102](../experiments/E102-revision-evidence-credit-oracle.md)唯一固定位置oracle把全部50上的正确选择提高Q10.42[3.13,18.75]、G8.33[−2.08,20.83]、Min21.88[9.38,35.42]pp。因此探索对象从泛泛“评价器也读错”变为**已经出现的修订证据，被全序列重建的前缀credit抵消**。它与已有semantic reconstruction/future-use rewards的距离在于修订证据与被解释前缀之间可观测的竞争，而非我们首创token或semantic reward。suffix还是T2 oracle，原候选含cue来源，不声称自动方法、训练收益或唯一神经机制；[E103](../experiments/E103-native-pool-revision-credit-selection.md)正在检验同原观察候选池中的功能后果。现有证据够支撑一个值得追的探索切口，尚不能直接认证合格idea。
