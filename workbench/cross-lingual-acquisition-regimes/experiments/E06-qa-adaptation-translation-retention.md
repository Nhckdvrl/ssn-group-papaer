# E06：qa-adaptation-translation-retention（2026-10-02）

- **状态：** DONE（三条件完成，实际代价待E08同硬件校准）
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
- 启动资源：fvcrc20空闲GPU3，三条件依次测量，记录实际Blackwell硬件；不把pre/post可能的硬件差异掩盖为同设备因果控制。FP32协议固定。
- 数字：FWB/MWB/+P英→德before→primary→instruction BLEU为24.16→21.15→21.50、11.47→7.92→9.21、21.36→21.59→22.16；德→英28.90→27.84→28.14、20.11→15.91→16.55、26.01→27.81→28.13。
- MWB primary−before两方向paired sentence95%CI为[-5.35,-1.95]/[-6.79,-1.92]；instruction−before仍[-4.05,-0.52]/[-6.45,-1.39]。single seed及固定news范围不变。英→德source copy FWB1→48→40、MWB27→103→101、+P2→12→11（每方向200）。
- 结果文件：`results/e06_qa_translation_retention.json`，全部input/输出hash、chrF、CI、诊断；原始 `artifacts/qa_retention/`。权重保存/加载不在generation elapsed内。
- 按决策表：P05记录真实训练痛点候选；先E08统一before硬件/协议，不立即开防遗忘方法grid。E07准备标准译料监督参照；不以任务换名主张novelty。
- 主张变化：无L2/L3升级，原leading acquisition叙事仍撤回。
- POST-HOC：无新增prompt或幸存切片；E08为发现后的必要环境校准，另写卡。
