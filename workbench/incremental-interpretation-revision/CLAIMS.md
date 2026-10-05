# 主张账本 — Incremental Interpretation & Revision

**状态：2026-10-05 / PROPOSED baseline residency。**

当前有一条局限于固定模型/协议的本地测量事实C03，尚无已确立的paper idea。C00–C02仍是待验证对象，不能写成revision机制finding。

| ID | 待验证对象 | 等级 | 当前证据 | 升级条件 |
|---|---|---|---|---|
| C00 | 本地 harness 能在公开 GP 数据上复现一个已知的 GP-specific behavioral deficit | L0 | [E00](experiments/E00-baseline-reproduction.md) / [结果](results/E00-summary.json)：全 16-prefix 主效应 −2.81 pp [−11.50, 5.89]，顺序敏感，gate 未通过 | E00 阳性对照通过，并报告 item-paired CI |
| C01 | interpretation revision 可被“最终解释支持”和“初始错误解释残留”两个读数分开测量 | L0 | [E01](experiments/E01-component-revision-map.md) / [partial](results/E01-partial-summary.json)：独立Step5审核3句/13QA，104任务；NPZ对比只有一个lexical set，role与semantic不同响应待全量核对 | 受控构式中不同读数的响应具有稳定、可重复结构；不把语义兼容命题强标错误 |
| C02 | 不同 cue timing / cue strength 条件下存在可区分 competing accounts 的 revision structure | L0 | 仅 territory hypothesis | 预先写出不同解释的预测并由 E01/E02 区分 |
| C03 | 固定Qwen3-8B的GP/nonGP问答差值随query顺序反向，且反转不依赖assistant prefill或few-shot demos | L1（measurement；非novelty） | [E03](experiments/E03-e00-order-and-assertion-audit.md)、[E07](experiments/E07-native-readout-transfer.md) / [E07结果](results/E07-summary.json)：neutral/native/base交互+60.87 pp [44.93,76.81]；全部8个boundary×system×instruction交互正；67-set sensitivity同方向 | 下一步[E08](experiments/E08-reading-focus-versus-final-query.md)将final query固定，区分reading focus与回答启动/位置；目前不归因为内部parse或一般LLM能力 |

**禁止提前升级：**
- 上游已报告的 garden-path effect 不是我们的 C-level novelty；
- “某模型答错很多”不是机制主张；
- probe/hidden-state separability 不能单独升级为“模型保留旧解释”。

## 作废 / 降级 / 未通过记录
- 2026-10-05 用户修订：取消agent用C00校准结果限制E01的停步gate；保留旧结果/证据等级，直接推进[E01](experiments/E01-component-revision-map.md)。C01/C02是measurement对象，不预注册novelty；最新论文ownership见[知识库](../../library/themes/incremental-language-processing/FIELD_MAP.md)。
- 2026-10-05：E00 不升 C00。句先有已知方向，但 prompt suite 整体不稳定；不得把选择句先视作通过。E03 注册追 why，原 E00 结果完整保留。

- 2026-10-05：[E04](experiments/E04-known-positive-control.md) 正方向 +19.84 pp [14.04, 25.82]，但 nonGP 30.71%、raw specificity DiD CI 跨零；[E05](experiments/E05-response-meaning-calibration.md) 8B 的 assertion response 下句先 +30.43 pp、题先 −23.91 pp。C00 不升级；原协议有效性问题未解决，不能把 positive direction 当严格 gate。C01/C02 未运行。

- 2026-10-05：[E06](experiments/E06-attachment-versus-event.md) GP subject-role控制仅0–5.80%，object-No高分不作为恢复证据；C00/C01/C02仍L0。nonGP joint读数是P06的测量痛点，不作隐藏parse或novelty主张。

- 2026-10-05：[E11](experiments/E11-extension-role-reference-audit.md) n1外审概率pilot：无歧义blocked extended的原短NP role PYes=.0404→fullNP=.9999，final semantic=1；不再将这项role extension下降解释为digging-in/commitment。四配置fullNP同向，head有题先失败；GP extended的新增问句未审完，结论范围明确限制。不是拒绝C01，也不是升级其能力/机制主张；旧E01分数和全部prompt保留。

- 2026-10-05：[E12](experiments/E12-input-probability-versus-answer-access.md) source processing存在提前Q效应，24clusters的GP−cue disamb交互+1.47 bits [.47,2.52]由cue facilitation主导；source word预测与最终QA不可混作同一读数。C03固定协议测量保留，C01/C02仍L0，不据此主张内部parse/承诺机制或novelty。
