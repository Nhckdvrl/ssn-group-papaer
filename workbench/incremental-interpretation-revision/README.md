# Incremental Interpretation & Revision

## 状态（中文进度页）
**当前执行：用户于2026-10-06明确要求暂停，研究目标已暂停，无新实验/API任务。** 完整尝试、失败、反证与未完成项见[阶段总结](PROGRESS_SUMMARY_2026-10-06.md)，文件入口见[索引](FILE_INDEX.md)。失败原因诊断与转向建议见[诊断](DIAGNOSIS_AND_REDIRECTION_2026-10-06.md)；全文精读与公开数据审计后的方向筛选见[筛选](SCREENING_2026-10-06.md)（推荐C1，待人决定）。注册状态与科学等级不因暂停自动改动。
**状态：** PROPOSED — 2026-10-05 人明确授权先做 training-free baseline residency；不改变当前 ACTIVE-MAIN / ACTIVE-EXPLORE 分配。  
**territory 卡：** [Territory Card](../../search/our-taste/TERRITORY_INCREMENTAL_INTERPRETATION_2026-10-05.md)  
**数据计划：** [DATA_PLAN.md](DATA_PLAN.md)  
**目标会议 / 截稿：** ACL / EMNLP / NAACL；按证据成熟度选择下一周期。  
**上次人审：** 2026-10-05

**一句话（当前版本）：**
> 研究语言证据逐步到来时，LLM 如何形成、承诺并修订解释，以及旧解释在“看似已经改对”之后是否仍继续影响后续处理。

**重要边界：** garden-path 是第一个 calibration substrate，不是注册 novelty；ACL 2025/2026 已经直接研究 GP 难度、lingering misinterpretation、human/LLM comparison 与 recovery dynamics。

## 论文形态卡
当前探索[I01](ideas/I01-event-reference-or-lexical-echo.md)：**角色证据为何在某些表达条件下反向影响下一事件的参与者预测？** 尚未找到可确认的顶会主旨；继续追造成此边界的变量，不进入写论文。

## Idea 组合
I01仍PILOT、C05仍L1并收窄。E39–40在描述NP＋account/identity/report框架中，移除反身、显式否定与only后，old J正向（absolute D近0）、newother同V反向；E41双方ready仍反向，E42原生条件续写也保留。**E43最小名字事实、E44普通名字场景没有保留稳定绝对反转**，不能宣称一般跨事件角色机制。E45名字在原frame仍反向但old absolute control偏弱；E46析因发现identity主newSame D−6.56 [−7.94,−5.25]bits，identity×event−3.34，report非必要；E47清单本身引起−3.85bits、引用与断言仅差+1.08，身份断言非主必要因素；E48表达匹配作用强；E49 formal复述失败、E50普通actor锚定复述98.05%而名字列表41.41%，先E51拆two-names预设与角色/实体数量，外审自然材料同步准备。未认证好idea，继续验证；不是扩大模型或新开对象。C04的GP历史响应与source-free C05分开。

## 主张摘要
[账本](CLAIMS.md)保留全部阴性、prompt波动及降级。C00–02仍L0；E00 pooled GP差−2.81pp CI跨0，用户取消停步gate后执行E01，没有追认校准通过。C03是query顺序的固定协议测量。C04是GP history×角色表述的局部概率交互，E23实际续写失败未稳定。

C05最新边界：[E40](results/E40-summary.json) newother/sameV J两order−9.92/−7.24bits；[E41](results/E41-summary.json) ready仍−6.24/−6.61；[E43](results/E43-summary.json) absolute D全为正，old neutral扣除也负；[E44](results/E44-summary.json) 普通平衡场景old D+10.17/+9.05，新other无协议+2.62/−1.32(last CI跨0)，ready+5.76/+4.12。E44 native576/576明确正确。不能用neutral subtraction自动认证纯关系效应，不能把条件字符串概率叫世界概率或false belief。原negative结果不删，普通语言transport反证如实保留。

[知识库](../../library/themes/incremental-language-processing/FIELD_MAP.md)记录实际读取范围及ownership：GP/lingering、priming、retraction、state-QA/预测gap、一般role binding均有直接近邻。下一增量须来自精确必要变量及自然功能后果，不能靠“有人没测过这个模板”认证novelty。

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
