# Bayesian Teaching Enables Probabilistic Reasoning in Large Language Models（Nature Communications 2026）

[公开v3全文](https://arxiv.org/abs/2503.17523v3) · [期刊页](https://www.nature.com/articles/s41467-025-67998-6) · [作者blog](https://research.google/blog/teaching-llms-to-reason-like-bayesians/)。51页PDF完整下载并逐页提取；正文§1–4、关键补充C、D.1/D.3/D.4、E、F.2、G已深入读，F.1部分；其余补充/全部示例/图像未独立审，代码与raw未复现。blog全文已读，不能算额外实验支持。

1. **形态：** 受控行为对象＋竞争训练信号＋跨域泛化。不是泛泛测“会不会Bayes”，而是交互中从用户选择隐式推断偏好，能否使未来建议逐步改善。
2. **背景与压力：** 显式算概率/报confidence不是助手自然使用信息的透明读数；准确建议也可能只靠常见偏好的先验。多轮后是否有增量，以及增量怎样依赖信息，才区分适应与猜测。
3. **改变前提 / idea来源（DOCUMENTED）：** 先建立可精确求解的任务，发现原模型几乎不随交互改善；再比较“每次教真实正确答案”的Oracle与“只根据已有证据作最优猜测”的Bayesian teacher。后者会犯错，却可能更好地教会证据积累。训练不是为救一个benchmark，而是区分监督终点与推断过程的作用。
4. **距离：** Hu & Levy2023区分prompt judgment/readout；Lin2022等偏好对话工作已有交互助手；Zhao2025并行工作已有偏好推断困难；神经符号Bayes已有外部显式推理。本文的增量是用隐式交互、竞争teacher与迁移共同支持近似概率推理。不能claim首次“有信息但不使用”、首次Bayes distillation或首次跨训练目标解释。
5. **数据/基线：** 624模拟用户reward functions、四特征、五轮，每轮三flight options，100 held-out option sets；Gemma2 9/27B、Llama3 8/70B、Qwen2.5 7/32B、两个闭源端点。三中等模型训练：每用户十条五轮交互，三training seeds；多特征、hotel、web-shopping迁移；500真实用户，每人五次选择。模拟norm只在已知reward/选择过程假设下最优，不自动是现实沟通规范。
6. **关键证据与边界：** 相同基座、不同teacher的训练可区分解释，正文Bayesian优于Oracle；补充40%随机错误Oracle不能复现改善，三个teacher prior仍有大幅增益，削弱“只是加入错误”与“只换正确prior”。信息量干预从5000候选options挑选：g是给真实reward function的log probability增量，不是一般熵减；fine-tuned更敏感但高信息区仍饱和。三种来源的支持不能简化成内部实现了Bayes算法。
7. **特别重要的成功/null：** 真实用户原模型首轮已强，模拟用户按真实人群偏好重加权也提升，支持常见偏好prior的贡献；真实选择与自报偏好约60%一致，norm与行为目标要分开。已提供最优posterior仍不能明显改善直接建议，因此至少两个任务环节存在瓶颈。numeric替换text没有改善只能削弱特定格式解释，不能严格证明两种表示都被正确解析。
8. **规模/训练问题：** 现象随规模/训练变化不会自动降低价值；重要的是条件响应和竞争解释能否被区分。匹配基座和teacher、训练种子、迁移域可让“训练相关”成为解释对象。反之仅不同模型平均分，或Base不适配接口，不能单因果归能力。当前我们保持training-free，不因这篇有方法就立即训练。
9. **对我们：** 不继续IQAP答案同义词优化；用实际知识/理由证据与独立读取、不同判断目标约束解释。无对话prior用于诊断，不能自动减掉就得到latent belief。人类相似性、规范正确性、自然使用目标三者分别定义。若需要构造数据，先定义自然信息生成过程和可区分预测，再决定数量；不先写故事、造标签。
