# When the LM misunderstood the human chuckled: Analyzing garden path effects in humans and language models（ACL 2025 main）`[证据级别：全文（arXiv 2502.09307v1，经 arXiv GCS 镜像）]`

1. **论文形态：** 引入成熟构念 + 人机同任务测量（三种相互竞争的心理语言学解释，各配一个操纵）。
2. **背景与压力：** 之前的 LLM–GP 研究多用间接指标（surprisal 与阅读时间相关），模型族也窄；不清楚造成困难的是不是同一类因素。
3. **改变的前提：** 让人和 LLM 做完全相同的理解问答；把"GP 难"拆成三种解释：句法重分析（GP vs 换序对照）、合理性（把 the deer 换成 the child）、动词论元需求（及物 vs 反身/非宾格）。
4. **idea 来源（DOCUMENTED）：** Christianson 2001 / 2006 的残留误解、Patson 2009 的复述任务；把心理语言学里的竞争解释落成正交操纵。
5. **与最近邻的距离：** 相对 Li 2024（24 NPZ，4 个模型）增加了三因素设计和人类数据；相对 Irwin 2023（BERT，错误模式不同于人）给出"规模越大越像人"；相对 Arehalli 2022（surprisal 低估）改为直接测理解。
6. **方法与数据：** Subj/Obj 结构，45 组 × 6 条件（公开发布 69 组 / 276 条问答）；人类每人单题；GPT、Llama-3、Qwen-2.5、Gemma-2、OLMo checkpoint；8 种提示的平均概率；复述和文生图作为补充读数。
7. **证据与短板：** 人类的语义（合理性）效应强于句法效应。作者在 §2 明确说，及物问句的准确答案是"不一定"，但仍把 Yes 记为错误。我们对公开结果的审计显示，这类条目在**无歧义对照句**上同样大量答 Yes（`workbench/.../results/D0-Amouyal-released-item-type-audit.json`）。作者自己也提出疑问："整句给了 LLM，为什么仍然失败？"，但没有回答。CoT 未带来显著变化。
8. **可迁移的研究动作：** 把竞争解释各自落成一个操纵；用生成型读数（复述）交叉验证问答读数。
9. **对我们：** 这是 C1 的主要数据来源和人类锚点。反身/非宾格条目是"初始命题确实为假"的干净子集；"整句可见仍失败"是我们要回答的问题。
