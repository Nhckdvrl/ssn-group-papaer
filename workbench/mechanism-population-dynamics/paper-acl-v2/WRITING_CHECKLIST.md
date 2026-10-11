# v2 写作核对清单（继承 v0 → v1 的全部修正，改稿后逐条复核）

## 专家评审（第一版意见，最高优先级）
- [x] 不写 AI 味的句子：不用口号、比喻和对仗（born to copy、birth certificate、weights forget、anchor、scaffold、critical period 作为主标题）。
- [x] 摘要先讲问题与主线，再讲结论，不堆实验细节和数字。
- [x] 主线和支线的关系写清楚；每个支线（尤其 Flan）开头说明它在主线中的任务。
- [x] 定义不过强也不过弱；不用先天 / 后天二分。

## 措辞与证据对齐（v1 各轮修正）
- [x] “层的位置”写成大体共享（层剖面相关 0.4–0.7），不写“所有模型同一层”。
- [x] “哪个头”写成“由初始化偏向 / 跟随初始化”，并给出最强头相同 12–30%（随机 6%）；不写“固定每个头”。
- [x] 不写“whatever their corpus / on any corpus”；写“across natural-language corpora”，代码语料不保留。
- [x] 行为：写“初始化对行为的影响不跨语料传递”，不写“初始化不影响行为”；一格一个模型，交互与噪声不可分。
- [x] 语料主效应为 0 是对称性保证的，只能作为检验，不能作为证据。
- [x] DataDecide 的 seed 同时设定初始化与数据顺序；顺序不对应任何头，能偏向特定头的只有初始权重。
- [x] 早期窗口：噪声在最初几个百分点后改不动；换语料一直改写一部分、越晚越少（与 Table 2 一致）；窗口跟随累积学习量而非步数；保存在参数中而不是优化器状态中（不写“由权重本身保持”）。
- [x] “两个量跟踪这一变异”，不写“解释了大部分”；“can account for” 尺寸趋势。
- [x] 梯度噪声：受控实验在固定尺寸下改 batch / lr；30× 模型指跨语料一致度不升高。
- [x] 功能词 partial ρ 为正（共线），不写“adds nothing”。
- [x] “none of the statistics we tested” 预测哪个头。
- [x] 认出初始化：权重本身同样能做到（0.01–0.04），SeedPrints ≥ 60M；不写 provenance 应用，不写“权重忘了 seed”。
- [x] 消融迁移：19.5% / 层匹配随机 10% / 异初始化 2.0%，“只部分迁移，只在同初始化之间”。
- [x] Flan：1–2%；“strengthens / adds”，不写 installs；模板合并检验 0.93 ± 0.29、0.98 ± 0.32；1B 以下 Answer: 单独常带有大部分效应；新增注意力按原有份额（30%）落在已有检索头上，不写“集中”；布局 0.45 vs 其他消融 0.40 vs 异初始化 −0.03。
- [x] 基准：10 个基准 + 平均，154 格。
- [x] 附录初始化扰动：10% 为 0.74（两个初始化 0.57 / 0.91），100% 为 0.03。
- [x] 全尺寸核查：4M–750M 636 个 run + 1B@7500 49 个 run 从标签初始化开始；表中尺寸用 DataDecide 命名；checkpoint 列（750M 为 43%，1B† 为 11%）。
- [x] Pythia 到 12B 的证据是两个几乎相同的语料；DataDecide 的多语料交叉到 1B。
- [x] 相关工作：置换对称 / 对齐（Li 2016、Entezari 2022、Ainsworth 2023）、同一盆地（Neyshabur 2020、Juneja 2023 “though not always”）、Frankle 2020、Achille 2019。
- [x] Limitations：GQA；从第 9 页开始；正文 8 页填满。
- [x] 无 overfull；aclpubcheck 终版 All Clear。
