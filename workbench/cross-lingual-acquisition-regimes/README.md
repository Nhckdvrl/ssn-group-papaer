# C：多语言数据与跨语言学习

更新：2026-10-02。**有效学习 baseline 已建立，尚无论文 idea；最新用户要求先审查投入价值，当前不追加训练。**

## 当前决定与调度

人审依据：用户 2026-10-02 独立研究审计及本次明确要求纠正后继续推进。
保留领域与资产，停止冻结弱模型小信号的局部延伸，允许任务微调和小额 CPT。
总登记表的 PAUSED 调度状态暂保留；本次按人的明确授权持续推进本题，已从 baseline 修复进入训练干预，
不自行暂停其他 ACTIVE 线或占据新的 ACTIVE 名额。持续驻留的调度归属需人统一确认。

原 README 的“no method at entry”“冻结 regime 信号成立后才允许训练”、
仅凭近邻重叠或所谓天花板关闭题目的规定不再是当前执行依据。
是否训练由因果识别缺口与成本决定，按总执行协议预注册，不默认启动从头训练九宫格。

## 当前母问题

多语言模型学习新任务或新领域内容时，有限预算应该用于目标语内容、
翻译新内容，还是可复用的跨语言桥接？哪些训练选择真正改变后续学习，
哪些只改变已有能力的调用？收益是否伴随源语能力或旧能力退步？

这是研究入口，不是 novelty 声明。首先建立正常工作的学习 baseline，
从实际失败与有后果的差异提出最小干预，不能先给预期结果起名字。

## 解释与证据边界

- acquisition-limited → alignment-limited **撤回领先地位**；仍属未独立识别的备选假说。
- 四篇 parent 的数据内容、质量、暴露和训练阶段不同，不能当成同一因果量的冲突。
- MuBench 构成简单 exposure-saturation 预测的反压力，不等于识别了纯 pairing 效果。
- 冻结任务近随机不意味着模型不能学习；CI 跨零不意味着实践上等价。
- raw、token/character normalized、prior-adjusted 是不同读数，不作必须一致的四张选票。
- 本次审计不是独立重跑全部 52 次实验；原始大资产未进 Git。

## 已有资产与处置

八轮有 **52 次完成运行、186,336 条 item-cell 记录**；不是独立样本数。
保留 checkpoint/version/hash 审计、评分器、自然 QA 和撤回记录。

MONOWEB 翻译阳性对照，固定 WMT16 200 条/方向、5-shot、FP32：

| BLEU | FWB | MWB | MWB+P |
|---|---:|---:|---:|
| EN→DE | 24.16 | 11.47 | 21.36 |
| DE→EN | 28.90 | 20.11 | 26.01 |

仅确认训练数据干预在本地有效，不是完整数值复现或新发现。
Macaroni 近地板续写、更多 donor permutations、联合错误方向和一般性的翻译细节损失
回到诊断资产，不再优先扩展；不能据此关闭多语言领域。

历史方法与结果：[P0](P0_PARENT_AUDIT.md)、[首轮](EXPERIMENT_LOG_2026-09-30.md)、
[第二轮](SECOND_WAVE.md)、[第三轮](THIRD_WAVE.md)、[第四轮](FOURTH_WAVE.md)、
[第五轮](FIFTH_WAVE.md)、[第六轮](SIXTH_WAVE.md)、[第七轮](SEVENTH_WAVE.md)、
[第八轮](EIGHTH_WAVE.md)。这些是历史记录，不是当前训练禁令。

## 当前执行

**P01 / E01：统一英语 NLI 学习 → 德语迁移曲线。**
MONOWEB 三个 34K checkpoint 同起点协议、相同英语训练数据、适配方法和预算。
先用 FWB 的英语开发集确认 recipe 有效，冻结 recipe 后比较三条件。
完整报告 EN/DE 绝对能力、学习曲线、类别混淆与源语代价，不只报 transfer ratio。
适配种子重复不冒充预训练种子重复。训练端干预解释仍受单一预训练家族限制。

三适配seed终点EN/DE均值：FWB **83.61/77.19%**、MWB **82.37/75.86%**、
MWB+P **83.23/77.09%**。学习baseline可用；没有新的论文idea或机制解释。
完整曲线、seed SD及证据边界见 [E01结果说明](results/E01_LEARNING_BASELINE.md)。

- [实验卡](experiments/E01-monoweb-english-nli-learning.md)
- [主张账](CLAIMS.md) / [痛点账](PAIN_LOG.md) / [形态卡](PAPER_SHAPE.md)
- [会话日志](logs/2026-10-02.md)

下一步依实测决定：学习未跑通先修 baseline；有真实迁移瓶颈才设计桥接/内容干预。
“parallel improves transfer after fine-tuning”本身已有大量先行工作，不能作为贡献。

**持续探索P03 / E02：新监督内容覆盖 × 桥接复用 × 条件连接。**
同起点MWB短程CPT，对比覆盖任务实例或同域不重叠实例，固定文本切换paired/split attention，
再统一英语任务学习；不使用错误pair损伤作为唯一对照，不预写收益故事。
[实验卡](experiments/E02-reusable-bridge-task-learning.md)，当前是发现pilot而非新idea。

