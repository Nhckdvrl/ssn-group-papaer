# E39：projection-third-family（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2；第三家族边界，不预设方向
- **对应：** C02/P02/P09
- **问题（一句话）：** E38同源背景先验与speaker certainty读数的可用性和证据作用，能否在独立Mistral家族的真实Base/Instruct端点保留？
- **设置：** E38原1760行、原human840均值、同strict numeric parser；Mistral-7B-v0.3 @caa1feb0e54d415e2df31207e5f4e273e33509b1 / Instruct-v0.3 @c170c708c41dac9275d15a8fff4eca08d52bab71。两个端点共用完整官方Instruct tokenizer；bare保留官方单BOS，chat官方system/user生成模板。FP32/单sequence/noTF32，原greedy/max_new_tokens5，保存原输出和LP。与E38跨家族bare有BOS差异，不能因果比较家族。
- **读数：** 与E38同一coverage-aware摘要：分interface/task/embedded/predicate的valid覆盖、human MAE上下界、actual-fact high−low；invalid不算能力错误，不只比较有效输出排名。生成numeric是被询问的rating，不是模型内部belief概率。
- **阳性对照：** E38已通过的所有原source/human事实对齐与公开cache审计复用；跑前两个端点实际完整token SHA相同，原system/user事实逐项存在；首末prior/projection输出ID重复相同、LP误差<.001才运行全矩阵。
- **噪声地板 + MIE：** 无抽样seed；20item cluster bootstrap2000/seed0；重复用于校对而非独立重复。CI仅材料，不代表训练seed总体。无minimum paper效应，先以可用性决定是否可解释。
- **混杂审计：** 5token预算对tokenizer非等compute；Mistral空格/数字分词不改预算救分数。官方chat最后user保留system，完整输入检查；不重渲染加入assistant而丢system。Josie四原prior标签错配仍保留并按actualfact对齐。human只p非polar；两个交叉prompt版本姓名随机不同，不作belief/certainty因果比较。听者背景信念、说者确信程度、解释不确定性三对象不互换。
- **决策表（跑之前写）：** A两入口及stage可测，原结构保留→记录强成功并比较已声明边界；B覆盖或答案格式支配差异→仅可用性结果，不继续局部prompt修复；C原证据作用在第三家族不同→边界观察，需原人类规范/独立材料再审，不统一criterion；D源/数值gate失败→保留失败，不放宽阈值。
- **算力预算：** GPU0/1各一个已下载端点，3520生成/端点，总7040，预计<2 GPU·时；锁GPU且不干扰E38其它端点，不重复完成的原实验填槽。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
CPU完整source/token gate已通过（results/E39-source-preflight.json）；输出仍未获得，C01/C02保持L0。

2026-10-03 完成：两端点各3520，总7040生成；source/input/repeat全通过，见 results/E39-projection-third-family-summary.json。原5token Base→Instr bare prior MAE变化−.10435 CI[−.15009,−.06167]、projection−.00244[−.05262,+.05068]，但E42证明Base914/914选入numeric延长后全为prose，Instr1625 nonEOS中124变invalid。旧bare stage归因隔离，不能把上述点估计当能力差异；原数字/失败保留。C01/C02不升级。
