# 反复回到 Xeno：真正独立的科学问题（2026-10-12）

基于 [45 页原论文重新精读](papers/PIERUCCI_2026_XENO.md) + [核心论文精读](papers/CORE_READS.md)。**地图不是自动选题，也不构成已验证假说。**

## 1. 先准确理解“新在哪里”
Xeno 问的不只是“缺了一条人工概念标签”。作者把**表征形式**（direction / manifold / circuit）、**跨模型共性**（universality）与**语义可达性**（human concept translation）分离，并提出 **designation → model-native geometry/relation → causal relevance → semantic interpretation 最后尝试** 的研究顺序。成功结果不必须是漂亮的 human-readable label；也可能是一套可复现的、能作预测的模型原生关系定律。**这是值得探索的研究纲领，但尚未证明对应对象真实存在。**

## 2. 不是零人做过；要认真区分“重叠”究竟在哪

| 谱系与有力证据 | 确已做过 | 尚未等价于 Xeno 哪一部分 |
|---|---|---|
| Goyal et al. NeurIPS2025 Spotlight | 无人工概念标签地学 **causal differentiating concepts**，合成与 refusal 有严格对照 | 目标仍是找到可解释的人类因子；并未研究语义不可充分翻译时怎样形成可预测的模型原生科学 |
| Gurnee et al. Transformer Circuits2026 | J-space 可测 **verbal reportability**，干预/跨任务证明其功能 | verbalize 失败不能证明语义不为人类概念可表达；其对象不是 J-space 之外真正 model-native semantic structure |
| Parisini et al. 2026 | 任务 Fisher 几何探测**已有概念集缺漏** | 真实任务 C3 是事先知道而刻意隐藏；不是未知模型本体的直接发现 |
| Ma et al. NeurIPS2025 / ICML2026 | 强解释反例、词面混杂能推翻错误 concept claim | 测量解释可靠性，不能证明 model-native 语义不存在或已被穷尽 |
| Causal Abstraction / MIB / SAEBench | 对预先规定的高层变量/任务测因果抽象与实用性 | 通常默认高层描述已被人类指定；发现和语义可达性没有同时被独立测试 |
| Paulo&Belrose ICLR2026；Sheng&Fu 2026 | feature seed instability、比较粒度改变“机制相似”结论 | 结构稳定性与语义可翻译性不是一回事 |
| Sutter et al. NeurIPS2025 | 灵活因果对齐会产生**伪解释**，随机网络也可能有高分 | 负对照标准，不是证明所有新的内在结构都不存在 |
| Williams et al. Philosophy Position 2025 | 表征本体/解释/内容的理论问题已有讨论 | 没有完成 Xeno 所要求的真实系统开放式发现和模型原生规律构建 |
| ViSAE ICML2026 | 原文表4/7/8：视觉大词表明显改变解释覆盖和背景 steering（50.3→98.5% worst group） | 人类词表越大，不能直接推出陌生关系维度完全不存在 |

**不能以“概念缺失”“unsupervised feature discovery”“steering”作为 Xeno 论文的独立新颖贡献。也不能因为这些近邻就将它的实质命题判为已解。**

## 3. 同一可观察异象有四种竞争解释
- **E1 表达力差**：单词标签失败，但组合逻辑、程序或长描述能充分预测 holdout 激活与干预；
- **E2 分析器幻觉**：SAE seed、数据、特征抽样、坐标或 off-manifold 干预制造了对象；
- **E3 普通的计算中间量**：稳定重要，却可以归于捷径、低级统计、已知机制组合，而非未知语义；
- **E4 人类概念不足（相对给定表达集合）**：即使 E1–E3 的强对照全部通过，仍存在稳定、跨任务、可干预、提供额外可预测关系的 ξ。**不能夸大为原则上永远无法被人类理解。**

## 4. 三个值得保持开放的“探索空间”，都不是固定论文 idea

**A · 不依赖翻译的内部表征科学。** 能否在不知道概念词义的情况下，对跨上下文 ξ 建立独立预测关系（什么同时变化/什么不变/如何影响自然计算），且相较等预算的人类语言、程序/组合概念解释提供可检验增量？强基线 Goyal 无标签发现、J-space、Ma2025 hard negatives、MIB；反事实：如果复杂的人类解释已能同样准确预测，Xeno 的经验余量可能消失。

**B · 找到哪一层“对象”是自然的。** SAE features、联通边、可逆坐标、跨层群关系、因果等价类，哪一个在更换工具、随机种子、变换坐标与 model family 后稳定预测行为？强基线 Paulo/Belrose、Sheng/Fu、Sutter；核心不是换个方法提高 overlap，而是确定何种**模型原生关系规律**免疫分析器选择。

**C · Collective xeno 与 agent 消息的功能语义。** 共同训练的多 agent 是否形成稳定 sender-state / message / receiver-state 因果关系，而人类基于消息文本的意图、奖励和上下文解释对接收方后续选择仍不足？需要 receiver swap、同消息不同 receiver、训练前后与改写消息对照，排除简单暗号/压缩协议/普通 latent state。此线应先读 emergent communication 和表征共适应强文献，不能直接猜效果。

## 5. 好的研究动作：先让各种解释分别承担风险
- 从**自然发生的任务/模型行为或已报道现象**而非随意造“外星向量”出发。
- 先找强 baseline。预注册真正区分 E1–E4 的读数、近似误差和随机/错误模型对照；做 blind discovery 与 held-out intervention 而非“事先隐藏已知 C3”。
- 至少两种不同证据：统计预测/结构稳定 + 自然分布的因果预测；可跨不同模型或训练配置时再升级结论。
- 允许自然语言、逻辑表达、数学规律解释 ξ；对“语义不可充分表达”只给**明确限定的操作性结论**，不能以无法命名的主观感受做成功标准。
- 有**实验异常→竞争解释→反证→更一般理解**的链才算进入 idea；不把阅读笔记扩写成十个臆测题目。暂时不排时间、不启动 GPU。

## 6. 本次精读留下的可核查缺口
- Tang et al. NeurIPS2026 **Position** 《Concept-Based MI Needs a Concrete Evaluation Paradigm》Zenodo PDF 下载超时：可以确认存在与问题，不可冒充全文读过；
- Delisle & Tan 《Bypassing PC1...》NeurIPS2026 作者确认收录但未发现可核全文；
- NeurIPS2026 Downloads 另一篇不同标题的 circuit description level 论文作者/全文尚未核验；**不能偷换成已读 Sheng&Fu**；
- Song et al. ACL2026 的正式 PDF 过大/入口受限，只核到摘要和早期版本片段；
- ViSAE 已由 alphaXiv 提供可核的 19 页原始论文，完成主要方法/图表/强消融阅读；
- 新近邻随 2026 正式 proceedings 发布仍应更新。上述为**确实无法完成的获取问题**，不伪称全量完成。
