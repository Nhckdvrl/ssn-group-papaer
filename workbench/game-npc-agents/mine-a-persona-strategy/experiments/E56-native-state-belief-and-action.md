# E56：自然台词后的任务事实读取与行动——边界、状态与取舍（2026-10-15）

- **状态：** DONE；三家族各2000完整原生分支、1200独立事实回答完成。
- **类型：** PILOT / 竞争解释；不预定“错误信念”或人格失效。
- **对应：** I04/P12/C02；E55自然satchel案例说已交付、actual仍自持，另有条件协商/合法长期目标；E53状态记录敏感性。
- **问题（一句话）：** 自己的社交台词之后，NPC怎样读取物品/完成状态并行动，差异来自仍处于对话模式、任务状态误解，还是合理目标取舍？
- **数据：** E55固定200 confirm原图、同一Step请求；每模型完整seed5501的两一致P自然u全部使用，不按执行结果筛。运行前要求每model source stage_outputs已含全部200×2，读取u后固定，不重生成、不换原任务。仅在初始物品仍自持、尚无物理行动的同一native图分支。
- **设置：** 三家族各单GPU，case-seed5601、BF16/local fgvd/vLLM，动作.7/512/≤6；同一u/P/世界/菜单三条件。original_history保留E55完整对话任务指令；phase_end仅明确“对话阶段结束，现可执行物理动作”；phase_fact再加原图实际物品归属及本轮无物理交付/装备/消耗的事实，不指定哪个目标。人物P始终一致。
- **独立读数：** 在同一context另开独立temperature0事实check，问当前holder、原任务/请求是否已物理执行，及不考虑是否愿意配合时哪条合法命令实现请求。original/phase_end不在问题里暴露R命令答案；phase_fact有显式事实恢复。回答不喂给动作policy；这测可被问出的事实判断，不能独自称内部信念。实际action与后果另存。
- **强能力对照：** 每图两P另有force_exact_own/force_exact_request，system末尾明确授权执行给定完整native命令、菜单仍完整。E55“carry out the requested transfer”只是一句语义指令，在satchel案例模型把Castle Guards误指Bodyguard；不能用该控制失败推“模型不会give”。新对照不覆盖旧结果、不作为人物应当行为。
- **读数：** holder/event判断与原图/执行日志核对，source接受/拒绝/协商分层、原任务/request/other/未裁决、0解析/合法性、P×条件差、phase_end与phase_fact的配对差。200图bootstrap95%，一个新动作采样seed，不与E55三seed统计混合；后续是否增加seed由未解决的解释决定，非bar。
- **阳性对照：** 原两native路径；准确literal命令能力、事实cue。条件协商/自己台词“Here you go”单独保留，不预先叫完成或失约。
- **噪声地板 + MIE：** 同一u/P/context/seed配对，全部200；连续效应和区间。shadow readout与action的task framing不同，读数不一致要报告，不伪装隐藏知识证明。
- **混杂审计：** phase_end检验历史中“conversation不执行物理动作”的范围是否残留；phase_fact新增的都是真实现有状态，没有改world/奖励。低步数内谈判等待可合理，未裁决不自动失败。source目标有短中长期层级，不规定角色唯一正确选择。facts和强命令对照不得修改Persona。
- **决策表（跑之前写）：** phase_end恢复→接受任务边界解释；结束仍误报完成、facts恢复→目标状态解释可干预；事实回答正确而policy仍称完成/不行动→追踪问答读出与决策竞争，尚需白盒因果；literal请求正确而语义请求错误→对象/受益者绑定解释；多为条件谈判→原测量缺少对方回应，恢复真实交互再解释；全一致→研究成功条件。所有方向和普通恢复均保存。
- **算力预算：** fvcrc20三空闲卡，先确认模型/环境/数据；与本地E55四卡共7≤8。约1.5–4 GPUh，源u未齐不占GPU等待；0云NPC。**实际：** 待运行。

## 结果
32B与Gemma各200图×两P×五条件=2000完整分支；每模型另1200独立事实回答。32B仅结束对话阶段使原任务实际完成由180/400升至361/400，原任务P配对提升firm+47.5pp [40.5,54.5]、agreeable+43.0pp [36.0,49.5]；额外实际状态提醒几乎不增加完成。Gemma从278/400到383/400，firm+23.0pp [17.0,29.0]、agreeable+29.5pp [23.0,35.5]。接受普通阶段指令范围解释，不把原无动作现象当人格/记忆失效。

32B的original/phase_end两条件holder回答400/400正确、请求命令393/400正确；phase_end原任务已完成误报4/400，请求误报0/400。Gemma事实状态多数正确，请求命令准确率随问法变化，数据全留；不能把独立问答当隐状态。

phase_end实际请求转移的人物差32B+10.5pp [6.0,15.0]，Gemma+1.0pp [−1.0,3.0]。明确字面controller请求的完成率32B88/400、Gemma129/400，仍大量执行原goal；own控制分别388/400、397/400。完整请求命令在菜单且指令实际进入system，现象是原目标/身份与controller之间的行为裁决，不称单独motor不能执行。

0模型JSON失败；源引擎拒绝32B6次重复block、Gemma3次重复block/装备容量，全部原轨迹保存，不修改游戏规则。结果 `results/E56_32b_state_action.json`、`results/E56_gemma_state_action.json`。27B同卡继续。


27B完整200图×两P×五条件、2000分支/3407调用完成，0JSON失败，results/E56_27b_state_action.json。phase_end的实际请求人物差+8.0pp [4.5,12.0]；事实补充同+8.0pp。独立事实、原目标和精确指令控制全部报告，保留各模型的不同机制线索。
