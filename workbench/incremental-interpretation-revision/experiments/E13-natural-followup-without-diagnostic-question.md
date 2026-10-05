# E13：没有诊断问句的自然后文，是否仍受初始解释影响？（2026-10-05）

- **状态：** PLANNED
- **类型：** MEASUREMENT / P09下一信息问题，非paper novelty
- **对应：** C01 / C02 / P06 / P09
- **问题（一句话）：** 原句的GP历史是否在没有理解题时影响自然后文的自反/相互事件承接，还是当前错答主要来自诊断任务？
- **设置：** 已发表Slattery2013 Experiment2/AppendixB原24两句items，作者GP/comma×两NP选项四variants共96；不构造新后文或语义gold。source PDF固定SHA与copyright见[D0](../results/D0-Slattery-source-audit.json)，raw与normalized保持cache-only。统一schema下question/gold=null。独立opencode全24源item/96variant作transcription advisory，normal-finish/逐ID/hash完整检查，旧失败保留，不称Step5或人审。原句末到第二句的frozen Qwen3-8B conditional word概率，现有模型/env；无SAE/probe/训练。
- **至少两个解释：** (a) question-triggered / extra metalinguistic demand：没有问题时完整第一句已足够支持第二句，GP/cue的后文差接近邻词一般波动；(b) input-history / unresolved interpretation：初始分析即使已有后续完整句证据仍改变自然后文条件概率，且GP效应受作者NP-option factor影响；(c) generic text/noisy-channel spillover：差值均匀作用于第二句、非局限于自反/相互事件承接；不能称旧meaning persistence。不能用任一surprisal差直接证明内部两个parse。
- **读数（推理前固定）：** 主读数第二句全部词mean surprisal(bits)，同source-set×NP option GP−comma及其NP-option交互；24cluster paired bootstrap/10000/seed20261005，分别报两个option。次读数22原item中regex定位的首个himself/herself/themselves/each other字面词区间的平均bits及其前后各最多两词；缺字面reference的source9/10报告null，只在这个次读数缺失，不删除主读数项目。所有第二句逐词数值保存cache，不事后挑高差窗口或答对项。source前12/后12有不同参与者组合，按作者排序块另报，不假定英语NPZ所有词汇同效应。
- **阳性对照：** 同一作者两句四variant的第二句字节/word完全相同，源GP/comma只改变作者可选comma和指定NP；源句概率及第二句邻词/尾部给通用spillover参照。此前SAP source disamb GP−cue强读数作为harness校对，不把一次局部后效应当新idea。
- **噪声地板 + MIE：** 已知FP32同prompt概率漂移小（不自动换成bits）；报告bits与CI，不设置正确率/显著性停步线。literal-word区域是源字符串规则，不由agent语义指定新disambiguator/critical window。
- **混杂审计：** 作者originality明确；NP选项是发表操作，不新增plausibility gold，保留source_option0/1名而不假设其绝对可行性。S2自身仍有局部词汇线索，效应缺失不能推出毫无历史trace。源text删除running header通过PDF列/几何crop，保留NFKC/空白规范化规则及hash；独立外审确认变体展开和source-level问题，agent不作语义gold。普通causal LM likelihood，不通过元语言prompt索取判断，R8 prompt能力主张不适用；无额外提示词模板。第一源词若无起始context，明确不评分，主读数S2不受影响。
- **决策表（跑之前写）：** 没有Q仍有reference区域×NP-option效应、邻域不均匀 → 保留后文用途的history解释，下一语言操作区分重新整合与局部semantic兼容；只有普遍shift → 追noisy-channel/句子异常处理，不叫lingering；S2效应小但旧QA强 → 降低用QA直接定义revision的支持，转具体被晚cue改变的事件依赖；mixed → 报完整分项并结合E01，不扩模型/模板来找赢家。已有Slattery/Cao/Li/Hanna均有相关owner，是否可形成增量要由新证据决定。
- **算力预算：** 独立单卡、96短文本预计<.02 GPU·h；外审2并发，和当前E01外审4并发合计≤8。资源下载零（复用已缓存PDF）。**实际：** 未推理。

## 结果（推理之后填写，保持以上读数）
- 数字与CI：尚无E13推理。
- 独立审计：待返回；source四variant同S2和shared schema已机械核对。
- 主张变化：无。
- POST-HOC：无。
