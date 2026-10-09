# E73：同一采样轨迹上的回复预算与来源条件化（2026-10-10）

- **状态：** DONE（4-context预算校对；未通过原direct阳性门槛）
- **类型：** PILOT / E72接口校对（探索材料，非独立机制确认）
- **对应：** I04/C17/C19/P12；E72的direct96-token阳性对照被截断。
- **为什么现在：** E72关闭thinking后仍出现长分析，短预算与thinking2048的准确率差不能证明推理模式修复绑定。必须先排除censoring与采样变化，再讨论能力/程序。
- **设置：** Qwen3-8B先做4contexts seed72001（固定取E72前4，未按答案选）；same animals/fruits、yes/no、Alex/Sam。source_only、orthogonal_prefix、entity_binding、single_source四schema，全4个自然source×kind query，三接口：chat默认、chat加Source指令、thinking加相同指令。不再加linked配置（E71已确认关系效应；本卡校对direct/think）。
  - 完整user任务与E72逐字相同，thinking模板enable_thinking=True，medium（Qwen3.8支持，Qwen3原template可能忽略）；非thinking为False。保持temperature0.6/top_p0.95/top_k20，一次long生成最多4096新tokens，1样本/query，无训练。
  - 每batch固定decode seed=730000+interface_index×10000+batch_index。相同prompt长轨迹在96/2048/4096处截断后分别parse；不混用来自不同随机样本的短长结果。
  - 两个预定batch/interface额外真实运行short96、short2048：snapshot长运行前的CUDA+CPU RNG，恢复后short；必须与long的对应prefix逐token一致，允许正常EOS后padding，但不允许因为看答案调seed。generation_config不准有forced_eos/其它依赖长度的处理器，beam=1，禁用编译（避免max_length改变kernel造成非机制差异）。共同prefix检查失败→VOID该预算归因，原输出留存。
  - parser沿E72：仅合法最终Answer行，thinking须关闭</think>；完整token长度/EOS保留。prefix中的中间猜测不当最终结果；有效输出、截断、错误标签分开报告。非thinking可以自然写分析，不声称其没有显式推理。
  - 候选logprob不重跑，E72的条件选择与自由生成分开。load missing language keys必须为空；记录model/config、template、脚本与依赖hash、版本、硬件、wall time。
- **读数：** 各schema/interface在三个budget的accuracy、合法答案率、truncation、输出token数；配对4096−96、4096−2048、thinking−nonthinking在同budget（不可从不同prompt模式之差归因单一module）；仅所有contexts平均，不筛有效答案。
- **阳性对照：** entity/single；同batch短/长采样prefix逐token一致；模型加载完整、prompt hash与E72匹配；targets/opposite-source配对与记录行数断言。预算censoring不单独作为能力失败证据。
- **噪声地板 + MIE：** prefix误差必须0；正控在long预算accuracy/format≥0.80且trunc≤0.10，才讨论mixed能力。4096−96 accuracy差≥0.20且CI不跨0则确认预算混杂；same-budget thinking差≥0.10且CI不跨0只是行为程序线索。若long仍未闭合/格式差，则界定接口/预算问题，不继续扫模型追失败。
- **独立确认门槛：** pilot controls有效、same-budget重要差≥0.10且CI不跨0，或long mixed≥0.90而E72 raw orthogonal≤0.75，才16 fresh contexts seed173001（confirmation词库、Alice/Bob、Left/Right、toxic/safe）有界确认。32-context能力确认等接口有效后再决定，不以4context饱和率宣称泛化。
- **混杂审计：** 4context discovery很小，CI仅描述材料；按schema/mode统计的采样不独立种子试验，非frontier可靠性评估。单条long路径的censored accuracy不估计所有可能短路径；prefix阳性在指定sampler/硬件/批量验证其有效性。prompt模式仍不同，budget只是可匹配的一项资源。
- **决策表（跑之前写）：**
  - 同轨迹long恢复且short未完成 → E72的低生成分数主要有预算混杂，不能声称binding failure。
  - both同budget都好、thinking无额外收益 → 特殊thinking开关非必要；非thinking的自然分析也可能完成计算。
  - 同budgetthinking好且direct完成却答错 → 保留程序/策略差异，后续因果测试，不能直接称faithful reasoning。
  - 两模式long都差、正控好 → 才保留有界mixed差异；再测试新材料和独立模型。
  - 正控差/大量long截断 → 不做容量或组合缺陷判断；先修真实接口/测量问题。
  - prefix不同 → 方法VOID，找采样/长度依赖来源；不拿不同路径包装延长预算的因果作用。
- **算力：** 本地GPU2（E72仍在GPU0/1独立运行），Qwen8B/conda verl-clean，模型NVMe复用，不改正在运行的E72源文件；预计单卡10–25分钟，额外short仅预定batch。27B后续仅在其E72接口有效与该budget校对成功后做，不盲目平铺。
- **产物：** scripts/e73_budget.py、scripts/analyze_e73.py；小run/analysis JSON入git，完整trajectory tokens/text及prompts JSONL留NFS。原E72短预算结果保留，不替换。
- **定位：** 延长scratchpad、reasoning与native/TF接口不等价已有大量研究；本卡为科学归因校对，不能单独构成ICES新贡献。后续有价值的问题仍需区别完整Source计算、正向label支持与函数约束推断。

## 结果：预算与格式均是实质混杂

`results/e73/qwen3_discovery/{analysis,run,prefix_audit}.json`；192条长轨迹，固定预定4contexts全部保留。**48次真实短生成前缀核对、0 mismatch**。科学运行924.247s。原严格解析器的4096-token accuracy如下；CI为context bootstrap，n=4很小，不作规模规律。

| schema | chat默认 | chat+Source指令 | thinking+Source指令 |
|---|---|---|---|
| source_only | .500 | .500 | 1.00 |
| orthogonal_prefix | .3125 | .375 | .8125 |
| entity_binding | .4375 | .8125 | 1.00 |
| single_source | .750 | .750 | 1.00 |

orthogonal thinking同一轨迹2048→4096 accuracy .1875→.8125、截断.8125→.0625，直接确认不能把短预算低分解释为能力失败。相同4096预算，thinking−instructed-chat差：source_only+.500[.3125,.6875]、orthogonal+.4375[.125,.6875]，但**direct单来源.750低于预定.80正控**。因此不触发原卡能力确认、不称独有多来源组合缺陷。

### POST-HOC格式审计（不替换主读数）

认真看已完成无合法答案样例，发现`**Answer: yes**`等装饰被原严格parser漏掉；这是可避免的测量遗漏。新脚本只移除独立Answer/Final Answer行的Markdown装饰/标题符号；不同答案行冲突、unknown/缺失、复合`Red yes`仍不接受，不从推理正文择标签。全192条×3budget共同审计，原strict指标均保留，无严格正确答案因校正丢失。

4096格式校正后的accuracy（`format_audit.json`，POST-HOC）：默认chat source_only .8125[.750,.9375]、entity .8125、single .9375、orthogonal .500；instructed-chat分别.500、.875、.750、.375；thinking原值不变。默认chat已具备不少来源判断能力，“关闭thinking不会绑定”的说法进一步不成立。Source指令的真实错误仍存在，不能都归解析器；其坏于默认模式的pilot差尚未独立确认。

**实际改变的判断：** E72不支持能力失败；格式是测量变量，长预算非thinking也可能写自然语言分析。thinking在这批样例上可靠完成说明有效程序存在，但不能只从trace认定faithful机制。新的独立确认若开展，须先固定语义解析规范、完整预算与有效正控；不能将事后校正视为原确认门槛已经通过。
