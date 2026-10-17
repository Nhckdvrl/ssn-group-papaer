# E10：现代本地模型与作者闭集动作接口的强基线（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（D1–D4；P02排除弱默认/解析解释，不是新控制方法）
- **对应：** C01 / P02；E09的probe格式不合规不能直接当位置知识缺失。
- **问题（一句话）：** 使用较新Qwen3.5-27B和作者原生choose_action闭集schema，原生人物/意图→动作链是否显著可靠，剩余异常是否仍有实质游戏意义？
- **设置：** 作者Action Castle pin不变，Qwen3.5-27B@fc05daec18b0a78c049392ed2e771dde82bdf654，existing fgvd；玩家intruder/feed原序列，seed101/102/103，128输出token/.7温度。先各1个完整episode核能力与成本，再原定全部seed。条件：作者free-text ReAct，作者single choose_action schema（vLLM本地JSON约束实现同样schema，重新经过原precondition gate，非脚本action）。另加single schema + current-observation-viewpoint一句说明作为普通strong-prompt对照。没有新reward、场景、唯一策略gold；不声称native云tool-calling精确复现。
- **读数：** 原始格式/命令、工具args、首次与retry合法率、material delta、NPC去向/阻挡/玩家后果；expression/intention在独立支线记录，不混入行为历史。JSON只保证格式/verb，不保证参数/局部世界/角色目标正确。模型加载/vision禁用/实际template/SamplingParams/model hashes均manifest固定。
- **阳性对照：** CPU已验证合法动作改变state，illegal拒绝；native schema包含原动作verb枚举和free arguments；每次工具call再过原parser。保持无script fallback。
- **噪声地板 + MIE：** 3预定seed全部保留，先描述本模型/本场景内方差；若新版/闭集/单句恢复原P02，则归于基线和接口，不升级能力或新机制claim。逐动作非独立，CI以episode为单位，n=3只作pilot。
- **混杂审计：** Qwen3.5不同架构/发布时间不能只归因size；free-text与JSON模板差异/约束cost明确记录；不以强prompt含新事实而冒称训练方法。普通视角说明和JSON分别比较，参数长短/调用预算记录。
- **决策表（跑之前写）：** strong基线已达作者目标→分析成功条件并转真实自然利益决策；只修语法→重新审剩余真实策略；新模型仍受原player-view历史误导→先修baseline观测归属，非persona创新；若有稳定未被强提示/接口解释的异常→另写有未见确认的科学pilot。
- **算力预算：** 单卡先跑一对episode，再全3seed，总≤1GPUh；探索允许并行独立GPU，本项目07:00 Asia/Tokyo起≤8卡。无云API。

## 结果（跑完后填写）
已完成，以下为结果。

运行前补充：纯文本任务明确`language_model_only=True`，不触发多模态预处理器；native schema为本地约束JSON参数，并非SDK native tool message协议精确复现，返回原作者LLMAgent._decide_structured与parser；hash/版本/模板与token统计均写manifest。

完成18episodes；总wall时间2128.83秒（含启动；单GPU wall上界，不等于纯推理时间）。原摘要见results/E10_native_episode_summaries.json。

POST-HOC归因校对：parser对逗号命令有递归子调用，raw records数量不是LLM决策数量；用作者decision/tool parser重建并匹配所有root，零missing，raw不覆写。不能将子命令的successful和parent同计为两个LLM选择。以下只修readout归因，不改变世界规则或评分目标。

- freetext: LLM root合法77/224，首次合法46/135，root material变化41；3seed与两原script全保留。
- native_schema: LLM root合法68/231，首次合法39/135，root material变化35；3seed与两原script全保留。
- native_schema_viewer: LLM root合法74/221，首次合法49/135，root material变化32；3seed与两原script全保留。

JSON单工具和普通viewer说明未明显恢复合法行为，解释范围仅此任务/interface预算；不能据此认定Persona无效。后续E12原生逐工具+普通一句是更强控制。n=3seed/同3角色，未把逐动作二项CI冒称跨角色证据。
