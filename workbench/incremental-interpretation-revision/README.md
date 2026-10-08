# Incremental Interpretation & Revision

## 状态与授权

- **注册：** PROPOSED（人授权的 baseline residency；不改变 ACTIVE-MAIN / ACTIVE-EXPLORE 分配）。C06–08 L0，C09限定问答协议L1；尚未认证合格idea，未进入候选。
- **2026-10-06 人决定：** 从暂停恢复，重置到[ROUTE](ROUTE.md)，放弃I01/C05；先广后深，允许白盒，使用同节点8张H20。
- **执行模式：** 自主推进[EXECUTION_BRIEF](EXECUTION_BRIEF.md)，原人审节点自审后继续；仅§6.7真正卡住或人专属开关线/状态/候选决定时回来。
- **数据/API：** 现成成熟数据优先直接用；需新标注/修改/定点审计时只用Step Plan `step-5-preview`、≤5项/批、全局并发≤8，禁止现金接口。HF仅国内镜像，推理离线。
- **硬资源约束：** 2026-10-08 09:00北京时间前释放全部GPU。08:19已提前停用并删完剩余权重，09:01实际核验本用户GPU/本工作queue/模型权重均0；本用户目录约38GiB、项目约17GiB。科学数据与结果保留。见[资源释放](RESOURCE_RELEASE_2026-10-08.md)。
- **territory：** [T15](../../search/our-taste/TERRITORY_INCREMENTAL_INTERPRETATION_2026-10-05.md)；ACL/EMNLP/NAACL按证据成熟度选周期，不投Findings，不参考EACL。

## 当前研究问题

强模型看到完整句后，旧关系的撤回与正确替代关系的建立为何可能分离？进一步问：当自监督内容奖励重建的观察本身必须改读，它是否把原表达的可预测性误当作正确修订的credit？这是[I06](ideas/I06-late-verb-frame-reanalysis.md)/[I07](ideas/I07-self-supervision-inherits-interpretation-bias.md)的探索切口，不能先假定一般机制成立。

最初的归因区域仍是增量编码过时、作答选择、合理性组装、测量语义四方竞争。GP错答案、消歧surprisal、双向/重复阅读不能单独认证内部解析。原作者部分No表示not necessarily；源支持、明确矛盾与可能的额外事件分开，不能把所有GoldNo当世界虚假。

**当前结论：没有合格idea。** 已有问答与自由关系表达的分离、撤回旧关系与建立新依赖的分离，以及两族有限候选中的重建credit竞争；尚未连成有足够解释力与重要后果的叙事。[整体诊断](REASSESSMENT_2026-10-07_2355.md)末节核对了E107终图，并承认重复“局部正结果→收缩→补实验”的执行问题；实验卡和精读数量不能代替科学推进。

| 核心结果 | 完整证据与实际含义 |
|---|---|
| [E52](experiments/E52-genuine-revision-reading-map.md)广面起点 | 1732公开QA/309 GP pair，14模型/5族；任务语义与能力证据分开；§1精读和“我的理解”已写日志 |
| [E67](experiments/E67-reading-goal-to-free-relations.md)/[E99](experiments/E99-goal-qa-correct-with-explicit-misreading.md)旧三族Goal后果 | 同S QA正确＋明确误角色联合增17/12/30pp；完整自由角色3204输出已封版，非仅QA均值或唯一latent parse |
| [E98](experiments/E98-query-guidance-versus-interpretation-fidelity.md)当前三族实际输出 | 1800actual；GP QA收益Q/G均CI含0、Min0；联合错角色仅Q明确+20.83[10.42,33.33]pp，不能讲当前共同Goal收益悖论 |
| [E96](experiments/E96-modern-native-belief-credit.md)原生proposal/self-grader | 50发表pair/三族/300P/600LP；换消歧观察target使fidelity alignment三族+.444/.500/.500且CI正，主要MVRR；不等于完整理解完好 |
| [E101](experiments/E101-disambiguation-region-reconstruction-credit.md)/[E102](experiments/E102-revision-evidence-credit-oracle.md) | 固定候选前缀credit三族偏旧解释、后段Q/Min偏修订；T2位置oracle改善选择10.42/8.33/21.88pp，G总体CI含0；原pool含cue来源 |
| [E103](experiments/E103-native-pool-revision-credit-selection.md)同原S八候选 | 全50/三族1200assignment；原角色类别Min +8.33pp不能解释为完整意义修复，E107新依赖读数未显示稳健完整恢复；MVRR无新增good候选 |
| [E105](experiments/E105-added-proposals-reconstruction-faithfulness.md)/[E106](experiments/E106-positive-observation-innovation-credit.md) | Q whole预算1→8改善13.54[5.21,22.92]pp，不支持更多搜索更错；唯一无T2 positivegain无稳健跨族修复，不调cutoff |
| [E104](experiments/E104-belief-r-revision-evidence-credit.md)跨域原1744 | 机械then后缀使UPDATE Q/Min更差；then未认证语义revision证据位置，不能据此反驳真正跨域机制，也不扫描其它cut |
| [E107](experiments/E107-critical-dependency-commitment-audit.md)完整依赖审计 | 243/243双遍、57裁决、0未解决；全50明确依赖suffix−whole Q+6.25[−2.08,16.67]/G0/Min+4.17[−4.17,12.5]pp。Q/Min条件候选14/50与13/50源有prefix反对、suffix支持正确依赖的credit竞争；仍非广泛修复或训练后果 |

