# E46：真实计划执行位置能否解释人物／责任条件的交叉

- **状态：** DONE；两完整后缀与独立1200帧回放完成。
- **类型：** 原生强普通基线／竞争解释诊断，不是新方法。
- **对应：** P11；E44/E45，人物指令→新增承诺→实际行程。
- **触发：** 3502四格已完整：原角色native去Williams，原角色facts先Irvine lecture；reserved native继续lecture，reserved facts却去Williams。部分话语称lecture已结束，但source当次计划仍有未开始／当前的lecture相关stop。角色效应不先压成偏好强弱，也不从话语推内在belief。
- **竞争解释：** H1已有责任的当前执行位置未进入对话，产生goal-progress语境差异；H2人物规范确实改变愿意采纳的教学目标；H3话语习惯／原budget截断后redraw／随机未来。普通goal-progress信息已有UGST/TACL2026、源planner/read_plan等近邻，不冒称首次追踪目标。
- **设置：** 同3502/787精确prefix、原27B、source budget/schema/温度、两角色指令original/reserved；在现有clock_and_duty上追加本NPC当前计划及原schedule.stop_index、source当前活动、performing/waiting标记。逐stop的completed/current/upcoming沿作者planner._revise_immediate的格式，由实际指针计算；每次speech及其原chat fallback均提供同一真实快照。其他角色／组件不变，后缀至原1200frames。
- **状态解释：** 这是agent计划／schedule执行位置，不是公开lecture物理完成flag，也不把perform文字当真正教学／草图作品。已执行计划前缀可能受source conversation-credit逻辑影响，按source原样披露；不据它给唯一正确决策。
- **读数：** 原全部逐句对话、outcome具体承诺、source生成计划、真实地点／活动、parser、fallback与成本。是否提及过去／未来lecture及所采取目标逐例审阅，不造自动hallucination成功bar。与3502已有四格及native A/A共同解释。
- **阳性对照：** runtime实际指针／状态字段资格；标注文本和作者planner对应；两路径的source LLMAgent.converse强制fallback检查；787frames/source77请求完全相同；完成episode独立cassette重放1200一致。实现正确性不作科学裁决。
- **噪声地板 + MIE：** 单发现性case、两人物指令，保留原seed及call-count分化，无总体CI或效果比例阈值。若仍需跨场景判断才追加；不为整齐铺矩阵。
- **混杂审计：** 新增本人可知信息和长度，不解释纯措辞；world/state/reward/目标评价不改。scheduler状态不是material成功真值；信息进入对话阶段而非重写planner规则。既有历史保持原温暖经历，仅局部角色描述干预。
- **决策表（跑之前写）：** progress解释交叉→接受普通goal-state机制，重新解释E45；仍有角色效应→进一步看生成目标／执行及跨角色预测；仅改变话语→不推行为或belief；发现数据／parser伪影→校正并保留。无自动去留，未规定训练／steering／loss。
- **算力预算：** 先CPU真实prefix／字段及fallback资格，随后两个空闲本地单卡分别两角色之一、各完整后缀，沿E44约5分钟+载入，0API。当前远程剩余原始E45任务计入总卡数，项目≤8。现有fgvd/deps／缓存，raw cache/runs/e46_*。

## 结果
两格完成，original/reserved为81/61本地调用，所有首次请求与787帧前缀一致；独立零模型1200帧回放均完全相同。CPU字段及真实fallback资格见 `E46_runtime_progress_and_fallback_qualification.json`，完整结果见 `E46_complete_grounded_progress.json`。

提供真实计划位置后，两条件都进入原Irvine讲座活动。original随后形成两次immediate新教学承诺，转向原地草图活动；reserved形成一次scheduled的11:00 Williams推导承诺，1147帧起步行。计划／活动文字不等于讲座或草图物理完成；这一case只能解释任务采纳与执行渠道，不能作为普遍persona偏好。original教授speak两次解析失败，reserved零次，E47检查该竞争解释。无总体CI或科学阈值。
