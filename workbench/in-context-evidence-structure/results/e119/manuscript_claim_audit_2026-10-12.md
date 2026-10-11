# 整篇论文的关键主张适配审计（2026-10-12）

**性质：paper-critical 论证审计，不是新一轮原始数值封版。** 对应 C21–C24/P17；未跑 GPU、未改科学脚本/读数/claims/论文、未调整等级或工作台状态。原 E115–E119 数值审计保持封版。

**结论：已有证据支持有界的形成路径解释，并已接回允许读取全部来源的预测；尚不能把 actual-donor 重建直接当成原生操作的必要性证据。** 最重要的是明确解释对象和补一个操作层面的竞争检验。C24 的完整矩阵是有效功能证据，但不能替这条缺失的推断。若全文坚持“选定反事实的部分形成解释”，不需要为了剩余误差枚举全部网络；若标题/摘要要让读者理解为共享输出原生耦合的操作解释，下面第一项应优先。

## 问题—已有证据—缺项

| 问题与主文位置 | 已有证据能支持什么 | 仍缺什么/如何对齐 |
|---|---|---|
| **1. 充分的 donor 路径是否是自然运行中承担该效应的操作？** 摘要末句 “explain how”、Introduction 第19行 “a causal account”、§7第168行 “an explanation … subsequent native prediction”容易比实际证明强。§3第54行的“非必要/非唯一”说明是正确的。 | E109/E112 限定 B 历史答案 sender、A-label receiver、全层、不拟合系数，仍重建 namespace 的逐 query 双差分。这并非把 donor A-label 本身恒等复制：本次 raw 复算 K 的 Qwen/Mistral r=.969/.966，RMSE=.810/.265，zero=3.267/.865。E114/E119 还测了全 A target，并非只有 label：Qwen E114 B-shared 下 KV 对 label r=.899/RMSE1.560（zero3.388），对全 A r=.808/2.318（zero3.926）；14B 对应 .934/1.047（2.610）、.908/2.007（3.620）。功能参与及部分预测成立。 | 现有干预先重算 prefix，再只把 A-label 缓存放回 recipient；其余缓存恢复原样。未直接检验在完整原生 prefix 中移除该消息操作后，namespace/关联效应是否按预测减弱，以及是否只是一般扰动/attention竞争。弱 prelabel donor 不等于 prelabel 原生计算不必要；actual donor 高 r 也不排除冗余或替代通路。当前可写 “a partial causal reconstruction of specified formation counterfactuals”；不能据此称主要/必要/唯一原生操作或给中介份额。 |
| **2. 自然多来源任务的有效功能与受控模板机制是否已连上？** Introduction 第11行的 annotators/users 入口与 §9第194行的真实文本范围。 | 单方面受控情绪任务中 single-A 很强，三家族/14B 有直接形成阳性；E116 真实 MHS 文本有 .344/.0645/.112 nats 的 native 局部形成作用，原阳性仍成立。 | MHS single 私人规则约52–63%，不能区分可靠学会规则后的证据形成与弱能力条件下的局部敏感性。当前 §9 的限定准确，摘要不能把该结果读成人类私人标准的可靠学习/部署。若要支持超出简短模板的功能解释，需要一个模型能独立学会两种私人方向的自然文本设定，而不是再加一个 floor 附近数据集。 |

**一个可直接改文、无须新实验的目标指代问题：** 摘要 “criterion-related functional responses … the label-formation pathway only partially reconstructs the latter” 容易将 E119 的 r=.668、RMSE=.646 vs zero=.746 指向 whole-history native criterion 响应。实际 target 是 criterion 反事实下的 **actual A-label 交换**。建议明确写 “partially reconstructs criterion counterfactuals at the label interface”。§6.3/C24 的正文范围基本准确。完整 native、label 与 edge 改动不同缓存接口；其矩阵不同不识别不同程序，也不证明标准信息只能在某阶段形成。Food 固定在 Service 前，当前只能陈述固定词序下的方面功能区分。

## 最多两项决定性实验建议（未执行）

