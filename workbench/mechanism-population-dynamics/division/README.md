# 分工重现：分别训练的 MoE 会不会自发分出同一套专家分工

**状态（2026-11-04）：** 8 个 run + 1 个完全相同配置重跑训练完并读完；结论见 [PRELIM_FINDINGS_v2](PRELIM_FINDINGS_v2.md)：重跑之间深层分工也只一致 .47（E171），扣掉自然一致后跨初始化重现这个上限的约一半（相对只换顺序约 2/3，seed 刀切 ± .04），重现的部分沿语言区分组织（格层面 .71–.85，残差 .55），深层初始化印记持久（.12–.17），路由器不是几何的自然聚类；头的“方向相反”撤回。GPU 已释放；未登记主张；待人决定同配置重跑与是否带给导师。

## 问题
同架构、同数据、只换初始化训练的 MoE 语言模型，扣掉“同一个词去同一个专家”（词知识一致）和“同样的隐状态几何怎么切都相似”（几何一致）之后，专家的语言分工是否仍跨 seed 重现？在训练的什么时候定下来？同一把尺子量注意力头，结果是否一样？

导师的问题是起点，不是要死守的题目；推进中若出现更有意思或更重要的现象，按信息量决定是否转向。

## 为什么这样做
复盘见 [RETROSPECTIVE_2026-10-31](../moe/notes/RETROSPECTIVE_2026-10-31.md)。要点：此前所有 MoE 实验都没有只差初始化的独立训练；公开模型里没有多 seed MoE 套件，而我们的资源最适合多 seed 的单卡训练。

## 入口
| 内容 | 位置 |
|---|---|
| 实验卡 | [E167 多 seed MoE 分工](experiments/E167-multiseed-moe-division.md) |
| 转交说明（坑、导师建议、相关工作、进展、薄弱点） | [HANDOFF_2026-11-03](HANDOFF_2026-11-03.md) |
| 审阅与规划（11-03：逐条核对、含义缺口、定位表、下一步） | [REVIEW_2026-11-03](REVIEW_2026-11-03.md) |
| 给导师的文稿（11-03 改订版；11-02 版保留） | [SLACK_TO_SASANO_2026-11-03](SLACK_TO_SASANO_2026-11-03.md)、图 `results/e167/prelim_figure_v2_ja.png` |
| 对照与分解（11-03 起） | [E169 簇零假设](experiments/E169-cluster-null-for-routing-agreement.md)、[E170 语言学分解](experiments/E170-linguistic-decomposition-of-reproducible-division.md) |
| 初步结果 v2（11-03：解释修正 + 语言学内容） | [PRELIM_FINDINGS_v2](PRELIM_FINDINGS_v2.md)、六联图 `results/e167/prelim_figure_v3(_ja).png` |
| 初步结果 11-01 版（数字保留，解释已被 v2 取代） | [PRELIM_FINDINGS](PRELIM_FINDINGS.md)、四联图 `results/e167/prelim_figure.png`；逐 token 角色 [E168](experiments/E168-matched-expert-transplant.md) |
| 模型与训练 | [moe_model.py](scripts/moe_model.py)、[train_moe.py](scripts/train_moe.py) |
| 数据准备 | [prepare_data.py](scripts/prepare_data.py)（Dolma v1.7，约 60 亿 token，`~/mechpop_cache/e167_dolma_6b`） |
| 结果 | `results/e167/`（小文件进 git；checkpoint 只在本地，见下） |

## 资产位置
- 训练数据：`~/mechpop_cache/e167_dolma_6b/{train,held}`（uint16 .npy，manifest.json 含逐文件 SHA），训练前复制到各节点 NVMe。
- checkpoint：`~/mechpop_cache/e167_runs/<run>/ckpt_<tokens>.pt`（bf16，不进 git）。
