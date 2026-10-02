# 资产与原生协议

更新：2026-10-02。资源约束只引用根目录 [RESOURCES.md](../../RESOURCES.md)。

## 1. 资产状态不能混写

`论文/入口 → 仓库快照 → 下载及hash → 加载成功 → 训练/控制闭环 → 数值复现`。

下面是**整理前账本已记录的官方入口和快照**，本轮保留其来源，不声称重新逐仓运行验证，也不把它们视为已兼容的统一锁文件。完整旧核对记录见 [历史ASSETS](../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/ASSETS.md)。目前没有本地GPU复现结果。

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
| 原生小模型加载与训练步 | 未执行 | E00 |
| 原生规划闭环与计时 | 未执行 | E00 |
| 数值复现、独立训练seed | 未执行 | E01 |
| 共享评测清单/数据缓存 | 未执行 | 随E00/E01建立并供方法实验复用 |

新记录追加在这里或具体实验卡，不另建“最终资产表2”。

## 6. 面向当前资源的批量实验记账

以实际可用且授权的卡为分母，不合并研究室和实习地点的私有数据。每类GPU分别测单run时间；A100/PRO6000/H20的数量不是性能等价计数。

可优先并行：同checkpoint多planner/任务评测；同小backbone不同数据/目标的独立训练；多seed与消融。复用冻结encoder缓存时固定encoder/config版本，encoder参与训练则不能读旧feature。节点数据尽量一次stage后复用。

每批记录 `train_gpu_hours / eval_gpu_hours / env_cpu_hours / io_wait / peak_vram / effective_concurrency`，把准备成本、探索失败成本与最后确认实验成本分开。不把一次planner成本微基准或参数量直接当成“一天能复现完整论文”的证据。
