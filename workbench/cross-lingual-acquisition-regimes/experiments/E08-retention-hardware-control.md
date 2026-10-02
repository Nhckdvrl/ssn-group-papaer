# E08：retention-hardware-control（2026-10-02）

- **状态：** DONE（1200条primary均与legacy完全一致）
- **类型：** REPRO（真实适配代价的必要校准，不是新冻结probe分支）
- **对应：** P04/P05
- **问题（一句话）：** E06适配前后的翻译/照抄变化，能否在同一硬件、精度与解码实现下保留，而不是旧测量环境或默认cache差异？
- **设置：** 原始FWB/MWB/+P34K固定HF revision，与E06同fvcrc20 GPU3；同400条输入、FP32权重/计算、batch8、greedy256、newline/EOS、explicit cache=True。primary及E06原固定instruction各一遍，不改prompt。独立输出，绝不覆盖legacy原始输出。三组在一张卡顺序跑；记录原始manifest/hash及与E06实现的协议一致性。
- **读数：** 两方向corpus BLEU/chrF、原句精确照抄/empty/cap/overflow；对照legacy逐item预测一致率，并与E06 post做同硬件paired sentence95%CI。既有200 news句不是跨领域总体估计。不得只挑照抄句或幸存条件。
- **阳性对照：** 原始干预翻译差已在E00阳性复现；同输入hash/所有ID顺序、无输出过滤；原始完整LM而非classification backbone旧head。
- **噪声地板 + MIE：** greedy复跑用于测环境差，不是新的训练seed。若差异足以改变E06代价判断，明确降级旧pre/post结论；不能用200句CI代替训练种子重复。
- **混杂审计：** 与E06后测硬件/库/精度/解码协议统一；训练seed只有17，预训练家族且干预内容不完全相同仍未控。original instruction对照此前没有，本次预注册、不能挑prompt。精确照抄是可审计输出行为，不等同全部语义遗忘。
- **决策表（跑之前写）：** legacy与本次近似且pre/post下降保留→把P05作为真实训练痛点做最小训练干预；环境差解释主要下降→撤回/降级，不启动防遗忘故事；下降只在primary、instruction恢复→优先接口而非知识丢失；不稳定→保留未定，不追加prompt搜索。
- **算力预算：** 同一空卡依次三组总≤3 GPU·时；与E04总并用5张。**实际：** 尚未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
E06发现时数字已经可见，所以本卡是后续校准，不冒称为独立预期发现。尚未运行。

完整校准完成：三条件×两方向×200条primary prediction与legacy逐条完全一致（1200/1200），同Blackwell/FP32/explicit cache也未消除E06下降。生成loop AST核对完全相同。
MWB同instruction before→post两方向11.86→9.21、20.74→16.55 BLEU；delta=-2.65[-4.31,-1.09]/-4.18[-7.21,-1.95]。
+P德→英instruction before28.42→post28.13，delta=-0.29[-3.52,1.94]：不能只用primary26.01→27.81宣称任务学习增强翻译。
结果 `results/e08_retention_hardware_control.json`，原始 `artifacts/retention_hardware_control/`。P05环境混杂被削弱，适配seed/任务/family/领域边界仍在；无L2/L3升级。按事前表，E09可进入全部条件的实际训练重复，E10可测既有CPT的保持。
