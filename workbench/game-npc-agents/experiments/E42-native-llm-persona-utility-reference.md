# E42：作者LLM决策范式的本地强模型利益控制参考

- **状态：** PLANNED；先CPU接口与单完整episode，再并行。
- **类型：** D1/REPRO＋竞争解释测量，不预设新方法。
- **对应：** I03/P10，E34/37/41中的语言角色输入、功能控制与训练经验。
- **问题：** 同原角色/身体/世界/利益读数，未经RL的强LLM是否已有C属性利益控制？源个性表述与普通具体偏好提醒的差异，能否解释当前学习政策的观察？
- **来源与边界：** 作者B5 llm_policy.py是v1/12动作/1.7B/greedy；其文档明确v3需重写prompt。本次恢复其“人物＋可见游戏state→原合法动作”范式，明确称v3本地强模型参考，不冒充原1.7B表格复现。原v3-large/20动作/16NPC引擎与奖励函数不变。
- **竞争解释：** H1语言属性本身可理解，但策略形成/覆盖不充分；H2原抽象表述或目标信息不够具体，普通提醒即可恢复；H3实际状态中多目标利益相容/有动态成本，所以不应要求每次换C都换动作。所有结果与E37机会/完整四格一起解释。
- **设置：** 原E33五base401/421/441/461/481、15固定peers、world33011/12/13，C输入high/low，固定原身体与其他traits；每条件30个原生200cycle episodes。focal LLM；15伙伴分别用E34 No300或Full300 seed42原policy，两个自然社会策略环境。两个已缓存强模型Qwen3.5-27B/Qwen3-32B，greedy/nonthinking/8outputtokens/无付费API。两个prompt：原范式persona/needs/action菜单；仅追加一句“作者给定的此NPC偏好动作是…；同时照顾当前needs并按角色和处境选择”。披露的是本人作者偏好，不是隐藏世界reward或唯一gold；该句和额外信息单独记录，不能称纯措辞效应。
- **观测：** 69维source obs以逐字段数值呈现，自己与其他人位置/need信息严格沿source；不提供全局隐藏needs/trait/奖励向量。所有条件共享20动作菜单及作者公开动作恢复说明，避免不同接口能力伪影；无行动历史符合原B5无记忆协议。高/低私有目标在同一实际action tape上用原两reward配置计分并核物理byte一致，与E33相同任务绑定限制。
- **三层范围：** 人物表达为作者原文输入；决策指令未额外做自述问卷。Contextual intention不由单个数字假称语言意图。实际LLM首输出、解析/原随机fallback、合法执行和world后果完整记录；随后可在独立相同状态测具体意图，不能污染本episode。
- **读数：** 原利益完整四格/J_H/J_L/DD、needs状态、20动作分布、首输出合法率/随机fallback、成本；局部机会与轨迹分列。5base×3world均保留，两个模型同一Qwen系非独立模型族。不挑seed/checkpoint/最佳prompt，也不因没有crossover舍弃结果。
- **阳性对照：** source E33固定tape物理与reward差已经数值验证；69obs逐字段解码/重新拼回完全一致；相同greedy模型/输入数值重复动作。普通具体偏好句符合R8恢复对照；fallback次数可审计，不混作人物控制。
- **噪声地板 + MIE：** 原三个world重复/两模型/两个伙伴策略；greedy重复与世界动作相依分别解释。不设幅度/比例/自动科学淘汰bar。
- **混杂审计：** 基础prompt增加v3动作恢复说明，是必要适配并全部共享；具体提醒披露本人偏好带额外信息/长度，不能从其差异归纯语言机制。伙伴固定seed42不代表全部训练不确定性。两counterfactual reward worlds由同动作tape维持physical parity，同行信息协议沿E33，不推一般真实公共人格变更。
- **决策表（跑之前写）：** 强模型自然控制有效则保留正向结果并缩小RL特有解释；普通句足以解释则承认目标/接口绑定；若仍混合则用机会/轨迹定位而非预定loss。不是为gap造场景，不换原规则或评价。
- **算力预算：** 单CPU观察/固定动作核对及单GPU完整episode测实际成本后，最多8单卡worker（fvcrc21/20各四已空闲）运行2模型×2提示×2伙伴策略；每worker30episodes，共240/48000focal LLMcalls/768000 native physical actions。batch仅跨独立世界，单世界所有actor都fresh AEC；现有fgvd/deps、缓存模型，0付费推理/无云fallback，无跨节点同步。若成本与预计不同按测量调整并记预算，不能据此自动判科学价值。

## 结果
尚未运行。

单局成本/接口结果：CPU两case控制.080秒、69obs数值往返逐byte、两利益世界physical parity；本地27B完整原生200cycles/200calls，无随机fallback、重复输入greedy输出相同。model load159.10秒、整个任务403.55秒（含导入/加载/原生执行），采用跨30个独立世界batch预计每worker约15–40分钟，以实际进度记录为准。每条件相同200cycle与原利益四格不变；现在展开预定八worker，不设科学bar。
