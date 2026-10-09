# Model Diffing as Measurement — 可复用知识卡

**类型：** METHOD / PARENT MAP / MEASUREMENT DESIGN（不作为独立 `workbench`，没有本项目新运行数据）  
**来源：** `workbench/model-diffing-measurement/README.md`，2026-09-29 至 2026-10-09 的桌面调研；在 2026-10-09 按用户决定迁入本题材并删除原项目目录。原文见 [2026-10-08 前 Git 历史版本](https://github.com/Nhckdvrl/ssn-group-papaer/blob/a1d7dace5dc4513bdc43255d4166742fdc608cea/workbench/model-diffing-measurement/README.md)。

## 1. 研究对象：模型发生变化时，测量究竟多给了什么？

给定 base→SFT/RL/post-training 的模型对，差分方法可能从以下层级报告改变：

| 仪器/可访问层级 | 能观察什么 | 不能直接保证什么 |
|---|---|---|
| 黑盒查询 / 行为测试 | 某些任务或提示的实际输出变化 | 所有未测触发与内部解释 |
| Logit/KL difference、Diff Mining | 输出分布的连续变化与可能的训练目标线索 | 变化究竟由内部哪个因果过程承担 |
| Activation Difference Lens / raw activation | 隐状态中读得出的训练痕迹 | 痕迹是模型自然使用的机制，或有独立信息增量 |
| SAE difference / crosscoder / learned decompositions | 稀疏或可读的跨模型特征变化 | 特征是唯一解释、泛化稳定或因果必要的 |

中心问题：**什么时候访问模型内部，能在匹配成本与信息量的前提下提供行为/logits/直接激活差分没有的可检验增量？** 这不是“复杂方法必然优于简单方法”，也不预设开发新 crosscoder。

## 2. 必读的直接先验与已被覆盖的宽结论

| 论文/资产 | 给本问题的教训 | 证据属性 |
|---|---|---|
| [science-of-finetuning/diffing-toolkit](https://github.com/science-of-finetuning/diffing-toolkit) | 同一 harness 放行为、KL、ADL、SAE/crosscoder、Diff Mining 和 LLM 解释代理；强基线优先 | ARTIFACT；复现入口 |
| *Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences*（ICLR 2026） | 窄微调目标可能在不相关文本的激活里都很明显；简单 ADL 是必要基线 | PARENT；警惕模型 organism 太容易 |
| [*Diff Mining: Logit Differences Reveal Finetuning Objectives*](https://arxiv.org/abs/2608.26462) | 简单输出差分可强于复杂内部解释，内省成本必须有额外回报 | PARENT / CHEAP BASELINE |
| [*Simple LLM Baselines are Competitive for Model Diffing*](https://arxiv.org/abs/2602.10371) | 对模型差分提出的泛化性、抽象度、interestingness 等评价，已直接研究“简单方法和内部方法谁更好” | DIRECT PRIOR / NOVELTY PRESSURE |
| [*Overcoming Sparsity Artifacts in Crosscoders to Interpret Chat-Tuning*](https://papers.nips.cc/paper_files/paper/2025/hash/9902a53031ebbbab73898028073d4790-Abstract-Conference.html) | 模型特有的稀疏特征可能是编码/正则化伪影 | NEGATIVE CONTROL |
| [Dedicated Feature Crosscoders](https://arxiv.org/abs/2602.11729)、[Delta-Crosscoder](https://arxiv.org/abs/2603.04426) | 模型差分新方法快速发展，“再造一个 crosscoder”不是默认贡献 | METHOD PARENT |

此表继承原计划的文献定位；**不是本轮逐篇独立全文复核，也不等于相关主张经过我们的实验验证**。宽问题“简单 LLM/Logit vs 内部方法谁好”已有直接近邻，不宜原样作为 novelty。

## 3. 可复用的对比实验设计（设计，不是已完成实验）

**基线顺序 R0–R4**：冻结开源 toolkit 的 commit、模型对、数据、judge、资源需求 → 在 released narrow-finetune organisms 复现 ADL → 同数据复现黑盒/行为/logits/Diff Mining → 复现代表性 crosscoder/SAE 方法 → **匹配评估者可见信息、token/query 预算、前处理 GPU 时间、激活存储与超参选择空间**。

| 操纵维度 | 对比条件 | 真正要排除的解释 |
|---|---|---|
| 训练变化的广度 | narrowly fine-tuned；与广泛数据混合；更实际的 base→SFT/RL | 方法仅检测目标到处可读的“窄任务签名” |
| Reference corpus | 随机预训练、domain、无关、特定非信息性文本 | diff 是参照分布/触发词的伪影 |
| 可访问的信息与成本 | 黑盒、logits、raw activation、learned decomposition；统一查询与 judge 信息 | 贵的方法靠看更多数据或 token 赢 |
| 测量的效度 | 可读性、held-out 行为预测、跨 seed 稳定、干预中的必要/充分性 | “解释得漂亮”被当作因果解释或真实覆盖 |
| 泛化 | 至少两个模型家族、两种变化 regime；小模型先行 | 单一 organism 外推成 LLM 普遍机制 |

**证据梯度**：已知训练目标的公开 organism（校准）→混合/不显著微调→公开多阶段 post-training→必要时跨架构。不要只凭单个模型或 LLM-judge score 就宣称度量工具有效。

## 4. 结果如何改变研究方向（预先的判别表）

- 如果行为/logit baseline 已解释全部可验证变化：继续找更现实的 **regime**，而不是立刻造复杂分析器。
- 如果内部方法只在稀有触发、广泛后训练或特定分布的变化上有用：界定**内部信息的独有条件**，避免“总体更优”过强主张。
- 如果简单 activation diff 胜过 learned decomposition：查特征正则化、信息损失、reference corpus 等原因。
- 如果 learned decomposition 仅在因果 transfer/修复上提供可靠增量：将对象转为 **actionability**，做 held-out 行为和反事实对照。
- 如果实验对种子、语料或 evaluator 高度敏感：对象可能是 **measurement reliability / identifiability**，而非一种新算法。

## 5. 使用位置与边界

- 这是可供 [机制与表征](README.md)、[工具地图](INTERPRETABILITY_TOOLING_2026.md) 和实际科学测量研究引用的**知识素材**，不再登记为独立 workbench。
- 与训练机制/跨 run 对应性相关时，可以把“结构差异/特征差异”同“功能与因果角色对应”作对照，**但不得自动替换任何正在进行的机制研究问题**。
- 科学效度与对照规则请同时参阅 [解释性研究版图](INTERPRETABILITY_LANDSCAPE_2026.md) §3（mediator、naturality、actionability、external validity）。
