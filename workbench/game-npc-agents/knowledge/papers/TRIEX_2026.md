# TriEx — 2026 三视角扑克解释审计

- 原文<https://arxiv.org/abs/2604.20043>；作者代码链接<https://github.com/Einsam1819/TriEx>尚未clone/逐行核验。PDF SHA dfdc81bb542558a0f5852873163e16ebb5feaf28f6d7adea1fc7789cdce8bbad。
- 已读§3三视角、§4.2–4.3主表、Appendix A协议与B.2干预/rerun。50battles×30hands，PyPokerEngine、6LLM及固定algorithmic opponent；完整原生扑克不等于RPG人格任务。
- **DOCUMENTED：** 第一视角结构化action explanation、第二视角opponent belief、第三视角oracle审计。干预把显式belief数值经logit perturbation δ2.5改变，自然语言描述保持；另50次同belief rerun估计模型随机波动。不是activation vector干预。equity/pot-odds规则审计与oracle输出相关，不能当内在解释真值。
- **RECONSTRUCTED：** 单一自述难评faithfulness→行为/对手belief/审计多视角，需明确参照和rerun地板。三视角闭环与belief因果干预已有owner。
- **解释/未排除：** 对手belief条件改变实际动作值得借鉴，但NPC人物目标、具体访问Can与对手Will不能混；我们的三层测量不能宣称从无到有。尚未审公开code/全部Appendix D prompts，不外推所有解释机制。
