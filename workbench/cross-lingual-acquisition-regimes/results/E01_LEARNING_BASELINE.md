# E01：有效学习 baseline 与研究增量边界

本轮对应P01/C03；结果汇总见 `nli_analysis_seeds_17_29_43.json`，完整学习曲线见 `nli_learning_curves.png`。
这不是新论文idea，不将标准NLI迁移优势写成贡献。

## 完整主比较

准确率百分数，均值±适配seed样本SD（17/29/43）；不是均值置信区间。

| 条件 | EN test，32768例后 | DE test，32768例后 | EN / DE，8192例后 |
|---|---:|---:|---:|
| FWB | 83.61±0.50 | 77.19±0.30 | 77.89 / 70.90 |
| MWB | 82.37±0.52 | 75.86±0.42 | 74.49 / 67.98 |
| MWB+P | 83.23±0.34 | 77.09±0.21 | 78.42 / 72.85 |

有效任务学习和迁移baseline已成立。MWB+P相对MWB终点DE约+1.23pp，
但EN也约+0.86pp；相对FWB终点DE约−0.10pp，不能声称普遍更优。
8192例时MWB+P对FWB的DE差异约+1.95pp，但必须连同四个预算点、seed波动和完整schedule解释，
不是事后选早期快照证明新故事。没有独立操纵目标语先验能力，不恢复acquisition领先解释。

终点DE配对item bootstrap 95%CI（pp，条件于本次适配seed）：
MWB−FWB −1.33 [−2.09,−0.59]；MWB+P−MWB +1.23 [0.50,1.96]；
MWB+P−FWB −0.10 [−0.88,0.64]。
POST-HOC promptID cluster CI分别[−2.09,−0.55]、[0.51,1.96]、[−0.85,0.67]，
与预注册读数定性一致，但不构成独立实验或总体参数seed置信区间。
三适配seed内终点DE contrast SD分别0.14/0.40/0.26pp；8192例时MWB+P−FWB contrast SD达1.98pp。
因此不能只凭早期item CI很窄就说学习效率优势稳定。

## 识别对象

MONOWEB三组34K权重在相同英语MNLI监督、分类结构、训练预算和recipe下的EN/DE学习曲线。
三适配seed17/29/43全部报告，不按源语或目标语结果选seed/checkpoint。
每个主cell32768例、一遍、1455666有效输入token；相同tokenizer/input/head hash经分析器校验。
0/2048/8192/32768例是同一完整学习率schedule内的快照，
**不是为各预算独立优化过的学习效率/Pareto前沿**；早期差异不能脱离warmup解释。

## 能回答与不能回答

- 能回答：这些有真实数据干预的checkpoint是否能学会任务；冻结终点评测是否遗漏适配后差异。
- 不能回答：正确pairing的纯因果作用、acquisition状态的独立交互、所有reasoning任务的共性。
- 单预训练seed、单EN/DE家族；三适配seed只支持该家族内重复，不代表预训练重复。
- 跨条件英语能力也可能不同；德语优势不能全部归为额外的跨语言桥接。
- 原预注册paired-item CI条件于三个适配seed；另报seed SD，不能冒称总体训练分布CI。
- XNLI同prompt有三个hypothesis，追加POST-HOC promptID cluster CI；不替换预注册读数。
- train/dev完整pair不重叠，但dev702条共享train premise；EN test共享premise3条。
- 原始XNLI ZIP与HF逐文本/label/pairID核对；test没有参与recipe选择；预训练污染未控制。
- 分类checkpoint为backbone+新分类头，没有随任务微调的LM head；不能直接用它报告生成/翻译遗忘。

## 定位与下一项训练选择

| 已有对象 / 近邻 | 已有ownership与compression risk | 后续需要实测的增量，而非现在的claim |
|---|---|---|
| 英语任务学习→跨语迁移：False Friends / PreAlign | 标准迁移优势早有证据；仅加曲线/种子容易压缩成baseline | 找到会改变真实适配选择的失败，再用训练干预改变它 |
| 新知识与独立桥接：AdaXEval / LINK | 知识/桥接分离、域外语言干预不是空白 | 同内容、源语暴露与预算下，新内容翻译是否必要、旧桥接能否复用 |
| multilingual mixing：Building Multilingual Bridges | 普通非reasoning数据、混合时机促进迁移已有强预印本 | 不只胜过EN-only，要胜过有效的内容覆盖/混合baseline并解释成本 |
| 持续学习replay：Leitner replay / Active Forgetting | 遗忘、难度选样、learnability本身已有方法 | 若维护桥接有实际价值，区分保旧任务标签与保跨语言接口 |

后续探索优先绑定实际决策：每批新内容是否都要翻译，还是能复用不含新内容的桥接？
先选择明确的学习任务、有效训练基线和可验证的成本；对照必须有自然完整unpaired文本，
不能只用错误pair造成的损伤来推断正确pair的收益。
原先九宫格从头训练不默认启动；同起点短程训练、适配方法均允许，依具体识别信息选最小干预。
若目前差异完全随英语学习一起变化，下一动作应区分源语学习和额外迁移，而不是缩小冻结probe。
若当前差异很小，报告分辨率，不把CI跨零当等价，也不在桌面上关闭领域。

本页是实验解释与定位，不是人签字的状态变更。持续ACTIVE归属仍需统一调度确认。
