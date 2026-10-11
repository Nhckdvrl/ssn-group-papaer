# 近期主会横向扫描：覆盖、可跟进领域与证据边界

日期：2026-10-03。服务于[领域选择](TERRITORY_SHORTLIST_2026-10-03.md)，不产生实验主张，不改变 workbench 状态。

**最终排序按用户后续纠正更新：** Sasano-first；视频移出首推。补查得到[情境理解与信息组织](CONTEXT_BINDING_TERRITORY_2026-10-03.md)、[概念与知识表征](CONCEPT_REPRESENTATION_TERRITORY_2026-10-03.md)、[主动证据与反馈学习](ACTIVE_INFORMATION_TERRITORY_2026-10-03.md)三个优先候选。下表保留第一轮横扫覆盖，不能按表中顺序当推荐排名。用户要求停止子agent后已全部停止，最后一轮由主agent独立检索、核代码与整合。

## 1. 实际看到了什么

- 仓库对齐：README、workbench 登记表、RESOURCES、search 当前规则、Sasano taste、两条 ACTIVE 的状态/claims/pain/log，以及相关旧协作、NPC、RSI 资产。不是逐个重读所有历史 rollout。
- 本地 venue corpus 共 **65,716 条记录**，覆盖 2024–2026 多个主会；ICLR 含拒稿和撤稿，其他多为接收列表。分别执行领域 `density`、`nearest`、`shapes`。它们用于定位；摘要关键词比例不能说明审稿因果，接收名单不能算接收率。
- [PaperNotes](https://papernotes.org/)作广泛导航，核到多个 2026 会议入口，但其 NeurIPS 入口当时仍是 2025；不能把聚合页当最新接受状态。
- [NeurIPS2026 官方 Downloads](https://neurips.cc/Downloads/2026)已公开。本轮解析得到 **9,230 条 event**，包含非 main 内容，不能称“9,230 篇主会论文”。标题扫描后按主题回论文、作者站、代码核验；没有逐篇读完全部列表。
- 官方目录本地快照：`tools/venue_corpus/data/neurips2026_directory_2026-10-03.json`（git-ignore）。原 HTML 临时留在 `/tmp/sasano-search-20261003/`。新目录尚未混入旧 corpus；单篇 poster 页面与 OpenReview 接口本轮出现 403，分轨仍需补验。PaperCopilot 的 `nips2026.json` 当时返回 404。
- 追加读取领域 awesome 与 DailyArXiv，再回原论文校正。镜像有补录/窗口截断，不能据当前快照推全领域 arXiv 月增长率；详细入口与条目数见[互动 memo](INTERACTION_TERRITORIES_2026-10-03.md)。
- Slack 是八个公开 `r_人名` 频道的定向检索及 thread 复核，不是全工作区穷尽；见[证据备忘](SASANO_EVIDENCE_2026-10-03.md)。没有发消息。

标题正则的可复核结果：

| 对官方 event 标题的正则（忽略大小写） | 命中 |
|---|---:|
| `on.policy.{0,8}distill|\bOPD\b|OPSD` | 25 |
| `recursive self|self.improv|self.evolv` | 40 |
| `common ground|convention|communication repair|clarification` | 4 |
| `partner|ad.hoc team|human.ai co|cross.play` | 9 |
| `human.*(disagreement|judg|variation)|label variation|pluralis` | 6 |

这些是不同召回率、不同误报率的检索式，**不能按 4 对 25 推“冷六倍”**。其中含 workshop/非目标命中，需人工筛选。它们只支持近期 OPD 等已经有密集具名工作、值得细查 ownership；不支持任何领域的投稿概率。

## 2. 超出最初偏好的横向发现

| 领域：研究的真实对象 | 主源与本轮阅读深度 | 为什么值得 follow / 当前不作为首入口的原因 |
|---|---|---|
| 人类视觉相似性、抽象层次与模型表征 | DreamSim/NIGHTS、AligNet、BGS；全文关键实验及仓库，见[视觉 memo](JUDGMENT_VIDEO_TERRITORIES_2026-10-03.md) | 保留跨DL参考；有现成人票和冻结模型。BGS视频许可与依赖未全开，不能拿它作立即可跑承诺 |
| 共同任务中的沟通与伙伴适应 | Collab-Overcooked、LVLMs and Humans、Success+Cost、ZSC-Eval；全文/代码，见[互动 memo](INTERACTION_TERRITORIES_2026-10-03.md) | 最终保留第四备选；实际任务后果明确，语言作为协调手段 |
| 主动探索与证据收集 | [Reasoning aligns language models to human cognition](https://arxiv.org/html/2602.08693v1)，正文/任务/拟合与部分附录；LLF-Bench仓库 | 接近用户 reasoning 兴趣，先研究选择信息的行为。最新人类数据/代码的Drive资产尚未核实，不把目录题名等同最终论文版本 |
| 人在AI协助下的认知工作分配 | [Offloading Score](https://arxiv.org/abs/2605.29392)、[Path Dependence under Adaptive AI Delegation](https://arxiv.org/abs/2603.02950)；摘要/方法入口 | 问题自然且不靠训练大模型；关键资源是真人纵向数据，卡多不直接解决。目录收录不等于已核 main |
| 生成模型的默认审美与风格 | [LouvreSAE](https://louvresae.github.io/)，项目与HF模型集；完整论文未得 | 适合图像/游戏素材兴趣；26生成器的默认审美已有直接研究，Paper/Code占位、数据未验证，不能立即展开原基线复现 |
| 模型个体性与自我能力判断 | [Individuated Metacognition](https://arxiv.org/abs/2605.24299)全文；[Feedback Forensics](https://github.com/rdnfn/feedback-forensics)仓库 | 可连接伙伴适应；前者大量API和缓存未核，后者有预标注资产。不要重复“自信不代表真实个人能力”的既有结论 |
| 视觉组合与检索评测效度 | [CIRCUS](https://arxiv.org/html/2605.14787v1)，正文及方法/实验 | 从真实检索失败审计到人的有效性审核，是研究动作范例；单模态捷径已经被系统研究，且组合视觉邻域不算冷门 |
| 创造力测量与科学创意 | [Semantic Distance Tests](https://schapiro.ai/creative-ai-index/paper/)，作者摘要/研究设计；全文版本状态不一致 | 先验证测量是否预测真正创造性，符合taste；高质量人评仍是瓶颈，不能只用另一个LLM评分器造自动闭环 |
| 模型损伤与认知功能 | [Artificial Aphasias](https://arxiv.org/html/2605.16222v1)，正文及部分附录 | 约1B模型的干预说明不必训大模型才能做认知分析；临床效度和语言评估要求高，题材也不如游戏/视觉符合当前偏好 |

后五类是横向跟进线索，不冒充完成四卡的 workbench 提案。没有为了凑数量扩展时间序列、图算法，也没有以 EACL 作依据。

## 3. OPD / RSI：可以做研究，但为何本轮不排在前面

[Rethinking OPD I](https://arxiv.org/html/2604.13016v2)、[II: One Training Example](https://arxiv.org/html/2609.04172v1)和[EOS Disagreement](https://arxiv.org/html/2609.20511v1)均定向读正文、实验和关键附录，详见[论文卡](../../library/themes/reasoning-test-time/EXPLORATION_AND_OPD_PAPER_CARDS_2026-10-03.md)。

- **资源不是一票否决。** 1.5B级学生、已有教师、单节点小训练，确实允许高校做机制和实现失效分析。不能说“大公司才能研究OPD”。
- **探索周期仍有训练闭环。** One Training Example是一个输入反复采样、接收教师密集监督，仍有数百至千步更新；不是一个标签、零训练、零数据成本。离线看logit可筛查，动态主张还得跑训练。
- **自然问题已有直接 ownership。** 更强教师不一定更可蒸馏、少输入仍能覆盖许多状态、EOS语义失配引发长度膨胀都已研究。仅把这些现象再测到另一小模型不足以形成清楚增量。
- **值得学的研究动作：** 从标准基线不稳定 → 分开解码规则与训练目标 → 针对两者做干预。一个实现细节只有改变科学解释或实际后果，才成为论文对象。
- **RSI保持现有仓库分工。** 仓库已有 `data-centric-rsi` 内容与实验记录，不能重复造线，也不能沿用旧索引的“GPU=0”描述它。当前人审未要求改变任何状态。

结论是按本轮“快测量、少训练、自然对象”的偏好降低优先级，**不是关闭领域**。若用户最终更想研究学习动力学，可从现有资产另做范围与预算评审。

## 4. 阅读强度和缺口

论文卡明确区分全文定向阅读、摘要和代码/README；“全文”不意味着逐格重算论文全部数字。没有实际复现任何作者结果。论文的灵感来源分 DOCUMENTED（作者陈述）与 RECONSTRUCTED（我们的谱系重建），后者不写成作者私人经历。

互动领域列了12个主会校准与5个历史near-miss；视觉memo列10个跨相邻领域校准，但**每一个细领域的10接收+5高分拒稿并未全部满足**。评审原文未取得时，不从分数编造拒稿原因。它们足够支持此轮“选哪片领域继续看”的比较，正式workbench交接仍需补齐候选本身的基线复现、完整定位和主会证据形态。
