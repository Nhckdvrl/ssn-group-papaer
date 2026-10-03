# E65：E59全局答案变化的来源外预测（2026-10-03）

> 关闭后保留的历史证据：2026-10-03用户决定终止；原始输出、数据和实验runner现已删除。文中local raw路径为历史定位，不能再逐条重算；最终汇总保留。代码可从关闭前Git快照51a578c1追溯。

- **状态：DONE。** 本卡先于拟合与结果分析；E59结果已知，本次为竞争解释的收尾鉴别，不是新方法。
- **类型：D2 / 解释诊断，C03/P02。**
- **问题：** 仅全局类别偏好与尖锐程度变化，能否在未拟合的来源上预测OLMo2 SFT→DPO的四类分布变化？
- **设置：** 只读E59现有SFT/DPO924行与源IQAP；150 development项目、68来源，全量保留。3固定alias×2接口×2原读数都报告；primary common-chat/full W0，W1/W2为已有措辞检验。0新模型/措辞/采样/API/推理。IQAP65evaluation不读、不用于拟合。
- **竞争模型：** identity；bias-only softmax(log p+b)；temperature-only softmax(a log p)；combined softmax(a log p+b)；train-fold平均DPO分布为constant参考。b零和（3自由参数），a∈[0,8]；偏置每自由参数∈[−20,20]，固定1e−6 L2抑制数值病态。不调超参/增加特征/复杂度。交叉熵只拟合DPO软分布，不用human目标或语义标签拟合。
- **来源划分：** 按原Source整组，5fold，按组大小降序、固定seed20261003打乱等长组并贪心平衡item数；第二固定seed1作划分敏感性，不筛seed。每alias单独fit同样fold，不能拆同来源/同item的不同alias到训练与验证。所有项目恰好一次OOF预测，保存fold/source/item清单和hash。secondary将W0训练出的映射迁移到W1/W2同fold。
- **读数：** held-out transport四类平方距离/KL与identity/constant差；human分布距离的真实阶段增量与transport预测增量、残余增量；配对方向与类别误差。参数仅描述，不解释内部能力或DPO算法因果。完整逐项OOF结果存本地，小汇总进git。
- **阳性对照：** E59原config/raw/source hash与源/完整候选概率算术逐项验证；全量原Brier差重算与summary差<1e−10。人工已知global-map(a=.7,b=[.3,−.2,.1,−.2])和identity在相同SFT输入上的5fold预测必须MSE<1e−7；constant标签支持可拟合。检查组间无泄漏、归一化、参数梯度与finite；不是对新data的能力控制。
- **噪声地板 + MIE：** 固定float64 CPU；梯度finite-difference max误差<1e−5；拟合converged否则全组标不可用，不能宽松重定义。2000bootstrap seed0按Source重采样评估OOF配对读数；CI条件于已拟合模型/固定fold，不是training-seed或完整refit CI。第二split结果全部保留。
- **决策表（跑之前写）：** A combined在三primary-chat alias及两个split均比identity减少≥80%transport误差，且预测的平均human距离增量误差绝对≤.05 → 主要变化可由低维全局映射解释，C03仍真实任务观察但不追为语用能力线索。B简单模型不足且残差稳定 → 仅记录global账户不完整；需独立带norm材料检验语境结构，残差不能直接叫pragmatic机制。C参数/读数/source gate不成立 → 未识别，先定位bug，禁止更复杂拟合救叙事。阈值为资源决定heuristic，不是自动科学判决。无论A/B都只进入已授权的canonical人类条件数据核查，不开新邻接对象。
- **混杂审计：** 新拟合有少量自由参数，OOS非因果；a/b是任务响应映射，不等于温度/真实决策criterion。原paraphrase human norm未新采；人群比例非内在confidence。单checkpoint阶段共变训练数据/算法。constant偏好也可能来自原任务，不能泛化所有语用现象。
- **算力预算：** CPU only，0 GPU/API/下载；本轮新推理总上限15GPU·小时，数据核查未过前不启动推理。

## 结果
已完成24组（12设定×2split）来源外诊断；所有拟合/梯度/已知映射控制通过，primary combined参数未触及边界。0新GPU/API。

| primary聊天/full表述 | 实际human距离增量 | combined对identity的OOF误差减少 | 残余平均human距离增量（来源CI） |
|---|---:|---:|---|
| W0 | +.3128 | 96.25% | +.0040 [−.0044,.0124] |
| W1 | +.3419 | 93.23% | +.0078 [−.0276,.0793] |
| W2 | +.3771 | 90.92% | +.0189 [−.0274,.1173] |

第二split为96.25%/93.20%/90.96%，三个平均残余误差均≤.05，六个预定资源条件都满足A。CI较宽且未做等价检验，不宣布残余为零。

这不是“DPO不看对话”：constant参考比identity更差；纯bias只减少46.2%/40.3%/62.0%，纯sharpness为92.4%/89.2%/67.9%。combined仍依赖SFT逐题对话分布。结论是低维全局映射在来源外预测主要变化，不能把C03均值距离恶化当作已识别的语用能力下降；C03原任务观察仍L1，解释优先级降级、不追论文线索。

[汇总](../results/E65-global-transport-summary.json)；OOF保存于`/data1/xiangding/work/pragmatic-inference-calibration/runs/E65-global-answer-transport/oof.jsonl`。source hash、全部分组、参数、两split与control在汇总中，不筛alias/seed。
