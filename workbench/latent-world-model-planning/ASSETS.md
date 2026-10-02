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
| 数值复现、独立训练seed | 完整数值复现未完成；E16独立seed1/2运行中 | E01/E16 |
| 共享评测清单/数据缓存 | 两任务node-local HDF5、candidate/branch banks、1/2/4 I/O完成 | 整episode RAM cache复用 |

新记录追加在这里或具体实验卡，不另建“最终资产表2”。

### 2026-10-02 实际执行资产

- 环境：`/home/xiang/.venvs/latent-wm`，以既有 `lightwam` 的 Python 3.10/CUDA torch 创建 system-site-packages venv，未修改原环境。torch=2.7.1+cu128、transformers=5.3.0、stable-worldmodel=0.0.6；torch 低于 Fast-LeWM requirements 中的 2.10，opencv 为 headless 4.11。配方偏差须随结果披露，工程 pilot 没有安装完整 optional training stack。
- 已 clone：Fast-LeWM `de3e9dac539f5bbe6ff1656a2fb00938d62a3c7d`、LeWM `8edfeb336732b5f3ce7b8b210d0ba370a09e2cac`；各自在忽略的 `vendor/`，代码 MIT。
- Fast checkpoint：HF `naiverer/fast-leworldmodel`，revision `f95379fe193c8bfc6a59c9d8437d5052bd72ff71`；两个 object 均 71,897,531 bytes / 17,913,184 params。TwoRoom SHA256 `0822f1e3bc0f8822e68dd19ea92d82053f2f31a2e0f976051572dcb7605a8119`，PushT `7d2af06261610f0407283c5e812f2806d880448e2f680ede6ec62473393c0eca`。均在标准 HF cache，已实际加载且参数有限。权重/数据许可尚未核对，不能用代码 MIT 代替。
- TwoRoom dataset revision `6903a2de048b13819d812da0b4dd661290bc01e4`，`tworoom.tar.zst` 3,425,937,909 bytes，下载并解压完成；node-local `/tmp/latent-wm-data/tworoom.h5`，920,809 transitions / 10,000 episodes，224×224 RGB。解压 67.20 s，HDF5 SHA256 `129a36aa93ea0de488d2bcc876e396de9e3907bf66c6aae6394e542ef6a6d623`。PushT dataset revision `655cd446b9929369d7d406001da85c15d1457850`，压缩 13,136,247,974 bytes 已下载并解压（492.93 s；HDF5 46,300,921,856 bytes / 2,336,736 transitions / 18,685 episodes），原生批次已启动；压缩 SHA256 `7cfbd6d90fa2f27876379a5ff169715a36ed82edbda64f9e5b5bfa34d212f318`。zstd 参数路径为 HF symlink 时被工具忽略；改为 stdin 读取，原失败日志保留。
- 官方 LeWM 两 task 的 config/weights 也进入 HF cache；TwoRoom revision `77adaae0bc31deab21c93740d1f8bb947cd0bdec`、PushT `22b330c28c27ead4bfd1888615af1340e3fe9052`。TwoRoom 已按官方 tiny ViT/JEPA 配方 strict load 303 keys、18,034,478 params；[重建脚本](scripts/build_lewm.py) 与衍生 object/metadata 在 HF cache 的 `latent-wm-derived/`。只称严格权重加载，尚未数值复现。
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
