# E08：提前的阅读关注问题与固定最终问答（2026-10-05）

- **状态：** DONE
- **类型：** MEASUREMENT / P03竞争解释区分
- **对应：** P03 / P06 / C02
- **问题（一句话）：** E07顺序效应来自提前问题改变读句，还是最终问答的位置/重复/回答倾向？
- **设置：** 固定Qwen3-8B，FP32 frozen thinking off，neutral native，无训练。全部276原句/原题/原gold不改，69 paired sets。最终目标问句始终放在句后。前/后额外reading focus分别取本set initial或final原题、固定轮换另一set initial或final原题，外加无focus：9布局×无/一句generic revise=18配置、4968任务。先固定sorted set顺序循环轮换，不能按效果挑干扰题。
- **竞争解释：** task-conditioned evidence use预测focus在句前、且与潜在错误解释有关时出现GP-specific响应；answer/candidate priming预测focus极性/内容影响最终回答，句后同样或更强，可能不特异于GP；纯最终query位置解释预测目标固定在末尾后原巨大差异明显减弱。此处只检验行为预测，不宣称内部parse机制。
- **读数：** GP/nonGP×simple/lingering的PYes、accuracy、choice mass；focus initial−final；相关focus−对应极性无关focus；同focus before−after；这些差值的GP−nonGP交互；lexical-set paired bootstrap10000 seed20261005。全69 primary + 事前67 source-question clean sensitivity，prob/reflexive分项；所有布局报告。
- **阳性对照：** 无focus对应E07neutral/native句后目标任务的结构；system新增final/focus说明，非相同prompt复跑；nonGP simple；generic revise。原题的Yes/No语用局限保留，不把No高分叫恢复。
- **噪声地板 + MIE：** FP32重复约2.6e−5；CI与效应量而非预设accuracy gate。重复题会提高显著性/熟悉度，本身通过句后focus控制。
- **混杂审计：** source句/问题/标签均未经改造，无新增语义gold；程序检查69sets中GP/nonGP同题同gold、轮换无self、全部18×276唯一、目标始终最后。focus位置仍改变距离，before/after单一差异不能排除距离；相关与极性对应的无关题提供区分，不据一个contrast定机制。Step5额度问题不影响已发布原始QA的此项复制。
- **决策表（跑之前写）：** 相关focus句前产生独特GP交互→E01追特定语言cue如何改变该作用；句后同样/更强或无关题同效→优先回答启动/距离解释，不称revision；固定末尾目标后效应消失→原query-order不足以支持reading-goal故事。仅已知GP难度→只作测量，不包装novelty。
- **算力预算：** GPU2单卡独立，预计<0.12 GPU·h，复用已有venv/cache。实际304.65s / 0.08462 GPU·h。

## 结果（跑完后填写；不改上面的内容）
- 数字（含CI）：4968/4968任务。base无focus GP simple98.55%、nonGP simple100%；GP lingering14.49%、nonGP34.78%。相关initial−final focus对lingering accuracy的GP−nonGP交互：句前+1.45 pp [−10.14,+13.04]，句后−7.25 [−20.29,+5.80]；不支持简单的独特GP reading-goal交互，也不证明其不存在。
- 句后final focus−对应无关final：GP lingering +23.19 pp [13.04,33.33]、nonGP +21.74 [13.04,31.88]，交互+1.45 [−11.59,+14.49]；相同final focus放句前减去句后：GP −18.84 [−28.99,−8.70]、nonGP −21.74 [−31.88,−11.59]。更符合后置内容影响问答/语义整合，而非只对GP的早期承诺修订；“究竟回答启动还是正确推理”仍未区分。
- 保留不整齐的结果：before initial−无关initial的pYes交互−12.74 pp [−23.76,−1.47]，67-source-clean变−11.01 [−22.04,+0.40]；repair下仍负。initial/final本身交互CI跨0，near-floor GP与nonGP不同baseline可产生此模式，不能挑这一contrast称机制。全部概率、accuracy、choice mass、67-set、prob/reflexive分项均报告。
- 结果文件：[summary](../results/E08-summary.json)、[scores](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E08-scores.csv)、[config](../results/E08-config.json)、[figure](../results/E08-focus.png)；原句题/原模型输出在cache runs/E08。
- 按决策表执行了什么：降低“query先到即促进特殊revision”作为主旨的支持；回到E01语言cue/blocker/extension与双读数系统测量，不优化获胜prompt、不扩模型。读取2026近邻Ask Twice, Look Twice及其重复/读出ownership；近邻存在只约束定位，不关闭territory。
- 主张变化：C03只保留E07固定协议行为事实；C01/C02不升级。E08不能支持内部parse改变，也不能用No增加叫recovery。
- POST-HOC：技术统计复核将lexical-set顺序显式排序，避免Python hash seed改变有限bootstrap抽样；未改实验读数/条件/样本。两种PYTHONHASHSEED的E08 summary完全相同，analysis source hash单独保存，inference config原始code hash保留。
