# E129：明确预测函数目标能否恢复同一随机MoE（2026-10-25）

- **状态：** DONE（固定128M终点；教师分布监督改善预测保真度，但未通过恢复尺度）
- **类型：** PILOT（一次oracle函数学习诊断，不替代CE主线）
- **对应：** P17；E125/E126四格128M已完成，覆盖有效，但fine/dense/coarse均未恢复，困难不只属于fine MoE。
- **问题（一句话）：** 同一随机MoE在更明确的教师预测分布目标下，能否逼近冻结语言函数？
- **设置：** 与E125 M-cover逐项相同的随机初始化、512M池、有放回split source/window RNG、seed0/order0、**15,625更新/128,000,000 token**、seq512/batch16、lr3e-4/warm.1/cosine、aux/AdamW不变。仅将主目标从GT CE改为温度1的逐token `KL(q_original_dense || p_student)`。teacher全模型冻结；每批原dense前向no_grad，student只训练L9 MoE；不缓存巨量soft labels。
- **读数：** 主KL与GT CE分别命名，teacher/student GT NLL、held/POS KL与NLL、teacher配对CI、load/gradient/frozen hash、实际曝光。完整原MoE初始化hash和matched step的输入/source链必须等于E125 M-cover；固定128M终点不early stop。KL均值按token，不按batch放大seq_len倍。
- **阳性对照：** 同预测KL=0、已知不同分布KL>0；teacher没有梯度/参数变化；KL gate/expert与aux梯度非零；计分的GT NLL仍为真实CE；optimizer/RNG/coverage resume一致。
- **噪声地板 + MIE：** 保留原+.02 NLL工程恢复尺度，同时连续报告held KL及CI；不凭训练KL低宣称函数泛化。单seed、文件CI非seedCI。
- **混杂审计：** KL同时改变目标、监督信息量和梯度，成功不能单因归“标签噪声”；teacher有额外前向计算，不能当等算力性能优越性。低held KL仅表示所测输入分布预测接近，非全局同函数或内部算法相同。此诊断不自动把自然CE角色结论换成distillation结论，不混进CE种子群。
- **决策表（跑之前写）：** KL恢复/CE失败→配置在教师目标下可学，恢复困难具有目标依赖性；原CE主线按E128继续，是否研究更强函数目标须明确界定；KL train低/held高→函数泛化/覆盖瓶颈；KL也未恢复→该预算/协议仍未建立平台，不拿其低对应推自由分工。若CE恢复则回CE跨seed，不扩KL支线。
- **算力预算：** 单卡最多3 GPU·时，训练加teacher前向，探索同时≤8卡。**实际：** 1.989 GPU·时，固定15,625步/128M token完成。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- **数字：** held NLL=2.564098，原dense=2.493813；配对差+.070285，95%文件CI[.049983,.104594]、90%CI[.051750,.098022]，未达到原+.02恢复尺度。held KL=.070615，95%CI[.051044,.103636]。POS词形均衡NLL差+.030685 [.010334,.052292]。单初始化，无种子方差估计。
- **控制：** teacher未变且无梯度；与E125 M-cover完整初始化、骨干hash、held窗口相同；每步来源链通过，输入独立重放通过。固定128M终点，不选中途最好检查点。250,000窗口抽取中221,009个唯一，重复11.5964%，同CE。
- **结果文件：** `results/e129/seed0.json`、`endpoint_summary.json`；原始逐序列与模型在`/tmp/xiang-moe-20261025/e129_teacher_KL_seed0/`，耐久副本与SHA清单见`results/e129/assets.json`。
- **按决策表：** 教师目标下有所改善，但此预算/协议尚未建立恢复平台；继续E128原CE512M固定终点。不增加KL训练网格，不以未恢复bank推专家职责自由度，不替换CE主线。
- **主张变化：** 无。C06保持L1；没有跨seed主张。
- **POST-HOC：** 固定终点逐held窗口配对比较相同初始化/输入/日程的E125 M-cover，按32个文件bootstrap 1000次：KL变化−.019086，95%CI[−.021794,−.016609]；GT NLL变化−.009467 [−.012523,−.006456]。只描述单seed、所测分布上的目标差异，非等算力优势或标签噪声单因解释。脚本`scripts/e129_summarize.py`。
