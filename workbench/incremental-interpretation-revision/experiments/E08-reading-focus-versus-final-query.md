# E08：提前的阅读关注问题与固定最终问答（2026-10-05）

- **状态：** PLANNED
- **类型：** MEASUREMENT / P03竞争解释区分
- **对应：** P03 / P06 / C02
- **问题（一句话）：** E07顺序效应来自提前问题改变读句，还是最终问答的位置/重复/回答倾向？
- **设置：** 固定Qwen3-8B，FP32 frozen thinking off，neutral native，无训练。全部276原句/原题/原gold不改，69 paired sets。最终目标问句始终放在句后。前/后额外reading focus分别取本set initial或final原题、固定轮换另一set initial或final原题，外加无focus：9布局×无/一句generic revise=18配置、4968任务。先固定sorted set顺序循环轮换，不能按效果挑干扰题。
- **竞争解释：** task-conditioned evidence use预测focus在句前、且与潜在错误解释有关时出现GP-specific响应；answer/candidate priming预测focus极性/内容影响最终回答，句后同样或更强，可能不特异于GP；纯最终query位置解释预测目标固定在末尾后原巨大差异明显减弱。此处只检验行为预测，不宣称内部parse机制。
- **读数：** GP/nonGP×simple/lingering的PYes、accuracy、choice mass；focus initial−final；相关focus−对应极性无关focus；同focus before−after；这些差值的GP−nonGP交互；lexical-set paired bootstrap10000 seed20261005。全69 primary + 事前67 source-question clean sensitivity，prob/reflexive分项；所有布局报告。
- **阳性对照：** 无focus复用E07neutral/native句后目标任务；nonGP simple；generic revise。原题的Yes/No语用局限保留，不把No高分叫恢复。
- **噪声地板 + MIE：** FP32重复约2.6e−5；CI与效应量而非预设accuracy gate。重复题会提高显著性/熟悉度，本身通过句后focus控制。
- **混杂审计：** source句/问题/标签均未经改造，无新增语义gold；程序检查69sets中GP/nonGP同题同gold、轮换无self、全部18×276唯一、目标始终最后。focus位置仍改变距离，before/after单一差异不能排除距离；相关与极性对应的无关题提供区分，不据一个contrast定机制。Step5额度问题不影响已发布原始QA的此项复制。
- **决策表（跑之前写）：** 相关focus句前产生独特GP交互→E01追特定语言cue如何改变该作用；句后同样/更强或无关题同效→优先回答启动/距离解释，不称revision；固定末尾目标后效应消失→原query-order不足以支持reading-goal故事。仅已知GP难度→只作测量，不包装novelty。
- **算力预算：** GPU2单卡独立，预计<0.12 GPU·h，复用已有venv/cache。实际待记录。

## 结果（跑完后填写；不改上面的内容）
- 数字（含CI）：待运行。
- 结果文件：待运行。
- 按决策表执行了什么：待结果。
- 主张变化：无预定升级。
- POST-HOC：无。
