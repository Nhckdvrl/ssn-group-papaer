# 主张账本

没有语用能力、post-training 或 SDT 的实证结论。技术资产与科学解释分开；L0 待测不表示已观察。

| ID | 主张（一句话，可证伪） | 等级 | 证据（实验卡、结果文件） | 已知威胁 / 未控制混杂 | 最近更新 | 校对 |
|---|---|---|---|---|---|---|
| C01 | 原始 MultiPragEval 数据与公开评测协议可在本地 open weights 上复现并保持客观评分。 | L0 | [E01](experiments/E01-substrate-audit.md)、[E02](experiments/E02-multiprageval-native-reproduction.md)；原14B四语言三seed完成；原数字误差与解码限制见状态页 | 官方 config、checkpoint/chat template/解码差异 | 2026-10-03 | 未校对 |
| C02 | 至少一个自然 parent substrate 能分别识别 warranted 与 unwarranted inference，不能把所有错误叫 false alarm。 | L0 | [E01](experiments/E01-substrate-audit.md)、[E05](experiments/E05-annotation-feasibility.md)；标签可识别性未成立 | literal accuracy ≠ FPR；任务难度/措辞与 inference-choice 标签 | 2026-10-03 | 未校对 |

## 技术资产（不是paper贡献）

Flan-T5-XL 1,365个选择与作者公开结果全部匹配，概率MAD=0.000077；[E04](experiments/E04-hu-native-logprob.md)、[结果](results/E04-flan-parent-parity.json)。这是D1复现资产，不据此升级pragmatic claim。

## 候选解释（不作为 finding）
- H-A：训练阶段/规模提高语境辨别能力。
- H-B：主要改变推断倾向。
- H-C：两者都变；也可能没有跨现象共享的 criterion。
- 来源 **RECONSTRUCTED**：ALTPRAG gains × PaCE literal-side cost。只能同设定检验，异构数据的差不是因果证据。

## 作废 / 降级记录
当前已有baseline行为读数，没有已升级的scientific claim。

- 2026-10-02 E03技术校对：初版Qwen3未显式关闭thinking，与parent不一致；16.4204 MAE作废为能力/复现证据，保留原文件并按原protocol重跑。不是预注册hypothesis的反例，也不是新finding。

- 2026-10-03 E08：BF16 batch-dependent与Flan target-left-padding读数不通过gate，原文件保留，隔离科学解释；FP32/right-pad替代运行通过，不事后改旧结果。
- 2026-10-03 E19：Flan数字候选非一token，atomic协议不可用；GPT2-r2绝对position gate失败、无预测，r3显式position修正后通过。IR缺40条件不插补。
- 2026-10-03 E17：旧item-summary的MAE bounds对应E|X−t|，不能用于|E[X]−t|；新summarize_sampling明确分开，两份历史文件均保留。
- 2026-10-03 C01/C02仍L0：精确复现与技术修复不自动形成语用主张；仍无合法SDT gold；stage任务读数已出现但未形成可靠科学主张。

- 2026-10-03 E21/E16/E19/E20：OLMoE Base与SFT虽共用Jinja template，但bos=None/50279及special-token mapping不同，actual chat prompt/token SHA不一致。旧聊天结果隔离于stage归因；E12裸入口仍有效，E26逐词token parity通过，E27固定完整tokenizer并控制两个BOS。原文件不覆写，不升级能力。
- 2026-10-03 E24/E25：ImplicatureX源BF16 pair和不总是1，True>.5与True>False不等价。小模型自然recognition数字对算术/选项顺序敏感；仅源数据描述和技术复现，不据此 claim universal hallucination 或整个parent结论无效。

- 2026-10-03 E29：首轮access regex窄导致8run全部在模型加载前停止，0预测；r2源变体全量预检后完成。OL SFT/DPO裸入口全量历史parity各一题超.001，整入口隔离细粒度归因，不局部替换行。role full恢复同时partial恶化/极性不一致，不称知识能力恢复。E30仅数值debug。

- 2026-10-03 E28/E31–37：强现代端点与两组自然强度素材全部完成，有界strict/Flan控制完成。C01/C02不升级：IQAP含词汇/terminal prior、Circa负强度有巨大order effect；一句指令改善强侧可能恶化弱侧，不能用单侧恢复claim能力。原数据/条件/两order均保留，完整结果可审；E35第三family仍运行。没有post-training统一criterion证据。
- E35跑前两次CPU gate：Hu尾部重复空格会retokenize；官方Mistral chat_template完整重渲染assistant时丢system。二者0 GPU预测，冻结原generation prefix与nativeassistant内容后全量前缀通过；不算模型语用错误。
