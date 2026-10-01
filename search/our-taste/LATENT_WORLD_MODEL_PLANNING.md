# Territory 卡：紧凑潜在世界模型与规划

日期：2026-10-02。通道：our-taste。状态：用户授权调查与登记；**PROPOSED，不替换现有 ACTIVE 线，不是 candidate。**

完整证据与论文编号：[系统调查](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md)。工作台：[latent-world-model-planning](../../workbench/latent-world-model-planning/README.md)。资源：[RESOURCES](../../RESOURCES.md)。

## 1. 领域，而不是预设现象

研究紧凑 world model 的表示、动作条件动力学和规划器如何共同支持可靠决策。入口是成熟开源系统的复现与建设；不指定必须出现“prediction 与 success 负相关”、某个 latent shortcut 或某种 verifier 失灵。

允许方法从建设中生长，也允许从强方法的成功反推哪些旧设计已不必要。科学问题不缩成“18M 模型刷一个小任务的分数”。

## 2. 热度与形态卡

- 宽主题页已有世界模型／视频生成接收统计，但不是本 territory 的密度，不复制成窄切片接收率。
- 近期直接近邻横跨表示训练、几何、逆动力学、生成式搜索和结构化 transition；调查已更新到 SALT（9/27）与 ATLAS（9/28）。这是活跃谱系，不是空白。
- 窄切片 `density / shapes / nearest`、最近接收与 near-miss 的完整名单**未运行／未齐备**；执行机补到定位表。不得以缺少统计表为理由禁止强基线建设，也不得声称本轮已满足完整 D5。
- 潜在论文形态：设计改进＋解释证据；失效边界＋修复；构念／识别方法＋受控验证。只有工程统一、已知现象复测或更多 seed，不自动成为科学贡献。

## 3. 谱系卡

1. DINO-WM／PLDM → LeWM → SMWM：冻结视觉表示、端到端不塌缩、动作相关信息。
2. Value-guided／Temporal Straightening → RC-aux／ATLAS：距离、局部曲率、有限预算、关系几何。
3. 多步 rollout／JEPA-WMs 配方分析 → SALT：训练分布与递归误差传播。
4. 终点成本搜索 → ACID／LeFlow／HWM：动作一致性、proposal、时间层级。
5. Offline goal learning → OGBench／SWM：覆盖、goal stitching 与可独立操纵的环境变因。

以上是论文关系的重建，不是作者创意过程的传记记录；各原文、阅读范围和已有 claim 见系统调查。

## 4. 立足点卡

- **首个可训练基线**：LeWM 官方代码／权重／配置；保留其原生环境，不先迁移到最新依赖。
- **公共工作台**：stable-worldmodel；复用 collect/train/evaluate、solver、环境变因。它不是我们的原创贡献。
- **异质表示参照**：JEPA-WMs 发布的 DINO-WM 与优化 JEPA-WM 小模型路径。不是一开始下载 DROID／ViT-G 全套。
- **直接后续参照**：RC-aux；根据分支接入修正后的 Temporal Straightening、SMWM、SALT、ACID 等，不要求全部同时跑。
- **非 world-model 对照**：OGBench 中匹配任务／数据的 GCBC 与一种合适的 value／hierarchical 方法。
- 目前是官方资产入口已核对，**本地训练、数据字节、权重完整性和性能未验证**。资产状态见 workbench/ASSETS.md。

## 5. 有出处的压力清单

| 压力 | 出处 | 首要研究动作 |
|---|---|---|
| 防塌缩不等于任务信息充分 | P03/P08/P12 | 真未来表示的任务读数与实规划对照 |
| 多步监督不保证单调改善 | P04/P06/P11 | 固定物理时间、训练预算、历史通道分别比较 |
| 内部 verifier 不等于外部可执行性 | P04/P09/P10 | 保存相同候选集并在可重置仿真中审计 |
| 示范时间差不是最短距离 | P04/P13 | 覆盖／轨迹连通与目标定义拆开 |
| “OOD”可能是不同实验对象 | P05/P12 | 外观、动力学、目标与历史变化分开 |
| 小模型仍可能 I/O-bound／evaluation-bound | P05 官方代码与存储 benchmark | 单任务预检后再增加并发 |
| 版本和配方会改 baseline 强度 | P07 UPDATES、P03 当前 config | 固定 commit、原生复现与统一协议分别记账 |

这些是文献压力，**不是我们已经跑出来的 P## 痛点或 L1 现象**。

## 6. 选择与容量

相邻候选包括 offline goal-conditioned RL、online reward-driven world models、大型视觉模型局部适配；它们作为对照／后续扩展保留，不各开一个 workbench。选中本 territory 的理由是可共享的训练、可重置环境、模型内部和决策接口，能用独立任务提高实验吞吐。

现有 ACTIVE-MAIN：video-world-model-temporal-interfaces；ACTIVE-EXPLORE：mechanism-population-dynamics。本轮仅登记 PROPOSED，不暂停任何一条。后续算力调度由人决定；一旦获准执行，本地 agent 按 HANDOFF 自主推进建设与测量，不需要对话 agent 逐轮审批实验。

目标会议：ICML／ICLR／NeurIPS，条件合适可考虑 CVPR；具体届次与截止日未确定，填“—”。
