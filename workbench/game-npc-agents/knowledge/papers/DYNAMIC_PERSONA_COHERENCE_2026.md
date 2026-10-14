# Beyond Static Persona Consistency — ACL2026 Long（官方）
- 来源：[PDF](https://aclanthology.org/2026.acl-long.1336.pdf)，SHA256 95c071f42dfb1d539c7933d0fd90c6f747c20fb1b5a25150aaef51056ec390bd。
- 阅读范围：§3–5、Table1/2、Appendix B评分/修复示例、D跨judge/E语言/F敏感性；非全代码复现。作者anonymous DPC-30A1代码链接web不可访问，未审代码，不能称确认实现。
- **DOCUMENTED**：固定identity L与动态S/M state，GPT评估event impact累计clip0–10；PCC证据NLI/情绪/意义评分，低分PDS改写、高分PCR复用。5personas×3models，约100–150turn、5seeds204–208。主评价GPT-4o T.3，独立Claude全15配置、DeepSeek仅2persona；多语言也只2persona×1model×2seed。
- 作者Table2平均PCC .7254→.8902(S/M)→.9195(+PDS)；84.9%增益由state tracking贡献。是文字反应/自动评分，未给原生合法物理动作与游戏利益的因果结果。采用既定state/rubric，不能把内向人物某个台词当唯一真实策略选择。
- **RECONSTRUCTED**：人格持续不等于情绪僵化→身份/适应分层、累计状态、逐句纠偏；已经拥有动态人格与状态适应方向。
- 未排除：同judge/rubric回路、event流选自Ours对照、外在游戏回报的解释范围；独立judge部分覆盖已明确，不能忽略。
