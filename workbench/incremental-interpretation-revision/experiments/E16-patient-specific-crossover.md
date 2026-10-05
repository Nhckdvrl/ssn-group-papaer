# E16：患者特异续写还是一般 self/reciprocal 偏好（2026-10-05）

- **状态：** DONE
- **类型：** EXPLORE
- **对应：** P10；C01/C02解释边界；E15后竞争解释拆分。
- **问题（一句话）：** GP历史使后文特异偏向前文那个患者，还是只普遍降低原self/each-other续写？活动指向变化调节哪一部分？
- **设置：** 同pinned frozen Qwen3-8B、FP32/SDPA、seed0、TF32=false、batch4，无question/chat。沿用E14/E15全部22源、两个作者NP选项、GP/comma、none/continued-same/continued-separate/began-separate四桥；每个上下文仅新增“另一个作者NP”作为S2 object的续写，共352新输入，复用旧own-NP/reference评分。主7明确episodic源，全22、source block、option0/1/both、all/eligible/acceptable/episodic分项保留。
- **数据与审计：** 原S1/桥/S2其他文字完全不动，S2目标仅在作者提供的两个core NP之间交叉；没有新问题或semantic gold。两个独立Luna审查masked材料各176，判断语法、变换忠实、指称、selectional oddity。selectional oddity原样保留，不把新人物未提到当syntax error；它是lexical bias的一部分，交叉平均消除NP的基础偏好。生成脚本 `scripts/patient_crossover.py build`；材料在cache/E16-material-preparation-v1，仅hash/stat进git。独立审查须全量覆盖后执行；所有输入评分，不选择结果好看的source。
- **读数：** M = bits(other NP)−bits(own NP)，正表示偏向前文已提患者。两个S1 NP choices在source内均值构成交叉设计；D_M=M_GP−M_comma，GP/comma实体提及次数及NP均相同。主A_M=D_M_continued-same−D_M_continued-separate。同步分解R_own/R_other（NP−ref）且逐项核对 A_R_own=A_R_other−A_M。cluster bootstrap10000、seed20261005、95%CI。不是accuracy、不证明内部event graph。
- **阳性对照：** cue也应可利用前文的NP提及，报告两条件M与全体偏好而非只报差值。旧E14/E15效果不重跑，hash锁定；新旧model配置一致，原own-NP/新增other-NP的pre-target token IDs逐条一致，HF/manual span loss核对。
- **噪声地板 + MIE：** 原FP32词级漂移约1e−5bits；7源主切片sampling不确定性主要。没有任意阈值；CI、效应量和逐source共同改变解释。
- **混杂审计：** 交叉S1 choice×S2 target消除NP基础词频偏好；GP/cue提及次数相同但句法线索不同。other-NP通常引入新实体，故绝对M含mention advantage，不能称错误绑定；GP/cue交互与桥调节才区分解释。原source两NP的plausibility/selectional差异报告独立flags及option分项。明确episode切片继承E14事前定义，不按新结果重标。noisy-channel句法repair仍未区分，患者特异结果不等于semantic revision完整性。
- **决策表（跑之前写）：** D_M明显正且A_M解释E15的主要变化 → 患者特异reuse比一般ref-form抑制更受支持，下一步用身份词匹配/合法与malformed结构控制分离事件绑定与文本repair；D_M小/A_M小而R仍变化 → 降低患者特异解释，追ref-form或一般语义预期；D_M正但A_M小 → 有患者特异GP响应，桥变化另有来源，不能讲scope-controlled reuse；源组反向或CI宽 → 保留混合/异质性，检查材料结构，不扩prompt/model sweep。
- **算力预算：** 一张空闲H20，352新inputs，预计≤.03 GPU·h。**实际：** 17.082s / 0.00474495 GPU·h；352新输入。
- **命令：** 在workbench内 `source scripts/env.sh`，`$IIR_PYTHON scripts/event_identity_infer.py --experiment E16 --data $IIR_CACHE/E16-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E16`；统计 `scripts/patient_crossover.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E16 --out results/E16-summary.json`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

- 独立审查352/352acceptable，selectional odd128保留、指称新实体160保留，无semantic gold。运行前352个pre-target token contexts与原own-NP完全相同。
- 7 episodic源：无桥 D_M +7.843 [5.422,10.183]bits；continued-same +7.823 [5.387,10.230]；continued-separate +5.712 [4.096,7.306]；began-separate +5.418 [3.862,7.040]。
- 固定continued A_M +2.111 [1.167,3.137]，7/7 source正。A_R_own −1.974 [−2.783,−.694]；A_R_other +.138 [−1.058,1.301]。全22 A_M +1.382 [.679,2.089]、A_R_other −.044 [−.589,.526]。逐source恒等式均通过。
- [统计](../results/E16-summary.json)、[config](../results/E16-config.json)、[去文本分数](../results/E16-scores.csv)。执行git `90cf43402`；原E14/E15配置/权重一致。
- 更支持患者特异响应，原桥调节不能全归一般ref-form抑制。但own NP本来就是提及过的实体，尚未排除GP改变一般实体可及性/词汇关联；下一对照应比较依赖原事件的patient continuation与不依赖原事件的实体提及，不把关系记忆当已验证。
- C01/C02维持L0。结果不能独自说明syntactic repair完成、内部event graph或novelty。