E93/E95/E97/E100的cap、unknown、Tie和整族仪器不可用全部保留，不记为0能力或“已懂仅评分错”。完整范围与失败版本见各实验卡；I07/I08仍SEED，不因近邻已做部分工作桌面判死。新故事须证明值得兴奋的具体关系更新机制或后果，不寻找完全空白。

## 知识库与资产

- [领域地图](../../library/themes/incremental-language-processing/FIELD_MAP.md)、[86篇主文精读索引](../../library/themes/incremental-language-processing/REVISION_READING_INDEX.md)、[跨领域综合](../../library/themes/incremental-language-processing/REVISION_RESEARCH_SYNTHESIS.md)。5综述/2 position/79研究；所读版本/附录/接收/代码核对分开，摘要与下载不混计。
- 最新近邻：ABBEL/ReBel/Agent-BRACE的belief内容信号、TRLM的inverse feedback、IW-OPD的prefix compatibility、Self-CTRL的一致性、Causal Quotient的表示/使用/尺度、BeliefMem的候选置信记忆、Dark Room的奖励传递机制。定位与increment写在论文卡，不自动输出关线判决。
- 外置根目录：`/data1/xiangding/work/incremental-interpretation-revision/`；`E##/`保留原数据、输入/配置、输出/LP、审核、map及complete标记；原始数据、模型、PDF不进git。当前95个已存在map文件索引及17模型0权重状态见[释放清单](RESOURCE_RELEASE_2026-10-08.md)，历史/interim不冒充独立完成结论。
- E52主资格入口`E52/qualified-v3.jsonl`，原v2/双轮/裁决资产保留。E53旧T4-native-v2为6244/6247双遍、635裁决、3未解决，属于语态澄清前协议，不当当前role-v2能力证据；没有继续读partial效果。
- [scripts/README](scripts/README.md)与各实验卡提供复现入口；当前tokenizer/config/revision/manifest可用、权重已释放。重新GPU/下载需人新增资源授权，模型只走国内镜像。
- 历史入口：[E00–51总结](PROGRESS_SUMMARY_2026-10-06.md)、[旧路线诊断](DIAGNOSIS_AND_REDIRECTION_2026-10-06.md)、[FILE_INDEX](FILE_INDEX.md)、[DATA_PLAN](DATA_PLAN.md)、[CLAIMS](CLAIMS.md)、[PAIN_LOG](PAIN_LOG.md)。原事实与失败均保留在git历史/实验卡/日志。

## 人的决定记录

2026-10-05选择territory并授权baseline residency；2026-10-06暂停归档E51后，接受诊断并恢复新路线；同日授权自主执行，覆盖普通流程中的停步gate。2026-10-07晚要求以高信息量实验找到值得追的idea，数据质量优先、无需今晚补齐完整训练论文；随后明确09:00释放GPU和模型空间。agent未作开关线、状态或候选决定。
