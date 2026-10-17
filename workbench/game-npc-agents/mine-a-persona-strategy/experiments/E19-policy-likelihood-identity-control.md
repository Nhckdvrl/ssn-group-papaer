# E19：条件动作似然与角色输入信息的控制（2026-10-14）

- **状态：** DONE
- **类型：** REPRO / measurement校准（P06）
- **对应：** E17 / E18 / C01；不是新的人格能力证据。
- **问题（一句话）：** no_consist真实焦点轨迹是缺乏角色输入信息，还是其encoder/projection几何不适合读取这类信息？
- **设置：** 沿E17冻结full/no_consist seed42与已缓存test100×3个体轨迹，每条200time steps；100候选仍同source test人物。新诊断scorer只计算sum_t log πθ(action_t|observed_state_t, embedding_j)，取100-way top1/3与gap，不训练/修改policy、世界、reward、标签。η原/校准检索完整保留，两scorer比较的是相同角色输入ID，不能偷偷改变主metric定义。先前16NPC200cycles可完整回放。数据表型/state可依persona改变，似然条件在实际观察上，读数不将body可解码当controller作用。
- **读数：** 100候选top1/3、真实code vs最佳alternate的loglikelihood margin、persona簇bootstrap95%（2000/191919），各mode平均native reward、模型hash与候选集固定。条件似然直接使用生成policy，因此**不是独立人物语义/BigFive效度评价**；能区分code不代表正确执行某种抽象性格。Actor改变的Fixed-state KL作者已有，似然原则是标准方法，本实验不冒领它为新算法。
- **阳性对照：** Actual code在同state下恰是采样分布来源；与不同code相同π时应不可辨、不能用强先验作弊。source_id数组来自原actor给定的embedding，非η输出。π和φ全部frozen，fp32同原MLP，GPU只加速数值打分；每条actual动作与source native cache对应。
- **噪声地板 + MIE：** finite trajectory的误辨保留，100类chance1%；若似然远高于η（至少超过η2×且bootstrap差区间>0）则η低识别不支持“policy角色信号消失”；若二者都弱，则保留行为收敛/utility constraint或投影失效解释，后续需要状态/utility机制而非新loss强填。一个policy seed是pilot，其他policy seed未运行不得说generalization。
- **混杂审计：** 似然scorer需要白盒policy，不能与η实时低成本decoder效率混比；以观察为条件，不计算不同candidate导致整个world反事实；label ID与人格语义分开。源unit与当前own200不同，E18已审，不拿论文表格直接减。NoConst vsFull extra decoder fit预算E17单列。
- **决策表（跑之前写）：** code可高识别→定位encoder几何/单位而非policypersona能力；两scorer一致弱→认真看policy和Utility状态；某些persona可辨某些不→按预定全部100保留并观察语义/状态条件；资产/维度错→报fail不补假数据。
- **算力预算：** 1GPU≤30分钟，原fgvd/overlay，0API；07:00起全部项目≤8GPU。只评分已有native traces，不新增游戏规则。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

seed42完成：同100候选/每人3own200迹，φ-g cosine full6.7%/no_consist1.0%，policy likelihood full21%[15.3,27.3]/no_consist27%[20.3,34.0]（persona-bootstrap95%）。不是独立语义人格评价；2方法排序反向不能直接作policy utility或人格能力结论。按照有信息才复核规则，公开policy seed43/44完全同protocol确认，全部保留。

三公开训练种子完成：似然full top1=21.00/36.33/20.33%，no_consist=27.00/25.00/26.33%。原η与条件似然对同ID目标的差为full+21.67pp [17.22,26.23]、no_consist+24.56pp [19.78,29.44]；按同100persona簇bootstrap、条件在三份固定政策上，并非训练seed总体CI。**Full−no_consist平均−0.22pp [−5.67,5.44]，无一致排序反转**，首seed线索降级。结果results/E19_three_policy_aggregate.json。代码信息可读不等于语义风格效度；conditional scorer使用生成policy白盒预算单列，不替换原评价。C01 L1，新科学增量0。
