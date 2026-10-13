# E09：原生NPC视角归属与当前位置的最小决定性对照（2026-10-14）

- **状态：** DONE
- **类型：** PILOT（P02竞争解释；无需事先认定新idea）
- **对应：** P02 / C01，E07真实轨迹。
- **问题（一句话）：** 在同一作者原生角色和状态，离开已有驻地的动作主要来自player-view narration、位置整合/叙事prior还是普通动作能力？
- **设置：** E07的首3个真实NPC决策snapshot（troll/guard/ghost），不选有利seed；完整原始消息与状态通过之前原生parser命令重放取得并核对。冻结角色、目标、局部信息、原规则；条件：原版、单句明确first-location-block是NPC观测、Game narration加player-viewer来源标注、等量无新状态/来源的中性说明、移除history（作为不等信息的诊断，不能单独支撑方法效益）。本地Qwen3-32B与Gemma3-12B，预定201/202/203，温度.7；每格独立决策与独立current-location probe（probe不写入动作上下文）。总3角色×5条件×3seed×2读数=90call/model。同时补E07预定102/103原生episode和递鱼玩法的101/102/103，保留全部。
- **读数：** current-location probe按引擎精确房名匹配；原始Reasoning/Action/Duration、首次合法率、是否从已在的作者驻地离开、原生state delta和block变化。离开不是自动“违背persona”（巡逻也可能合理）；只有位置probe与动作理由/实际移动共同证据才谈错位。人物表达/场景意图另作独立影子支线，无LLM judge定性gold。
- **阳性对照：** exact current location来自engine；每个snapshot先用原录下的命令重放，state delta必须精确一致；simple独立无历史location probe；作者script合理守位只作参考，不是唯一gold。
- **噪声地板 + MIE：** 3固定decode seed和3原生角色，只描述这三个snapshot的配对差；若正确视角/一句指令消除位置错误并改变全部角色同类departure，足以把P02降为接口解释，无需泛化claim。若mixed则检查逐轨迹，不据小样本升L2；CI若给出，只针对固定snapshot重复decode，不把90call当90独立场景。
- **混杂审计：** 单句说明与neutral尽量匹配token数并记录；source-label添加元数据但不增底层事实；history删去改变信息量，单列诊断。系统/用户位置、叙事/action anchors/seed/模型mode一致，分开非thinking与可选thinking的budget。snapshot只从已观测异常来，是发现性样本；所有机制/新颖性推断必须再做未见确认。
- **决策表（跑之前写）：** 单句/来源标注恢复→P02由普通接口混杂解释，不创建“人格gap”或创新修复claim；history removal有用但来源无效→进一步分长度/recency/多NPC信息；无历史也位置错→核probe/API模板/强模型能力；位置正确而策略仍离开→检查合理巡逻/目标后果信息，不把动作自动判错；如果出现超出上述解释的稳定跨角色现象→另写竞争解释与未见pilot卡，不能自动上steering/RL。
- **算力预算：** 2张独立卡，各先单model90calls与少量完整episode，总≤1.5GPUh；本研究任何时候07:00 Asia/Tokyo起≤8卡。零云端推理。

## 结果（跑完后填写）
未运行。

### 运行前补充（尚无E09模型结果）
3个自然snapshot的原动作与state delta精确重放3/3通过。每model另加6次独立expression/intention影子测量（每角色各1），不写入action上下文。当前位置probe保留条件提醒；避免替换输出contract时误删one-sentence/neutral控制。主行动/位置读数仍按原90call设计，合计96call/model。

### Qwen3-32B结果与测量审计（另一模型尚未结束）
96次本地独立调用（主90+影子6），原版literal-location2/9→one-sentence6/9，viewer5/9、neutral3/9、no-history2/9；原版/one-sentence合法动作均5/9，viewer2/9、neutral6/9、no-history5/9。
**POST-HOC格式审计**：原版3条literal失败其实含正确房名但加角色前缀；按“首行唯一房名、无go/move意图”的规则二级审计，original5/9、one-sentence6/9、viewer6/9、neutral3/9、no-history5/9。不覆盖/重标预注册literal读数；literal在这里测了任务/格式遵守，不能单独当位置知识准确率。原版与no-history的差异尚不足支持简单history因果解释。格式审计数据见 `results/E09_qwen_location_format_audit_POSTHOC.json`。
Expression/Intention已在独立支线保存。Qwen32的额外E07三seed/两玩家策略均完成；E09+5个新episode总412.40秒含载入，所有失败保留。没有升L2。下一步补作者native闭集schema与更新强模型，而非提前做表征/训练。

Gemma3-12B成功完成相同96call、168.23秒含启动。literal own-location原版9/9，single-sentence9/9、viewer9/9、neutral8/9、no-history9/9；动作合法原版3/9、提醒/来源/neutral各0/9、no-history2/9。raw trace显示多为攻击/haunt不在场对象；位置知道不等于动作目标/参数正确。两家族的结果不支持“统一的位置错误导致所有NPC行为失败”；P02须分位置/视角、角色目标、合法参数和输出contract。没有科学claim升级；D1强基线仍需作者per-action tool描述/完整nativeloop及thinking预算控制。
