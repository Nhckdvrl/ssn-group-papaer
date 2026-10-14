# E35：原始三NPC的目标—互动—执行闭环（2026-10-14）

- **状态：** RUNNING
- **类型：** REPRO／原生任务测量；不训练、不预设异常。
- **对应：** C01基线可行性／D1原生多角色系统，E30计划来源资格的后续；不为此新建idea。
- **问题（一句话）：** 原始校园三NPC在本地模型下，人物、作者责任／公共事件、真实对话、计划与合法行动分别怎样进入完整闭环？
- **设置：** agent-sandbox pind7b872e，原world_data_upenn.yaml及default cast Diego／Professor Tanaka／Sofia，原公告10:00 gravitational-waves lecture、地点／关系／配方／地图／SimClock均不改。使用官方PennStepper，保留events与地图median_travel_minutes；不用缺这两个参数的simulate。只覆写模型客户端工厂，保留原LLMPlanner、reflector、importance和真实对话；embedding仍None。原serial decide_workers=0，不引入模型并发或改时钟。Qwen3.5-27B本地BF16，原messages/schema/temperature/tokenbudget，固定seed3501，1200ticks（08:00–11:20）。
- **源系统边界：** 原real-brain路径会禁用scripted meeting dialogue；mock路径保留作者脚本，两者不混作模型表现。原llm非空标记只用于打开native分支，实际客户端全本地，create_llm_client若被意外调用即报错，不许SDK云回退。planner的原地点过滤和static fallback逐人记录。只把明确已作出的承诺当执行待核对象，不能从学生／教授等抽象标签指定唯一选择。
- **读数：** 全部persona／初始公告与memory／实际模型输入输出；每个parser root调用、重试、合法性、前后world state；对话逐句、conversation_outcome、commitment／PLAN memory、计划修订及随后动作。10:00在场只能叫地点／时间符合，perform lecture文字不是完成讲座的物理证据。优先完整读取成功、失败与异常轨迹，不先做persona干预矩阵。
- **阳性对照：** 先原CPU mock同场景1200ticks，确认三人、原事件／旅行预算、原地图和动作闭环；原相关测试有失败先查明。LLM分支断言注入剧本列表为空、三个planner来源明确；模型实际calls日志为调用事实，原ledger可能为0不能据此称0模型调用。硬云客户端guard，GPU使用前复查空闲。
- **噪声地板 + MIE：** 单episode不做总体CI／人格因果结论。CPU确定性状态作为引擎资格；对话承诺由完整上下文逐例人工式审阅并允许不确定，不用同一模型当真值裁判。首次真实会话两参与者的outcome与后续动作若存在才称完整互动实例，没有就如实报告未发生。
- **混杂审计：** 新接入本地模型不等于作者在线模型复现；原预算／温度保留，单seed、无semantic embedding、原模块fallback未消除。作者已研究公共锚点、对话承诺、计划循环修复，不冒领。计划可以合理改变，不把偏离初始schedule自动当失败；本地parser／适配错误单列。
- **决策表（跑之前写）：** CPU／来源gate不过→只修适配；首完整本地interaction／episode→读取全部轨迹并列至少两竞争解释，尚无异常则不造矩阵；预算内没有会话→报告可达性／意图／执行位置，不强行让角色相遇；普通强提示解释足够则接受。新机制实验另写卡。
- **算力预算：** 先CPU gate≤2分钟。单空闲GPU、总≤8，0付费API；首次本地episode上限120model calls／1200ticks／30分钟模型调用墙时，启动模型载入另记。达到上限保留partial和停止原因，不自动换seed／追加。预计约0.5GPU小时，复用fgvd/deps与已有模型；raw既有cache/runs/e35_*，不进Git。

## 结果（跑完后填写；不改上面的内容）
尚未运行。

CPU gate：作者63tests／12.25秒；原场景1200ticks、26/26 root parser合法、10.20秒，mock剧本来源明确，不算LLM表现。GPU0本地27B单episode已启动。

用户执行准则更新（2026-10-14，原读数不改）：取消以预设MIE／比例／若干base过线作为科学价值裁决或舍弃线索的规则；原卡决策条款仅保留历史。结果按现象、竞争解释及顶会近邻实际证据解释，自由探索。资源预算与实现正确性核对照常记录，不等同科研淘汰bar。

适配记录：首local运行载入487.23秒后因descriptor缺provider失败，0模型calls／0frames；该记录保留/tmp/npc_e35_local。补provider=local-vllm（只作原native分支和manifest元数据，实际factory全部override且云guard），CPU preflight走过三个角色共9个原planning calls，.317秒无错误；preflight返回None触发static属于接入测试，不计模型能力。随后同seed3501原任务重跑，输出/tmp/npc_e35_local_v2，不换seed。

首次本地模型实际运行1184/1200 ticks、120calls、20/20 root parser合法、4次自然对话、8份双方outcome，三人planner均llm。120-call自设上限导致partial，记录保留。原resume实现明确只恢复memory／位置／schedule cursor，不恢复物品／perform timer／conversation cooldown，不能视为精确续跑。因此采用原strict cassette从初始世界重放：1184帧全部逐帧一致、120次响应全部匹配；第1185tick确需新回答。现只用同一27B和原调用序列seed续完剩余16ticks，未改world或fallback。后续有限episode默认不再额外设置call／墙时截断。

完整结果：1200/1200帧、129次真实本地调用、20/20 root合法、5次自然对话／10份双方outcome；续跑新增9calls中5speak、2outcome、2immediate plan revision。原1184帧逐帧精确重放，合并cassette独立零模型回放后全部1200帧与续跑一致。总0付费API。教授给Sofia讲解、Diego吸收建议并返回Meyerson素描是正面成功证据；第五次对话刚形成新即时承诺，episode边界后尚未观察，不能记失败。教学等语言行为与书写／交接marker的物理状态分开；不能从对话中的动作描述自动推定物品状态。原始资产已持久保存cache/runs/e35_original_cast/，结果results/E35_original_cast_complete.json。
