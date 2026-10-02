# E06：qa-adaptation-translation-retention（2026-10-02）

- **状态：** PLANNED（E03完整LM保存后运行）
- **类型：** REPRO（训练流程的能力代价，不是新idea）
- **对应：** P03/P04
- **问题（一句话）：** 英语QA学习后，原有翻译差别是否保留，下降是否只是任务格式变化？
- **设置：** E03三条件seed17终点完整LM+tokenizer，不是NLI分类权重；原始WMT16前200对、五shot/harness/corpus不变，FP32/greedy/batch8/max256/newline停止。沿既有before输出共同eligible ID，无表现筛选。post primary与统一一句 `Translate the final phrase into {German/English}. Output only the translation.\n` 恢复对照都保存逐题，溢出算空/错，不排除。
- **读数：** 两方向corpus BLEU主/chrF辅；post−before、instruction−post，200句paired bootstrap95%CI、空/复制/cap、hash/成本。无中间LM时间机制推断。
- **阳性对照：** 既有三模型两方向BLEU24.16/11.47/21.36与28.90/20.11/26.01；输入hash、QA completion和真实共同训练的LM head核对；scorer/signature一致。
- **噪声地板 + MIE：** 小固定news集发现性诊断，item CI非topic/训练seed方差；约3 BLEU是扩展优先级，不是等价或自动否决门槛。有实际代价再扩完整测试/种子。
- **混杂审计：** 原始pre已见、post未测，非独立confirmatory发现；一句恢复不能证明所有能力完整，无恢复也不能证明知识删除。只量训练流程代价，不以冻结prompt单独证明机制。
- **决策表（跑之前写）：** primary下降但一句恢复→格式/调用变化，不称遗忘；两者下降→实际代价候选，独立注册训练救援；保留→留资产不追加prompt小优化。无novelty升级。
- **算力预算：** 三单卡各≤1 GPU·时，总≤3；白天总≤8。 **实际：** 未运行post。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 运行前实现核对：QA保存的config关闭training cache，post生成显式 `use_cache=True`，与原始模型默认生成和E03评测一致，不改变训练权重或读数。
- 数字（含 CI / 种子方差）：
- 结果文件：`results/...`
- 按决策表执行了什么：
- 主张变化：C## Lx → Ly
- POST-HOC 分析（事后才想到的，单独标注）：
