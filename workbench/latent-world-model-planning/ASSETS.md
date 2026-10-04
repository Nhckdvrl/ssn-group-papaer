# 资产与原生协议

更新：2026-10-02。资源约束只引用根目录 [RESOURCES.md](../../RESOURCES.md)。

## 1. 资产状态不能混写

`论文/入口 → 仓库快照 → 下载及hash → 加载成功 → 训练/控制闭环 → 数值复现`。

下面是**整理前账本已记录的官方入口和快照**，本轮保留其来源，不把它们视为已兼容的统一锁文件。完整旧核对记录见 [历史ASSETS](../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/ASSETS.md)。已有工程 GPU 结果，尚无完整数值复现。

| 用途 | 入口/历史固定版本 | 执行建议 |
|---|---|---|
| 紧凑端到端基线 | [LeWM](https://github.com/lucas-maes/le-wm/tree/8edfeb336732b5f3ce7b8b210d0ba370a09e2cac) | 首选训练支点；保留原生环境，解析任务override |
| 环境与规划接口 | [stable-worldmodel](https://github.com/galilai-group/stable-worldmodel/tree/63988116d34cde56aea1240d5e58eb158ac67dc0) | API仍可能变化；不要强行与其他快照升级到同版 |
| Reachability训练/规划参照 | [RC-aux](https://github.com/Guang000/RC-aux/tree/cbdf3786b149df8145d6c7314f32f460d43c9695) | 严格区分训练目标、planner权重与continuation控制 |
| 冻结视觉特征参照 | [DINO-WM项目](https://dino-wm.github.io/)、[JEPA-WMs](https://github.com/facebookresearch/jepa-wms) | 先选合适小模型；锁所用代码、数据和权重版本 |
| 时序目标参照 | [Temporal-Distance JEPA](https://github.com/HKBU-KnowComp/Temporal-Distance-JEPA/tree/b4c17ca4649c9bf47272fa66c38da7a684f2a020) | 历史账本记录同repo有LeWM/RC-aux variants；执行前确认具体配置 |
| 长期预测/零样本RL | [Bagatella TD-JEPA](https://github.com/facebookresearch/td_jepa/tree/840a745455a124f04a58ae7ee31d7d5054e381f5) | 与上一行不是同一方法；只在对应比较需要时接入 |
| 数据、环境与非WM对照 | [OGBench](https://github.com/seohongpark/ogbench/tree/1d4140997f60c52c6fb0702ec100dc988b18c548) | 可以独立JAX环境；原生reward/goal接口分清 |
| 几何方法参照 | [Temporal Straightening](https://github.com/agentic-learning-ai-lab/temporal-straightening) | 先读官方UPDATES；论文版与修正版分开，不选弱旧版本 |
| R2 cheap-fidelity | [Fast-LeWorldModel](https://github.com/Yuntian-Gao/Fast-LeWorldModel/tree/de3e9dac539f5bbe6ff1656a2fb00938d62a3c7d) | official implementation；同LeWM数据布局；README列TwoRoom/Reacher/PushT/Cube与HF checkpoint；E13首轮优先资产 |
| R2 adaptive-depth近邻 | [DeepJEPA](https://github.com/deepjepa/DeepJEPA/tree/d52bfb232c19376b6f6731b9380bc2d6d7762ffb) | 截至2026-10-02官方README仍写code即将发布；只作直接近邻，不假定可运行 |

历史TwoRoom expert代码核对另使用了SWM快照 `8b2e8c685dd7f11d4189f5c09d9b6bfffd5cdca4`。这与表中平台快照不同；选择哪个取决于可复现的原生组合，不能把两次审计当同一release。

## 2. 数据与权重入口

LeWM历史账本列出 [HF collection](https://huggingface.co/collections/quentinll/lewm)；RC-aux列出 [HF发布](https://huggingface.co/biubiu116/RC-aux)；JEPA-WMs有 [模型](https://huggingface.co/facebook/jepa-wms) 与 [数据](https://huggingface.co/datasets/facebook/jepa-wms)。这些是定位入口，不代表全部任务已下载/加载。OGBench由原生dataset API按具体任务下载，不用通配命令拉全套。

执行机资产行须含：paper ID、code commit、dataset/checkpoint revision、SHA256、字节数、许可证、split/preprocessing、实际硬件、加载方式与状态。实习数据/凭证/内部主机名不能写进公开仓库。

## 3. 复现与比较中保留的关键事实

**配置与版本。** 默认epoch、`devices:auto`、workers与任务override不等于论文配方。记录resolved config和checkpoint missing/unexpected keys；单卡任务显式限制设备，避免意外占满节点。

**环境不是名字相同就等价。** 原PLDM Two-Rooms、SWM TwoRoom、不同maze实现，观测通道、速度、门、终止条件可能不同。先对齐控制接口，再谈横向比较。

**时间单位。** 记录真实env steps、frameskip/action repeat、模型rollout长度、执行prefix、goal offset和cost reduction。它们不同；不强制把所有方法改成同一个错误协议。

**训练/规划分离。** RC-aux原文允许planner coupling为0；Cube主表就是0。其固定评测组标准差不是独立训练seed标准差。LIBERO action-head transfer不是原生latent MPC。

**任务信息。** 历史代码审计记录Bagatella TD-JEPA OGBench任务推断使用replay样本与privileged physics reward relabel，常用10k样本；它不是“免费知道任务”，也不等价于一张goal image。E13跨范式阶段逐配置核对，并分别记任务信息、训练计算、部署计算。

**数据干预。** 历史审计记录OGBench locomaze有navigate/stitch/explore等生成方式，manipulation有play/noisy。它们同时改变多项因素，适合探索性对照；不能直接作严格单因素因果证据。

**旧设计错误。** 原E03/E04只改长episode元数据，固定短clip损失可能完全看不到干预。该旧实验保留归档；新设计先确认实际载入的样本/标签发生变化，不因此关闭数据或可达性研究。

## 4. 成本与实际可用性

先量单run峰值显存、GPU/CPU利用率、数据等待、checkpoint保存、完整episode和规划耗时。缓存一次、节点复用；确认1/2/4并发时I/O退化后再增加。规划cost-call微基准不代表完整推理时间；表征预计算仅在encoder确实冻结且版本一致时复用。

LeWM原文报告紧凑单GPU训练；RC-aux提供约18.7M的本地实例。不要据此推断所有JEPA/长期RL/视频方法都同样便宜。跨范式长训练按实际时间安排独立槽位，不强依赖多机同步。

## 5. 待执行记录

| 项目 | 本地状态 | 下一步 |
|---|---|---|
| 原生小模型加载与训练步 | Fast 两任务原生完成；LeWM有限数据1680+600 updates实际运行 | E01原生配方与独立seed |
| 原生规划闭环与计时 | 两任务配对闭环/计时；长短goal256pairs完成 | 第二预测对象/恢复方式 |
| 数值复现、独立训练seed | 完整数值复现未完成；E16三完整pipeline seeds已完成 | 原生配方/第二task与不同data regime |
| 共享评测清单/数据缓存 | 两任务node-local HDF5、candidate/branch banks、1/2/4 I/O完成 | 整episode RAM cache复用 |

新记录追加在这里或具体实验卡，不另建“最终资产表2”。

### 2026-10-02 实际执行资产

- 环境：`/home/xiang/.venvs/latent-wm`，以既有 `lightwam` 的 Python 3.10/CUDA torch 创建 system-site-packages venv，未修改原环境。torch=2.7.1+cu128、transformers=5.3.0、stable-worldmodel=0.0.6；torch 低于 Fast-LeWM requirements 中的 2.10，opencv 为 headless 4.11。配方偏差须随结果披露，工程 pilot 没有安装完整 optional training stack。
- 已 clone：Fast-LeWM `de3e9dac539f5bbe6ff1656a2fb00938d62a3c7d`、LeWM `8edfeb336732b5f3ce7b8b210d0ba370a09e2cac`、RC-aux `cbdf3786b149df8145d6c7314f32f460d43c9695`；各自在忽略的 `vendor/`。RC-aux只借用实际open-loop实现开展component pilot，未完整复现；代码许可与weights/data分开核对。
- Fast checkpoint：HF `naiverer/fast-leworldmodel`，revision `f95379fe193c8bfc6a59c9d8437d5052bd72ff71`；两个 object 均 71,897,531 bytes / 17,913,184 params。TwoRoom SHA256 `0822f1e3bc0f8822e68dd19ea92d82053f2f31a2e0f976051572dcb7605a8119`，PushT `7d2af06261610f0407283c5e812f2806d880448e2f680ede6ec62473393c0eca`。均在标准 HF cache，已实际加载且参数有限。权重/数据许可尚未核对，不能用代码 MIT 代替。
- TwoRoom dataset revision `6903a2de048b13819d812da0b4dd661290bc01e4`，`tworoom.tar.zst` 3,425,937,909 bytes，下载并解压完成；node-local `/tmp/latent-wm-data/tworoom.h5`，920,809 transitions / 10,000 episodes，224×224 RGB。解压 67.20 s，HDF5 SHA256 `129a36aa93ea0de488d2bcc876e396de9e3907bf66c6aae6394e542ef6a6d623`。PushT dataset revision `655cd446b9929369d7d406001da85c15d1457850`，压缩 13,136,247,974 bytes 已下载并解压（492.93 s；HDF5 46,300,921,856 bytes / 2,336,736 transitions / 18,685 episodes），原生批次已启动；压缩 SHA256 `7cfbd6d90fa2f27876379a5ff169715a36ed82edbda64f9e5b5bfa34d212f318`。zstd 参数路径为 HF symlink 时被工具忽略；改为 stdin 读取，原失败日志保留。
- 官方 LeWM 两 task 的 config/weights 也进入 HF cache；TwoRoom revision `77adaae0bc31deab21c93740d1f8bb947cd0bdec`、PushT `22b330c28c27ead4bfd1888615af1340e3fe9052`。两task均按官方 tiny ViT/JEPA 配方 strict load 303 keys、18,034,478 params；PushT derived object SHA256 `0c095fc4a26856678f67bf299f261506b45f1a25fbdb4cbb8828b4a8281dc048`。[重建脚本](scripts/build_lewm.py) 与衍生 object/metadata 在 HF cache 的 `latent-wm-derived/`。只称严格权重加载，尚未数值复现。
- 首轮实际硬件 RTX PRO 6000 Blackwell Max-Q，独立单卡任务；不跨硬件合并 timing。raw banks/HDF5/logs 先写 `/tmp/latent-wm-runs/`；完成批次已复制到持久非 git `/home/xiang/.cache/latent-wm-results/<run>/`，结果文件逐项记录 artifact pointer/hash。
- 工程结果：[TwoRoom](results/E00_E13_E16_20261002_tworoom_engineering.json)、[PushT](results/E00_E13_E16_20261002_pusht_engineering.json)。生成数据的 replay error 为 0，dataset setter 的 factual-suffix precision 单独报告。
- 原生 [TwoRoom 结果](results/E00_E13_E16_20261002_tworoom_native.json) 包含 E13 离线/实际 GPU 计时/配对闭环与 E16 restore/隔离审计；released checkpoint 训练数据与评估 anchors 的重合尚未核对。

## 6. 面向当前资源的批量实验记账

以实际可用且授权的卡为分母，不合并研究室和实习地点的私有数据。每类GPU分别测单run时间；A100/PRO6000/H20的数量不是性能等价计数。

可优先并行：同checkpoint多planner/任务评测；同小backbone不同数据/目标的独立训练；多seed与消融。复用冻结encoder缓存时固定encoder/config版本，encoder参与训练则不能读旧feature。节点数据尽量一次stage后复用。

每批记录 `train_gpu_hours / eval_gpu_hours / env_cpu_hours / io_wait / peak_vram / effective_concurrency`，把准备成本、探索失败成本与最后确认实验成本分开。不把一次planner成本微基准或参数量直接当成“一天能复现完整论文”的证据。


## 7. R2新资产核对（2026-10-02）

Fast-LeWM官方README已核对：基于LeWM代码、使用相同HDF5数据布局，提供PushT/TwoRoom/Reacher/Cube训练与评测入口，并指向`naiverer/fast-leworldmodel` checkpoints。当前锁定公开main快照`de3e9dac539f5bbe6ff1656a2fb00938d62a3c7d`；**TwoRoom/PushT 已在本地加载并运行**。

DeepJEPA最新arXiv为`2610.00368`（submitted 2026-09-30）。公开repo快照`d52bfb232c19376b6f6731b9380bc2d6d7762ffb`仍只有项目说明并称code即将发布；执行机每次准备E13确认一次release即可，不为等它阻塞Fast-LeWM/LeWM首轮。

### 2026-10-02 真实方法/确认资产

PushT HDF5 SHA256 `b6ebd9ac94bbe9e383f6e7a9cd92d74e9aa665ea57b758ed3717b0ee7df8d4fb`；[原生结果](results/E00_E13_E16_20261002_pusht_native.json)含GPU实际计时与8paired闭环，所有scoring controls差0。[E13 A2](results/E13_20261002_fidelity_value.json)256pairs完整执行，但后续GPU共卡，耗时不作speedup证据。[factual controls](results/E00_E13_E16_20261002_factual_controls.json)304起点完整保留，PushT长时恢复非exact。

[E16 seed0](results/E16_20261002_equal_data_seed0.json)：基础100episodes/9295rows/7295有效clip，encoder参与训练，缓存的是uint8 pixels而非旧latent。base30模型在 `<HF cache>/latent-wm-trained/E16_lewm_base100_seed0_e30.ckpt`，SHA256 `8c67528b8b9ad9290a6e04c9d42b15b6daf10787265c8f71abe0b928482c1996`。七方法checkpoint都在HF cache的 `latent-wm-trained/E16_methods_A100_s0/`，完整hash/600updates/precision/独立seed/模型配置见JSON；训练A100计时与RTX基础训练分开。

原始bank/heads由RTX单卡生成，所有ledgers在hidden文件不存在时密封：ledger SHA256 `c2f932ad015a97e83a3cc92a5b0f0b79c4bf0ca0d8ff600fa51f5b098a2b51b8`，hidden SHA256 `18106a5f144ead2378827499021bb60e02d366b49b412c4f31486446dcc231a8`。跨授权节点仅stage约41MB压缩base100 pixels/actions缓存+约130MBpublic/hidden bank，避免重复12GB数据传输。base-cache SHA256 `fb46e630ce6d6fcc2fb9ee09346017d723afdbb51bc71627fc4a7360ee11f68b`，manifest逐字段核对。

新seed1/2由[独立pipeline](scripts/independent_acquisition.py)执行，checkpoint仍HF、data local、raw完成后复制持久cache。同进程连做base/bank/methods以摊薄NFS Python import成本；不修改既有环境，不开多节点训练。E00 [1/2/4读数](results/E00_20261002_io_concurrency.json)是指定HDF5 fancy-index读法，不能代替磁盘带宽或多GPU训练测量。


### optimizer audit与新批次（2026-10-02）

- CPU optimizer audit：`/tmp/latent-wm-runs/20261002-optimizer-isolation-audit/`，含复现/torch optimizer源码hash；小JSON已进results。旧E16 raw/模型完整保留，公平比较降级；源base checkpoint文件不变。
- 修复train-only复跑沿用原durable base/bank：seed0 `20261002-E16-base100-s0-e30` / `20261002-E16-acquisition-bank-s0`，seed1/2 `20261002-E16-independent-s{seed}/{base,bank}`；新模型HF `latent-wm-trained/E16_methods_optclone_s{seed}`，raw/完成后durable `20261002-E16-methods-optclone-s{seed}`。
- E13零训练horizon audit已完成，durable `20261002-E13-horizon-breadth-RTX-s0`，小summary/hash进results；不受optimizer alias影响。
- E17 raw `20261002-E17-query-proposal-RTX-s0`，head checkpoint HF `latent-wm-trained/E17_query_proposal_RTX_s0`；E18 queue raw `20261002-E18-continuous-adaptation-RTX-s0`。公开Fast object不提供训练episode split；只把新head/calibration split称held-out，released WM未见性未核对。

2026-10-03：E18连续适配`20261002-E18-continuous-adaptation-RTX-s0`与E13动作基`20261003-E13-action-basis-RTX-s0`已完整durable，portableJSON在results。A5 `20261003-E13-commitment-cadence-RTX-s0`真实GPU0与data×compute `20261002-E16-data-compute-RTX-s0`真实GPU1各fresh Python运行；完成后同名durable，后者checkpoints HF `latent-wm-trained/E16_data_compute_s0`。旧paused queue已清理，不重复运行。

2026-10-03最新完成：fair acquisition全部三pipeline、A5共同计划、E17 continuationcost352与E11 observer384均durable同run名；portable config/hash/summary在results。E17三heads及frozen/predicted featurecache存HF `latent-wm-trained/E17_continuation_cost_RTX_s0`，所有原2000-loss histories与observerNPZ traces留raw。GPU0已释放；A6两模型candidate bank源与prereg准备中，LeWM PushT303keys/18M object由官方HFweights strictderive进HF `latent-wm-derived/`，尚无其GPU科学读数。

2026-10-04上传补记（覆盖上条pending描述）：E13 A6 reference-retry1、A7 candidate-quality-CPU、E17 task-factor-cost均有完整同名durable artifact，portable config/hash/summary见results；A7/任务几何完整独立科学校对待做。E16 exposure仅30epochs snapshot，无整批complete，恢复入口见E16卡。

RC-aux官方完整TwoRoom object已在标准HF缓存：`biubiu116/RC-aux` revision `1cb0e604f348191afb1393d63769d752d6b0881d`，文件 `rcaux/checkpoints/pixel_control/tworoom_rcaux/rcaux_tworoom_object.ckpt`，75,086,534 bytes，SHA256 `56979b8791dc76bab066c8c7a5aaa1c2947be8911b7a50202b69be46ab866099`。严格312keys（303 backbone+9 head）CPU加载、真实pixel/predictor与coupling=0原生cost控制通过；证据JSON/审计脚本在HF `latent-wm-derived/rcaux-tworoom-cpu-contract-20261003/`。不称GPU数值复现。HF发布eval coupling=.35，object存.85；官方Lightning完整tensor相同性未核对。原生criterion的history/future索引及budget clamp与论文表达存在差异，不能据此判发布success有bug；未来baseline必须记录具体input shape/criterion/coupling。

固定BASE100 trainseed缓存：node-local `E16-base100-trainseed-cache`，7数据/架构文件各自SHA在manifest，归档 `E16-base100-trainseed-cache.tar.zst` 41,024,404 bytes，SHA256 `411a34b3fa79b0dde25e7ce49d59e44fac16c4a14a749076c6a766f3eb37d62d`。源9295rows/7295clips/100episodes/原norm与eval48不变；CPU预控 `/tmp/fixed_data_train_seed_cpu_preflight.json`。解压后逐SHA核验才训练；目前无已核对新trainseed GPU结果。

2026-10-04人审后新资产：fixeddata seed1/2完整模型分别HF `E16_fixed_data_trainseed_RTX_s1/s2`、raw/durable `20261004-E16-fixed-data-trainseed-RTX-s1/s2`；新BASE1000曝光恢复source30epoch16950 SHA9997279f…，new HF `E16_data_exposure_resume_s0`，不覆写原partial。E20 Stage0与bank44及joint actual CPU/CUDA预控分别durable `20261004-E20-legal-effect-bank`、`20261004-E20-legal-effect-bank44`、`20261004-E20-joint-training-preflight`，12/88anchors全部真实branches。四万envsteps含所有warm/reset/replays，无GPU训练数据生成。node archive SHA cb27e11df5653052d3fe6967f6c325258cf3824e1182ff80851c079ad07eb5f0，raw/frame/trace不入git。方法训练artifact与HF同unique run名 `20261004-E20-joint-{METHOD}-A100-s{seed}`，source模型三seed0/1/2完整保留；精确queue/rootlaunch/读数见E20与日志。

2026-10-04新接续：官方AD-WM源码7c27ebfdc4a2ba8e5a16268f2e4aa852fda72144（ignored vendor/ad-wm）；HF ad-wm/ad-wm revision31ab745259718946aa83f2d6df19dfebb0c8ebd4仅seed3072 TwoRoom/PushT完整object+configs/manifest已下载，均77.14MB、19,220,654 params、321keys，包含原inverse/MI heads；SHA分别92ee6859434001ed500eec52da77d20a1efac6e6da5c1595c5640d2550794ef0与e61130c558de9ed5c9c740a58ecb08a97c5c92473b45fd275a425fb46f281e9e，位置为标准HFcache对应snapshot。CPU完整namespace/residual/strict/native控通过，首次missingaction失败保留；见E01_20261004_adwm_cpu_controls.json。新GPU reference部署待终点，不称原论文完整数值复现。PLDM官方代码clone ignored vendor/pldm，尚未环境安装或numeric replicate，不移动SWM数据去冒充其TwoRooms。

E20全15Nav joint模型/raw已complete，source/config/每模型u600/u2000 SHA和开发query矩阵在E20_20261004_joint_candidate_results.json，raw audit durable20261004-E20-joint-result-audit。新独立source episode控制缓存20261004-E20-fresh-control-bank48已factual48exact，node-local归档SHA4f51ad7d20418bc3b7621a862bc699644846778f16a1ca50d13ff838fa7ed3f1，已stage两个A100节点；模型仍HF。Pushtransfer CUDA五arm预控durable20261004-E20-transfer-preflight，实际新五arm queue和全部Nav19model/A100闭环queues见E20卡/log；禁止重复启动。

E01/E14新同data完整训练资产：A100 node-local `/tmp/latent-wm-data/E16-base100-trainseed-cache` archive411a34b3…已实际解压并逐原7文件/manifest SHA检查，避免重新读全HDF。代码matched_learning.py0400260fc47d21629414582d266eb39bca47693905f118b6e1782cdff666d077，官方AD namespace/source train.py AST pure函数保留，无环境升级。新HF/raw命名 `20261004-E01-matched-{ABS/RESIDUAL/FULL-AD}-A100-s{seed}`与`20261004-E14-{VGIQL-JOINT/VGIQL-SEPARATE}-A100-s0`，5650endpoint仍待complete。完整CPU/CUDAretry3及失败/limited旧版本均durable留档；models与optimizer/RNG不入git。原Push五arm已complete，全部checkpoint/hash见E20_20261004_pusht_candidate_results.json；新的strong-native全Nav15model与physical15model都在原RTX闭环，不混A100/RTX timing。

2026-10-05补记（覆盖前述pending）：E20 physical/native各15方法与三个BASE完整，独立audit durable20261004-E20-fresh-{physical,native}-control-audit，portable数字/config/trace pointers进results。E01九同data matched模型及E14两个value模型全部u5650已complete，HF/cache原命名不变；完整部署由matched_control_queue继续。E20 experience_utilization.py源码4c4d5c45d06ed5da2a54f79bf6e568b06c9c53ebc0d7055aba4273bee1b8ce4b，两actualpreflight durable20261005-E20-experience-{cpu,cuda}-preflight；九新trainHF/raw命名20261005-E20-experience-{IID-BRANCH/REPLAY-ONLY/MIX}-A100-s{0,1,2}，controller命名20261005-E20-experience-control-{ARM}-s{seed}-{native/physical}-RTX。独立队列/PID与失败接续见log2026-10-05，禁止重复。Push新48 prepare用本地原HDF，原发布WM的pretrain episode未见性仍未知。

E01/E14十一完整训练审计durable20261005-E01-E14-matched-endpoint-audit、E20九经验利用完整审计durable20261005-E20-experience-result-audit，结果与实际checkpoint/optimizer/source hashes进portableJSON。Push新48 prepare已complete（factual/warm/diagnostic/goalpixels exact，5760steps）durable20261005-E20-pusht-fresh-control-bank48；实际控制raw/durable20261005-E20-pusht-control-{METHOD}-{native/physical}-RTX-s0。模型仍HF，完整raw状态矩阵不入git。

E16曝光u56500/100epoch已complete39/48，HF E16_data_exposure_resume_s0/BASE1000_u56500.ckpt SHA97b9080f34f341bd408ec17d37997b645324fb0587a90b75ed36b2520ae10f0a，原raw/durable20261004-E16-data-exposure-resume-RTX-s0。独立endpoint计数/optimizer/RNG audit durable20261005-E16-exposure-endpoint-audit，旧完整30epochcheckpoint/source留存。新fresh48评测raw/durable20261005-E16-BASE1000-fresh-{native/physical}-RTX；helper/source/hash原协议，训练更新10x与singletrainseed范围单列。

2026-10-05新增完整审计：matched1056、经验利用864、Push672、freshBASE1000足曝光96，各portable JSON在results；raw/trace/checkpoint保留既有HF与durable资产根。E14三个source六value固定u5650已全DONE且独立审计，models沿20261004-E14-{VGIQL-JOINT/VGIQL-SEPARATE}-A100-s{0,1,2}；新seed实际启动2026-10-05。Stage4 geometry的四cell需查训练complete；source保留充分ABS encoder与value_phase_u2825，来源预算不同，未声称novel。

### 2026-10-05新增已运行资产

完整RC-aux HF `models--biubiu116--RC-aux/snapshots/1cb0e604f348191afb1393d63769d752d6b0881d/rcaux/checkpoints/pixel_control/tworoom_rcaux/rcaux_tworoom_object.ckpt`，SHA56979b8791dc76bab066c8c7a5aaa1c2947be8911b7a50202b69be46ab866099，312state keys/9head，pinned vendor cbdf3786b149df8145d6c7314f32f460d43c9695；完整官方criterion、原归一化、history port边界见E01卡，不称paper数值复现。

新增value全部三训练source、geometry四cell与Push两模块checkpoint继续HF `latent-wm-trained/`；完整轨迹/rows保留durable `20261005-E14-three-seed-control-audit`、`20261005-E20-geometry-control-audit`、`20261005-E01-rcaux-full-control-audit` 与各原unique run。git结果为summary、config/hash/统计/指向完整raw audit；已有四份matrix JSON本次仅去大rows，不改任何计数/CI。

既有venv只补缺少scikit-learn1.7.2/scipy1.15.3/joblib1.5.2/threadpoolctl3.6.0，--no-deps，Torch2.7.1cu128/NumPy1.26.4/SWM0.0.6不变。依赖失败早于efficacy并完整留档。


### 2026-10-05：预测对象重复与独立goal-policy轴

- E13 source0/1/2十二Fast同capacity/head模型各u2825在标准HF `latent-wm-derived/20261005-E13-object-{geometry}-{arm}-A100-s{seed}`，完整独立训练与1152闭环审计已写portable。首版重复controller全部错误输出只diagnostic，旧source/log保留durable20261005-E13-object-repeat-controller-seed-shadow-failure，正式source1/2只用unique-v2-control-*。
- [GC-IDM官方仓库](https://github.com/hdnndh/Latent-Geometry-Beyond-Search-Amortizing-Planning-in-World-Models)，本地ignored vendor/gc-idm，固定commit48c45b1cb2b34dd2c1c61d222c8309de567fde55。只复用真实GoalConditionedIDM/原Dataset；原eval文件PairwiseIDM导入缺失，原Policy类AST完整抽取和独立原body parity先控，未改变其类方法。无额外环境安装/官方完整数字复现声明。
- E14G0十八policy heads `latent-wm-derived/20261005-E14-goalpolicy-{PRED/VALUE}-{GC-IDM/GCBC-MATCHED/PAIRWISE}-A100-s{0,1,2}/epoch50.ckpt`，initial.pt、state/optimizer/RNG齐备；400updates/409600样本/每head，原9295事实FP32feature caches复用。所有训练预控/终点审计PASS，实际controller12预控PASS，36组1728整批闭环进行中。raw/durable20261005-E14-goalpolicy-*/结果config记hash；无需重下载全pixels或新建conda。
- Push G1 features只编码first86原HDF事实、freeze发布LeWM，node-local `/tmp/latent-wm-data/E14-goalpolicy-pusht-RELEASED-frozen-features`，durable20261005-E14-goalpolicy-pusht-RELEASED-features。源模型在HF，训练episode与fresh48source分离，published pretraining未知；未跑完不称已建成asset、尚未Push policy训练/部署。


G0最新：18heads与完整1728 controller已DONE、训练/部署preflight和independent全matrix auditPASS；portable E14_20261005_goal_policy_control_results.json正式full audit-v2。所有控制budget100，50 readout是100-budget prefix，没有另跑50-budget policy；首audit含糊label source/artifact保留，v2不改任何成功数/动作/CI。

PushG1原A100开HDF失败，在任何编码前，无样本/效用；原failure20261005-E14-goalpolicy-pusht-RELEASED-features。原46GBHDF实际只在RTX /tmp nodecache；unique features-retry1同86ep/9374帧完成、frozen303 full state与BN hash不变/native encode exact，subset≤2.15e−6。G1 raw head `latent-wm-derived/20261005-E14-goalpolicy-RELEASED-{arm}-A100-s0` basename继承旧组件但**实际训练RTX**，hardware在launchlog和featuremetadata，非A100 timing。三个50epoch400终点独立auditPASS，adapter source/hash保留；source0一个headseed/encoderpretrain未知。新的288Push deploymentqueue正在原RTX预控，实际值尚未核对，不称complete/原paper复现。
