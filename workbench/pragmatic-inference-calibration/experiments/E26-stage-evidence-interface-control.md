# E26：原任务中的训练阶段与输入入口控制（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2–D4，技术混杂排除，不是新metric
- **对应：** C02/P02/P09；E21/E22出现Base聊天选项质量低，stage与接口混杂
- **问题（一句话）：** 训练阶段对说话者知识条件下的解释与撤回推断的影响，能否在原始文本入口及同一聊天模板下测出；生成格式失败与条件概率读数是否给出不同边界？
- **设置：** Qwen2.5-3B Base SHA3aab1f1954e9cc14eb9509a215f9e5ca08227a9b / Instruct SHAaa8e72537993ba99e69dfaafa59ed015b17504d1；EPITOME原784 unique原子题、SI760原下注题，不改题；原子bare和一句format/common Instruct chat两入口，下注bare/common chat各一，不加救援prompt。OLMoE Base9b0c1aa87e34a20052389dce1f0cf01da783f654 / SFT6f7a5b02aa069fdcb8d0cb6b837b9905a3d995d7，ImplicatureX原271×6states×2orders×parent/format，补bare入口，对照E21 common SFT chat。独立8GPU、FP32、TF32关、batch8；max50/first-newline下注parser与E20完全相同。
- **读数：** 原EPITOME9个access/utterance条件的连续delta p2/p3与knowledge correctness，保留原rounded score；下注valid/invalid/truncated，全40items accuracy上下界，不对有效子集作无条件能力解释。原子选项总质量/global top是否在候选内单列。ImplicatureX四类分报baseline、cancel-minus-irrelevant、support mass、原recognition/joint；paired item bootstrap2000 seed0，不赋SDT gold。重点stage×入口的交互，不进行总分排名。
- **阳性对照：** 源文件SHA与原prompt严格校验；Base/Instruct全部匹配token IDs及common template；已有E19 Instruct数值与bare原子重跑校验（新增support记录不改概率算法）。首末batch1/8概率与质量差<.001；不通过则停止该run，不解释能力。下注warmup及错整数/parser fixtures沿用；E21 canonical一致。
- **噪声地板 + MIE：** deterministic数值gate，CI只覆盖题目抽样；无独立训练种子，微小取消delta保留.001边界，不将符号翻转自动当finding。约2GPU时内有信息的interface audit；无新论文MIE。
- **混杂审计：** 两谱系训练数据/目标变更不能归因纯RLHF；Base common-chat是控制而非native。low support不能据归一化判断能力；无效生成不当pragmatic error；IR只有6完整源题，不填缺失。知识问题和解释问题不同字串，非机制证明。原some与numeral语义争议按2013/EPITOME记录，不自造negative条件。
- **决策表（跑之前写）：** A stage对连续证据效应在两入口一致且候选支持充足→进入跨谱系/现象边界测量；B stage差主要随入口/支持质量消失或反转→elicitation混杂，不能解释为能力提升；C只有初始endorsement改变、条件效应不变→推断倾向解释待后续更直接控制，不称criterion finding；D生成不可解析且atomic有信号→该生成协议不可用于能力归因，保留失败，不追加prompt救故事；E source/token/numeric失败→隔离并审bug。
- **算力预算：** 8独立卡：0/1 Qwen两stage原子；2/3 Base下注bare/chat；4/5 Instruct下注bare/chat；6/7 OLMoE两stage ImplicatureX bare。预计≤2GPU时。GPU4/5其他常驻进程保留，锁只协调本项目。无训练/闭源judge/子agent。

## 结果
跑前冻结。结果落外置runs/E26-*；只汇总派生结果入git。读数、入口与parser不在见结果后修改。

### 2026-10-03结果更新
已完成本卡原运行；后续stage输入差异见E27，旧raw保留。派生数字见results/E21-E23-implicaturex-stage-summary.json与results/E22-E26-stage-controls.json。未升级C01/C02；技术/任务描述不当能力finding。
