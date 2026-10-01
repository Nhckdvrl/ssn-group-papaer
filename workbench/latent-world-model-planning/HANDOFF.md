# 给本地 agent：从强基线建设中探索，不证明预设结论

## 0. 任务与授权

用户要求寻找并登记适合独立单卡／单节点实验的 workbench。本目录目前 **PROPOSED**；已有主线和探索线不变，不能自行抢占其算力或改变状态。用户分配执行资源后，按本文自主推进，不需要等待对话 agent 逐轮替你选实验。真正改变研究线状态和论文方向的决策按仓库人审规则进行。

**本任务不是复现 RC-aux 后再加一项 loss。** 任务是建设一个可以反复研究表示、动力学、数据与决策接口的平台；从运行中的成功、困难和系统测量生成 idea，允许方法与理解相互推动。

先读：根目录 `AGENTS.md`、`RESOURCES.md`、workbench 登记表、本目录 README/CLAIMS/PAIN_LOG、ASSETS、[系统调查](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md)。检查当前机器已有 repo、数据、模型和旧实验，复用能核对来源的资产；不要假定这里已下载任何东西，也不要删除或重做已有视频主线实验。

## 1. 先建立两个记录层，不急着迁移全部代码

**原生复现层：** 每个官方 repo 固定 commit、环境、checkpoint、任务配置与官方目标生成规则，分别复现。环境可以独立，避免统一依赖引入新 bug。

**公共比较层：** 只统一任务清单、观测／动作／时间约定、评测结果和必要测量接口。等原生结果可信后才进行适配；适配前后在相同输入上做等价检查。stable-worldmodel 是优先复用的底座，不是必须先重写所有 baseline 的理由。

所有运行写 resolved config。原生论文行、当前官方修正版、我们统一的比较协议必须是不同 experiment ID，不能混表后称为公平复现。

## 2. 建设顺序（由证据触发，不按日程）

### B0：执行 E00，确认一个最小闭环和真实成本

先选 LeWM 的 TwoRoom 或其他已在该节点可用的小任务，验证数据读取、checkpoint、环境、动作尺度和成功判定。TwoRoom 用于工程闭环，不把高成功率／天花板当成科学发现。

核对 `ASSETS.md` 的版本风险；先 1 张卡、低环境并发。记录 I/O、CPU、显存、训练 step 和完整 episode 耗时。先少量训练步验证梯度和 checkpoint；这不等于数值复现。不要启动默认 100 epochs，更不要把 `devices:auto` 交给多卡节点自行决定。

**通过：** 实环境完成 observation→encode→plan→act→success 闭环，数据／动作／目标可追溯，成本可测。
**失败：** 区分版本、加载、renderer、数据和模型问题；保存复现命令。可以改用同领域另一成熟实现，不据此宣布科学问题不存在。

### B1：可靠 baseline，而不是扩大方法组合

先把一个 LeWM 原生结果复现到可解释的水平，再增加一个含接触的任务（优先 PushT，前提是数据 I/O 可承受）。公开 pretrained checkpoint 的复现和重新训练的复现分开。

为了区分家族效应，接入一个冻结视觉特征参照：优先 JEPA-WMs 官方发布的小模型路径／DINO-WM，或已可用的 PLDM。RC-aux 是首个直接 successor，不是唯一世界模型。接入哪一个由现有资产、协议和测量需要决定。

先对齐官方 evaluation seeds/groups，再运行独立训练种子；默认至少 3 个训练种子作为初始方差估计，但样本量由任务效应和测量精度决定。不能把 3 个 evaluation seeds 写成 3 次训练。

首次完整训练前，用 B0 实测速率估算成本，把训练次数、评测次数、真实环境步和数据读量列出来。不要先发出“模型×任务×种子×horizon×数据比例”的全笛卡尔积。

### B2：把标准测量建成共享资产

按 §3/§4 保存接口和结果。先观察标准任务及合理变因，不通过构造大量特殊条件“找一个总会失败的点”。成功模式、方法之间的一致性、很便宜的基线已经解决问题，都要记录。

不同模型／数据／训练 checkpoint 的比较，优先复用相同任务清单与候选动作池。一个训练产物可派生多组 planner 评测，避免每个问题都重新训练。

### B3：从测量与近邻分歧生成研究动作

有实际 P##／E## 后，用仓库模板生成 idea 卡。可选研究动作：重设计表示或 transition；改变训练分布；改 proposal／score；提取可验证的任务充分性条件；建立具有真实后果的测量方法。

允许在驻留开始就实现有出处的方法对照，不要求先有惊人的 anomaly。每次 intervention 必须能改变一个明确决策，不是机械叠加模块。

如果某条解释被否定，保留平台，在同一领域转到其他压力；如果两个连续 lead 被平凡对照或直接近邻吸收，停止继续加限定条件，回看完整压力地图。不要不断从头换领域，也不要在同一个局部 trick 上无止境调参。

## 3. 最小评测合约

每条 episode／run 至少保存以下字段：

```text
code_commit, dependency_lock, hardware_id, model_family, checkpoint_sha256
train_seed, data_split_seed, eval_seed, planner_seed
train_dataset_revision, train_episode_ids_hash, eval_manifest_hash
observation_keys, image_preprocessing, action_units, action_bounds
history_length, frame_skip, action_block, planning_horizon
replanning_interval, max_environment_steps, goal_source, success_checker
planner_type, samples, iterations, cost_reduction, auxiliary_weights
success, task_native_distance_if_available, env_steps
wall_clock, model_cost_calls, peak_vram, data_wait, failure_reason
```

