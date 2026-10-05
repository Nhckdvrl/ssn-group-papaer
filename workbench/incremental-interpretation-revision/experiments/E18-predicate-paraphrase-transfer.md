# E18：换谓词表达后，原患者偏好是否转移？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01 / P10；不做模型/prompt sweep。
- **问题（一句话）：** E16/E17的活动相关患者偏好，需要重现原动词，还是能迁移到表示同一基本活动的其他谓词表达？
- **设置：** 同本地pinned frozen Qwen3-8B、FP32/SDPA、TF32=false、seed0/batch4、无question/chat/instruction。原22 sources×2 S1 NP options×GP/comma×none/continued-same/continued-separate×own/other NP targets=528新输入，复用E16 original-predicate概率。主原7episodic sources；全22及 independently faithful-activity / episodic∩faithful-activity / grammar-acceptable strata、两个NP options都报告。
- **材料与审计：** 一名Luna仅依据author S2构作predicate释义，另两名Luna每名264独立复核rendered全文。S1/桥不改、target author NP不改，尽量保留actor/aspect/modality/后文。v1/v2保留；v2在推理前补充因果位置约束：新活动意义须在target前到达，不能靠target后future词。semantic-match允许明确related/changed/uncertain，不能为分数/样本量改标签；没有gold correctness。全部输入评分、mechanical+grammar eligible与faithful-activity层明确分开。license限制的原文/衍生句留cache；hash与counts进git。
- **读数：** M=bits(other NP)−bits(own NP)，D_M=GP−comma，比较original vs paraphrase。K=D_original−D_paraphrase，A_paraphrase=D_paraphrase_same−D_paraphrase_continued-separate，A_K=A_original−A_paraphrase。两NP先source内平均，paired cluster bootstrap10000/seed20261005，95%CI和每source；报告D的转移量而非用K的CI跨0证明完全等价。
- **阳性对照：** original-E16的D及桥交互冻结复用；paraphrase cue的own/other提及偏好与GP同时报告，不能由new整体floor推断词汇echo；同context两个target的pre-target token IDs一致、target loss HF/manual核对。
- **噪声地板 + MIE：** 既有FP32词级漂移≈1e−5bits；semantic清晰且source样本量小导致的CI明确报告，不设任意效果gate。若faithful样本不足，报告不足，不把全部近义句当严格同义，也不以uncertain词汇跑sweep挑winner。
- **混杂审计：** 释义可能改变词频、论元框架或活动范围，GP/comma及cross NP choice控制基础lexical偏好而不保证意义完全相同；独立activity-match/pre-target availability决定事前可信分层。whole-S2 futura信息不影响目标概率；所有已复核材料和annotation理由保留。释义转移能限制exact surface repetition解释，但仍有语义关联、源句noisy-channel repair及句法恢复未完成等竞争解释；尚不能叫“被丢弃的解释重新激活”。
- **决策表（跑之前写）：** faithful源上D及A明显迁移 → 狭义原动词echo不足，下一决定性对照改源证据合法性/late explicit role，不加模型；D/A下降且语义保持可信、cue控制可用 → lexical reinstatement解释增加，缩小I01叙事；相关但改意谓词的结果与faithful不同 → 追语义差异，保留不确定性；样本小/CI宽 → 找published matched句而非结果后换synonyms。不关闭territory，不自动宣称novelty。
- **算力预算：** 一张空闲H20，528新输入，预计≤.03 GPU·h。**实际：** 22.283s / 0.00618983 GPU·h；528新输入。
- **命令：** workbench内source `scripts/env.sh`；`scripts/predicate_transfer.py build/adopt`，推理 `$IIR_PYTHON scripts/event_identity_infer.py --experiment E18 --data $IIR_CACHE/E18-material-preparation-v1/audited-v2.jsonl --out $IIR_CACHE/runs/E18`；分析 `scripts/predicate_transfer.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E18 --out results/E18-summary.json`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

- 审核528：504acceptable、24marginal（grapple into…）；faithful activity240个variant，但按同source两个NP/两条件完整配对只有9源；原episodic∩faithful为4源，其中source23语法marginal。这一局限预先flags保留，不用“全体近义表达”等价代替严格切片。
- faithful9源：释义后的D_M与same/separate调节仍存在，A_paraphrase+1.439 [.895,1.908]bits；与原谓词A的差+.273 [−.931,1.506]，CI跨0不等于等价。
- 原7 episodic（包含related含义变化）及全部22各分项保留。全22 D_M_none+4.693 [3.449,5.992]、same+5.489 [4.061,7.002]、separate+4.283 [3.104,5.558]；A+1.206 [.775,1.620]。
- episodic∩faithful4源：D_M_none+6.505 [4.685,8.616]、same+6.955 [4.886,9.679]、separate+5.756 [4.028,7.643]；A+1.198 [.280,2.117]，3/4正。但含source23marginal，不能把这层夸成独立高质量大样本。
- [统计](../results/E18-summary.json)、[config](../results/E18-config.json)、[分数](../results/E18-scores.csv)，执行git `0d314aed5`。
- 按transfer分支：限制exact original-verb echo，但semantic association、source noisy-channel修复与未完成句法恢复仍竞争。接E19明确同episode角色信息的双向对照；不继续换同义词找赢家，不称已恢复后再激活。I01仍PILOT，C01/C02仍L0。
