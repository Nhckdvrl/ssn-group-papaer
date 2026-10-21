# E01/E02原回复的POST-HOC言行审计

复读Qwen四条件全部48条Preserve输出，未重跑模型、未改变旧动作计分。口径见[AUDIT_RUBRIC](AUDIT_RUBRIC.md)，逐条raw哈希/理由见[annotations](historical_audit_annotations.jsonl)。同执行agent审阅，非独立真人评价。

| 旧条件 | Action Match | 审阅Effective范围 | 备注 |
|---|---:|---:|---|
| E01 Situated | 7/12 | 4–6/12 | 宫廷施压明确反向承诺；成年患者施压与宫廷基础场景有歧义 |
| E02 One Line | 8/12 | 6–7/12 | 宫廷施压仍明确反向承诺；基础场景条件隐喻有歧义 |
| E02 No Persona | 8/12 | 7–8/12 | 宫廷施压含可能演出暗示 |
| E02 Full Card | 11/12 | 11/12 | 11个动作命中项的台词均兼容；此处不抵消Change漏救 |

用户指出的言行不一致是实质证据：动作0/4翻转不等于对话0/4改变。但5/12是选定歧义解释后的一个可能值，不能称唯一认证真分数；基础court_solo也不能自动按明确拒绝处理。本审阅未证明“隐性投降”必然导致物理行为改变；引擎执行仍依赖具体接口。

另外两项机制解释需保留为假说：“not dying on my watch”可与救援脚本泛化兼容，也可能是夸张语气；未测内部严重度表征，不能断言感知被篡改。Original低分混合了公开资料/宴会歧义、Llama一次拒答及动作—台词冲突；E02 No Persona还保留正例纠偏，所以不能作为零反馈Helpful Prior的直接证明。当前三种策略不足以证明不可避免的plasticity/locality/coherence trilemma。
