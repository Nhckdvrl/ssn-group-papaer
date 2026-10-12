# 近邻所有权、重合与还需确认的增量

本表不输出自动 novelty 判决；其作用是避免把现成认知重复包装。正式 nomination 前必须打开原论文实际主文/关键附录和开源代码更新边界。

| 文献（证据状态） | 已经拥有的结论/设计 | 当前项目容易重述的弱命题 | 真正不同的实验主张需要什么 |
|---|---|---|---|
| Amouyal 2025/2026 ACL MAIN，既有卡主文 | 人-LLM跨结构 GP 困难、plausibility、复述，统一问答 | GP 异常/强模型也难 | 经任务语义清理的因果计算解释或普遍性边界 |
| Hanna & Mueller NAACL25 MAIN+附录，已复核 | 多解析 features、GP prediction/QA 功能分离及有限介入 | 看得到不一定用，两个读数不一致 | 可外部验证的新关系依赖形成的因果条件 |
| Slattery/Sturt/Ceháková 历史研究，已有卡 | good-enough、残留、局部/混合解读 | 撤回与建立是两件事 | 预测失败条件/机制，非重新贴标签 |
| Yoshida ACL26 MAIN，已有卡 | surprisal 解释 GP 读时的存在性证明 | 一项测试不支持就否定处理模型 | 对被测对象作正确 counterfactual |
| ABBEL v2 MAIN+部分附录/代码，已有卡 | 可训练 belief 内容、观察重建评分 | 用观察验证记忆的想法 | 真实观察重解释造成 *可预测的* 错误 credit，能影响学习/选择 |
| ReBel v1 MAIN+部分代码，已有卡 | 延迟 predicate feedback / credit | 所有 belief reward 都误奖 | 区分 reconstruction 与 predicate checker 适用条件 |
| TRLM / IW-OPD / Self-CTRL，已有卡 | inverse feedback、prefix compatibility/token allocation、consistency | 逆向分数/删前缀就是方法 | 语义上为何 revision evidence 与 observation prefix 竞争的新机制 |
| Causal Quotient 2610.05292预印本 MAIN+方法附录，已有卡 | recoverability/use/scale 分别测，causal quotient | 形式上状态在但使用错 | 具体新依赖的可验证生成、存储、使用规律 |
| Zhao et al. ICML26 摘要（本次） | compressed experience 的因果使用缺陷 | agent memory 不一定忠实 | 解析冲突的依赖级变化、非泛忠实使用 |
| Zou et al. ICML26 摘要（本次） | active evidence selection 和 belief tracking 互相制约 | agent learning evidence 信号受损 | 在固定观察下特定语义重解释的可识别错误机制 |
| MemoPilot ICML26 摘要（本次） | memory 更新经多轮 GRPO 训练 | 首次优化 memory 更新 | 对训练对象提出有原因的缺陷与可检验干预 |

**本项目不可宣称：** “第一篇发现 LLM 读错 GP”“第一篇区分 parse 和 QA”“第一次发现恢复旧读法不等于新依赖”“第一次用 prefix/suffix likelihood / inverse feedback”“证明 ABBEL / ReBel 的训练有问题”。

**保留开放性：** 近邻已研究宽命题 ≠ 我们的具体问题被覆盖。关键是把自己要解释的对象、输入干预、因变量、竞争预测与近邻对齐，尝试寻找更深的统一规律；只要真实重要且未解释充分，即使不是完全无人研究，也可能构成强论文。

直接来源：公共知识库的同名论文卡与会刊主页：[Hanna](https://aclanthology.org/2025.naacl-long.164/)；[Amouyal 2026](https://aclanthology.org/2026.acl-long.1040/)；[Yoshida](https://aclanthology.org/2026.acl-long.1694/)；[Zhao 2026](https://proceedings.mlr.press/v306/zhao26aw.html)；[Zou 2026](https://proceedings.mlr.press/v306/zou26b.html)；[MemoPilot](https://proceedings.mlr.press/v306/cai26b.html)。
