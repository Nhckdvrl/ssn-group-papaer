# Ask Twice, Look Twice（ECCV2026 eXCV workshop；作者v2主文）

[最新作者原文](https://arxiv.org/abs/2607.15565v2)，CMU。已读完整主文§1–8（1–16页），附录A实验/样本、D的直接边界、G全部跨问句示例；其余附录只核对表/片段。29页PDF；workshop接收由作者arXiv评论核对，不写成ECCV主会。

1. **形态：** 反直觉行为→两个计算阶段→极简修复。
2. **压力：** 提前知道问题理应指导视觉编码，但question-first在四个VLM上更差，Gemma27B例外。
3. **改变前提：** “让感知知道问题”与“让答案读到问题”是不同计算需要，位置选择不能只优化其中一个。
4. **idea来源（RECONSTRUCTED）：** 人类目标引导直觉与标准image-first实践相冲突→固定内容交换位置→分开看图像与答案→全层直接edge干预→重复问句解决两个位置需求。DOCUMENTED人类adjunct questions提供历史类比。它并不需要所有模型出现相同deficit，Gemma仍有方法收益。
5. **邻距：** Prompt Repetition/Re-reading已有重复；Lost-in-Middle已有距离；Gupta/Gandelsman同期同现象+midlayer patch/TTT，作者明确承认近邻，主打计算阶段解释和训练免费修复。局部相同没有成为自我放弃理由。
6. **实验：** 5开放VLM，NaturalBench1900 groups、POPE9000Q、Winoground400groups、VQAv2 2000Q。核心Qwen3VL8B/Gemma27B；greedy16tok。层探针150个STI错/SIT对条目仅机制显微镜；真正因果knockout250个outcome-independent条目。paired5kbootstrap与McNemar。重复图像近2倍cache/3.9倍attention prefill，不叫零成本。
7. **证据边界：** Qwen3VL question-first→last NaturalBench+8.1pp；echo Q基本持平last，echo image再+2.4。全层answer→Q直边切断在SIT损5.6pp、STI近0，反之image直边STI损9.6pp/SIT近0；间接路径仍存在。对象词logit-lens可读不直接证明关系/答案正确；G的跨Q和diffuse重写是单图例，不把5%特异向量当总体。VQAv2采用whole-word containment放宽匹配，不是原封不动标准短答EM。
8. **可迁移动作：** 找一个违背合理直觉的操作结果，把直觉隐含的两个阶段拆开；给会改变解释的核心因果对比。近邻方法是工具，边界和反例可以形成更好的问题。
9. **对我们：** 不能把Q-before-S/echo或“编码与读取不同”称新贡献。开放的新问法是：自然句需要修订的角色关系，提前目标是否改善其他未询问关系，抑或使解释只服务某用途？用完整公开四构式、多问句迁移回答，避免把任务词可读叫可复用解释。
