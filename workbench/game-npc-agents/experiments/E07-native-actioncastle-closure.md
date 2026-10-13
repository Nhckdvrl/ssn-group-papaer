# E07：作者原生 Action Castle 的本地决策闭环（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（D1–D4，接口准入；不是论文全量复现）
- **对应：** C01 / E06 矿区 A baseline gate。
- **问题（一句话）：** 真实作者目标能否从人物资料进入本地模型，再经原生合法动作改变世界，且正确区分模型动作与脚手架贡献？
- **设置：** ccb/agent-sandbox@d7b872e396df2ef05ff8391de53e0563ca698cf3，MIT；原生 Action Castle 与作者 hw1_llm 目标；不改地形、动作前提、奖励或通关规则。首先 CPU scripted/mock 阳阴控制；随后复用 Conda 与缓存 Qwen3-32B 或可用强模型，单GPU，固定seed 101、102、103（先101单episode量成本，再全部保留）。玩家用原生合法动作的规则序列；纯ReAct不加脚本fallback，原版允许的1次失败反思单列。所有调用本地或规则，模型/依赖revision与文件hash入manifest。
- **读数：** ①人物表达原文（独立支线、不进入默认action历史）；②针对该观测的意图原文（独立支线）及same-session条件须单列；③每次原始command与parser success/fail；④实际角色/物品/位置/属性delta、block状态、玩家生死/移动；⑤LLM调用/token/wall time、重试/脚本次数。优先无额外问卷的原版行动轨迹；不以BigFive/“贪婪”等刻板性格设唯一正确行动。角色目标成效仅报告作者定义可客观检验者；不能把 engine block 当模型维护目标。
- **阳性对照：** 原生 troll 持club attack会改变玩家伤势/生死；give fish/eat fish 能按原规则改变饥饿与桥阻挡；guard/ghost原生脚本可执行。同一初态合法动作的结果必须与直接脚本回放一致。
- **阴性对照：** 无武器/无目标/错误地点等原生不合法动作应拒绝并不改变相关世界状态；growl/snarl/warn的台词成功不能被标为库存/生死/通行改变。mock不是模型证据。
- **噪声地板 + MIE：** CPU固定state/命令复放两次应完全一致（除trace时间戳）；模型3个预定seed不删失，先描述原生能力与观察，未设定persona效应量，不依据三条轨迹声称普遍gap。
- **混杂审计：** 工具有效性/动作归因由阳阴控制和原始state重放核验；玩家命令、目标、人物文本、可见信息不擅改；token/时间全记；同/跨会话三层测量分开；首次/重试/脚本分开。模型污染、单游戏外推、表达主观度与小样本仍未控制，故仅L1可行性范围。
- **决策表（跑之前写）：** CPU控制失败→修harness并留失败记录；强本地模型不合法动作多→先审parser/动作信息/强提示，不能判人格失败；闭环成功→查看全部成功失败轨迹、从真实异常写至少两竞争解释；原生引擎状态已机械决定结果→不把通行/守门表现归于persona，选仍有策略选择的原生指标或其它自然底座。
- **算力预算：** CPU≤0.5小时；初个episode GPU≤0.25小时，确认3seed≤1小时；测出实际成本后才扩充。07:00 Asia/Tokyo起项目总占用≤8卡。

## 结果（跑完后填写；上半部分改动另注）
CPU阳阴性控制8/8通过，两次重放完全一致，0 GPUh、0模型调用；原生growl只改台词，未拥有武器的攻击失败且无world delta，club攻击改变玩家状态与物品位置，玩家给鱼触发原引擎自动吃鱼并解除桥阻挡。最后一项由玩家动作+引擎完成，不能当LLM决策。见 `results/E07_cpu_controls.json`。本地模型单episode正在启动；依赖恢复曾缺prompty/aiofiles，已用现有Conda加隔离overlay补齐。

### 运行失败保留
首次Qwen3-32B启动成功加载权重，但flashinfer采样kernel warmup因`ninja`不在未激活环境PATH而失败（0模型决策）。原始日志和manifest保留于`e07_qwen32_intruder_s101`，不计入NPC成功/失败分母；后续通过正确环境激活修复，不改场景/模型/seed/评价。

### 首个本地模型episode（全部轨迹，无筛选）
Qwen3-32B@9216db5，现有fgvd Conda，GPU0单卡。完整玩家6步episode，26次parser动作、16成功；其中NPC20次尝试、11合法，4次改变material state；7个总material变化包含3个玩家移动。20本地LLM调用，输入13,403token、输出734token；包含载入/warmup总173.54秒。无script fallback、无云调用。失败工程启动与成功episode分开，修复运行使用本地PyTorch sampler（VLLM_USE_FLASHINFER_SAMPLER=0），其它模型/场景/seed未改。
模型有真实可执行行动（移动/威胁等），C01 L0→L1（基线可行性）；单seed不升级科学主张。返回原本驻地却先离开的样本列P02，至少四竞争解释，下一实验先分出位置/语法/观测/运行模式，不能现在宣称言行gap机制。

预定3seed×2玩家策略全部完成：intruder NPC合法11/20、14/23、12/21；feed为23/45、21/47、15/48。全部无script fallback；source原规则/角色目标未改。按episode统计，不给逐动作假独立CI；汇总 `results/E07_six_native_episodes.json`。C01仍L1可行性。
