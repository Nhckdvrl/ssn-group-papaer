# E129：明确预测函数目标能否恢复同一随机MoE（2026-10-25）

- **状态：** RUNNING（GPU KL/aux梯度、同CE输入次序与无teacher梯度检查通过）
- **类型：** PILOT（一次oracle函数学习诊断，不替代CE主线）
- **对应：** P17；E125/E126四格128M已完成，覆盖有效，但fine/dense/coarse均未恢复，困难不只属于fine MoE。
- **问题（一句话）：** 同一随机MoE在更明确的教师预测分布目标下，能否逼近冻结语言函数？
- **设置：** 与E125 M-cover逐项相同的随机初始化、512M池、有放回split source/window RNG、seed0/order0、**15,625更新/128,000,000 token**、seq512/batch16、lr3e-4/warm.1/cosine、aux/AdamW不变。仅将主目标从GT CE改为温度1的逐token `KL(q_original_dense || p_student)`。teacher全模型冻结；每批原dense前向no_grad，student只训练L9 MoE；不缓存巨量soft labels。
- **读数：** 主KL与GT CE分别命名，teacher/student GT NLL、held/POS KL与NLL、teacher配对CI、load/gradient/frozen hash、实际曝光。完整原MoE初始化hash和matched step的输入/source链必须等于E125 M-cover；固定128M终点不early stop。KL均值按token，不按batch放大seq_len倍。
- **阳性对照：** 同预测KL=0、已知不同分布KL>0；teacher没有梯度/参数变化；KL gate/expert与aux梯度非零；计分的GT NLL仍为真实CE；optimizer/RNG/coverage resume一致。
- **噪声地板 + MIE：** 保留原+.02 NLL工程恢复尺度，同时连续报告held KL及CI；不凭训练KL低宣称函数泛化。单seed、文件CI非seedCI。
- **混杂审计：** KL同时改变目标、监督信息量和梯度，成功不能单因归“标签噪声”；teacher有额外前向计算，不能当等算力性能优越性。低held KL仅表示所测输入分布预测接近，非全局同函数或内部算法相同。此诊断不自动把自然CE角色结论换成distillation结论，不混进CE种子群。
- **决策表（跑之前写）：** KL恢复/CE失败→配置在教师目标下可学，恢复困难具有目标依赖性；原CE主线按E128继续，是否研究更强函数目标须明确界定；KL train低/held高→函数泛化/覆盖瓶颈；KL也未恢复→该预算/协议仍未建立平台，不拿其低对应推自由分工。若CE恢复则回CE跨seed，不扩KL支线。
- **算力预算：** 单卡最多3 GPU·时，训练加teacher前向，探索同时≤8卡。**实际：** 未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：
- 结果文件：`results/...`
- 按决策表执行了什么：
- 主张变化：C## Lx → Ly
- POST-HOC 分析（事后才想到的，单独标注）：
