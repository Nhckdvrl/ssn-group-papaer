# E72：裸续写、原生聊天与推理，是否面对同一来源条件化边界？（2026-10-10）

- **状态：** RUNNING（8B与27B均在原生生成；两模型候选评分已完整）
- **类型：** PILOT
- **对应：** I04/C17/C19/P12/P13；强模型意义压力测试，非新增方法。
- **为什么现在：** E71关系码实验可用已知prefix/shortcut解释；继续只在Qwen3-8B裸续写中定位状态，可能把接口/输出校准当稳定能力缺陷。需要直接对比native接口和允许推理的行为，允许强模型解决来收窄问题。
- **设置：** 固定8contexts seed72001，animals/fruits、yes/no、Alex/Sam；沿E58四个未见source×kind query，rule方向与code permutation独立随机。Qwen3-8B与Qwen3.8-27B（HF revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0）。两者同Qwen家族，后者为混合DeltaNet/attention；明确不是跨开发者的frontier证明。R1-distill等独立推理模型待该pilot明确再考虑，不用模型数量换增量。
  - source_only：16个带来源的word→label demo，无Tag/prefix扩展，query以Label:结尾。
  - linked_prefix / orthogonal_prefix：沿E71 D1，但code为Red/Blue；所有Source字段真实、可充分决定输出。query给定code只是已知前缀，不提供gold class；只取自然4queries，不加入歧义冲突。
  - entity_binding阳性：同样16记录/来源×kind平衡，用animal/fruit类别名代替具体word，query直接询问该category的来源label；是字面entity×property检索，难度/长度与推断category的任务不同，只作基本能力对照，不据差异证明新组合缺陷。
  - single-source阳性：source_only只保留所问source的8demo；不称能力上限。
- **接口条件：** raw默认 / raw加一句Source指令；chat关闭thinking默认 / chat关闭thinking加同一句Source指令；chat开启thinking加同一句Source指令。
  - raw记录两候选的精确continuation logprob，无自由生成；chat direct记录相同Answer:接口的候选logprob，另做自由生成。两类准确率分开报告，不能混作同一指标。
  - native chat user包含完整任务和最后的未完成记录，再要求仅报最终classification code（Answer: yes/no），不额外提供source rules/类别gold。Source指令为“Use only examples from the requested source; each source may use a different mapping.”
  - 关闭thinking沿tokenizer官方enable_thinking=False；开启thinking用官方template（Qwen3.8 reasoning_effort=medium，避免默认xhigh过长），最大2048新tokens；direct最大96。固定do_sample=True temperature0.6/top_p0.95/top_k20/seed0，所有条件同采样参数，1个样本/query；无seed/答对样本筛选，统计只覆盖contexts与这一采样协议。
  - parser只接受think关闭后/明确</think>后独立Answer: <label>行；thinking未结束、截断/无合法答案均报告并计入生成accuracy分母。不能从预算耗尽推出无法解决。保留完整生成文本与token数。
- **读数：** 各schema/interface的候选margin/accuracy/source排序、生成accuracy、格式有效率、截断率、token数；paired chat-direct−raw、Source指令−默认、thinking−direct（生成指标）。native与raw的输出规范不同，所以差异是接口整体效应，不归为单一prompt token因果。
- **阳性对照：** entity_binding与single-source；候选score同prompt重复no-op≤0.10nats；候选分数手动token重建≤1e-5；truth/cell计数与source反向labels断言；chat enable_thinking模板截断行为核对。代码/model/config/version/hash、所有case完整保存。
- **噪声地板 + MIE：** paired accuracy差≥0.10且CI不跨0，或生成/候选accuracy≥0.90且主要弱接口≤0.75，才进行32新contexts seed172001（occupations/vehicles、toxic/safe、Alice/Bob、Left/Right）有界确认。若positive controls<0.80/无效格式>10%/thinking截断>10%，先界定接口/预算限制，不扩大模型表。不做两候选NLL跨model绝对比较。
- **混杂审计：** chatting与raw不是token等价；家族/架构/训练阶段不独立操纵。生成accuracy与候选accuracy不能互换。仅两语义类别，真实人类标注者未覆盖。reasoning内容不因看起来合理而视为忠实机制；本卡先约束能力范围，不宣称内部计算改变。候选与额外监督无训练，不在query给gold。
- **决策表（跑之前写）：**
  - strong native/default轻松解决 → 收窄“默认来源失败”的模型/接口范围；不增加困难格式强保现象，也不宣布ICES所有机制价值消失。
  - 一句Source指令已恢复 → 优先策略/接口激活解释，不能叫容量缺失。
  - thinking额外恢复 → 支持预算/程序补偿的行为线索，后续才检验trace/路径；不从CoT文字直接推出机制。
  - entity与single好、混合坏 → 可探索条件组合；仍需等价难度、output校准控制，不能仅此宣称双能力无法组合。
  - candidate好而自由生成坏 → 保留输出格式/采样解释，不把parser失败当绑定缺陷。
  - 所有接口仍差且controls好 → 只支持指定有界任务边界，再选真正独立模型确认；不能称普遍计算规律。
- **算力：** 单节点本地GPU1为27B、GPU0在E71结束后跑8B；优先conda（27B openslime，新transformers；8B verl-clean）。模型从已完整HF snapshot暂存NVMe一次，预计55.6GB复制约15分钟（NFS弱I/O，不计GPU科学运行）。先加载/小n完整pilot，不并行下游训练；默认卡空时不抢其它进程。
- **产物：** scripts/e72_native.py、scripts/analyze_e72.py；results/e72/*/run.json与analysis.json入git，prompt/score/generation JSONL和模型权重不进git。
- **定位：** E46b/E09已有指令与thinking边界；Cho Hidden Calibration已指出token决策空间不等于hidden分类能力；本卡为研究意义的压力测试，不据此宣布新机制。Qwen3.8仅代表较新本地推理模型，不替代闭源frontier/独立家族。


## 运行中校对（不是最终能力结论）
- 两模型完整加载，language missing/unexpected/mismatched keys为空；27B为text-only兼容loader，vendor transformers，无MTP加速。原始loading_info保留。
- 8B四种候选score共640行已完整，no-op/token-sum=0；direct96-token自由生成多为长分析未结束，包括single/entity阳性，说明回复预算不足。保留原输出，不能把低生成accuracy当绑定缺陷。
- 27B四种候选score共640行已完整、控制见control_report.json；原生生成与8B的2048-token thinking仍在运行。缺少有效接口/预算控制时不触发独立能力确认，不把未完成推理当不具备能力。
- 原模型/seed/读数不变；下一步先设计同prompt、相同采样前缀的短/长预算配对校对，预定后执行，不后补成原卡成功。
