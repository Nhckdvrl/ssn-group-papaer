# CoSER：人物动机与给定情境已有的强对照

- 来源：[ICML2025官方全文](https://proceedings.mlr.press/v267/wang25dk.html)、[代码](https://github.com/Neph0s/CoSER)。本地PDF `/tmp/npc_coser.pdf`。
- 阅读范围：正文§3–5、GCA设计、main tables、inner-thought／motivation消融Table5及附录入口；当前未审其作者代码和完整数据抽取流水线，不能称完成源码审计。
- 论文事实：771本书、17966人物；抽取对话、场景、人物动机与thought/action，部分非对话内容由模型推断。GCA把本人物profile／motivation、场景和其他人物资料作为给定情境；训练亦覆盖省略部分资料的组合。角色内心与动机对其他模拟参与者私有。模拟以文学场景对话为主、critic评价多维表现，不能冒称独立物理游戏状态的成功率。
- 已有对照：Table5同时比较inner thoughts与动机的启用／移除，正文报告多模型改善；Llama3.1-8B 52.99→51.97（有thought时去motivation），CoSER8B 56.45→54.65。人物动机信息影响角色表现已被直接实验，不能把加一句责任／目标提示当新命题。
- 我们的解释：真实NPC的计划、执行和状态可以提供不同证据层次，但“我们用了物理引擎”本身不是足够增量；必须有能跨角色／场景解释决策形成的具体新认识。E44首先是普通信息解释诊断，不是一篇替代CoSER的benchmark论文。
- 竞争解释／限制：thought与动机同时关联训练格式、评价场景及生成长度；这里摘录的是作者固定评价，不推一般所有角色必然受益，也不把profile与实际目标合并成一种心理量。
