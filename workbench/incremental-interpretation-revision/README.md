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
当前候选主旨[I01](ideas/I01-event-reference-or-lexical-echo.md)：**被排除的参与者为什么在下一事件里更容易被预测？**

已出现可检验的具体finding：具名role证据在原event帮助对应患者预测，换到同谓词新event反向；E33自然释义在换actor新event也反向，说明原stem重复不是必要条件；换人物不消除、换谓词使作用向正方向移动（绝对变正依赖事实词序）；native scope判读另呈正向外推。候选形态是“角色证据的迁移对象与边界→竞争解释→区分性语言干预”，尚未认定内部机制或普遍novelty。

## Idea 组合
[I01](ideas/I01-event-reference-or-lexical-echo.md)仍PILOT，有E29–E33连续判别支持，当前主张C05为L1。E32同词袋事实改序后predicate差仍+1.94/+2.36bits，但neutral/绝对方向变化，不能忽略focus。E33同基本动作8family的释义也迁移到otherActor新event（两order J−2.17/−2.14bits），原词重复不足、词汇boost仍影响，sameActor不确定。下一真正preliminary report的修订history对照，而非继续改同义词；所有构造继续独立逐条审核。不自动升PROMISING、不改变ACTIVE容量分配。C04的GP历史响应是另一测量，不用source-free C05追认GP-specific finding。

## 主张摘要
见 [CLAIMS.md](CLAIMS.md)。[E07](experiments/E07-native-readout-transfer.md) native顺序交互+60.87 pp [44.93,76.81]，C03为L1固定协议测量；[E08](experiments/E08-reading-focus-versus-final-query.md) 固定末尾目标题后，initial−final focus的GP交互+1.45 [−10.14,+13.04]，简单reading-goal故事支持不足。[E09](experiments/E09-published-comprehension-transfer.md) 原始SAP题句先cue−GP +33.33 [22.22,44.44] / +19.44 [11.11,29.17]，仍有mapping/顺序混杂；[E10](experiments/E10-question-versus-option-access.md) 拆位置后保留混合结构，不能归因task-directed parse。[E12](experiments/E12-input-probability-versus-answer-access.md) source消歧词交互+1.47 bits [.47,2.52]主要来自cue更易预测，不能叫承诺加深；转[E13](experiments/E13-natural-followup-without-diagnostic-question.md)原始自然后文用途：全S2 GP差−.031 / −.003 bits、两CI跨0，局部reference结果不确定。

[E01](experiments/E01-component-revision-map.md) Step5已审3/626句、13QA/104任务，其余因HTTP402额度不足待审；free opencode外审snapshot1/2原概率层保持gold=null；最新授权下snapshot3固定279句/1158eligible QA、999独立clear标签，4632任务三构式分卡已完成（.09771 GPU·h），correct仅外部标注agreement。NPZ同9源组initial-event extension交互句先+51.63 [21.60,84.02]pp、题先−20.29 [−53.11,9.93]，尚不支持统一承诺解释，[E11](experiments/E11-extension-role-reference-audit.md)首批196任务n1：无歧义long blocked role .0404→fullNP .9999（CI=null）；继续外审，追unambiguous extension也影响role的原因。[知识库](../../library/themes/incremental-language-processing/FIELD_MAP.md) 已缓存的多篇PDF和部分HTML/摘要条目、逐篇实际读取范围与近邻贡献归属；[E14](experiments/E14-event-identity-versus-extra-event.md) 无诊断Q、7明确活动的same−separate患者偏好交互−2.61 bits [−3.78,−1.09]，暂有aspect/referent混杂；接E15单词级控制拆解释。E15–E20得到患者特异、释义迁移和明确role事实响应；E21较小history gap主要cue下降。E22严格4源named−generic的relation-minus-neutral变化GP−2.79 [−3.68,−1.90]bits、cue−.17 [−1.12,1.20]，C04仅L1局部测量。E23 224续写首/次审10/6明确违反、84/88unknown，功能失败未稳健成立。E24独立24原source/12verb-family交互−.80 [−1.21,−.39]bits，方向迁移；E25新事件/新人物也保留信号（−1.25/−2.07bits），E28三类判断显示未知类别可用、同actor正负迁移强于换actor，而GP/cue接近且映射波动大，不能把它与likelihood强合为同一机制；E29移除S1仍有scope迁移，具名患者预测方向却在旧/新event翻转（+2.65/−1.86bits），neutral近0、generic不同；E30改second仍反向；E31同aspect换谓词使具名方向由−1.36转+1.53bits，扣neutral差+2.50 [1.47,3.68]，C05 L1；已有具体候选I01，下一释义区分原词与语义关系，未认定机制/novelty。

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

**最新审计授权（2026-10-05）：** opencode免费模型与Step均可逐条审数据；必要时用GPT Luna子agent复核。此授权替代此前Step-only要求，不追改已跑实验的null gold；审计来源、完成情况与不确定项持续记录。
