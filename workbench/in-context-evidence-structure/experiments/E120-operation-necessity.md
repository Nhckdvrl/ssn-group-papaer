# E120：原生证据形成操作的阻断与有限恢复

- **状态：** DONE-CONFIRMATION（2026-10-12，四模型16→32新材料全部完成）。
- **类型：** 机制/因果操作检验；不搜索head或层。
- **对应：** C21/C22/C23、I04、P17。
- **问题：** 历史B答案→A label在原生计算中是否对跨Source关系作用有必要贡献？在阻断其它B→A形成访问后，仅开放这条路径能恢复多少作用？
- **为什么现在做：** 实際donor系数1重建已经跨家族/材料有效，但它回答充分近似子图，不替代原生操作的必要性。对照Cho消融、CTA路径限制/恢复和Crosbie operation knockout，在同一自然问题内补这一计算环节；不是因局部CI或论文数量追加细碎控制。
- **设置：** 原E115明确情绪任务，8A/8B/8新query，origin/cross/within配对与shared/far输出全部保留。A raw固定、B输出stream/位置/输入multiset固定，cross翻关联、within仅同类移动；沿用CPU字节匹配与新词句validation。
- **干预：** 所有层固定4D注意力边mask，五种操作：(1)native；(2)阻断B答案区域→A label；(3)阻断A答案区域→A label（通用历史答案访问对照）；(4)阻断全部B→A前缀访问；(5)在(4)下仅恢复B答案区域→A label。答案区域包括实际word+separator，A receiver为原label word位置。其它边保持正常，softmax按允许边重新归一化，后续状态活演化。无需donor激活/拟合。整个query正常全Source或全程禁读B两种scope分别报告。
- **配置：** Qwen3-8B、Mistral-7B-v0.3、Llama-3.1-8B、Qwen3-14B各16 contexts seed120001 discovery→数值有效后32 seed120101 validation，正负均确认。五操作×三world×两namespace×两queryscope=60条件，另single A native/within-answer-off和两条instruction origin/cross，共64×8评分/context。FP32/eager/frozen，conda verl-clean，模型revision沿用E115/E119。
- **读数：** 每操作/namespace/scope的signed B-rule响应D=mean_q g(z_cross-z_origin)、abs(D)、within扰动；primary为native-minus-cross-answer-off的paired abs/signed关系幅度、cross-answer-off与within-answer-off的差、all-B-off至answer-only恢复的paired abs/signed关系幅度。所有accuracy、argmax、两私人方向与namespace交互保留。raw paired差为主，恢复比例只在完整响应非零时辅助，不当互斥中介份额。不以attention下降本身证明规则选择。
- **阳性对照：** actual native full-token与split-cache≤.001、zero-mask self相同；single两私人方向及通用历史答案off后的能力；query禁B且形成全禁B时cross/within差≤.001（数值graph-zero，非新科学结论）；全部层mask消费次数、causal范围、token几何完整；instruction“一句按请求来源推规则”对照保留。
- **噪声地板 + MIE：** FP32与graph-zero实测，10,000 context bootstrap seed910；不使用通用百分比阈值自动判断意义。paired效应及自身私有规则能力共同决定操作解释；若全模型能力也崩溃，不说选择性消除。
- **混杂审计：** 同A/B八个sender区域并非完全相同past边数/原attention mass，具体可用边数全部保存；within-source对照用于量级而非完美等mass。mask重归一化可产生额外竞争作用，故解释条件于该原生操作；恢复不是原始message/label整体强行移植。全Source query可直接读B，形成作用与最终direct读取不要求同时归零；native KO还可通过后续B状态间接作用，不能视为只修改纯A模块。全部条件/种子保留。
- **论文定位：** CTA已有跨示例路径必要性，Crosbie已有participating head与具体operation分离；增量为output×source关系的形成操作以及本Source功能来源，不宣称新mask方法。见PAPER_ALIGNMENT_2026-10-12.md。
- **算力预算：** 4个模型独立单卡，已有节点缓存一次加载；每批预计.1–.4 GPU时，总≤4 GPU时；空卡按实际nvidia-smi分配，GPU不用他人进程。
- **决策表（跑之前写）：**

| 结果 | 科学判断与后续 |
|---|---|
| B-answer-off降低继承关系而single规则保留，有限路径恢复重新引入关系 | 操作既有原生必要贡献又有受限图充分性，可把C21从重建解释接到原生计算，不要求全恢复 |
| B-answer-off仅微弱，而all-B-off明显且恢复弱 | 该路径可预测donor反事实但非主要原生必要通路；保留阳性重建，不宣称唯一算法，不搜索几十个head |
| B-answer-off与within-answer-off同样损害整体任务能力 | 一般扰动替代仍成立，不能称来源特异操作；回到完整证据解释而不是加n救方向 |
| 恢复只在shared而非far明显 | 输出身份对这项native形成操作的关系贡献有支持，报告signed/abs和实际能力 |
| 数值/graph-zero失败 | 先修工具并记录失败，科学评分不判读；不筛种子 |

## 结果（运行后追加）
| 模型，确认n32 | full-source阻断 | A-only阻断 | full-source有限图恢复 | A-only有限图恢复 |
|---|---:|---:|---:|---:|
| Qwen3-8B | 1.649 [1.108, 2.250] | 1.104 [0.543, 1.770] | -0.806 [-1.365, -0.266] | 1.455 [0.999, 1.945] |
| Mistral-7B-v0.3 | 1.054 [0.886, 1.227] | 1.039 [0.804, 1.289] | 0.140 [0.053, 0.231] | 0.647 [0.463, 0.835] |
| Llama-3.1-8B | 0.808 [0.517, 1.109] | 1.108 [0.834, 1.386] | -0.233 [-0.336, -0.122] | 0.958 [0.635, 1.276] |
| Qwen3-14B | 1.329 [0.967, 1.717] | 1.126 [0.669, 1.637] | 0.039 [-0.217, 0.287] | 1.120 [0.673, 1.646] |

**实际认识：** 直接阻断原生重新归一化attention操作减少另一来源关系作用，四模型full-source signed/abs均确认；只开放答案→label路径，在A-only读取下带回正关系作用，而full-source Qwen/Llama为负、Mistral正、14B跨零。这是受读取环境调节的条件贡献和受限图恢复，非唯一通路或全网络充分性。私人阳性和一般历史扰动另保存：Mistral single within-answer-off仅65.6%（native97.3%），Qwen cross-vs-within阻断abs差CI跨零，不把此操作宣称为纯来源特异模块。

**完整性：** 8批192context、98304评分；64条件全部保留，数值/图零和各层实际mask消费通过。[独立原始校对](../results/e120/independent_review_2026-10-12.md)复算9736项max0，实际token/edge集合重建完成；不是独立GPU复跑。原始评分在`results/e120/*_{discovery,confirmation}/behavior.jsonl`，analysis/run/完整性汇总及[操作图](../results/figs/fig_native_operation_necessity.png)可复核。

### 实现冻结（首评分前）

- `scripts/e120_operation_necessity.py` SHA256 `b4b155bfea8f83cde60e70cf1351189bd5066cf973b9cf0610cda011d89c18ad`。
