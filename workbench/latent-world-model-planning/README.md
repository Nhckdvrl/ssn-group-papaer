# Latent World Model Planning — 紧凑世界模型的表示、动力学与决策可靠性

## 状态（中文进度页）

**状态：PROPOSED。** 用户已授权系统调查和直接登记；没有启动 GPU 实验，没有更改现有 ACTIVE 主线／探索线。不是 candidate，不预设论文标题、失败现象或修复方法。

**territory 卡：** [搜索登记](../../search/our-taste/LATENT_WORLD_MODEL_PLANNING.md)  
**目标会议／截稿：** ICML／ICLR／NeurIPS；视觉贡献合适时考虑 CVPR；届次与截稿日待定。  
**上次驻留人审：** 尚未进行。  
**更新：** 2026-10-02。

**一句话：** 在可训练的小型潜在世界模型和可重置仿真环境上，建设共享的训练、预测、候选评分与实际控制评测接口，让研究从强基线建设、系统测量及方法对照中生长。

## 入口

- [系统调查、谱系与论文卡](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md)：18 个来源条目（含综述／导航级材料），逐条标阅读范围；近期直接近邻更新到 2026-09-28。
- [ASSETS](ASSETS.md)：官方代码、3 个精确 commit 快照、数据／权重入口、配方和 API 风险；公开可用不等于已经本地验证。
- [HANDOFF](HANDOFF.md)：给本地 agent 的建设顺序、最小测量合约、多分支探索和自主执行范围。
- [RESOURCES](../../RESOURCES.md)：用户确认的多卡、弱互联／弱 I/O 条件；独立实验优先，不限制科学问题的重要性。

## 为什么是 workbench，而不是 RC-aux 的一个改进点

共享底座是 LeWM 的原生复现路径＋stable-worldmodel 的公共接口；强异质参照包括官方 JEPA-WMs／DINO-WM，按需加入 RC-aux、Temporal Straightening、SMWM、SALT、ACID 等。数据与非 WM 参照来自 OGBench。

保留五类可复用研究动作：表示与任务信息；递归动力学；候选产生／评分；数据覆盖与目标组合；历史与分布变化。第一条解释不成立，不用重建整套实验，也不应不停给同一叙事加条件。

“预测好不等于规划好”、曲率校正、有限预算可达性、inverse consistency、生成式候选、state-affine transition 都已有直接近邻。它们是 baseline／定位压力，不是我们的新颖性主张。

## 与已有工作的边界

现有 `video-world-model-temporal-interfaces` 是交互视频生成的时间／控制接口主线；本目录研究紧凑 latent dynamics 与 goal-conditioned planning，不接管其模型、实验编号或机制结论。

现有 `mechanism-population-dynamics` 仍是 ACTIVE-EXPLORE。登记本目录不意味着自动启用第三条 ACTIVE 线；调度由人决定。

## 论文形态卡（初稿，不是已成立稿件）

- 当前主旨：尚未形成；先建设能比较不同表示／动力学／planner 假设的实验平台。
- 可能形态：设计改进＋解释性实验；失败边界＋修复；识别／测量方法＋真实任务后果。
- manuscript-critical contributions：尚无；不能把复现工程、已知负相关或新增 seed 单独算贡献。
- 证据目标：先可信 native baseline，再共同协议；训练 seed 与评测随机性分开；任务成功、计算成本、标准测量和受控干预共同支撑范围。
- 近邻与 compression risk：见调查 §3；尤其 JEPA-WMs、RC-aux、Temporal Straightening、SALT、ATLAS。
- 风险：代码／配置漂移；图像 I/O；CEM 评测成本；实验语义不一致；用廉价 toy 结果替代真实控制后果。
- 本次决定：按用户要求登记 PROPOSED，不自动激活或关闭其他领域。

## 驻留交付状态

| 项目 | 本轮状态 |
|---|---|
| D1 强基线复现 | 未运行；E00 是预检计划，不是完成证明 |
| D2 可复用资产 | 官方入口与代码快照已核对；本地环境／数据／脚本待建设 |
| D3 痛点日志 | 已初始化；只有来源明确的风险 R01–R05，没有伪造实测 P## |
| D4 系统测量 | 合约与建议接口已写；未产生结果 |
| D5 定位 | 核心谱系、近期近邻和阅读范围已登记；完整 venue-corpus／near-miss 清单待补 |
| D6 形态与 idea | 形态范围和压力组合已写；不把预设现象包装成成熟 idea |

## Idea 组合

正式 I## 尚未产生。调查中的分支是 SEED 级探索入口，不是承诺结果；本地 agent 可依据文献对照与实际 P##／E## 生成可执行 idea，无须等对话 agent 逐轮批准。

## 主张摘要

[CLAIMS](CLAIMS.md)：C00 为 L0 的建设可行性主张。科学主张为零；本轮没有训练曲线、success rate 或机制证据。

## 痛点摘要

[PAIN_LOG](PAIN_LOG.md)：记录官方来源暴露的兼容性／协议／语义风险。实测日志保持空白，等待执行。

## 决策记录

- 2026-10-02：用户明确要求记住资源、系统调查并直接注册。登记此 territory；仅注册，不修改其他工作线状态。
- 不将“模型小”推导成“任何卡都轻松跑／训练固定几小时”。先实测端到端资源；不依赖多节点训练。
- 已授权注册不是驻留结果的人审签字。后续启用算力与研究线状态仍由人决定。

## 资产位置

研究笔记与实验卡在本仓库；源代码链接和 pin 见 ASSETS。大数据、权重、视频和 raw rollout 不进 git；当前没有本会话创建的训练资产。

**首个执行入口：** [E00 原生闭环与资源预检](experiments/E00_native_baseline_and_resource_preflight.md)。按 HANDOFF 接续既有资产，不从零重做无关工作。