四格seed17完成，DE终点77.45–78.40%，conditioning的NLL杠杆未变成大终点迁移增益；
早期覆盖差同时影响EN，不追同一NLI的小信号。见[完整pilot](results/E02_BRIDGE_LEARNING_PILOT.md)。
**P04 / E03生成式QA基线完成**：FWB/MWB/+P的EN/DE F1为75.60/63.37、74.68/62.54、
74.35/63.53；单seed17，差小且CI宽，不是新idea。见[完整结果](results/E03_GENERATIVE_QA_BASELINE.md)。
**P03/P04 / E04完整完成**：DE F1四格63.66/62.94/64.14/62.53，覆盖×连接
交互−0.88pp context CI[-2.14,0.39]；不扩此小差异grid。[完整结果与边界](experiments/E04-qa-content-bridge-intervention.md)。
E05确认有效译料监督15442/16384；E07标准translate-train QA完成：EN/DE 72.89/66.22，
对英语only为−1.79/+3.68pp，源语代价和13.29%额外input token保留。
MT EN→DE/DE→EN 8.41/13.40 BLEU，未修复保持代价；德→英比英语only低2.51。
**P05 / E06发现适配代价候选**：MWB英→德BLEU11.47→7.92，一句恢复9.21；
精确照抄27/200→103/200，而三组QA终点相近。单seed/旧before硬件仍是边界，
E08同硬件1200/1200逐条复现；E09三A100并行做全部29/43适配种子重复；E10八LM测量完成。
E10 post EN→DE paired−split +9.10/+8.34 BLEU，而DE→EN −1.34/−2.78：
当前EN→DE单向CPT不能代表双向parallel，方向失败与JGP直接重叠，不据此命名防遗忘idea。
不先命名parallel防遗忘idea。[完整读数](results/e06_qa_translation_retention.json)。

用户再次纠偏后，已停止新增E11顺序扩展，保留未完成记录，不自动重启。
E03/E04已有有效任务学习，不再以“底座还需修”替代科学对象收敛。
已启动E09种子复验收尾用于资产校验；不围绕小差异继续追加条件。
新训练须先写清实际决策压力、最近邻增量及不同结果会改变什么，不能只因空卡开跑。

最新投入建议：不继续以当前acquisition解释或QA→MT保持lead组织新增训练；
E12仅生成骨架，已在实现/运行前撤销。已有E09按原承诺收尾，不追加条件。
有效底座并未解决贡献缺口：E10同instruction的前后保持交互远弱于post单向绝对差，
E07目标QA增益伴随MT代价仍可被一般任务干扰解释。保留资产与领域材料，
建议当前lead搁置；是否暂停C及未来恢复由人决定，不自行改登记表。

## 资产位置

- 模型：标准 HF cache `~/.cache/huggingface/hub/`。
- MONOWEB：`UCLNLP/monoweb` revision `4a42093acef06af33d2d5fdf2c26000d4f81d779`，
  `ckpt_exp_en_de_{baseline,monoweb,onlyparallel}/iter_0034000/hf_model`。
- 下载/定位：`scripts/cache_models.py` 与本地 `artifacts/model_manifests/`。
- 原始输出、下载论文：本目录 `artifacts/`、`sources/`（git-ignore）。
- 2026-10-02按用户要求清理28个已完成checkpoint目录，释放约137 GiB；
  代码、训练数据、预测、曲线、provenance/hash与日志保留。
  [清理清单](results/asset_cleanup_2026-10-02.json)；本地适配权重不能从HF下载恢复，需重新训练。
  仅暂留E09收尾/校对依赖的三起点seed17/29/43权重，不动共享HF缓存或其他题目。
- E01：`artifacts/nli_learning/train_{condition}_seed{17,29,43}/`，
  backbone `checkpoint/` 已清理，分类头/记录保留；不是完整生成式LM。
- E03完整LM：`artifacts/qa_learning/train_{condition}_seed17/checkpoint/` 暂留供E09校对；
  E02/E04的CPT及任务适配权重、E03 pilot、E07权重已清理，目录内结果与记录保留。
- 当前本地 conda：`/home/xiang/miniconda3/envs/openslime/bin/python`。
- GPU 使用人的授权节点空卡；独立单卡任务，不占其他进程，白天九点后最多八张并用。

## 定位纪律

JGP / MONOWEB / OpenSeal / TransWebEdu 已有 primary-source 审计。
False Friends、PreAlign、LINK、知识注入/桥接分离与数据复用工作是后续学习的近邻，
不是 veto 列表；对齐具体方法与实际训练失败，写清增量和 compression risk。
Standard-vs-Split、ParaRater 全文未完整取得，不冒称完成方法阅读。
当前没有 manuscript-critical contribution。只有科学读数改变训练决策且经干预验证，
才讨论论文叙事与增量。会议仅考虑主会；不以流程 heuristic 自动判死。
