# Shape / OLMo / Hybrid 探索：历史否定结果与测量陷阱

**状态：** CLOSED，原 `workbench/shape-olmo/` 已退出当前仓库树；**不是**活跃论文或实验授权。精确的旧测量与脚本可在 [清理前 Git 快照](https://github.com/Nhckdvrl/ssn-group-papaer/tree/81e319fdc3414b7b6d16c8950f0046646d198cb1/workbench/shape-olmo) 中查证。此处是简短的科学归纳，不代替原始结果。

1. **Hybrid token 级“签名”不能直接归因于递归状态追踪。** 在尽量匹配的 Pile 架构三联体上，内容/首次出现/重复的损失模式与单纯增加规模或延长训练高度相似；hybrid 首次出现 token 约 0.05 nats 优势在只保留近期 32 token 时仍存在，不能用作远程 discourse-state 证据。
2. **OLMo-Hybrid 的部分退化属于后续 DroPE 长上下文阶段，而非预训练混合结构的必然性。** 重复、闭括号、代码任务下降随训练阶段形成；较多候选时从前文选取目标出错更明显。不能未经对照外推成所有无位置编码的 hybrid 都有 primacy；Granite / Nemotron-H 提供阴性对照。
3. **失效对照与复现障碍必须一同记录。** Llama-2 DroPE 对照常规文本 NLL 差约 0.58、内容题接近随机，该 checkpoint 不具备强因果参照资格；OLMo-3 / OLMo-Hybrid 官方发布版并非“只差架构”；Transformer 库版本还存在 YaRN 行为风险。

**可迁移研究动作：**（a）跨架构比较先审计数据/训练/位置配方；（b）对看似结构性优势增加 scale/training-matched 对照；（c）明确区分历史信息来自远端还是近端；（d）对后训练阶段的行为变化做 checkpoint 定位。以上主要是**负结果与测量卫生**，未形成独立新论文。
