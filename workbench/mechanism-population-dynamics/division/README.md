# 分工重现：分别训练的 MoE 会不会自发分出同一套专家分工

**状态（2026-11-01）：** 8 个 run（6 个只换初始化 + 2 个只换数据顺序）已训练并读完，初步结果见 [PRELIM_FINDINGS](PRELIM_FINDINGS.md)：扣掉自然一致后，深层分工跨初始化重现约为天花板的 60–73%，但只在粗粒度（词类层面 .83–.90，逐 token 只有 .28）；头和专家的深度规律相反。已释放全部 GPU；未登记主张，等人决定是否带给导师、是否继续条件地图。

## 问题
同架构、同数据、只换初始化训练的 MoE 语言模型，扣掉“同一个词去同一个专家”（词知识一致）和“同样的隐状态几何怎么切都相似”（几何一致）之后，专家的语言分工是否仍跨 seed 重现？在训练的什么时候定下来？同一把尺子量注意力头，结果是否一样？

导师的问题是起点，不是要死守的题目；推进中若出现更有意思或更重要的现象，按信息量决定是否转向。

## 为什么这样做
复盘见 [RETROSPECTIVE_2026-10-31](../moe/notes/RETROSPECTIVE_2026-10-31.md)。要点：此前所有 MoE 实验都没有只差初始化的独立训练；公开模型里没有多 seed MoE 套件，而我们的资源最适合多 seed 的单卡训练。

## 入口
| 内容 | 位置 |
|---|---|
| 实验卡 | [E167 多 seed MoE 分工](experiments/E167-multiseed-moe-division.md) |
| 初步结果 | [PRELIM_FINDINGS](PRELIM_FINDINGS.md)、四联图 `results/e167/prelim_figure.png`；逐 token 角色 [E168](experiments/E168-matched-expert-transplant.md) |
| 模型与训练 | [moe_model.py](scripts/moe_model.py)、[train_moe.py](scripts/train_moe.py) |
| 数据准备 | [prepare_data.py](scripts/prepare_data.py)（Dolma v1.7，约 60 亿 token，`~/mechpop_cache/e167_dolma_6b`） |
| 结果 | `results/e167/`（小文件进 git；checkpoint 只在本地，见下） |

## 资产位置
- 训练数据：`~/mechpop_cache/e167_dolma_6b/{train,held}`（uint16 .npy，manifest.json 含逐文件 SHA），训练前复制到各节点 NVMe。
- checkpoint：`~/mechpop_cache/e167_runs/<run>/ckpt_<tokens>.pt`（bf16，不进 git）。
