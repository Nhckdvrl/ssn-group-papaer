# Just-in-Time Memory: Learning to Curate Task-Adaptive Memory for LLM Agents（2026-09-23 arXiv v1） `[证据级别：完整主文]`

来源：[作者预印本](https://arxiv.org/abs/2609.27334)。Salesforce；读完整§1–5/main页1–10，附录A提示开头与复现参数/训练表、B组件定义/检索k；部分附录长提示与生成case未深读。接收/评审未核对。

1. **形态/压力：** 方法题，由写入时不知道未来用途、不可逆压缩和延迟credit assignment共同缺陷生长。
2. **改变前提：** 原始成功轨迹保留，直到读时知道任务再生成临时payload；payload不持久化，训练其即时下游成功。不是又调embedding检索。
3. **idea来源：** DOCUMENTED：ReasoningBank固定抽象、SkillOS需组任务制造奖励→把策展时机后移；作者借重构式人类记忆。RECONSTRUCTED：共享缺陷同时压在信息接口和学习信号上，选择一个结构改变同时消解两个压力，故事尺度比单点涨分清楚。
4. **距离：** ReasoningBank/MemP在写时形成固定内容；SkillOS已有GRPO但写时；Synapse直接取原轨迹无task distillation；并行MemHarness读时但curation/execution同模型，作者强调独立curator迁移。不能把一般query-adaptive retrieval/working memory当新空白。
5. **实验：** ALFWorld140test/WebShop500/τ²三域，Qwen3-8B/Gemini2.5Pro/GPT5.4三executor；Qwencurator GRPO100steps、group8、固定训练bank，测试bank空起点、按batch10/5更新，3/4随机task顺序重复。BM25只对任务说明检索k3。训练exec非thinking，ALFWorld测试Qwen开thinking；WebShop加search guidance，基线复现修改作者披露。训练21/27小时，8H200服务器。
6. **结果/限制：** Qwenexecutor训练curator相对SkillOS SR +16.2/+16.3pp；跨executorALFWorld到GPT86.7 vs自训练88.1。τ²仅免训练，微均值+3.9，Airline/Retail未超过方差，不能称所有域增益稳定。更少executor tokens/steps不含额外curator调用总latency。无task条件/无raw轨迹/全存含失败各造成损伤，但总方法差不都由某一消融因果解释。memory过滤靠同executorjudge，不等同真实全成功。
7. **机制边界：** 临时任务专用摘要有效不证明共享状态被更新，跨executor迁移也不等于跨事实迁移。RL无retrieved资料退化支持学到策展用途，不证明具体关系完全正确。
8. **可借动作：** 不同用途对应同一原信息，不提前压到一个固定答案；从共同限制提出改变接口/学习信号的最小结构。新颖性可来自“何时做决定”及可复用性，而非新损失公式。
9. **对我们：** 不能把任务提前/源bank拆开直接当novel：视角/内存接口已经拥挤。真正空间是修订时旧关系撤销是否作为可复用状态改变，或每个用途都要再次组装；E65/E66是机制入口，不是把自然GP偷换成agent memory。只有验证清楚的关系对象后才迁移方法，当前无候选决定。
