# E153：MMLU独立任务窗口中的来源性质转移（2026-10-27）

- **状态：** PLANNED；新任务模型读数尚未运行。
- **对应 / 类型：** C14/P32，任务级测量与因果拼装PILOT，无新训练。
- **问题：** 语言窗口里的native预算性质及gate单独不足，是否也体现在独立学科任务表现，而不是只对LM损失成立？

## 原生资产与真正新增的信息

仍用E150完整核验的成熟A/B，不引入新checkpoint或选择训练seed。原来64窗口已参与探索、不是MMLU；因此不能据它们宣称能力层面的语义模块。新任务使用本地真实缓存的`cais/mmlu`，测试输入独立于E148–E152语言窗口。

已读作者EMO的greedy_prune_layerwise、data_utils、splits_mmlu，以及OLMES GenericMMLU/base_task：原流程是**cloze答案文本条件似然(RC)**，非字母选项分数；专家选择逐层推进，先前层已裁剪，按cal所有非padding位置的平均softmax选31R+1S。沿用这些逻辑，不将简化prefix路由诊断叫原论文复现。

## 冻结数据与格式（新模型读数前）

- 两个预定学科：`high_school_biology`、`high_school_mathematics`，依据原任务覆盖与缓存可用性选择，不依据新模型表现。各取official dev固定5条作5-shot示例；official validation全部32/29条作选专家cal；test各固定64条，seed153001无放回，全部保留。
- 在选定test前按精确question+choices内容核查与dev/cal重复，重复仅从候选池排除并登记；不看模型答案。记录Arrow文件/内容/问题ID/采样/SHA。
- OLMES RC格式：header为该subject的multiple-choice介绍，每个示例`Question: ...\nAnswer: <正确答案文本>`，双换行分隔；test仅到`Answer:`。对四个`" "+choice_text`分别teacher-force计分，不把正确测试答案用于选专家。全部文本不截断；若>4096先登记统一数据/格式修订，不能按表现删题。
- 此pilot使用独立official dev/validation/test，不复刻作者当前代码的test再拆分(当前脚本为前60%/后40%)或论文全表口径；不声称完整MMLU复现或预训练无污染。

## 来源与预算干预

沿D/G/R/S定义，固定4格构成G×其余功能包的2×2：AAAA、ABAA(B gate only)、BABB(B D/R/S with A gate)、BBBB。它区分路由参数与其余学出计算的转移，不重新扫16格/层。

每个subject用native A/B的cal分别选一个task-level静态31R+1S mask；使用逐层greedy，每选一层即以该mask计算后续层cal输入。所有4来源格都读full、selectorA32、selectorB32共12条件/subject，固定两mask，不让hybrid重选更有利mask。按原pool-softmax程序限制logits，shared保留1。

选择用FP32 softmax平均概率、无test监督；mask程序与物理删gate行在实数下等价，BF16 kernel维度与tie细节未声称逐位复刻作者物理prune。cal+dev允许已知标签作示例/选专家；test标签只用于最终评分。全程只读源参数/buffer。

## 预定读数与统计

- 主任务表现：四候选答案**raw条件loglikelihood和argmax accuracy**；同时报告按字符长度归一化accuracy（OLMES RC默认）以呈现长度偏差，不挑更好的口径。
- 连续任务读数：四个答案likelihood归一化后的true-choice CE、correct-vs-best-wrong margin、真实正确答案token平均NLL。choice-score CE/KL不称为完整LM概率分布。
- 完整→受限同来源格：accuracy下降、choice CE增加、四候选归一化分布KL；另单列**首个答案token处**的真实全词表KL，不外推为整答案分布KL。
- 对G×功能包四格报告full与受限self-baseline的成对差及交互；先看native任务性质是否成立，再解释hybrid。所有12条件、两topic和macro都全报；native B若不具该任务性质或区间宽，不能用LM窗口替代结论或换题追阳性。
- 按question成对bootstrap1000次、seed153001，并在两固定subject内分层再macro等权；不把两个subject或两个checkpoint当独立初始化总体。样本64/topic的精度限制直接报告，CE与accuracy分开，不以一个替代另一个。

## 阳性对照

- 模型无关的cloze/5-shot拼接与因果target-mask已知答案；constant-logit toyLM的多token条件likelihood、padding和candidate重排oracle。
- tiny原生源码的greedy均匀gate已知keep集合、旧层mask实际影响下游输入、无权重修改/无残余hook。
- 真模型先复现E150 cal位模式；全128槽mask恒等；cal的4candidate相同prefix首答案logits逐位相同，防未来/标签泄漏；全部原生参数/buffer前后hash。
- 原有E151全R/S零化阳性说明计算影响真实预测，不据此选新学科/输入。

## 噪声地板 + MIE / 混杂审计

原生/全mask重放地板0，uniform BF16；预训练F32/BF16尺度沿E150单列。test固定且输入未参与LM窗口，仍不保证训练污染不存在。题数/长度偏差、任务划分、cal逻辑与作者全表不同均登记。G-only混合可能损害完整任务质量，因此所有受限结果与同格full及绝对表现并列；不能把差full造成的小drop叫模块化。

## 决策表（跑之前写）

| 观察 | 更新认识 |
|---|---|
| native B任务预算性质与LM同向，G alone不足而功能包/交互有作用 | 增强性质涉及真实任务的证据，仍不是语义最小模块或训练单因素规律 |
| CE同向但accuracy不确定 | 连续预测有证据，能力读数精度不足，不混称完整复制 |
| native性质不成立或反向 | 限定LM结论的任务范围，不换预算/学科筛阳性；先审格式/基线再做科学判断 |
| hybrid full差但drop小 | 作为质量/鲁棒性权衡，不当恢复模块证据 |
| 程序/causal mask/重放失败 | 修明确实现并保留失败，不当科学阴性 |

## 资源与当前结果

预算2 GPU·时，含2模型加载、两subject greedy cal、128test问题×12条件×4答案、所有控制/失败/I/O。单卡B4答案候选，max context4096，2份BF16预计<90GB；探索并发≤8，优先复用既有mechpop/缓存，无新训练/下载/环境。raw `~/mechpop_cache/e153_mmlu_source_transfer/`。

未运行，未升级主张。该卡不是看到新任务结果后的POST-HOC补写。
