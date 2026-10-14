# NCP-Bench：叙事约束与 NPC 私人利益的边界

- **来源：** [ICML 2026 官方页](https://proceedings.mlr.press/v306/ma26ap.html)、[全文](https://arxiv.org/html/2608.08160)、[代码](https://github.com/NLP2CT/NCP-Bench)。PDF `/tmp/npc_ncp_2026.pdf`，SHA256 `4de58ab3b6f72946cb8d2bbb0f34c86fa00a0e16b284c836ad58ba5c23bc7106`。
- **阅读：** §3–6、Appendix B/E，evaluator/runner/baseline及 fact-update/conflict 提示；未逐项检查全部故事或附录 H。
- **论文事实：** 100电影故事含事实、承诺和轨迹节点。Narrator 输出文字，LLM auditor 检查状态更新；没有独立物理引擎。Achievement 成功与一般承诺状态分开。HiAgent 降低承诺冲突不能等同所有成功指标改善。人类演示仅一个故事的两种目标。
- **源码事实：** pin `780aeb559ce216a57cbd934b5a20bfd35018c4f6`，`/tmp/npc_ncp_bench_audit`。候选更新先提取、检查和二次确认，runner 再接受。提示已区分尝试、未来预告与当前事实，不能曲解为所有台词直接成为世界事实。未运行 API。
- **解释／竞争解释：** 长期叙事约束与承诺执行已有 ownership；共同故事约束不自动代表 NPC 私人利益，检查器分歧也不等于策略失败。
- **距离：** 直接约束 E30 的计划修订及 E31 的 event／动机解释，不声称首次承诺跟踪。
