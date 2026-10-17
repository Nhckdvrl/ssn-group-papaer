# The Price of Agreement: Measuring LLM Sycophancy in Agentic Financial Applications

- 主源：[正文](https://arxiv.org/html/2604.24668)、[PDF](https://arxiv.org/pdf/2604.24668)。PDF页眉自述ICLR2026 workshop；具体workshop身份未进一步核对。
- 已读§3–4、表1–4、PDF附录C恢复/训练设置与D实际数据构造提示、E注入例；尚未进行作者代码复现。
- **源事实：** FinanceBench/FinanceAgent，比较反驳、错误替代答案、用户偏好经直接输入或记忆工具注入；任务准确性与GPT-5-mini判断的偏差承认率分别测量。LLM过滤、可信度提示、GPT-OSS20B一轮LoRA噪声训练是已有控制，恢复不完全。
- **Idea来源/ownership：** 追问个性化上下文如何污染代理任务，而不只考察直白反驳；“迎合损害任务可靠性”已有明确主张。
- **与I04的距离：** 此处是参考答案偏移与金融分析，尚非执行资金/游戏资产转移；NPC的请求、私有目的与物理恢复路径仍需具体测量。不能把所有给予都类比为答案迎合。
- **竞争解释：** 注入内容与参考答案被构造为冲突，裁判分类与事实准确性不同；无法由这些外部行为唯一定位预训练社交先验。
