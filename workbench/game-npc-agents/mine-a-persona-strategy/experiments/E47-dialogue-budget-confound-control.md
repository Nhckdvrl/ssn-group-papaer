# E47：人物条件差异是否依赖对话截断／fallback

- **状态：** DONE；两完整后缀159次本地调用与独立回放完成。
- **类型：** 原生强基线／混杂解释，不是新方法。
- **对应：** P11，E45/E46；在角色实际目标选择的解释前排除协议影响。
- **触发：** E46原角色81calls、教授speak两次JSON截断，reserved61calls、教授speak零截断；实际任务／行程不同。E45亦有部分speak length→JSON failure→chat redraw，可能改变后续采样序列和目标承诺。不能直接归纯人物偏好。
- **设置：** 同3502/787精确prefix／真实plan progress／两角色指令／原世界和planner，继承E46。仅教授对话speak与其原freechat fallback输出上限128→512；其他角色、非对话、schema、temperature、初始seed、原任务结束1200不变。两新完整后缀。世界规则和评价不变。
- **竞争解释：** H1角色语义影响新增任务选择；H2较长表达触发协议redraw而影响行为；H3更大输出容量本身容许不同内容。512仍不保证永不截断，保留所有错误；长句不是更真实价值的真值。
- **读数：** 首次same-input输出是否延续原128截断prefix（仅数值资格、未保证），完整表达／承诺／plan／实际世界行程、所有parse errors、fallback、tokens与成本。与E46全部原预算结果共同保留，不筛最佳budget。
- **阳性对照：** 教授两个对话路径均512、Sofia及非对话仍原budget；上游LLMAgent.converse强制失败资格；同787frame/source77请求、原plan字段、独立完整cassette重放。R8普通指令恢复与state事实控制已在E44–46提供，预算是进一步协议竞争解释。
- **噪声地板 + MIE：** 单发现性state，两角色，未来call数和采样可分化；无科学阈值、总体CI或“必须过线”。只解释当前观察，不推一般心理构念。
- **混杂审计：** 较长输出可能改变内容／对话done以及source conversation-credit，因此不把差异全归格式。指针仍计划执行状态非物理完成flag；旧历史和其他组件角色保留，局部角色干预范围不变。所有结果按真实层次报告。
- **决策表（跑之前写）：** budget大幅改变此前关系→重解释协议渠道；差异保留→更有理由检验goal生成／执行渠道；尚有截断→如实报告而非淘汰科学线；只有语言变化→不升级行为claim。不靠此研究局部优化分数。
- **算力预算：** CPU原生fallback／预算资格，随后两张已空闲本地GPU2/3各完整后缀，项目总≤8，0API，现有fgvd/deps/cache。单局成本沿E46实测，实际超长token成本完整记录。raw cache/runs/e47_*。

## 结果
真实source fallback／预算资格完成；两格完整1200帧，original/reserved 98/61次调用，教授structured speak均零解析失败。两格独立零模型回放1200帧一致，完整表达／承诺／活动／全部其他解析错误见 `E47_complete_dialogue_budget.json`。

reserved与E46全部1200帧完全相同；original全frame为789/1200相同，教授activity为847/1200相同，后续从草图改为声学／波检测教学，并起步去Williams。original仍有两次immediate、reserved一次scheduled新承诺。预算解释影响具体后缀，但当前差异不能全部归为教授JSON截断。长输出也影响内容、done与计划推进，不能称纯格式恢复，也不能由单case推人格总体。下一E48辨识显式conversation agenda渠道，未预定新训练。
