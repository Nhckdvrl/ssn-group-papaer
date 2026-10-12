# 文献管理：阅读事实、知识缺口和下一轮真正需要读的内容

更新：2026-10-12。迁移 149 原资产不是重读149篇、153文件不是153篇论文、历史86篇MAIN不等于每篇附录与实现已被核真。[原阅读台账](READING_LEDGER.json)记录过去版本与所读节；[历史阅读索引](REVISION_READING_INDEX.md)保留原计数。新笔记必须在此 workbench/knowledge 维护，不回外围library。

## 精读等级不是道德勋章，而是来源边界

- PRIMARY-MAIN-VERIFIED：这次明确查看作者正式/注明版本的主文背景→方法→主要表图→讨论限制，并标记具体未看的附录；这不等于复现代码。
- SECTION-VERIFIED：只复核了清楚标出的主文节/关键表；引用不能外推到整个论文结果。
- ABSTRACT/INDEX ONLY：只有入口、摘要或目录，不能作精确方法最近邻或因果否定。
- HISTORICAL-RECORDED：迁移的旧主文阅读记录，可信度依旧由旧台账/缓存SHA决定，本次**没有**再次取回原机PDF。
- SOURCE-CONFLICT：作者HTML、accepted PDF、会议正式稿或代码实现不一致；并列记录版本和具体差异，不自动选择最想要的解释。

## 本轮重新阅读/核对的论文及缺口

