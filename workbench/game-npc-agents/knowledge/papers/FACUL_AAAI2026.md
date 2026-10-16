# F.A.C.U.L.: Language-Based Interaction with AI Companions in Gaming（AAAI 2026 Technical Track: Humans and AI）

证据：正文＋关键附录；未复现。接收身份由[AAAI 正式页](https://ojs.aaai.org/index.php/AAAI/article/view/38842)核实，2026-03-14 出版，40(21):17841–17849；未核 oral/poster。实际读[arXiv v2 正文](https://arxiv.org/html/2511.13112) Overview、Instruction Reasoning、Scene Recognition、Experiments/Table1–4、附录 Algorithms1–2、Case Study/Failure Cases/Table5/Human Evaluation。作者[项目页](https://sites.google.com/view/FACUL-demo)的代码按钮指向[官方仓库](https://github.com/tencent-facul/code)，2026-10-16 仓库为空，不能称完整系统/数据可下载复现。

1. **形态与压力：** 商业合作 FPS 系统。玩家需要表达命令轮盘难覆盖的对象、顺序及语境依赖；系统同时受实时部署约束。
2. **Idea 来源：** DOCUMENTED：置信度高的指令由 BERT-FID 处理，复杂指令交域内 Qwen2-1.5B；实体检索结合当前空间状态，再接行为树。RECONSTRUCTED：把语言开放性放在意图/指代层，有限可靠技能承担执行。
3. **改变的前提与接口：** LLM 经人工校验数据 SFT 后生成 Python，调用 move/attack/open_door 等原子 BT 技能；25 类意图、6 类实体。自然语言输入开放，不代表行为接口无限。
4. **数据/强基线：** 100 局收集 2,550 个指令样本，玩家反馈与失败复核构成评价数据。Table4 的“意图＋环境识别”准确率：域内 LLM＋微调 CLIP **89.2%**，完整混合系统 **87.2%**，快速版本 **73.9%**。完整系统主要提高吞吐；这些数不是整局任务/私人目标完成率。
5. **关键负例与证据边界：** 附录明确有限 BT 不支持的行为会拒绝，复杂空间指代仍失败；Table5 包含买不起昂贵钥匙、友军不可攻击等拒绝实例，属于展示而非私人利益的受控因果证据。24 人偏好研究招募已熟悉系统的常玩玩家，不能直接外推全部玩家收益。未核训练 seed/全部算力。
6. **与近邻距离：** PANDA 研究人物对游戏动作/探索的影响；Dragon 让角色用行动与说话完成目标；SayCan 分离语言有用性与技能可行性；PUBG Ally 提供可行性检查及 BT 闭环。FACUL 的增量在商业 FPS 语言交互及效率整合，不以每个组件全新为必要条件。
7. **可迁移研究动作：** 把普通 LLM＋真实状态＋可靠技能作为强起点，同时报告理解、决策、物理执行及不支持请求。继承可行性/反馈，不重造实时架构或训练分类器。
8. **对我们整体问题：** 本文研究合作伙伴，人物特质列为未来方向。我们的目标是解释有自身作者动机的 NPC 在人物、玩家请求变化与物理前提中如何选择并执行；E80 可检验玩家真实回应/履约与可靠技能各自改变什么。普通技能基线应保留角色自主选择，不能替 NPC 默认接受请求，也不能把对方拿到道具定义为唯一成功。
