# E33：新事件关系预测跟随原词，还是跟随动作意义？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C05 / I01 / P11；继续同一角色证据迁移问题。
- **问题（一句话）：** 没有重现旧活动stem、但在该场景保留同一基本动作及角色的释义，是否比E31固定不同动作更保留预测aftereffect？
- **设置：** 24源/12family、具名事实；旧anchor和角色约束完全不改，新bridge/readout的activity noun及进行中谓词换为独立构造者每family固定一个自然释义，不换targets。新event为began、distinct，与E31/E32一致；两原fact order都测same/other actor。另保留negate-first的old-event释义及neutral阳性控制。新960raw，无问答/native/训练。原词与固定different-action分数复用E29/E31/E32，三点对照预先固定，不按释义结果换词。首版字段与二版均保留：首版误将stem限制理解为禁止其他family，过度换成clasp/squeeze；二版只禁该family原stem，hug↔embrace可用，仍有意义差的如heal→treat/ shave→hair removal明确标related。最终字段hash事前固定，独立两Luna各480审完整rendered句子：基本动作匹配/患者角色/事件范围/语法/动作意义在target前是否可得。same-basic-action不等于所有可能世界严格逻辑同义。
- **读数：** M=bits(other NP)−bits(own NP)，D=initial-only−reference-only，J=D_activity−D_neutral；新两order各actor D/J、para−sameV、para−differentV及old-event D/J；报告all12、parent固定prior9/anchor-clear11/acceptable9、审计eligible与independently-basic-action-clear共同完整family层。只同一family两原source平均后paired bootstrap10000/seed20261005/95%CI。审计related/changed/uncertain单独全报，语义清晰样本少也报告，不伪造最低样本通过gate。最有信息的比较是para相对于原词及不同动作，不能只以para CI跨0讲词汇echo胜出。
- **阳性对照：** 旧event的释义D/J对同role事实应可用；若不响应或审核不匹配，先解释词义/论元而不将new-null叫不会semantic transfer。原E31/E32同V与differentV完整冻结复用。old neutral text未改时记录exact duplicate counts，fresh值与父分数一致性为instrument check。两个targets pre-token identity、masked HF/manual loss、旧fact-prefix原字节机械核验。
- **噪声地板 + MIE：** FP32索引核验约1e−6bits；语义匹配和12family更重要。明确不确定层与每family，不让模型分数决定同义标签/释义选择，不做词汇/seed/model sweep。释义本身的频率与argument-frame差属于局限，配对role+neutral降低基线差但不保证完全消除。
- **混杂审计：** 新动作同basic category可能改变程度/方式，不能直接证明语义关系表示；后文词频、名词自然性及focus仍竞争。读数在patient到达时计算，不能靠target后才到的释义解释因果效应。旧fact order的实体可及性改变已由E32证实，各order分别分析。旧original读数只有negate-first，不能伪造两order原event阳性。original stem只在新bridge/readout排除，旧anchor/fact保留才能测迁移；不将plain likelihood当真实错误。
- **决策表（跑之前写）：** clear动作层para J方向靠近原词且比differentV更反向、old control有效 → 狭义新句原stem重复不足，语义动作/关联备选竞争更强，仍不证明内部relation memory；para靠近differentV且old control有效 → exact wording/词面检索解释增加，下一自然身份/语境干预；所有new下降且old control也下降/审核mostly changed → 材料不能回答原问题，如实报告而不换synonyms追winner；两order不同 → focus与semantic retrieval共同决定作用，保留交互；CI宽 → 报告范围，不自动关线或扩模型。
- **算力预算：** 现成venv、本地pinned Qwen3-8B FP32/SDPA、TF32=false、seed0/batch4，独立一H20，≤.04 GPU·h，全部审后评分。**实际：** 0.01093296 GPU·h / 39.359s，960输入全部评分。
- **命令：** `scripts/action_paraphrase_transfer.py build/adopt/analyze`；`event_identity_infer.py --experiment E33`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

## 跑前材料核验

字段v2 SHA256 `53af46bed8c0dfa1265e38b15576c111448ab36b71f69b2fc163fdda6827607b`，960候选SHA256 `0ced9807641d11fd0d2af95f16934c106301db2b77c04a23981aae7610cfe6a6`，24源各40variant，96 old-neutral exact unchanged。旧event控制明确保留`continued that particular [original activity]`身份桥，只改末尾readout谓词/名词；新event的bridge与readout均无原stem（旧anchor/fact原样）。最初build因旧readout实际是`In that same...`而assert，空输出目录删除后修正，未生成坏版、更未推理。两者不作纯词频匹配，旧control只核对释义角色用途是否响应。


## 2026-10-06跑前全量审计

两独立审480/480，全960 old fact preserved/角色/event identity/target前动作clear；semantic-match clear672/related288，没有把encounter/wash/hair removal/treating追认同义。共同完整basic clear 8 family：cuddled, disrobed, dressed, embraced, fought, hid, hugged, kissed；96旧neutral无改，标签clear不扩大整个family。grammar acceptable472/marginal488，两审标准不同，保留全部意见，未自动修改词。事前加basic∩anchor-acceptable7与basic∩parent-faithful6敏感层，原whole-cohorts各自仍报；未运行模型。960输入的pre-target token identity已通过。


## 2026-10-06结果

- 全960评分，所有输入/data/config/hash覆盖，96 unchanged旧neutral score与父run差0；HF/manual masked目标loss check通过。audited basic clear共同8family、与自然anchor交集7、与parent-faithful交集6，各层定义在模型运行前。
- basic clear8旧event释义 D_activity +3.441 [2.668,4.041]、J+3.926 [3.005,4.912]bits，原词旧event J+3.513，para−original+.412 [−.577,1.340]；释义用途对角色证据仍有效，不以CI跨0证明等价。
- new **otherActor**：negate-first释义D_activity −1.969 [−3.454,−.712]、J−2.165 [−3.541,−.949]；affirm-first D−3.333 [−4.803,−1.692]、J−2.144 [−3.877,−.296]。新bridge/readout无旧stem而反向仍在，exact repetition-only不足。相对原词J减少反向强度+.593 [.102,1.092] /+.827 [.241,1.383]，词汇boost仍影响。
- new **sameActor**：negate-first释义D−.015 [−1.049,.983]、J+.390 [−.529,1.418]；affirm-first D−2.775 [−4.677,−.700]、J−.396 [−2.094,1.430]。matched-neutral作用CI宽且跨0，不能把otherActor反向推广成所有actor不变。
- clear8的para−fixed different action J：negate-first sameActor−1.705 [−2.615,−.972] /other−2.180 [−3.651,−.770]；affirm-first same−1.746 [−3.018,−.598] /other−1.143 [−2.336,−.100]。即使sameActor绝对J不确定，释义与不同动作仍可区分。自然7/strict6、all12（包含related动作）方向结构均完整报告。
- 按决策表：semantic action-level关联与contrast/focus竞争增强，词面重复不足且有lexical boost。C05扩充L1具体条件、I01仍PILOT，不能宣称隐关系存储、一般LLM规则或human-like mechanism。下一actual correction history与初次给定role fact匹配，区分修订后的备选与普通最后fact priming；不继续调近义词/问答标签。
- [summary](../results/E33-summary.json)、[每family](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E33-per-family.csv)、[config](../results/E33-probability-config.json)、[全预审](../results/D0-E33-paraphrase-audit.json)、[clear8图](../results/E33-action-transfer.png)/[all12图](../results/E33-action-transfer-all.png)，英文静态科学图另有PDF。实际运行git `4752d1ea`；原始/衍生全文与逐项审计只在cache。
