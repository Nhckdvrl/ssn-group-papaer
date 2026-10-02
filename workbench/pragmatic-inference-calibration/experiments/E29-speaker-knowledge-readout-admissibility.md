# E29：原知识问句的角色/表达/极性可识别性（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / controlled intervention，触发来自E26已观察结果，非预注册scientific claim
- **对应：** C02/P02/P09；知识control未有效，不能继续把detect/use差作解释
- **问题（一句话）：** source知识问句的低分，来自区分说者/听者、量词表达对知识的影响、Yes/No极性偏好，还是各入口都不能测出原知识条件？
- **设置：** 原EPITOME40items×9access/utterance=360知识问句全量，无选择异常子集；8模型Qwen2.5-3B Base/Instruct、Qwen3-4B、原Qwen1.5-14B-Chat、OLMoE Base/SFT/DPO、FlanT5XL，SHA沿用E19/E22/E27manifest。bare/common-chat（Qwen2.5共用Instruct完整tokenizer，OL完整SFT tokenizer；Base聊天是控制非native，Flan两入口同raw只作指令对照）。四变体：原问句；原问句前一句明确‘说者的知识、非听者得到的信息’；去掉同引语中量词陈述，仅保留原looked-a-of-3句；原问句know改does-not-know，反转Yes/No原parent方向。FP32/noTF32，batch8，每run2880reads。
- **读数：** 原access规范full=Yes/partial=No及负问反向，按九条件报告P(parent-norm)与argmax/选项support、two-polarity一致性；roleclarification与access-only原题paired Δ、item-cluster2000bootstrapseed0；原parent概率与既有E26/E27 atomic逐项校验。这不是licensed/unlicensed inference标签，也不是新能力metric。
- **阳性对照：** 源CSV/SHA/784prompt重建同E19，360知识keys唯一；原问句动词与删句regex逐项assert，只修改指定片段，保存各promptSHA与原key。各模型Yes/No一token，首末prob/mass batch1/8<.001 gate；旧概率差> .001则隔离，不解释恢复。模板完整而非字符串，OL共享SFT BOS50279。
- **噪声地板 + MIE：** deterministic，CI只item抽样，无训练种子；原parent知识规则只是该任务规范，不称模型真实心智。effect大小及负问方向一起看，不自动用小sign升claim。
- **混杂审计：** actor clarification改变attention/指令；去量词会改变communicative evidence，不等于纯单神经机制；negative增加否定难度，因此要原问、反向与删句联合。full perceptual access对应know遵循2013/EPITOME知识check，人类也不完全如此；不能自动当objective binary warrant。Base/chat支持弱不能据归一选择断能力；T5重复接口不算独立证据。E26出现异常后才设计，本卡是跑前冻结的followup，历史现象不是预注册发现。
- **决策表（跑之前写）：** A一句角色澄清恢复且极性一致→知识readout具有elicitation混杂，不能称latent能力不足；B去量词恢复而澄清不恢复→值得查表达与access证据交互，先strong-model/语义审计，EPITOME已有knowledge-use ownership；C极性不能反转→Yes/No偏好或否定/task混杂，原control不适于能力解释；D原问强模型已正确→小模型lead降级，回主问题；E各种入口均失败/支持低→readout不可识别，不扩大为语用能力claim。不新增救分prompt或挑某入口写finding。
- **算力预算：** 8独立卡，按模型各一slot，等待E27已有GPU锁释放；≤2GPU时，无新下载/训练/API/子agent。源history与serial protocol不改成paper精确复现，只有parallel发布材料的控制。

## 结果
跑前冻结，原题与全部失败保留；instrument control，不宣称novelty。

实施校对：首轮八作业在加载模型之前全部因access句匹配过窄而停止，0条预测；原始目录/日志E29-knowledge-*保留。item36原文met、item38原文listened to，现按三种原动词保留第一句并删除第二句；360原题×4变体CPU全量校验通过，资产data/E29-stimulus-preflight.json。重新运行E29-r2-knowledge-*，不改变实验决策/读数/样本。

完成：8模型各2880、共23040原始读数，首末gate通过；全量旧parent概率校验发现OL SFT/DPO裸各1/360差>.001（.002337/.002949），两个入口仍隔离，E30另卡debug。results/E29-knowledge-controls-complete-summary.json保留所有描述与quarantined字段，40item cluster。Q3chat role fullnorm .93854→.99996，但partial a1 .64767→.05150、a2 .19686→.00565；full正负问一致性.18125。不能称“知识恢复”或latent failure。
