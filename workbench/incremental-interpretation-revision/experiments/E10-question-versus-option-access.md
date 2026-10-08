# E10：拆问题与选项的位置（2026-10-05）

- **状态：** DONE
- **类型：** MEASUREMENT / E09异常why
- **对应：** P03 / P07 / C03
- **问题（一句话）：** E09顺序/选项效应来自带着问题读句，还是回答时访问问题与选项？
- **设置：** 固定E09原SAP 144句题/24lexical sets与FP32 Qwen3-8B，无训练/native thinking off；问题pre/post×选项pre/post×无/一句revise×Opt1=A/B，共16配置2304任务。原系统/句题/gold/选项不改，新增两个mixed位置（1152次推理）；两个相同位置的corner复用E09的1152输出，逐prompt byte/hash核对在运行前完成，不重复发明score。
- **竞争解释：** 提前任务改变句子处理→选项固定末尾时Q前/后仍产生GP-specific差异；选项访问/label默认值→移动选项会明显改变分数和mapping敏感性，即便Q不变；问题访问→Q末尾更好且与选项位置不同。行为不能唯一识别内部编码，但因子比E09一起移动两者更能区分这三个解释。
- **读数：** family pooled/NPZ/NPS/MVRR×all/作者Excel target/control×16配置的correct、Pcorrect、choice mass、Psource Option1；同options位置Qpre−post、同Q位置Optpre−post、两者×GP−cue交互及Q×options。全部报告，两mapping/一句revise都保留，不挑最好布局。lexical-set paired10000 bootstrap/seed20261005，pooled先在set内平均构式。
- **阳性对照：** E09两个corner精确输入对照；explicit cue、原作者control问题；两个mapping。原gold的No/选项拒绝不是最终结构建立的证明。
- **噪声地板 + MIE：** FP32重复0flips/max约2.6e−5；不设gate。效应/CI与因子结构决定继续追哪种解释；稀疏n=1保持CI null。
- **混杂审计：** 全部问题/选项来自已审计原作者资料，无新增语义gold或自标注；只移动块。mixed布局需要同时记住Q或options，仍有距离/格式差异，不能将某一显著Q效应称task-conditioned parse；两位置corner输入完全等于E09，复用原输出的experiment/hash注明。选项内容/字母对照是E09真实异常引出的控制，非继续prompt赢家优化。
- **决策表（跑之前写）：** 选项末尾固定后Q效应保留且GP特异→结合E01语言操作追阅读目标与后续证据的交互；主要由options移动决定→归于访问/标签策略，停止以顺序本身孵化novelty，回到cue/extension的解释后果；两者混合→只报混合结构，并用有语言预测的对照继续。无论结果都不扩模型sweep，不改研究对象。
- **算力预算：** GPU0独立单卡，新增1152任务预计<0.06 GPU·h；reuse E09无需新GPU消耗。**实际：** 新增70.26s / 0.01952 GPU·h；1152个E09输出复用，合计2304个分析行。

## 结果（跑完后填写；不改上面的内容）
- 数字（含CI）：全部2304行完整（1152新、1152复用），corner prompt/hash与原E09完全一致。固定选项末尾、Q前−后：Opt1=A GP +1.39 pp [−6.94,+11.11]、cue −18.06 [−29.17,−6.94]，交互+19.44 [8.33,31.94]；Opt1=B GP −1.39 [−11.11,+9.72]、cue −4.17 [−13.89,+5.56]，交互+2.78 [−6.94,+12.50]。主要正交互并不是GP独特改善，而可由cue回答变差产生；mapping改变后交互不稳定。
- 固定Q在前、选项前−后的GP−cue交互：Opt1=A 0.00 [−11.11,+11.11]、Opt1=B +12.50 [2.78,22.22]。固定Q在后则+4.17 [−1.39,9.72] / 0 [−8.33,+8.33]。问题与选项位置都影响行为，结构依赖mapping，不能归为纯选项距离或独立的task-directed revision。repair与三个family分项全部保留。
- 结果文件：[完整统计](../results/E10-summary.json)、[scores](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E10-scores.csv)、[config与复用provenance](../results/E10-config.json)、[图](../results/E10-access.png)。
- 按决策表执行了什么：报告混合结构，降低以query-order孵化主旨的支持；不继续找获胜布局。主对象回到E01语言操作与角色/自然语义读数的异常，先解释unambiguous extension也使role困难的原因；原始自然题E09也有真实cue影响，不能把全部GP困难归为元语言伪影。
- 主张变化：无预定升级。
- POST-HOC：无。
