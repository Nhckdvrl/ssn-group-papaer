# Idea 来源与实验设计逆向训练：过程材料优先

重要原则：论文结构不等于发现顺序。只有作者明确记录的经过可称为真实idea来源；其余只能标为我们依据论文重构的可能推导。

## 案例1：Merullo 2024 — 从熟悉的第二任务找到同构计算

**有作者一手过程证据**：[附录K](https://arxiv.org/html/2310.08744)。Colored Objects此前就已被研究、团队很熟悉；研究者注意到它与IOI都要求从干扰候选中筛出答案，遂拿来做第二任务。附录还提到初步查看过其他任务，没有发现类似强重合。

**逆向未知结果**：当我们只知道IOI有mover/copy-suppression组件，且Colored Objects也要选候选，应预测哪些组件会被复用、哪些下游响应将相同？下一步不是画Jaccard，而是按此机制对CO做干预。作者确实进一步研究了相关下游效应。

**对我们**：不能把IOI+CO的跨任务复用、XL top-10零重合但role仍相似当成首次发现；应额外检验不同训练run的**联合复用组织**。

## 案例2：Singh 2024 — 从发展相关走向训练期因果

**有论文直接写出的动机和方法来源**：[正文Introduction](https://arxiv.org/html/2404.07129)。以前induction heads与loss phase change同期形成，但只看progress measures无法证明训练过程中何者是因。论文借鉴神经科学optogenetics，发展训练中activation clamping，分析match/copy相关的三种子电路与多头many-to-many结构。

**逆向训练**：仅有某个head时间线时，怎样判定它是能力形成原因还是伴随标志？钳制其中一个子计算，保留其余学习，看后期行为能否出现。它把“同时出现”变成了“缺少某一步是否仍能形成”的问题。

## 案例3：MDA 2026 — 把data attribution的预测对象改为机制形成

**从论文可核对的问题与方法**：[正文§1–5](https://arxiv.org/html/2601.21996)。传统样本影响多看整体loss/预测，MDA为具体head形成目标做influence估计，再用targeted删除/增强对照random重训，连接影响分数与形成效果。

**我们的重建，不是作者访谈**：若知道一个head做什么却不知道哪些数据形成它，就改动数据归因的估计对象，再用再训练反事实闭合证据链。

**对我们**：MDA附录F.2.2已看到多头接手现象；不能把一次“头易主”当新发现。若要追多头发展，应同时有原样rerun、targeted/random mask、多头因果结果和自然任务行为。

## 案例4：Yin 2025 — 检验大家习惯连接的两个概念

**论文证据**：[ICML版](https://proceedings.mlr.press/v267/yin25e.html)：IH能复制，FV heads更直接影响复杂few-shot ICL；一些FV早期是IH，作者明确称IH可能充当stepstone只是推测。

**我们的idea重建**：人们容易把“induction负责重复复制”直接等同于“induction驱动广泛few-shot学习”，可用同一任务中IH/FV归因比较拆桥。发现演化相邻，还应另设计**训练期间功能性中介干预**去检验必要性。

## 案例5：本workbench E75 — 真正应该保留下来的过程

[E73](../../heads/1-original/experiments/E73-ioi-component-transfer.md)先出现410M同初始化兄弟仅~0.05的低transfer；[E75](../../heads/1-original/experiments/E75-ioi-transfer-gap-decomposition.md)不是立刻宣称“算法分化”，而是分三种可能：比值/测量、头换人伴随自修复、计算机制真的不同。随后测直接/总效应、功能剖面、target任务DLA对齐，并承认该对齐用了目标侧信息。

**它值得学的部分**：让一个实际反常触发多个可排除的竞争解释，而不是为了确认预设story死守第一张图。

**它最终仍未解决的桥**：target上找回目标head，不证明source贡献了信息；与已有Tigges/跨任务电路工作接近。下一步应以同信息预算target-only控制和新的具体path预测来判断研究值不值得继续。

## 一个操作模板

读论文/实验时，把结果全部遮住，只保留前一个实验已经知道的东西，回答：
- 下一步认知缺口是什么？
- 至少两个竞争解释如何在一次实验上给出不同预测？
- 哪个最简单的干预能准确区分？
- 真实结果出现后，它迫使我们修改哪一个预先相信的说法？
- 文献里是否已有同一个观察或更强解释？

没有作者明确过程材料，不要编造“作者灵机一动”。尽量找附录、开源commit、作者演讲/复盘等证据。
