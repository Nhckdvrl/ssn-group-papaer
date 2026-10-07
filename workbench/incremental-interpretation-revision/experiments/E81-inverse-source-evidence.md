# E81：答案选择与逐词解释Source的逆向证据（2026-10-07）

- **状态：** RUNNING；生成器E431在运行前改本线E81，非POST-HOC。
- **对应：** I02 / C06–C09 / P17，GP先前关系的修订在作答接口还是源证据匹配中失败。
- **问题：** E80输入信任没有共同保持。用另一个计算对象直接问：错误答案是否仍能比正确答案更好解释原Source每个词？这与可靠性措辞/Source消费mask不同，既不等E70标签，也不加防御网格。
- **定位/来源：** Min等ACL2022 Channel Prompting已有P(input|label)的分类方法，正式main/AppB已精读，card/ledger记录范围；逆向评分本身不是novel。Clark2025显式源噪声算法与这个label条件语言评分不同，不叫同一个noise posterior。增量若有需具体解释GP源证据与答案的分离、定位怎样修订，并有可预测跨用途后果；不能只换数据跑旧方法就认定合格idea。
- **数据：** E65完整892QA/356S/178clusters四构式M27/NPZ89/NPS36/NPVP26；原Source/Q/G2 gold及映射不变，SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b。0API，无新数据/标签/改写，不审成熟数据；全部GP/cue保留。
- **条件：** NATIVE完整E65 NONE重用。INVERSE对每个原Q和两个候选都给相同G2规则、原选项映射及一个 proposed answer，要求生成与该源支持判断相符的一个语法句；assistant延续固定为原Source并teacher-force整个S，计算每个Source token的joint LP。原S在prefix中不存在，两个候选都完整评分，gold仅用于分析。只一版指令、无示例、无学生自由生成。words/letters及两映射完整，三个原FP32家族8独立H20。
- **主读数：** 选最大whole-Source LP的原gold correct，及softmax两候选Source LP得到的归一化正确证据分数，initial/final/all及joint全Q；INVERSE−NATIVE全部GP/cue/两readout。归一化Source证据不是校准语义posterior，不将它的大小与native单token概率当同一概率变量；共同correct/joint与GP/cue保持为核心。10000 lexical cluster bootstrap seed81。
- **阳性对照：** 原cue/Source支持规则；全CPU Source字节/SHA、候选gold/映射、prompt中无Source、Source target token相同、无重复BOS。固定首Source原native LP仪器<.001，inverse单条件与batch同LP差<.005；每个Source token逐项保存。评分只含Source，绝不含proposed answer或gold token的LP。
- **噪声地板：** 完整mapping flip/paired CI；不筛seed或提示。原T2 landmark有缺失，因此不擅自补词/把token位置叫消歧；本轮主读wholeSource，不另加位置网格。
- **混杂审计：** label先行会影响Source编码，任务/输出对象也改变；没有等compute或pure Bayes分解保证。No覆盖未断言广泛集合，Yes较集中，可能只是反向任务偏好；看全部真假关系/cue保持，而非No增长。候选假设是可见的外部条件，不认证native解析能力或正确latent parse；R8恢复指令基线E54完整保留。若任何归一化分数极端饱和，correct/联合/两映射及原LP仍完整报告。
- **决策表（跑之前写）：** 三族两构式真实错误correct和joint共同改善且cue/另一关系保住→查哪些原词给候选差异，设计一个关键证据对比以分辨结构证据与一般标签先验；原初始改善而final/cue下降→候选偏好，不包装机制；null/异质→此评分动作收束，不换模板扫胜，回实际原子脚印或新核心对象。若仅旧channel在GP有效无新解释，仍不够合格idea，不因近邻自动关线。
- **算力预算：** ≤2GPU·h，892×4读出映射×3族=10704新逆向条件/21408 Source序列；8卡Q3/G2/L3原SHA分片、FP32/eager/seed81/offline。母baseline不全重跑，不结束现有轻服务。raw/PDF外置E81，仅代码/卡/摘要进git。

## 结果

尚无科学效果。先写卡后实现、CPU预检及运行。

三族CPU3568原native SHA与3568新逆向条件/族全部通过，原Source target tokens两候选相同且不在prefix；maxSource18tokens，max总161/158/179tokens。8卡PID：2509123, 2509124, 2509125, 2509126, 2509127, 2509128, 2509129, 2509130。
