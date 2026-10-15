# Mascot: Multi-Agent Socio-Collaborative Companion Systems

- 主源：[arXiv v3](https://arxiv.org/html/2601.14230)、[作者仓库](https://github.com/hello-diana/MASCOT)、[作者EMNLP2026 Main页面](https://ahren09.github.io/publication/emnlp26_mascot/)。已读§2–3方法、表2–3/消融、Appendix C.4–C.6评价与数据；仓库只读README所列执行路径，未声称源码/训练复现。
- **源事实：** Qwen3-8B Speaker先按persona reward做GRPO，固定Speaker后训练Director分配说话与指令；Qwen3-0.6B奖励模型来自GPT-4o打分的偏好。LoRA r16、每阶段一轮；格式奖励要求长思考与短回复。ED/QMSum及OOD ESConv，包含人评、不同裁判与提示扰动；源实现同时保留非论文默认的DPO可选项。
- **Idea来源/ownership：** 区分个体人物保真与群体非冗余贡献，训练两级策略；社会迎合、人物趋同和说话组织已有明确研究。去掉人物对齐与去掉Director的消融影响不同评价轴。
- **与I04的距离：** 所谓行为主要是对话贡献，不含NPC实体资产/私人任务链；不能直接把它的改进视为真实策略改善。反过来，也不能因使用语言裁判否认其人评与对话任务贡献。
- **竞争解释：** 人物定义、语言风格、说话机会与群体质量耦合；多裁判稳健不等于识别了内部因果机制。I04应提出真实行动预测，而非照抄两级GRPO。
