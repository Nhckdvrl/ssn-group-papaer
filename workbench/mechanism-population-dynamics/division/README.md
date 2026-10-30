# 分工重现：分别训练的 MoE 会不会自发分出同一套专家分工

**状态（2026-10-31）：** 用户决定摒弃 E144–E166 的计算组织线，回到导师最初的问题，自训多 seed 小型 MoE。当前在准备数据和训练代码，尚无跨 seed 结果，也没有主张。最多 8 卡（fvcrc10/11/12/15/20/21 的空闲卡）。

## 问题
同架构、同数据、只换初始化训练的 MoE 语言模型，扣掉“同一个词去同一个专家”（词知识一致）和“同样的隐状态几何怎么切都相似”（几何一致）之后，专家的语言分工是否仍跨 seed 重现？在训练的什么时候定下来？同一把尺子量注意力头，结果是否一样？

导师的问题是起点，不是要死守的题目；推进中若出现更有意思或更重要的现象，按信息量决定是否转向。

## 为什么这样做
复盘见 [RETROSPECTIVE_2026-10-31](../moe/notes/RETROSPECTIVE_2026-10-31.md)。要点：此前所有 MoE 实验都没有只差初始化的独立训练；公开模型里没有多 seed MoE 套件，而我们的资源最适合多 seed 的单卡训练。

## 入口
| 内容 | 位置 |
|---|---|
| 实验卡 | [E167 多 seed MoE 分工](experiments/E167-multiseed-moe-division.md) |
| 模型与训练 | [moe_model.py](scripts/moe_model.py)、[train_moe.py](scripts/train_moe.py) |
| 数据准备 | [prepare_data.py](scripts/prepare_data.py)（Dolma v1.7，约 60 亿 token，`~/mechpop_cache/e167_dolma_6b`） |
| 结果 | `results/e167/`（小文件进 git；checkpoint 只在本地，见下） |

## 资产位置
- 训练数据：`~/mechpop_cache/e167_dolma_6b/{train,held}`（uint16 .npy，manifest.json 含逐文件 SHA），训练前复制到各节点 NVMe。
- checkpoint：`~/mechpop_cache/e167_runs/<run>/ckpt_<tokens>.pt`（bf16，不进 git）。
