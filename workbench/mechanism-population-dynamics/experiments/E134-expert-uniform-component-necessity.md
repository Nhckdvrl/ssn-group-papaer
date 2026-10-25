# E134：专家身份相关的加权偏差项对预测有多必要（2026-10-26）

- **状态：** READY（干预读数产生前登记；无新增训练）
- **类型：** MEASUREMENT / PILOT；对E130–133现象的任务必要性检查。
- **对应：** P22：弱作用对应不自动等于任务重要的分工变化；E132随机foreign bank仍保留较多预测效果，需直接检验原生加权偏差项，而不是继续换匹配指标。
- **问题（一句话）：** 移除相对专家逐输入均值的原生加权偏差，同时保留输入相关的专家均匀分量与原门值总量，会怎样改变整模型预测？

## 对象、分解与六个条件（结果产生前固定）
- **设定：** E130全部5个真实固定终点（seed0–4，L9）；另加已固定资产的公开原生OLMoE main L9，检查受控设定边界，而不是为L3凑模型。所有模型同Dolma held512窗口/262144 target token，仅比较各自内部的干预差；跨模型差异不能单因归冻结，因为训练量、数据、架构等也不同。
- 对同一输入h，原生MoE输出记y(h)，实际应用的top8门值记w（沿各自norm_topk设置并保留实际dtype约定），`s(h)=sum w`。定义 `m(h)=mean_ALL64 f_e(h)`、`c(h)=s(h)*m(h)`、`r(h)=y(h)-c(h)`。
- c称**专家均匀分量**，不是预设的generic/common knowledge，也不是数据集均值向量；m仍可能包含复杂专门知识，c仍保留router总量信息。r不等同E130的标量U/A指纹。分解代数本身不算科学发现。
- 六条件：native、c-only、r-only、zero、c+r重组、单个全局`gamma*c`。所有位置使用替代L9输出，其他参数/层保持原生；不微调、不改输入或router门值。保持返回dtype及Tensor/tuple合同；c/r在FP32缓存中定义、返回原输出dtype，重组直接测数值复现。
- **全局gamma：** 在独立training-only Hcal8192上，以 `sum <c,y>/sum ||c||²` 闭式拟合一个模型级标量，不用任务标签/held、不做每专家/输入缩放或截断/搜索。raw c结果完整保留；gamma只区分整体增益与更复杂变化，不据其恢复分数宣称同函数。分母为0则该条件明确不可测，其他条件不删。
- **Hcal：** 原train固定64窗口、seq512、stride4、seed91024。受控模型可复用同源Hcal；公开OLMoE必须用自己的原生prefix重新提取（不能用dense的H）。held与train文件隔离，cal只用原生块输出作无标签向量回归。
- native/c/r/zero/gamma/recompose全部保留，不按原+.02或新相关线选模型；原主实验/匹配结论与所有旧读数不改。

## 阳性对照、读数与算力
- **阳性对照：** exact代数tiny oracle；所有专家为同一函数时，c在实数模型中等于原native（保留s，避免E120数据均值钳制伪影）；真实首batch identical-bank与重组给有限精度地板，不假定BF16严格等变。source模块/参数/顺序不变，prefix相同；缓存每batch重置并核对输入，不能误用另一batch。
- **主读数：** 与E127/E132同BF16全序列logits→FP32 logsoftmax；对native的逐token KL、GT NLL变化、top1及配对文件95%CI/每来源结果。额外记录cal gamma/向量重建误差及c/r/y幅度，但不凭幅度宣称行为重要性，不将NLL变化比值解释成“百分之多少知识/功能”。
- **噪声地板 + MIE：** native重复/重组/identical-bank实测数值误差；与zero、raw c、gamma c、r的连续预测后果并列，无固定NLL/rho通过线。文件CI是给定模型/校准的评测不确定性；公开模型一个checkpoint不构成跨模型总体规律。
- **成本边界：** 计算m要执行全部64专家，不能将此称为相同8-expert预算下的替代或压缩方法。它是函数/行为干预，不是效率主张；公开/受控都记录实际算力与dtype。
- **预算与资产：** 全部6设定只读评分/校准合计≤2 GPU·时、并发≤8卡；优先空闲GPU1/3，不打断E131 GPU0/2共同训练。public pin/tokenizer/config见`results/e134/asset_preflight.json`；大缓存和raw在`/tmp/xiang-moe-20261025/e134_*`，小摘要计划`results/e134/necessity.json`。

## 解释边界与决策表
- c损伤小、r/zero损伤大→在本层/分布/此替代类中，不保留专家身份相关偏差也可维持预测；不证明专家知识、所有路由、固定稀疏预算或分工全无用。
- 仅gamma*c恢复→一个全局增益足以恢复此任务得分，仍不等于同预测函数；c差而r好→相对该参考中心化的加权项重要；两项分别都差→互补/下游非线性，不能把损伤加总；两项分别都好→可替代/冗余而非所有职责不存在。
- **阴性非对称：** m会调用许多未在该支持域受训的专家，可能受支持外输出污染；c失败时r可能在抵消该人工均值。因此阴性只能说明相对此参考，native偏差项必要，不能直接证明语义专精。
- 若public与受控效应不同，报告设定边界而非冻结的单因效应。所有分支都不自动升级/关闭方向、不追加gain/标签/层网格；与E131历史结果一起审视这些指纹差异的研究意义。

## 定位与来源
- Shared-expert/common-local思想有DeepSeekMoE与Towards a Statistical Understanding of MoE等近邻；同权重上下文路由变化的精确分解/行为patch有Routing Divergence Is Not Evidence of Behavioral Influence。它们不等于本卡的事后均匀中心化，但均禁止把共享概念或代数分解冒称首创。
- 此处具体增量是：在已有跨训练指纹与bank移植观察中，直接检验所选偏差分量的预测必要性并检查原生公开MoE边界；不将单次测量自动当论文lead。

## 结果（运行后追加）
- 数字/CI：尚未运行。主张不变；E131原62500因果终点继续。
- POST-HOC：由E132/E133观察启发的新前瞻干预，不覆盖原测量。