| 论文 | 实际本轮查看 | 得到的可迁移实验设计认识 | 未覆盖 |
|---|---|---|---|
| Ceháková & Chromý 2023 [全文](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288817) | 正式HTML：材料、Exp1–5、coding、总讨论 | 接受度pilot→三种独立依赖→在线RT→开放错误类别→呈现方式cross-check；Exp1是pilot，不要误称全部只有4个编号 | OSF逐行原始数据与R脚本未跑 |
| Maina-Kilaas & Levy 2026 [v1](https://arxiv.org/html/2603.23624v1) | v1 HTML：引言、方法、Exp1 Maze、Exp2 SPR、数值与限制 | “强承诺”效应需把critical词是否句末与长度正交；非句末只是反向趋势，3阶交互未达到作者阈值 | 模型拟合代码/受试者原始数据未独立运行 |
| Amouyal et al. 2026 [v1](https://arxiv.org/html/2510.07141v1) / [ACL正式入口](https://aclanthology.org/2026.acl-long.1040/) | v1主文与部分附录表，正式PDF前部与表1；具体human/LM评估口径 | 统一任务仍有time/prompt/logic gold边界；“GP接近人类=必须删旧记忆”是作者推测 | 最终PDF全部附录/每条标注及发布数据未审计 |
| Slattery et al. 2013 [期刊](https://www.sciencedirect.com/science/article/pii/S0749596X13000247) | 期刊HTML实验摘要、Exp1/2原理、总讨论；对照 [历史详卡](slattery2013-competing-representations.md) | 用新解析结构约束与另句旧痕迹分别识别竞争理论 | 本轮未重读完整正式PDF逐页 |
| Hanna & Mueller [v1](https://arxiv.org/html/2412.05353v1) / [NAACL正式](https://aclanthology.org/2025.naacl-long.164/) | v1局部主文/§4–6与附录要点；原卡已有正式版范围 | probe→causal prediction→downstream QA，特征操作定义修订/修补 | 未对作者所有特征图与运行代码重做正式全版核查 |
| ABBEL [v2](https://arxiv.org/html/2512.20111v2) | 主文方法、full-context对照、reconstruction方程与结果；原卡记录此前附录/代码 | 在形成训练对象前诊断实际遗漏；posterior−prior而非简单正确性排序 | 未重新审全部附录/代码运行与训练结果 |

## 当前知识库的真实缺口（不被旧MAIN计数遮住）

**P0：会直接改变科学解释的**
1. **已补读核心主文** [Christianson et al. 2001](christianson2001-thematic-roles-linger.md)：本轮取得作者实验室正式40页PDF，核五实验方法/关键结果/讨论；其原文**已意识到语用推断并设计GP对照、反身RAT动词控制**。新的未完成项是逐素材/原始统计复核，而非‘只读摘要’。
2. [Huang & Ferreira 2021](https://doi.org/10.1016/j.jml.2021.104288)：如何条件化 RT 于正确/错误问答、哪个层次的语法“正确”却整体解释缺失？需要实读完整实验表与统计；目前作者摘要和二手比较不能解决与Slattery的张力。
3. [Ceháková et al. 2025](cehakova2025-disrupted-final-interpretations.md)：**2026-10-12已有后续阅读提交补足作者公开完整文章正文**，包括四种问句的语义、对照、回归量与各模型的替代解释；尚未运行Zenodo的stimuli/R脚本。与[Sturt 2007](sturt2007-semantic-persistence.md)的全文核对仍是阅读任务，不能混称两篇均已完成。
4. [Amouyal 2026](https://aclanthology.org/2026.acl-long.1040/) 的逐题数据、human vs LM设置以及更严格的 3-valued gold 重标；这是“问答是否测到修订”的核心压力。
5. [Hanna 2025](https://aclanthology.org/2025.naacl-long.164/) 最终版修订/repair操作细节和feature interventions的反向、无关因果控制；它比泛泛再读SAE综述紧迫。

**P1：为了形成更广但不跑偏的机制认知**
- [Clark 2026 targeted noisy-channel](clark2026-targeted-noisy-channel.md) 与 [Clarke2025](clark2025-resource-rational-noisy-channel.md)：改变输入信任/噪音先验可模拟“纠正失败”，与先前parse竞争究竟有什么可区分预测。
- [Madureira 2024 restart-incrementality](madureira2024-restart-incrementality.md)：区分反复重编码的双向编码器与原生因果生成器的因果单元，不机械迁移“旧token不能更新”的结论。
- [Storer & Zimmerman 2026](storer2026-incremental-contextual-trajectories.md)：已知critical-region classifier对数据拆分敏感，仍需查长附录与lexical holdout；RoBERTa重新编码的动态与因果LM不同。
- [Hu & Levy 2023](hu2023-metalinguistic-measurement.md)、[Hu & Frank 2024](hu-frank2024-task-demands.md)、[Hanna](hanna-2024-gp-mechanisms.md) 形成一个**测量→资源交互→因果使用**方法链；不要简单说“自报不可信、概率可信”。
- [Belief-R](wilie2024-belief-revision.md)、[ABBEL](lidayan2026-abbel.md)、[ReBel](tang2026-rebel.md)：比较“新输入否定旧前提”“内容更新奖励”“长期belief依赖”的训练目标，不能仅凭表面有belief字样直接归为同问题。

**P2/外围**：多智能体、视觉echo、广义RSI、长记忆存储、扩散模型remasking、3D空间等曾被用于启发和交叉；留存索引，可在某个具体假说需要时重新进入。它们不是本workbench的主研究史，不因为原卡多就自动获得优先级。

## 文献精读的新记录模板

每条写：canonical DOI/venue/日期与实读版本；精确阅读范围；作者科学问题（自己说的）；被默认接受的前提；两到三种竞争解释；每个实验之前仍缺什么、为何选该实验、预期正反结果；材料/样本单位/基线/指标/统计/成本；实际反证/局限/发布资产；距离最邻近工作的增量；我们的可迁移动作与**不该迁移的东西**；剩余阅读债务。将 AUTHOR-STATED、RECONSTRUCTED、OUR-HYPOTHESIS 显式分离。

深读不以“读了几篇”优化。若某研究问题重要且解释开放，可以沿经典论文、之后反驳、最新改进深挖；若最近邻已经解决特定问题，替换问题而不是靠重命名求创新。
## 新增经典谱系补记（本轮）
- [2001 原始五实验精读](christianson2001-thematic-roles-linger.md)：正式PDF主文；文献里最强的语用竞争解释排除动作。
- [2006 结构启动](vangompel2006-garden-path-priming.md)：本轮仅正式摘要/实验3相关节选，仍有主文实验数值欠账。[2009 复述](patson2009-paraphrase.md)：**后续独立阅读提交已经取得作者正式6页全文、完整Methods及Tables 1/2**，不再把它标为摘要-only；未复算原参与者数据。
- [Ceháková 2023 本轮补完](cehakova2023-diverse-reanalyses.md)：正式PLOS HTML Exp1–5、关键数值与错误类别，历史只读E1–3片段已补；OSF数据与R代码仍是欠账。
- [Maina-Kilaas 2026 修正](mainakilaas2026-digging-in.md)：Exp2是36项而不是历史误记24项；记录对照正交性与RT选择。

## 2026-10-12 新增全库相互矛盾记录的纠错

- [Christianson2001原卡](christianson2001-thematic-roles-linger.md)最初在表2/表3错误地把GP-implausible两列写成non-GP控制，已按原文改正；这改变对于“语用 vs GP超额”的可支持范围，不能只标TYP0。
- 知识库内163份根层Markdown+5份专题的本workbench相对文件链接经Git树全路径校验；不会把没有直接在本仓库树里找到的跨仓库/外部链接声称为已核真。完整限度见[本次校验](../audit/KNOWLEDGE_QA_2026-10-12.json)。

## 2026-10-12 审查后的阅读债务
- Hanna & Mueller 2025：作者 HTML 本轮抓取失败，沿用旧卡的 NAACL 正式版阅读记录；需再核 Appendix C faithfulness 与 §6 QA 的具体数字。
- Huang & Ferreira 2021：仍只有摘要；它是"全局解释是否完整"的关键人类证据，须取得主文。
- Emura & Sugawara ACL 2026、Oh & Demberg 2026、Steele 2026、Futrell 2019、Kim & Schuster 2023：仅摘要，见 abstract-only 卡；前两篇应升级为主文。
- Ceháková 2025：D0 只收了部分项且 Step-5 把若干双宾语/互指题标 NEITHER（见 results/REPLACEMENT_DEPENDENCY_COHORT_2026-10-12.json）；需对齐原材料与人类逐项数据。
- NeurIPS 2026 / ICLR 2026 新一期：未系统扫描"incremental interpretation / reanalysis / belief update"主题，下一轮先做。
