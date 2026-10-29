# MoE：学习历史怎样选择专家分担与可重用计算

> 母问题：相近任务为什么可以由不同的专家职责与协作实现？哪些关系由任务约束，哪些由学习历史选择；这些关系怎样影响预测和组件重用？

**截至2026-10-29：E144–E164已完成，当前0卡、总并发上限4卡，成熟资产阶段0新训练。** 三条核心论证及实际路由通路检验已有直接干预；C14维持本设定内L2。目录整理、统一CPU入口、全文再定位与新55学科440题均完成。本轮已形成英文论证稿及三幅新主图；用户新授权的E165数值/输入已冻结，即将受监督单卡执行。头线仍CLOSED，正式ACTIVE登记不变。

## 当前最值得讲清的发现

| 结论 | 决定性证据 | 为什么重要 |
|---|---|---|
| **相近成功容纳不同分担** | B/F完整文本NLL=2.6218/2.6212，任务raw均39.06%；F选择部署更稳，去S的文本损伤却比B额外增加1.8509 [1.3311,2.3010] | 更易裁剪/选择与更依赖伙伴可以同时出现；部署可选择性没有唯一规定职责实现。见[E162](experiments/E162-full-course-native-division.md) |
| **性质载体与必要伙伴可以分离** | 共同P骨干/gate中，R_B单独使低预算答案NLL改善.1882 [.1155,.2641]，但完整NLL恶化.0802 [.0144,.1473]；S_B单独没有携带同样性质 | 原生删除最重要的组件，未必承载希望迁移的性质；性质迁移与完整能力重用需要分别验证。见[E156](experiments/E156-native-common-parent-function-cross.md) |
| **同函数消息仍需合适的使用背景** | 固定S_P换R_B，其移除代价增加.3386 [.2354,.4439]；实际消息跨背景重用有.2605 NLL代价，norm/残差投影校正后仍为.2459 [.2096,.2819] | 函数身份、产生的消息及其使用关系是不同对象；所测局部几何校准只解除小部分配套代价。见[E159](experiments/E159-unchanged-function-partner-role.md)、[E160](experiments/E160-fixed-shared-signal-context-cross.md)、[E163](experiments/E163-native-message-geometry-and-reuse.md) |

**论证中心：** 训练形成的不只是一张可选函数表，还包括这些函数如何产生消息、其他计算如何使用消息。可选择性、性质可迁移性和实际计算可重用性可以分离；研究要解释这份分离怎样形成、在什么条件下重复。

![性质迁移与未改伙伴的作用](paper/figures/02_property_and_partner_under_fixed_routes.png)

新三幅主图有35项既有估计及原CI的[逐项来源](paper/figures/figure_sources.json)，无新统计检验。[英文4页论证稿](paper/main.pdf)连接三条结果和E164；[选择与依赖图](paper/figures/01_selection_and_dependence.png)、[实际消息图](paper/figures/03_actual_message_reuse.png)补全证据顺序。

## 模型和符号

R指每层被路由专家的加权输出，S指始终激活的共享专家输出；这里的R/S干预均覆盖16层函数套件。D是骨干与其余稠密计算，G是gate参数；固定G仍允许实际路由随hidden state改变。

| 端点 | 公开训练路径 |
|---|---|
| P | 标准预训练1T，退火前父状态 |
| A | 标准1T后，标准退火50B |
| B | 标准1T后，引入EMO约束退火50B |
| F | 全程EMO预训练1T，再退火50B |

四者同架构/tokenizer/active k；公开pin和权重SHA见[ASSETS](ASSETS.md)。这些是成熟公开路径，不是已核实的独立初始化总体或单变量时机实验。LM为64窗口/20文件簇，任务为生物/数学各64题；区间条件于模型和输入范围。

## 怎样读现有证据

| 需要了解 | 入口 |
|---|---|
| 科学问题、竞争解释与边界 | [RESEARCH_DIRECTION](RESEARCH_DIRECTION.md) |
| 领域位置、论文主旨与下一研究决定 | [PAPER_SHAPE](PAPER_SHAPE.md) |
| 主张、等级、撤回和逐次更新 | [CLAIMS](../CLAIMS.md)；[PAIN_LOG](../PAIN_LOG.md) |
| 全部协议、结果和未取得项 | [实验索引](experiments/INDEX.md)；每张原卡链接自己的raw/manifest/审计 |
| 权重、原始数据、精确源码包和恢复 | [ASSETS](ASSETS.md) |
| 复算与代码使用 | [scripts/README](scripts/README.md)；执行前读[AGENTS](../AGENTS.md) |

