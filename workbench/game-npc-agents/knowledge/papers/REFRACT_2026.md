# ReFract（2026-10-02预印本）

来源：[正文/关键附录](https://arxiv.org/html/2610.03356v1)，已审§3–5、AppendixF/G/I，Tables2–4；非NPC游戏，代码URL尚未确认。作者页标workshop，不据arXiv推断主会接收。

**DOCUMENTED / idea来源：** 同一句工业维护请求，对manager/technician等角色应有不同目标与行动权限。150专家核任务，Python Text World Model区分capability/knowledge gates和routing；81工具，全工具/相关工具、Function Calling/ReAct，5次重复。

**强已有证据：** 评价终态与整条轨迹的persona compliance、over/under reach；AppendixI已经用原生可达续路定义off-goal，而非唯一gold动作，不需模型logits。模型仅服从权限仍可用合法动作毁掉所有达goal路径；工具分布不同也不自动是正确差异。不能冒领“角色许可/实际执行与任务成功须分开”。

**限制/距离：** 工业user-role代理，固定角色税目/单domain/手工单调acyclic world；主体不是自主游戏NPC自身利益；它的perspective指角色知识/权限而非观察者指代。NPC生态、游戏动态与自主效用可扩展，但只换壳不足成贡献。公开artifact/逐任务可达性核验未完成，不能指其已失败。

**对P02：** ReflAct和ReFract都让普通state/goal grounding成为强基线；必须通过强接口/强提示和独立executed consequences之后，再谈新认识。
