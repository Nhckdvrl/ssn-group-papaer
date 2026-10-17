# E31：原人类/NPC任务的动作目标与行动顺序资格（2026-10-14）

- **状态：** DONE
- **类型：** REPRO / measurement资格；不声称评价器缺陷或新机制。
- **对应：** C01 / P07；E14/E16自然任务，非新训练idea。
- **问题（一句话）：** 原严格human-demo join中，哪些双方作者动作目标在原物理规则下有顺序依赖；事件完成与最终持有状态分别意味着什么？
- **设置：** 固定LIGHT pin71a06c…，原quests、2111human demos及已有strict join692；不改角色、目标、物品、位置、reward。只读source evaluator协议，再用原OOGraph/Event在CPU完成动作闭环。先全join逐条尝试双方原goal事件（两种顺序各从同initial clone开始），保留随机steal成功/失败及source门控；按原角色字面goal、motivation和实际player actions记录，不将“拿到物品”偷换成“完成偷窃动作”。随后仅对原目标中有共同对象的资格case，在原合法菜单内以该对象get/drop/give/steal及双方原goal做≤4动作的有界reachable查询。未找到只说bounded not found，不证明全局不可达；随机结果与结构合法性分开，source callback未恢复处明示。
- **读数：** source join/data sha、goal actor/对象解析、初始合法性、先A后B/先B后A目标可解析/执行/物理结果；实际human历史的goal事件。任务筛选由source语法/共同对象决定，不按模型成功筛选。枚举路径/合法返回/状态变化留档，goal EVENT和物理持有独立，不先制造抽象效用gold。
- **阳性对照：** 已有E14原12graphs成功gate；原give与steal都调用source，非法scope/持有拒绝且state不变；归还物品/取回均需真动作，不直接重置owner。每序列initial clone同一，路径预算和随机seed3101固定。
- **噪声地板 + MIE：** CPU结构资格无persona效应/MIE，无LLM/训练。随机steal原success_prob不能当确定的ordering effect；遇到随机失败单列，可用独立预设seed3102/3103重放资格但不挑幸存seed。任何有限路径只提供witness，不作不可能性证明。
- **混杂审计：** 原goal是作者的特定动作指令，动机文字未给唯一效用函数；事件与持有不同不自动等于错误评测。两作者quest绑定不是原RL训练partner或原bot私有goal复现；人类log只保证来源，不把机器人修改后的世界中的脚本动作当真人适应选择。包含人体与NPC的原始目标/动作可见性，后续model task需另卡。
- **决策表（跑之前写）：** 有自然顺序witness→选能区分协调能力/自身利益/玩家请求的具体任务，再写最小模型实验；只有已知goal字面问题→校准读数、不包装idea；缺可靠join/门控→继续源审计、不造toy；无高信息任务→保留负结果，转其他原生目标任务。
- **算力预算：** CPU≤30分钟、0GPU/API，既有fgvd/deps；raw在cache/runs，Git仅摘要与路径。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
首case CPU成本gate完成：1.37秒，原give/steal三seed均保留，存在原生≤4动作joint witness。实现预设每case最多500展开状态，超过仅记cap hit，不否定可达性；这一计算截断不改变goal/世界规则。全部strict joins资格扫描启动，0GPU/API。原QuestEnv.act按action_seq字面progress计分，当前只审其来源，不把OOGraph EVENT记录冒称完整原RL reward复现。

全扫描完成，61.35秒CPU/0GPU/API：692严格human joins形成1343双方quest配对，156有同物品，145至少一个预设seed有≤4动作joint witness，118三个seed均有；47可在≤2步，98的所有找到路径都需>2步，0case hit500state cap。有限深度未找到不证明不可达；同图/同quest多human demos相关，不作总体比例CI。“any seed witness”是存在路径，不是筛seed后的模型成功率。

同物品的两种顺序×3seed原goal事件1278次执行，其中1197没有源随机失败，差81是物理执行层，不改原事件计数。例boar/thief：give使boar持有煤、human的steal事件随即不合法；source两动机的真实效用（take coal/陷害boar）并非持有唯一gold。另mother/husband都get plate，但motivation分别盛食物/布置餐桌；get/drop/get witness只完成动作，不代表两人已吃饭/布置完成。

[结果与边界](../results/E31_human_goal_order_qualification.json)，raw cache/runs/e31_all_human_goals。此数据提供自然任务候选，同时证明不可把joint event witness当共同利益实现。尚未选一个能改变科学判断的模型pilot，先审实际human对话/行动与角色目的；不为了矩阵再跑全部模型。C01仍L1，新增科学贡献0。
