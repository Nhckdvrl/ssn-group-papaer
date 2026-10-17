# AgentMark — ACL 2026 Main 573

- 主源<https://aclanthology.org/2026.acl-long.573/> / <https://arxiv.org/abs/2601.03294>；代码<https://github.com/Tooooa/AgentMark> pin070daa1cb57aa3c053d89ff5b3a788f6585824ea。PDF SHA89c37d9f69b2befd39c12a06a87d1a7033d0c8429b8760bc0ee40249ae18cf33。
- 已读方法分布保持/容量/解码，ALFWorld/Toolbench/OASIS主结果、Appendix G1.1无elicitation基线三次、G1.4容量口径，core/getprobabilities与ALFWorld SDK路径；未执行SDK/API。
- **DOCUMENTED：** 水印通过行为选择携带信息，保持给定条件动作分布；planning behavior与execution分解、utility保持评估已有owner。模型elicited概率不自动等于未测潜在概率。G1.4 active embedding步骤(n>1)容量分母，与整episode bits-per-step分母不同。
- **RECONSTRUCTED：** 文字水印在tool/action agent难传递→把承载对象换为行为、约束边际分布。这个“执行与计划可分”已存在，不能作为我们三层记录的原创。
- **SOURCE事实/解释/未排除：** 已读工具采样/概率获取接口，但未审完全部模型/数据生成。行为可区分不自动指语义persona效度，水印utility保持也不保证角色长期规范；对应原生NPC需自己的信息权限与效用证据。
