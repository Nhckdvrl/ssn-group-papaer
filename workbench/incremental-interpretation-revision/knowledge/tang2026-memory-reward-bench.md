# MemoryRewardBench: Benchmarking Reward Models for Long-Term Memory Management in Large Language Models（作者v2，2026-01；接收未核对）

`[证据级别：主文精读＋构造／评测附录]` [arXiv2601.11969v2](https://arxiv.org/abs/2601.11969v2)，Soochow／China Mobile。29p PDF SHA017902eead6d428644c518f1017efbe34f151e0fe110d849bc2dfc293685bf6c；主文1–6 pp1–8全文，AppB/C pp12末–16及D1–5 pp16–17、辅助tag案例p29全文；p5Table3／p7Fig4–5视觉核。AppA和其余案例18–28／运行代码未全部读。

1. **论文形态：** memory process quality的generative reward-model benchmark；不用其“first”宣称代替独立定位。
2. **背景与压力：** chunk-memory是长上下文agent的中间状态，只有最终任务对不能判memory更新质量；已有memory bench主要评agent，转评judge是否能监督这种过程。
3. **idea来源（RECONSTRUCTED）：** 从最终答案评分→有memory轨迹的配对比较→把两个最终均正确但过程不同的材料单列→检查顺序、长度、图式与tag。新对象是评价中间memory的judge；一般“memory reward不可靠”已经明确拥有。
4. **数据／规模：** 2400配对／10settings／8–128k，来源BABILong／LongMiT、LoCoMo／MemoryAgentBench conflict-resolution、LongProc／LongGenBench／LongEval；Sequential／Parallel／Mixed。chosen正确结果，negative来自noise／删关键上下文／跳memory更新／改生成约束。process质量是作者构造偏好，不是人类完整自然memory真值。
5. **评测：** 13 generative LLM作RM，两轨迹加原context，随机AB；proprietary3/open10，temperature.7/top-p.95/max16384，未解析计错。Claude74.75、GLM68.21、Qwen3-Max67.79，Q3-8B57.33、Llama8B43.92。process同结局材料有位置偏向，outcome材料较稳定；不能以below50单独证明模型反向偏好，未解析项会降低分数。
6. **机制与边界：** 第四页已有“correct outcome but flawed memory”；general process-vs-outcome、长度退化、tags缓解均不是我们新发现。顺序/图式偏差是实测行为，作者将其归于causal training structures是解释，未有因果训练验证；sequential与mixed/parallel数据并非完全同难度配对。正文称Q3-32B62.88超过Q3-235B66.63与表不符，不借这个具体比较。长度表与总表Llama70聚合不一致，单调退化不是每模型每bin。
7. **构造校对：** AppB self-correct段文字称完整有错误/纠正的trajectory为chosen、去掉错误为rejected，与更简洁过程的主描述不一致，实际资产未核；不因此桌面判benchmark不可用。跳更新且终答仍对不自动意味所有任务未来用途更差，偏好范围要明确。tag案例p29无tag还将keywords改成element placeholders，不能独归语义tag本身。
8. **最近邻与我们的距离：** 其核心是generative judge可靠性，I07目前是未训练观测重建LP与正确修订失配；对象、信号和后果需明确。它不会自动完全覆盖我们，但泛称RM不会评memory、process比outcome难、加structured tags不够新。
9. **可迁移动作：** 优先复用成熟轨迹／原任务和已给标签，不为了质量重审全社区数据；真正需要构造“同目标语义的正确关系修订”才用Step Plan。I07接下来必须由独立真实任务锚测具体漏奖更新，并追训练／使用后果；不要转成另一套长context judge排名或位置控制网格。