E120–E142是受控可重复分解的起点，摘要见[历史受控窗口](notes/CONTROLLED_E120_E142.md)。E144–E147建立小而真实的预测配套及gate-only强对照；E148/E149短历史有预测响应、未检出强配套障碍。E158/E161保留内容组合的实测边界。它们是支持与边界，原数字、阴性和失败均保留，不强拼成同一机制。

## 最新结果：固定实际路由后，两种分离仍存在

[E164](experiments/E164-runtime-routing-property-transport.md)保持P骨干/gate/S_P，交叉R_P/R_B与两者产生的实际路由（支持和门值）。主分析为此前未使用的55个MMLU学科各8题，全部440题；旧128题只作精确guard和次分析。

| 新55科读数 | 估计与配对95%学科簇区间 |
|---|---|
| R_B低预算答案NLL改善：自然 / 固定P路由 / 固定B路由 | .4207 [.3221,.5234] / .2937 [.2027,.3904] / .3824 [.2904,.4746] |
| 同S_P的移除NLL代价增加：自然 / 固定P / 固定B | .3628 [.2703,.4612] / .2891 [.2104,.3645] / .1840 [.1169,.2461] |
| 完整质量与正确率边界 | 自然full NLL反而增加.1746 [.1196,.2325]；低预算raw准确率仅+1.14pp [−2.27,4.55]，尚未区分优势 |

**解释推进：** 性质迁移和同函数伙伴作用变化都不要求由R变化诱发的后续路由变化。路由也不是无关：B轨迹额外帮助R_B低预算NLL .1270 [.0877,.1667]，但在R_P下仅.0383 [−.0042,.0812]，函数×轨迹交互为−.0887 [−.1242,−.0500]。这把参数包来源与实际实现通路分开；固定路由仍允许S、attention等响应内生，不能叫孤立专家的自治能力。

低预算choice CE同向改善1.1386 [.8431,1.4676]；正确率单列，不把概率质量收益说成已提高答题能力。新旧面板同时改变任务与validation校准样本数，不能把幅度差单归任务；区间不是训练seed总体。

[完整矩阵与逐学科结果](results/e164/summary.json)；[全部来源对比图](results/e164/figures/source_effects_NLL.png)；[固定路由的共享作用图](results/e164/figures/shared_partner_role.png)。13238数值/13548元数据独立公式复算最大差7.99e−15，旧LL/KL、回放对角、因果前缀及来源终态全部通过。1.444648 GPU·时，峰值55.112GB，最多1卡，监督exit0，0新训练/下载。源码43aee97a、plan43877611…048a7与raw SHA见[manifest](results/e164/manifest.json)、[资产入口](ASSETS.md)。结果提交48f30265，[封存凭证](results/e164/artifact_seal.json)逐项核对90个实文件，保留精确源码/输入与原始结果。

```bash
~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py E164 all
```

E163的局部几何结论与29650项独立复算保持不变；完整结果/失败/源码包均由[结果导航](results/README.md)进入。E143未运行；E158原逐层扫描未取得。下一步先将三条实证与E164组织成清楚的论文论证；更广成熟谱系及真实形成分叉是后续重要缺口，不用同端点层/方向/selector扫描代替。

## 本轮下一项：E165，尚无新模型结果

新增全文67页与[定位比较](../../../library/themes/moe-routing/SELECTABLE_COMPUTATION_AND_HISTORY_2026-10-29.md)后，主线聚焦成熟组织中选择、性质载体和实际使用的关系，不讲成选择与合作互相矛盾。E164的预算收益与full下S作用不在同一运行条件，尚未证明预算收益由shared补偿造成。

[E165](experiments/E165-mature-olmoe-selection-transport.md)选另一成熟OLMoE谱系的明确5.033T父状态→100B普通退火，26个来源/选择/实际路由条件；不将无shared架构伪造为S/R组。资产LFS、440题重新编码（最大2736）及CPU真实接口/独立公式fixture均完成；18份数值源0fb295d6、plan9570789c…e25a2已冻结，NVMe装载adapter单列SHA，受监督单卡执行，cap4 GPU时、总并发≤4，0新训练。P/A为该卡内部标签，不是EMO的P/A端点。