- 先按 episode 拆 train/validation/test，再切时间窗口；禁止滑窗跨 split、train/val 共享轨迹泄漏。
- `goal_source` 至少区别同轨迹未来、跨轨迹目标、任务预设目标；不能混成一个“泛化”读数。
- 单位先换算到真实环境步；改变 latent horizon、action block 或重规划周期，不一定是相同控制预算。
- hyperparameter 选在 validation；test seeds、任务列表和成功阈值固定。失败 seed、解析失败、checkpoint 无法加载不能静默丢弃。
- 模型间不能直接比较未经解释的 latent MSE 数值。优先报告模型内归一化读数、共同候选的排序、环境成功和任务原生距离。
- 成功率既给配对任务结果，也把训练种子方差单独报告；不要只给 pooled episodes 的窄误差棒。

## 4. 将“预测、评分、选择、执行”真正拆开

以下是建议建设的**测量接口，不是原创 claim**。

### 4.1 同一候选动作的三种读数

对固定初始状态、目标与动作序列 a，分别得到：

1. 实环境执行后的任务原生 utility／成功（U_env；有合法定义时使用）。
2. 编码真实终点后与目标的 latent cost（C_real_latent）。
3. world model 预测终点与目标的 latent cost（C_pred_latent）。

`2 vs 3` 检查动力学误差对打分的影响；`1 vs 2` 检查表示／目标成本与真实任务的联系；三者不能只靠 prediction MSE 合并解释。

仿真反事实执行前，先验证 save/restore 或 reset/replay 对相同动作能重现结果，包括环境 RNG、隐藏状态和 action wrapper。不能可靠恢复状态时，这个接口标为未验证，禁止把结果叫 oracle。

### 4.2 同一候选集合的选择

保存随机候选、优化过程中的候选、最后选中候选及其来源。先在**固定池**中比 score，再在相同预算下比 proposal/search。不要拿两个不同 CEM 阶段、不同动作集上的最低成本差，直接当作同一动作的预测误差。

若 U_env 有明确可比较的定义，可计算：

`candidate-set regret = max_a U_env(a) - U_env(a_selected)`。

这是所审计候选池中的 regret，不是全动作空间最优差距；部分候选未执行就不能声称得到精确值。不同任务的 utility 单位不同，不强行平均。

### 4.3 真正的 end-to-end consequence

最终仍要回到官方成功判定和闭环任务结果。planner 的更低内部成本、好看的 latent 几何、inverse consistency、probe accuracy 都不能替代它。

计算匹配至少包含两种可行比较：相同候选／model-call 预算和相同 wall-clock 预算。额外训练 verifier 的成本另记。既不把慢方法强行用相同候选数“公平化”，也不把更快模型多搜索的收益伪装成纯表示收益。

## 5. 多分支，但只有一个工作台

| 分支 | 触发它的真实材料 | 可采取的第一研究动作 | 必须阅读／对照 |
|---|---|---|---|
| 表示信息与目标 | 真未来编码也不能稳定排序，或某类任务信息被丢弃／被成功保留 | 对照 encoder 表示层、目标头、冻结/联合训练及特权状态诊断 | LeWM、SMWM、ATLAS；probe 不等于因果解释 |
| 动力学递归 | 编码真实未来可排序，预测 rollout 排序失真 | 匹配历史／物理时间；多步训练和结构化 transition 对照 | JEPA-WMs、RC-aux、SALT |
| 搜索与验证 | 固定候选能选对，生成/优化候选后实执行变化 | 固定池 reranking、proposal 切换、外部执行审计 | ACID、LeFlow；不只改名 inverse head |
| 数据与组合 | 方法差异随目标来源／覆盖结构变化 | 控制样本量而改变轨迹连通；WM 与 value/BC 参照 | OGBench、RC-aux 标签限定 |
| 历史／分布变化 | 在标准环境参数或可见历史改变时出现有结构的差异 | 外观、物理、历史分别操纵，再训练或适配 | SWM FoV、SMWM、上下文相关近邻 |

以上触发是选择实验的例子，不是模型必须失败的方向。若出现强 baseline 意外地好、简单配方稳定有效，同样可以成为研究动作起点。

## 6. 有限资源下广泛实验的组织

训练 job 产出固定 checkpoint；评测 job 读取只读 checkpoint 和数据，各卡独立运行。跨节点只交换小配置、指标与 artifact manifest，不进行梯度通信。各地点的数据与授权分开。

优先选能区分解释的少量正交干预，再扩大任务／训练 seed 验证；不要为了“卡多”同时放大所有轴。特征缓存只用于冻结 encoder 和固定预处理；压缩格式的解码差异先审计。记录同节点并发退化，避免把 I/O 饥饿误诊为模型或 GPU 问题。

## 7. 交付与自主推进边界

每次执行前生成实验卡，之后更新 CLAIMS、PAIN_LOG、日志与资产实际状态。D1–D6 按总仓库标准逐步完成，不事后把计划写成结果。

本地 agent 的目标不是“按本文所有格子跑完”。目标是尽快建成可信、可复用的强基线和测量接口，然后提出最有解释力的下一组比较。可以调整实施顺序、替换接入失败的 baseline、提出方法；必须写明证据与成本，不能擅自改变 ACTIVE 容量或发表未经支持的结论。

完成 baseline 和第一轮标准 measurement 后，输出：哪些东西已经可信、哪些仍是实现问题、有哪些有来源的研究动作、各动作最便宜的决定性实验、哪些近邻会影响其增量。不是只输出“成功率提高了多少”，也不是把需要进一步探索的内容全部交回给用户猜。
