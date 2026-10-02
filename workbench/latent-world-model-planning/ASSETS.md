# 资产、版本和资源账本

更新：2026-10-02。全局资源边界见 [RESOURCES](../../RESOURCES.md)。状态必须区分：论文描述、官方代码／下载入口存在、已下载验哈希、已加载、已跑通、数值复现。本轮只完成前两级；未下载大数据或权重，未进行 GPU 运行。

## 1. 已读取的官方入口与代码快照

下面的 commit 是本轮从 GitHub ref 读取的快照，**不是已证明彼此兼容的依赖锁文件**。先保存每个原生系统的运行环境，不能把三者强行装到一个最新环境。

| 角色 | 仓库与固定 commit | 本轮核对 | 首次执行还需确认 |
|---|---|---|---|
| 端到端小模型 | [lucas-maes/le-wm](https://github.com/lucas-maes/le-wm/tree/8edfeb336732b5f3ce7b8b210d0ba370a09e2cac) | README；`config/train/lewm.yaml` | 训练脚本、依赖版本、各 task override、权重转换 |
| 公共环境／planner 平台 | [galilai-group/stable-worldmodel](https://github.com/galilai-group/stable-worldmodel/tree/63988116d34cde56aea1240d5e58eb158ac67dc0) | README、paper；接口／格式／solver 说明 | 选择历史兼容版或该快照的参考实现；执行确认 |
| 直接 successor | [Guang000/RC-aux](https://github.com/Guang000/RC-aux/tree/cbdf3786b149df8145d6c7314f32f460d43c9695) | README；`config/train/rcaux_default.yaml` | 配置继承、逐任务 checkpoint、训练／规划权重对应 |
| 强冻结特征参照 | [facebookresearch/jepa-wms](https://github.com/facebookresearch/jepa-wms) | README 的小模型／数据／权重与安装表 | 首次接入固定 commit 和 HF revision；不要自动取大型分支 |
| 几何方法 | [temporal-straightening](https://github.com/agentic-learning-ai-lab/temporal-straightening) | README 与 [UPDATES](https://github.com/agentic-learning-ai-lab/temporal-straightening/blob/main/UPDATES.md) | 固定包含修复的版本、适配 encoder 和官方 validation/test 规则 |
| 数据／非 WM 对照 | [seohongpark/ogbench](https://github.com/seohongpark/ogbench/tree/1d4140997f60c52c6fb0702ec100dc988b18c548) | README、六种 reference algorithms、环境/数据生成脚本；**pin `1d414099...`** | JAX环境独立；M3优先复用 locomaze/manipspace generator，而不是另造数据框架 |
| M3 temporal-semantics baseline | [HKBU-KnowComp/Temporal-Distance-JEPA](https://github.com/HKBU-KnowComp/Temporal-Distance-JEPA/tree/b4c17ca4649c9bf47272fa66c38da7a684f2a020) | README、training/eval config、locked manifests；repo 自带 LeWM/RC-aux variants | **M3首轮优先复用**；固定 commit `b4c17ca...`；E14改真实 generating behavior policy，不复活旧 episode-factorization E03 |
| path-aware 近邻 | [XiaodiHuang-code/Traj_LeWM](https://github.com/XiaodiHuang-code/Traj_LeWM/tree/67577fa27242f6e888f40e399ab3e1b542b1367f) | source-only README、训练/评测入口、LTC calibration | 不首轮安装；I01 扩展 full-path supervision 时再接 |
| physical-grounding 近邻 | [Haodong-Yan/PSG-JEPA](https://github.com/Haodong-Yan/PSG-JEPA/tree/3bf67a47a9143f9f4fb4d39f839143c92902714c) | OGBench planning + LIBERO policy 两 track；依赖说明 | privileged grounding baseline，只有 representation/grounding lead 才接 |
| adaptive-capacity 近邻 | [arm-research/AAIR-ALeWM](https://github.com/arm-research/AAIR-ALeWM/tree/6717193bdc3b92e43f581b3c668ca9b82c299c70) | 本轮核对为 project-page release | **不是 code-ready baseline**；不能看到 repo 就假定 research code 已发布 |
| heavy visual-WM anchor | [kdwonn/CompACT](https://github.com/kdwonn/CompACT/tree/71b3029910d7460c5fa8658e17ab34e29c2c880c) | official CVPR code / training README | paper-scale tokenizer/WM 默认多 GPU；不作为 compact workbench 首轮训练 baseline |
| protocol/interface diagnostic | [24GUNV/LeWMRO](https://github.com/24GUNV/LeWMRO/tree/faff2ea4768767739b9cca55855dc5aacf13578f) | ICML'26 Workshop Oral code、terminal/prefix/running costs、receding-horizon eval、deceptive envs、tests、results manifest | **E06 protocol gate 可直接复用**；datasets/checkpoints 不在 repo，不能假定开箱即跑 |

Temporal Straightening 的 global-projector 修复 commit：[64a7585819e749bfec327ad984ee08570d07f0eb](https://github.com/agentic-learning-ai-lab/temporal-straightening/commit/64a7585819e749bfec327ad984ee08570d07f0eb)。这是已核对的修复标识，不能自动当成包含全部后续更改的最终锁点。

## 1.1 首轮最省工程的路线

### M3 / E14
优先从 **Bai/Xiong Temporal-Distance JEPA official repo** 起步：
- 已基于 stable-worldmodel/stable-pretraining；
- 同 repo 有 LeWM / RC-aux variants；
- Push-T / TwoRoom / Reacher / OGB-Cube 同代码布局；
- locked eval manifests 与 plan-seed结果已在 repo。

但新科学 treatment **不是**旧 I01 的 trajectory metadata 重切，而是：
- 真实改变 behavior policy；
- objective 实际看到不同 temporal pairs/gaps；
- support/coverage单独审计；
- fixed candidate / closed-loop 做 load-bearing readout。

公开 OGBench generator作为 discovery source，clean matched DIRECT/DETOUR intervention仍需在执行机按 E14 设计生成。

### M2 / E13
Bagatella TD-JEPA official repo与 OGBench / pixels 有成熟入口，适合 implicit-side native baseline；explicit-side优先用同 OGBench Cube family 的 LeWM/stable-worldmodel 路径。

**不要先强行统一训练代码。** 先保留 native protocol，建立 common task/data/result audit。

### M1 / E11
不需要先安装 belief模型。先用 simulator hidden-state reset / candidate oracle判断 finite-history 后是否仍存在 actionable ambiguity；过 gate 后再接 UWM-JEPA/FIRM/Branch-JEPA。

## 2. 公开数据／权重入口

- LeWM：[官方 collection](https://huggingface.co/collections/quentinll/lewm)；README 列出 `quentinll/lewm-pusht`、`lewm-cube`、`lewm-tworooms`、`lewm-reacher`。HF 的 state_dict/config 与旧 `_object.ckpt` 加载方式不同。完整 baseline suite 另有作者 Drive 入口，但本轮未下载。
- RC-aux：[官方 HF 发布](https://huggingface.co/biubiu116/RC-aux)。README 展示 TwoRoom 的使用例；**不能据此声称所有任务 checkpoint 已验证齐全**。
- JEPA-WMs：[模型](https://huggingface.co/facebook/jepa-wms)、[数据](https://huggingface.co/datasets/facebook/jepa-wms)。优先审计 Push-T／Wall／PointMaze 的小 encoder 路径；可视化 decoder 是可选组件，不是规划前置条件。
- OGBench：官方 `ogbench.make_env_and_datasets` 会按指定 dataset 下载；`env_only=True` 可只创建环境。不要为预检调用一个会自动下载全部数据的通配命令。

所有大文件只在授权机器的数据目录。新增实际资产时写入：URL、revision、SHA256、字节数、许可证、数据 split、预处理、节点缓存位置、可访问地点；不要把具体内部主机名／内部路径提交到公开仓库。

## 3. 必须处理的协议漂移

### 3.1 LeWM 默认配置不等于论文配方

本轮固定快照的 `config/train/lewm.yaml` 包含：224 输入、batch 128、bf16、history 3、workers 6、prefetch 3、`max_epochs: 100`、`devices: auto`。原论文附录中的部分实验配方并不是这个 100-epoch 默认值。

所以先导出 Hydra **完整 resolved config**，核对任务覆盖项和论文协议；不要照 README 一行命令就开始长训练。单卡任务显式限制 `CUDA_VISIBLE_DEVICES`／devices，避免 `auto` 意外占满节点。

### 3.2 平台 API 和 cache path

原 LeWM README 使用 `AutoCostModel` 和旧 checkpoint 约定；当前 stable-worldmodel README 使用 `WorldModelPolicy`／`PlanConfig`／`CEMSolver`，并明确说 API 仍在变化。两份 README 的默认缓存路径也不同。

始终显式设置 `STABLEWM_HOME`。先建立原生可复现环境，再抽取最小适配接口；不要把“统一平台”误解成必须先完成全仓库 migration。

### 3.3 RC-aux 训练、示例与论文行

- `rcaux_default.yaml` 的 reachability planner_weight 为 0.35；README 的 TwoRoom 演示使用规划权重 0.85。两者用途和覆盖项需解析，演示不自动对应论文主表。
- Wall 用 DINO-WM 原生环境脚本，包含 action block、receding horizon 和 softmin cost 等参数；不能照搬 TwoRoom 的 terminal-cost 理解。
- continuation 的 `strict=false` 要记录 missing/unexpected keys，并验证 backbone 权重确实加载；不能把重初始化误当方法增益。
- 固定评测组的标准差与独立训练 seed 标准差分别报告；LIBERO action-head 与 latent MPC 分开记账。

### 3.4 Temporal Straightening 的更新

官方 UPDATES 解释 global projector 的 latent_ndim 影响因果 mask、不同 encoder 配方和部分 baseline 强度变化；作者同时报告修正后的对照。复现必须选定论文版或修正版并标清，不能挑对自己有利的旧 baseline。公开更新是版本审计依据，不是我们发现了新 bug。

### 3.5 非 WM 对照

OGBench reference algorithms 基于 JAX；SWM／LeWM 主路径基于 PyTorch。允许用两个原生环境交换只读任务清单与结果，而非先重写所有算法。评测目标、observation、动作范围和数据权限必须匹配；特权状态基线单独标为 diagnostic，不与纯像素输入混排。

## 3.6 新代码的执行边界

- **TD-JEPA**：locked protocol 显示 (H=5)、goal offset 25、300 candidates；TwoRoom/Reacher 默认 iCEM，Push-T/Cube CEM。实验比较时 solver/cost必须拆开，不能把 method 与 planner change混为一体。
- **Traj-LeWM**：默认 10 epochs；LTC planning weight 通过 endpoint-only CEM candidates 做 IQR calibration。若未来作为 baseline，calibration 数据/seed必须与 test 分离，避免 test-informed scaling。
- **PSG-JEPA**：OGBench planning 使用 GC-IDM，不是 LeWM CEM；LIBERO 又是 OFT action head。只能在相同 planner/input protocol 下比较 representation，不能直接把论文 success 数字和 CEM methods 排名。
- **ALeWM**：当前 connector 核对 repo 是 project page；README 说 root 为 future code 留位，不代表 code 已可运行。
- **CompACT**：official README 报告 tokenizer paper training 8 H100、WM default 4 RTX 6000 Ada；虽然单 GPU script存在，也不能据此假定 paper-scale reproduction 适合我们首轮。

## 3.7 Replanning / scoring-time protocol baseline

LeWMRO 明确区分 planning horizon (H) 与 executed prefix (K)，并提供 terminal@H、prefix@K、running cost。E02/E06 若使用 (K<H) 的 closed-loop MPC，必须先做这一 protocol gate；否则可能把 scoring-time mismatch 误当模型/representation failure。

其 repo 固定 commit：`faff2ea4768767739b9cca55855dc5aacf13578f`。代码与 tests 可用，但 upstream datasets/checkpoints 未随 repo 发布；首次执行仍需按 provenance 获取 LeWM asset。

## 3.7 I06 semantic-negative code audit（跑前事实）

### TD-JEPA pinned commit `b4c17ca...`

已核对：
- canonical config: history size 3（LeWM base）+ `num_preds=5`，即训练时加载短 clip；
- temporal-distance positives在 loaded sequence内采 i<j，target是 observed step gap；
- cross negative由 **batch row permutation**构造，loss本身不读取 environment connectivity，也不以 original episode ID过滤；
- canonical negative margin由实际 window length/config决定；
- official `td_jepa_hinge_off` 只把 cross-trajectory negative weight设为0，其他主要组件保留；
- paper明确写这些是 heuristic negatives，允许 trajectories share reachable states造成 false negatives；
- official repo内已存 Push-T component ablation summary：去掉 cross-trajectory hinge 对多个planner settings有负面影响。

这正是 E08/E09 的 tension：**semantic validity 未被 sampler验证，但 negative term又有实证utility。**

### RC-aux pinned commit `cbdf3786...`

已核对：
- base history size 3；
- `rcaux.yaml` 将 `num_preds=5`、reachability `max_horizon=5`；
- same-window positives/temporal hard negatives由 observed offset + budget产生；
- cross negatives通过 batch维 random permutation goal产生，BCE target为0；不查询 environment reachability；
- paper/appendix明确说 trajectory offset是 empirical proxy，不是真 shortest-path reachability；
- temporal hard negatives的理论作用是让 budget h identifiable；因此 cross negatives的额外作用可以被单独审计。

### stable-worldmodel Dataset

当前 source 显示 dataset 以 `clip_indices=(episode,start)` 构造 sliding clips，再由 DataLoader shuffle clip rows。  
因此 E08 必须从 dataset/clip provenance恢复 source/goal 的 original episode/step，而不能把 “different batch row” 自动叫 “different trajectory”。

### TwoRoom audit feasibility

公开 TwoRoom dataset具有 episode/step与 agent position相关字段；environment也暴露 agent state。E08 优先用这些 privileged metadata做**measurement-only oracle/certified bounds**，不进入pixels-only model输入。

## 4. 资源判断：作者测量与本地测量分开

| 项目 | 已知事实 | 尚不能声称 |
|---|---|---|
| LeWM | 原论文报告单 GPU、小模型训练；官方代码和权重可用 | 我们的 GPU 上固定几小时完成、最低显存是多少 |
| RC-aux | 论文约 18.7M scoring modules；单 GPU 设置；cost-call 微基准 | 参数占比就是训练开销；35ms 是完整决策延迟；evaluation 一定比训练贵 |
| SALT | 论文自己的实验用单 H100 80GB | PRO 6000／A100/H20 的精确速度、所需显存相同 |
| 图像数据 | SWM README 的同一 PushT benchmark：HDF5 43.12GB、Lance 13.31GB、video 496.29MB | 所有数据都小；格式变化不改变解码；我们磁盘上的吞吐和作者相同 |

RC-aux 论文使用的 GPU 名称写作“RTX A6000 Ada”，名称本身不够规范；本账本保留原始报告，不替作者确定具体 SKU。详见 [RC-aux](https://arxiv.org/abs/2605.07278)、[SWM 格式 benchmark](https://github.com/galilai-group/stable-worldmodel#data-formats)、[SALT](https://arxiv.org/html/2609.33595v1)。

## 5. 首次实测表（全部待填）

| 硬件／软件 fingerprint | peak allocated/reserved VRAM | 数据读取 wait／samples/s | train step/s | planner ms／decision | env+render ms | episode wall-clock | 节点并发数 |
|---|---|---|---|---|---|---|---|
| 未运行 | — | — | — | — | — | — | — |

GPU 时间、CPU 时间、模型打分调用数和真实环境步数分别记；规划 horizon、action repeat 和 replanning interval 要一起报告。

扩大并发前，在同一节点从 1 个任务到少量任务测一次 I/O 与 CPU 退化。若数据加载卡住，先修存储／缓存，不要用更多 GPU 隐藏单任务失效；没有必要因 I/O 暂时差就判断科学问题不可做。

## 7. Problem-led新增资产（2026-10-02）

| mine | 资产 | 固定 revision | 当前核对 | 备注 |
|---|---|---|---|---|
| M2 implicit | [facebookresearch/td_jepa](https://github.com/facebookresearch/td_jepa/tree/840a745455a124f04a58ae7ee31d7d5054e381f5) | `840a745455a124f04a58ae7ee31d7d5054e381f5` | repo / pixel OGBench & DMC launcher / OGBench reward-eval code 已核对 | **Bagatella TD-JEPA, ICLR'26 Oral**；OGBench pixel=1M steps,batch256；DMC pixel default=2M,batch512；official reward inference≈10k samples，见 §7.1 |
| M1 belief diagnostic | [santoshkumarradha/uwm-jepa](https://github.com/santoshkumarradha/uwm-jepa) | `1ef57359fac031f725632c13668db4868d63459b` | repo / main ref 已核对 | hidden-velocity controlled baseline；不是现成 image-goal MPC solution |
| M1 structured memory | Flow Equivariant World Models | 首次 manuscript-critical 接入时再锁 | ICML'26 proceedings/project存在 | 不首轮安装；E11过gate再判断 |
| M1 typed state | FIRM-WM | release需再审 | paper定位已进P62 | 强 collision；优先复用作者release，不自行“复刻一个FIRM-like”冒充baseline |
| M1 physical-identifiability oracle | [pvwm/physically-viable-world-models](https://github.com/pvwm/physically-viable-world-models/tree/2402aedd05ba46c34172b9dfdb35dc2179034d59) | `2402aedd05ba46c34172b9dfdb35dc2179034d59` | repo/main ref 已核对 | broad same-appearance/hidden-physics claim已占；只在 E11 过 history gate 后作为 collision/control |
| M3 hitting-time neighbor | [MagnusBoock/IEL](https://github.com/MagnusBoock/IEL/tree/e0262e1c5f3491d9ef8039a854472baa93ce80c9) | `e0262e1c5f3491d9ef8039a854472baa93ce80c9` | `dataset_utils.py` / `iel.py` 已核对 | 直接用 `intermediate_indx-indx` 作为 hitting-time label；默认 `HT_expectile=0.25`；强 collision，不首轮迁移代码 |

### 命名规范

- `bagatella_td_jepa` = P65 ICLR'26 zero-shot RL / successor-feature方法。
- `temporal_distance_jepa` = P14 Bai/Xiong 2607.25337 plan-aware temporal-distance方法。
- 后者repo内部历史 config可继续叫 `td_jepa`，但实验 manifest 增加 `paper_identity` 字段，避免跨repo聚合混淆。


## 7.1 M2 official task-inference audit

Bagatella TD-JEPA pinned repo的 **OGBench pixel launcher / evaluator** 已代码级核对：

- OGBench pixel training：`num_steps=1_000_000`, batch `256`, DrQ encoder feature dim `256`；
- DMC pixel default：`2_000_000` steps, batch `512`；
- official evaluation通常 `10` episodes/task，`num_inference_samples=10_000`；
- `metamotivo/evaluations/ogbench.py` 从 **train replay buffer** 采样 next observations；
- task reward由 OGBench relabel function 对 `batch["next"]["physics"]` + action计算；
- 然后用 `(next_obs, reward)` 调用 model `reward_inference` 得到 task context。

因此 E13 的 fairness/accounting 必须拆成三本账：

1. **training compute**；
2. **task/query information budget**：goal image、known reward function、reward-labeled inference states、是否用 privileged physics relabel；
3. **deployment compute**：policy/model calls、MPC candidates、wall-clock。

不能把“10k reward-labeled samples vs 一张 goal image”的差别简单记成 inference latency。  
这不是在批评 TD-JEPA：这是它所解决的 zero-shot reward-task setting 的原生接口。E13 若要做 field-level comparative science，必须把 task specification 明示。

## 7.2 M3 OGBench behavior-regime audit

OGBench pinned `1d414099...` 的官方 data-generation code 已核对：

### Locomaze
`generate_locomaze.py` 支持：
- `path`：到单个 goal 并停留；
- `navigate`：episode 内反复采随机 goal；
- `stitch`：从 initial cell 到 BFS 距离约 4 cells 的 nearby goal；
- `explore`：每 10 steps随机新方向。

所有 dataset 保存 `observations/actions/terminals/qpos/qvel`。

### Manipulation
`generate_manipspace.py`：
- `play` = non-Markovian `PlanOracle`，跟随预计算 plan；
- `noisy` = Markov closed-loop oracle，per-episode Gaussian action noise，可再插入 random actions；
- 同样保存 qpos/qvel；Scene还保存 button states。

**科学边界：**这些公开 regime 非常适合 E14 Stage-A sensitivity，但它们同时改变 trajectory length、goal schedule、occupancy、policy memory/noise，因此**不能直接承担“behavior semantics causal effect”**。Stage-B必须按 E14 做 matched generation / support audit。


## 7.3 IEL / P95 code audit

官方 repo pin：`e0262e1c5f3491d9ef8039a854472baa93ce80c9`。

已核对：
- `GCDataset.sample_goals` 从同一 trajectory 中选 intermediate state；
- `batch['intermediate_distances'] = intermediate_indx - indx`，即直接使用 observed trajectory step gap；
- `iel.py` 将该 gap作为 hitting-time regression target；
- 默认 `HT_expectile=0.25`，对 hitting-time residual做 asymmetric expectile weighting；
- 同时有 goal-conditioned value / HILP-style consistency等组件。

所以 P95 不只是理论邻居；它在代码层已经显式处理 **trajectory-derived hitting-time geometry**。  
E15 若最终方法只是 lower-expectile gap regression、directed hitting-time head、triangle/quasimetric consistency，必须首先与 IEL/QRL exact compare，不能当 novel correction。
