# E11：LIGHT/Dragon 作者自然角色动机与可执行任务资格（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（D1–D4自然任务资格；不恢复旧E00/E02–E05）
- **对应：** E06 / C01；P02提示现ActionCastle需强接口校准，不能只依赖少量固定角色讲人格科学。
- **问题（一句话）：** 作者原生LIGHT/Dragon quest、world graph与人类轨迹能否恢复真实角色利益/合法动作/后果，而非只有单句动作标签？
- **设置：** facebookresearch/LIGHT@71a06cae8573048b1af41507ac52fe33b650fab3；原作者quest_stems.tar.gz（下载hash与build.py严格相同743d9a9d…7c7c7d），NAACL2021官方SupplementaryData zip（含light_quests.tar.gz、light_quests_human_demos.json）。仅CPU枚举字段、来源/许可、scene/character/persona/short-mid-long motivation/goal/timeline/graph分布；按文件名固定前3条代表例核原生引擎能否重放。抽样不得依据model表现筛选。完整data不入Git，manifest摘要入results。
- **读数：** 完整graph/合法action/timeline/人类request是否齐全；不把作者自然语言动机/精确事件goal/人类示范唯一动作混成一个gold。兼容当前OOGraph/GraphEvent的成功率与明确错误，动作前后state；CPUmock/规则不冒充LLM。
- **阳性对照：** archive SHA匹配作者资源声明；原图至少一个原合法示范可以执行并改变库存/位置；对应非法state动作应ErrorEvent且相关state不变。若作者gold matching环境没有物理执行，不能当世界闭环。
- **噪声地板 + MIE：** 全量数据枚举确定性无CI；固定前3原生例重放只证可行性。若任何当前引擎迁移会改变原规则，先报告版本差异，不强修成我们需要的新任务。
- **混杂审计：** 角色/目标/世界均取原数据；有对话不代表对手有完整author goal；quest completion和人格效度分开；新运行不继承旧E03假说/标签/状态；graph版本/许可/自然任务来源需明确。
- **决策表（跑之前写）：** 原native任务可恢复→补更丰富的自然利益决策/人物成功失败轨迹；仅动作文本无后果→明确缺口，优先作者环境而不自造world；依赖/格式冲突→复用已有Conda加overlay或隔离必要import，先低成本CPU，再决定是否完整LIGHT训练；自然目标冲突不明确→不能从刻板人格生成唯一gold。
- **算力预算：** CPU≤1小时，GPU0小时；不安装/训练旧ParlAI官方模型、不启云生成/教师/裁判。

## 结果（跑完后填写）
已完成CPU准入，具体结果如下。

来源/字段准入：7486条原quest全部含persona、graph、short/mid/long motivation、goal与timeline；官方补充提供2111条human demos。没有云生成。原archive与源码声明SHA完全匹配。timeline包含past/future六事件，并不保证每条都在当前graph合法；不把整timeline当唯一执行gold。

原生事件资格：固定前3条quest×2seed，Graph加载6/6，作者goal合法6/6、事件执行6/6，material state变化4/6。两次steal是原随机dexterity判定失败（合法并已执行），get/follow各2次改变状态；6/6非法对象get均ErrorEvent且graph不变。事件/graph/precondition/effect/随机概率全部来自pin源码；event host仅收集viewer消息并跳过无关Hydra/ParlAI/DB模型注册。**没有复现原RL policy/partner/speech scoring，也没有LIGHT本地LLM结果。**数据与结果见E11_quest_source_summary.json / E11_native_event_gate.json。0 GPUh/模型。
