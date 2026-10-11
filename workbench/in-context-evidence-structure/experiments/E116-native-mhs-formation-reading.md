# E116：已有真实评论任务中的原生形成/读取条件作用（2026-10-11）

- **状态：** PLANNED（跑前）
- **类型：** REPRO / C21与C23的功能联系和任务迁移。
- **对应：** C21/C23、I04、P17。
- **问题（一句话）：** 目前正常读取的形成解释只在短情绪材料验证，它是否也约束已有MHS真实评论文本中的私人规则判断？
- **设置：** 直接复用E109/E112的Measuring Hate Speech文本池、race/gender分类与两个相反Source私有约定，不创建新能力任务。文本来自真实数据，Source/private label规则为受控构造，非原始人类个人偏好。Qwen3-8B与Mistral-7B-v0.3 FP32/eager，各自16新context discovery seed116001→32新context confirmation seed116101；不同模型同seed语义context一致，无token/输出选样。Llama-3.1-8B在E115数值有效后用同被冻结接口/seed检验；无法使用时不替代成新模型清单。
- **配置：** 与E114完全相同的native A-cache formation×B-cache environment交叉和历史答案K/KV/V→A label形成边；所有query可读全部Source。沿用E109输出safe/toxic与far pass/flag；只翻B私人映射，文本不动。A raw/label/名字/全部token边界不变。原E114的within文本置换和固定label关联读数不适用于该操作，事前移除，不以MHS此结果证明C22。保留single A、whole-query gated与一句instruction两world对照。
- **条件数：** 2 rule worlds×15 namespace/edge/gated条件＋single A＋2instruction＝33×8query；每家族探索4224，确认8448评分。
- **读数：** 冻结E114原D=mean_q gold*(cross−origin)，各A/B缓存背景的signed/absolute条件作用与signed交互；两个target(label/full-A)与两个B背景的K/KV/V系数1rule重建r/RMSE/zero；single/private两方向和native/instruction候选margin/full-vocabulary argmax。context-bootstrap10000 seed910，原重建函数/seed109910。不拟合新系数，不挑种子/头/层。
- **阳性对照：** 两端native corner一致、self≤.001、首context全部8query实际token流full/split≤.001、source指纹/all-layer消费；只有B标签anchor允许变，A不变；计数/各p平衡。每family single与instruction公开。B映射反事实改变静态label，因此layer0固定KV不变对照不适用，不作虚假阳性。
- **噪声地板 + MIE：** 效果同时给CI与target/zero尺度。弱target或弱单来源不由高r宣称完整机制；private能力不足限制negative机制归因和标准已掌握的说法，不自动将已有有效形成反事实作废。所有数值有效记录确认一次，不根据n16正负或最好通道选择继续。
- **混杂审计：** 条件内matched token形状；同Source/输入/输出计数；namespace是研究变量、非语义词先验等价证明。context抽样可复用池中评论，新context不冒充disjoint文本。F/R是上下文化位置缓存因子、query继续演化、hybrid诊断。保持33条件与原signed/absolute，交互判断用signed。公共数据合法偏好构造不等于现实损失或普遍ICL定律。
- **决策表（跑之前写）：**

| 结果 | 更新 |
|---|---|
| 数值与消息接口有效 | 相同引擎确认32新context，包括弱/负结果；不按发现集选条件 |
| native形成/边预测与背景作用保持 | 将原生联系扩展到已有真实评论文本任务，报告精度/残差，仍不锁定主线 |
| gated形成保持而native路径弱或补偿明显 | 报告接口/任务机制差异，不以旧高r包装完整native解释 |
| 目标功能作用明确但冻结重建失准 | 当前形成子图不是充分任务迁移解释，保留差异，回原论文与主问题，不继续头搜索 |
| single/standard能力不足 | 报告所有原始分母，不能断言完整规则学会或普遍机制缺失；已有效的正反事实按自身范围解释 |
| 数值/几何失败 | 仅修执行并保存失败，不生成机制结论 |

- **算力预算：** 单卡独立任务；Qwen/Mistral可并行，模型已在节点NVMe。本任务不耦合训练/跨节点通信；每家族≤.8 GPU·时，Llama是否执行由E115数值/可用性而非正结果筛选。实际按run累计。
- **命令：** 同conda verl-clean运行`scripts/e116_native_mhs_formation.py --model /tmp/ices_models/Qwen3-8B --out results/e116/qwen3_discovery --n 16 --seed 116001`；Mistral改本地model path/out；confirmation改n32/seed116101/out，各自GPU独占。CPU preflight-only先行，同cached dataset，不重新拉数。
- **设计与叙事来源：** CoSToM把内部接口接到实际用途；NAACL2025 Crosbie/Shutova先head参与→具体pattern操作→NLP ICL benefit，EMNLP2024 Yu/Ananiadou用同label映射变化检查QK/OV。当前E114已测试具体形成操作，但正常使用仅短情绪；本项针对这个任务迁移缺口，非新组件或泛化行为地图。ACL Lepori的geometry/行为对照不替代本项功能消息干预。

## 结果（运行后追加）
待运行。源码SHA256：f3e05586bfec5a2b90954202aecc2f6f79c68e4a9df15afa5b77a9e9b3584ca4。科学注意力/重建引擎来自E114，任务和条件删除明确在跑前记录。