1. **完整原生形成的靶向移除与局部恢复。** 在既有强阳性单方面任务、冻结家族/全层/接口上，对 shared/far × B私人配对逐条件运行：只移除过去 B答案→A-label 的形成消息，允许所有后继位置自然演化，query 消费整个干预后 prefix，保留 native 与配对 A-only 读取。用同一 context 的干净 A-label 缓存作局部恢复，并以跑前冻结的匹配非目标形成边和 single-A 功能作扰动对照。首要读数是 namespace×B-rule 的有符号双差分、原始 logits 与完整标签正确率，不能只看整体 accuracy 下降。
   - **形成操作承担原生耦合：** 靶向移除选择性降低该效应，局部恢复带回方向性作用，明显区别于一般能力损伤。
   - **构造性 donor 路径/冗余直接读取：** donor 重建仍好，但完整 native 效应基本保留；若仅 gated 明显减弱，应限定该操作的条件作用，不能把旧阳性作废。
   - **一般扰动：** 与匹配控制/单来源能力共同下降、且不能选择性恢复；不能仅由 knockout 掉分宣布操作已识别。
   操作须在新结果前定义；消息置零与 softmax 重归一化不是同一个干预，不能在结果后选更有利版本。无需扫描头、层或系数，也不要求排除全部冗余机制。

2. **在可可靠学习私人映射的自然文本中冻结复验同一操作。** 只选一个自然情绪分类设定、两家族、新材料确认；A固定，独立交叉 A/B私人方向与共享/分开输出，B固定 label stream 的跨类/同类配对对照沿用，不按模型逐例正确筛材料。同时报告两方向 single-A 阳性、native 配对效应与第一项冻结操作的作用。**学习到的 B关系进入 A证据**预测效果随 B私人约定而反转、依赖新 query 的情绪；**静态输出偏置或一般文本扰动**预测主要共同偏移/同类移动，不能稳定给出该关系双差分。这项回答机制的自然文本功能范围；不要求自然 annotator 身份或应用修复。若不主张这层范围，当前真实 MHS 的有界 margin 结果可保留，第二项不是自动投稿门槛。

## 近邻提供的方法依据与实际阅读范围

- [CTA §3.1–3.3](https://arxiv.org/html/2504.00132v2)：在完整/受限位置图中比较性能，再改变 donor 的 identity、space、mapping；歧义任务令“仅聚合”与“上下文化”产生竞争预测。这里可借鉴必要路径与功能对象的连接，不能把其 ≥90%恢复要求照搬成本文资格阈值。
- [Crosbie §7、Limitations](https://arxiv.org/html/2407.07011)：特定 pattern knockout 与整头消融比较，区分组件参与与操作；该操作检验限抽象任务，作者也不称唯一机制。已核正式 [ACL 条目](https://aclanthology.org/2025.findings-naacl.283/)，本次未逐页比对正式63页 PDF。
- [Cho §5.1–5.2、A.7](https://arxiv.org/html/2410.04468v3)：连接消融带匹配随机控制，保留 bypass；说明必要性、特异性和充分性是不同问题，未完整枚举所有算法。

本次完整读当前 PAPER_DRAFT、C21–C24、最新 PAPER_SHAPE/README/日志，重读 E109/E114 卡、消息干预与冻结预测实现，参照已封版 E109/E114/E115–E119 独立审计。重新从 raw 点算 E109/E112 的四通道 namespace r/RMSE/zero，以及 E114两家族/E119 native 的 label/全A重建与 signed 交互；E115–E119全部原始评分、样本几何和全层消费在此前本独立会话已核。**本次没有重新复算 E90/E91 或所有历史实验，没有独立 GPU 重跑，也未读尽近邻全部代码/附录。** 引用的 CI 沿用已有 raw 审计，本轮点算不冒充新的 bootstrap 确认。E120/E121 在读取时只是空骨架，不视为已完成证据。

审阅稿快照：PAPER_DRAFT SHA256 `b4d92cad796b9523ef35bad534ffc042ef2c5a84e2e6e2e6e2f8f7096ad703f34f3a`；CLAIMS `d018ee5aa02af145da6e823d1151308fe1ab9428018445e1c4bce547f9ea5da0`。仓库 process check：0 ERROR、33 WARN，包含历史卡警告与两张新增空骨架。
