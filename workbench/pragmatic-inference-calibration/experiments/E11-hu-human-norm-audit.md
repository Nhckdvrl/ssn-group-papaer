# E11：Hu原始人类分布与选项编码核对（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 measurement
- **对应：** P02、C02；自然材料已有human标签优先于生成gold。
- **问题（一句话）：** 原始人类响应可否无新增标注映射到我们的选项读数，gold-only是否掩盖原有歧义？
- **设置：** 原Hu repo固定E01 commit；human_data/fj七CSV全保留，排除没有对应prompt的item并显式报数；原prompt seed0的original_labels与五次randomized_option_order建立映射。三已完成模型Flan-T5-XL/Qwen2.5-3B/Qwen3-4B原169项×五order。不是no-story负条件；不把人类错选当unlicensed gold。
- **读数：** 来源行数/participant/item覆盖，按原选项的human distribution、gold endorsement、modal与gold冲突数；模型五order平均分布/argmax比例，标准Jensen–Shannon divergence与human top-choice agreement（描述性）；按item bootstrap2000 draw seed0。各phenomenon分开，混合平均不作能力scalar。
- **阳性对照：** 每个human行重建Correct必须与公开Correct一致；同item original option coding across五order完全一致；概率归一；已复现原Flan1,365选择。
- **噪声地板 + MIE：** 描述原数据，不设paper效应阈值。participant重复响应不当独立item；bootstrap以item为单位，不支持总体human-population因果。
- **混杂审计：** 保持raw human与published prompt/labels，歧义以分布保留；固定原数据不是自然真实日志；nonliteral错误类不自动FPR。原人类Control未在公开human/fj中，不能制造negative gold。
- **决策表（跑之前写）：** A编码Correct一致且多数gold共识高 → human分布进入D2；B编码不一致 → 暂停指标汇总先核对来源，不改gold救对齐；C存在modal/gold分歧 → 记录原有歧义供后续slice，不能挑掉分歧题提高分数；仍不能识别warrant → C02保持L0。
- **算力预算：** CPU、现有frozen结果，无新训练/API；GPU预算0。

## 结果
跑前登记。这是原parent人类测量的驻留，不claim首次比较human/model分布。
