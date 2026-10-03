# E60：独立social meaning parent的原数据与对象校对（2026-10-03）

- **状态：DONE。** 本卡先于仓库下载/CPU统计，0模型预测。
- **类型：REPRO / D1 source audit。** 对应C02/P02；不为流程注册idea。
- **问题：** Social Meaning原公开code/raw/human norm能否独立识别精度语境×表达形式的social judgment？正文的competent与appendix的confident是否实际用了不同问题？这决定它能否约束IQAP intent-uncertainty的解释，不能先假设两者同构。
- **读数：** pinned release与逐文件hash；独立场景/条件/trait/参与者/模型次数；原prompt字段、答案和原评分实现；human原条件均值与interaction、公开model cache原metrics数值parity（若存在）。先审对象，不新拟metric，不将两个数据集平均差当因果。
- **阳性对照：** 原六contexts×HP/LP×exact/approximate×六traits的完整性；选择/exclusion与重复记录逐项核对；源code的原复现路径与论文主表分开。不执行闭源API，不将missing raw填造。
- **噪声地板 + MIE：** CPU parse/hash与计数应精确；原均值/舍入parity按author precision。六场景不是371独立语境；人类与model repeats不能扩增scene n。未取得raw前不虚构CI。
- **决策表（跑之前写）：** A原资产与问题一致、统计parity→保留为独立parent；新的stage实验另开卡且明确新增问题。B实际trait/prompt mismatch→分别保存，不能假装同目标比较。C资产缺失→记录缺失，先使用能核对的资产，不换闭源judge补金标签。D对象不同→保留各自成功/边界，用于限定解释而非硬合统一criterion。
- **混杂审计：** 这是原数据驻留，非同speaker/utterance跨source实验；7point尺度、6traits、意图分布属于不同目标。作者显著effect筛选/参数选择、model judge依赖均如实核对。最新近邻拥有direction/strength及theory prompting，不claim首次。
- **算力预算：** CPU；公开repo/必要小型human raw尽量直接网络，不经shell VPN，≤100MB；不下载权重/不运行训练/闭源API。八卡继续E59。

## 结果
[source/cache audit](../results/E60-social-source-audit.json)与[human motivation norm](../results/E60-motivation-norms.json)完整。revision c60d6004781cafeb0cdd617105c96581cc93669f；4×4320=17280原cache，每432 cells×10 repeats完整、IDs/parse逐行一致，原metric functions与独立十effect arithmetic差<1e-12。MIN/ALT/KMA/COM原parser有效4222/4320/4316/4306；不将原缺失静默视正确。当前code所有144 MIN问competent等六trait，没有confident，但cache未存历史prompt，不能证明历史调用一致。

原human Exp1/2 retained362/390=752人、六scene×24cells/experiment，全部字段1–7或0/1符合codebook。已有完整362/390 raw和两研究README，Exp2仅paper给bicycle完整例，其他stimuli缺；不用新造context冒充原human norm。原paper说两实验pre-registered，OSF新README说仅Exp1正式pre-reg、Exp2为planned follow-up，版本边界保留。

原10pp近邻及ELM12pp正文/方法/related/讨论已深读，图片未独立审；source/cache code核心已读。公共code entry point参数过期，调用未改原metric functions。global table35/36三位小数可匹配，Gemini COM rho计算.916而论文.932待核；CDS小差如Claude MIN .539/.538与Gemini COM1.336/1.338，保留raw版本，不凑分。Exp2人类仍大量选lack-knowledge，不把consulted source硬标perfect knowledge或false alarm。

决策A/B/C混合：Exp1 norm/source可做有限独立驻留；历史prompt和Exp2完整stimuli不齐需明确限制。新科学未知是证据→动机与动机→人物评价的不同条件作用，不能把human correlation当causal mediation。C02与I01不升级。

执行校对：缺matplotlib依赖先停，直连TUNA只安装到指定venv；原DAS/ISS nonsignificant NaN保存为null（未定义≠0），未改原评分/人类labels，未调用API。
