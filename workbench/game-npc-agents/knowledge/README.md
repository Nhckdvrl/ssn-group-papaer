# Game NPC Agents · 独立科学知识库

**这是 workbench 内的活知识库，不是全局 `library/` 的复制品。2026-10-14 用户明确要求纠正连续两次过窄收缩。** 历史角色训练/目标控制笔记继续保留，但不是本项目唯一目标。

## 必须首先建立的领域整体认知
| 内容 | 文件 |
|---|---|
| 全景（8 个板块，不冻结新题） | [DOMAIN_ATLAS.md](DOMAIN_ATLAS.md) |
| 游戏 NPC 被攻击、信任边界与安全效度 | [NPC_SECURITY.md](NPC_SECURITY.md) |
| 游戏多 Agent 经济、市场攻击、机构与激励 | [GAME_ECONOMY.md](GAME_ECONOMY.md) |
| 正常人格成长 vs 失控漂移/攻击 | [PERSONA_DRIFT.md](PERSONA_DRIFT.md) |
| 最新文献身份与**本轮实际阅读等级** | [SOURCES_AND_STATUS_2026-10-14.md](SOURCES_AND_STATUS_2026-10-14.md) |
| 过去已核实论文主张与不能冒领的增量 | [POSITIONING.md](POSITIONING.md) |
| 下一批应深读/核代码的资产，按重要认知缺口优先 | [READING_QUEUE.md](READING_QUEUE.md) |
| 现有 2026 原生训练线文献 / 训练想法 | [NATIVE_GAME_NPC_FRONTIER.md](NATIVE_GAME_NPC_FRONTIER.md)、[METHOD_TERRITORIES.md](METHOD_TERRITORIES.md) |
| 历史目标控制/角色逻辑/训练研究及旧初筛 | [GOAL_CONTROL_REVIEW.md](GOAL_CONTROL_REVIEW.md)、[CORE_NOTES.md](CORE_NOTES.md)、[PAPER_LEDGER.md](PAPER_LEDGER.md)、[papers/](papers/) |
| 数据与测量原则 | [MEASUREMENT.md](MEASUREMENT.md) |

## 四种不同的认识，不许混
- **已核实的文献事实**：带会议/版本/数据/代码来源和真实阅读范围。
- **作者已有的贡献/推断**：只能说作者报告，不能变成我们的 claim。
- **我们的推测/质疑**：写成可证伪 hypothesis，明确最强替代解释。
- **我们的新观察**：只有有完整代码版本、运行输入、结果文件、统计与独立审计的 E## 才能支撑。

阅读等级 P0标题/来源；P1摘要；P2特定原文段/源码；P3正文和关键附录/实码系统精读；P4本地可复算。更新 source 时写阅读时间和实码范围，不因笔记写了几千字自升级 P3。原先的历史初筛不等于本轮完成全部 P3。

## 防止过窄与肤浅
不能再把“目标/旧计划”、“共享PPO”、“Prompt注入导致拒绝”、“Sybil攻击”先选为固定 story，再通过搜论文给自己壮胆。先研究各领域重要已有论证、哪些正常游戏行为不应该被归为攻击、哪些量真正预测自然世界后果，再把高信息量问题交给实验。允许只完成部分分支深入，但全局地图应维持。
