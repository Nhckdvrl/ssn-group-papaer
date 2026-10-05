# Incremental Interpretation & Revision

## 状态（中文进度页）
**状态：** PROPOSED — 2026-10-05 人明确授权先做 training-free baseline residency；不改变当前 ACTIVE-MAIN / ACTIVE-EXPLORE 分配。  
**territory 卡：** [Territory Card](../../search/our-taste/TERRITORY_INCREMENTAL_INTERPRETATION_2026-10-05.md)  
**数据计划：** [DATA_PLAN.md](DATA_PLAN.md)  
**目标会议 / 截稿：** ACL / EMNLP / NAACL；按证据成熟度选择下一周期。  
**上次人审：** 2026-10-05

**一句话（当前版本）：**
> 研究语言证据逐步到来时，LLM 如何形成、承诺并修订解释，以及旧解释在“看似已经改对”之后是否仍继续影响后续处理。

**重要边界：** garden-path 是第一个 calibration substrate，不是注册 novelty；ACL 2025/2026 已经直接研究 GP 难度、lingering misinterpretation、human/LLM comparison 与 recovery dynamics。

## 论文形态卡
尚未确定论文主旨。允许的生长形态：
- stable revision pattern → competing accounts → discriminating intervention；
- measurement mismatch → corrected interpretation of an existing capability claim；
- cross-ambiguity process account；
- only if behavior justifies it: white-box causal mechanism.

禁止预注册“LLM 不会完整修订”“旧解释一定残留”等结果。

## Idea 组合
尚无 PROMISING idea。先完成 baseline / measurement。首批压力：
- commitment timing；
- revision completeness；
- cue timing / cue strength；
- representation-to-use/readout disagreement；
- cross-ambiguity generalization；
- measurement validity.

## 主张摘要
见 [CLAIMS.md](CLAIMS.md)。[E07](experiments/E07-native-readout-transfer.md) native顺序交互+60.87 pp [44.93,76.81]，C03为L1固定协议测量；[E08](experiments/E08-reading-focus-versus-final-query.md) 固定末尾目标题后，initial−final focus的GP交互+1.45 [−10.14,+13.04]，简单reading-goal故事支持不足。[E09](experiments/E09-published-comprehension-transfer.md) 原始SAP题句先cue−GP +33.33 [22.22,44.44] / +19.44 [11.11,29.17]，仍有mapping/顺序混杂；[E10](experiments/E10-question-versus-option-access.md) 拆位置后保留混合结构，不能归因task-directed parse。

[E01](experiments/E01-component-revision-map.md) Step5已审3/626句、13QA/104任务，其余因HTTP402额度不足待审；此前授权free opencode外审探索层snapshot2 54句/228eligible QA，1824任务（snapshot1保留）、gold全部null。NPZ延长/role/semantic分离只作小样本线索，[E11](experiments/E11-extension-role-reference-audit.md)已外审head/full-NP/isolated，追unambiguous extension也影响role的原因。[知识库](../../library/themes/incremental-language-processing/FIELD_MAP.md) 16篇论文/17个PDF版本缓存、逐篇读取范围和近邻贡献归属；尚无已经证成的novel idea，继续围绕interpretation revision推进。

## 痛点摘要
见 [PAIN_LOG.md](PAIN_LOG.md)。

## 第一驻留块
1. D0 数据与 license/revision/hash audit。
2. [E00](experiments/E00-baseline-reproduction.md)：复现至少一个现代开放模型上的已知 GP-specific behavioral deficit。
3. 按用户修订直接推进 Jurayj componentized stimuli 的 GP / early cue / blocker / longer ambiguity 系统测量；保留E00的不稳定结果，不追认旧对照通过。
4. 行为出现稳定结构前，不做 probe/SAE/patching fishing。
5. 每个新实验必须写清它区分的至少两个解释。

## Ownership / compression
必须正面防守：
- Amouyal et al. ACL 2025：GP 难度、plausibility、verb type、lingering misinterpretation；
- Amouyal et al. ACL 2026：七类复杂结构的人/LLM processing comparison + released harness/data；
- Baitalik & Datta ACL SRW 2026：NP/Z、NP/S、MV/RR recovery dynamics；
- Zeng et al. Findings ACL 2026：delayed lexical disambiguation / deferred semantic drift；
- Jurayj et al. BlackboxNLP 2022：GP traversal + componentized stimuli。
- Li et al. CogSci 2024：逐段语义问答、逗号、parse shift 和 attention；
- Hanna & Mueller 2024/2025：多种parse的句法特征与后续问答特征不复用。

任何 lead 都要回答：
> 为什么这不是“已有 GP/ambiguity paper + 更多模型/更多结构”？

## 决策记录
- **2026-10-05：** 人明确选择“增量语言理解 / interpretation revision”作为下一候选 territory，要求注册进仓库并让本地 agent 开始。为遵守现有单 ACTIVE-EXPLORE 约束，状态登记为 PROPOSED，但 baseline residency 已被人明确授权；不得自行暂停/替换现有 ACTIVE 线。

## 资产位置
- 上游数据/代码先下载到本地 cache，不直接复制进 git；来源和 hash 见 DATA_PLAN。
- 本仓库新增脚本放 `scripts/`，实验卡放 `experiments/`，结果摘要放 `results/`；大模型/大 raw 不进 git。
- 本地 cache：`/data1/xiangding/work/incremental-interpretation-revision/`（upstream / normalized / models / runs）；[审计](results/D0-audit.md)、[复现入口](scripts/README.md)。下载显式无代理；复用已有 venv。

**2026-10-05 用户修订：** 人明确要求取消agent附加的停步gate，继续系统观察与idea生长；进入E01（不追认E00通过），构造/改造语义标注审计改用Step5，最多8并发。持续论文阅读写入既有 `library/themes/incremental-language-processing/`。先前等待科学分支的请求已被此指令替代，不再据此停步。
