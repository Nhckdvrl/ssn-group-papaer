# Auxiliary task demands mask the capabilities of smaller language models（COLM2024，作者v2主文）

证据：[作者v2](https://arxiv.org/html/2404.02418v2)§1–5、Ethics/Reproducibility完整；arXiv作者备注COLM2024，未另核对正式评审。HTML外置SHAeb1ec7603897c95938f7b5624c5f787b554e1b531f83a04b9a6f5b224154de83。

1. **形态：** 跨领域研究视角迁移＋评测交互规律，不是新能力benchmark或修复方法。
2. **压力：** 行为失败可能来自执行评测的辅助需求；儿童认知里已知的competence/performance问题也适用于LM。“不能回答”不等于“没有目标知识”。
3. **改变前提：** 不把evaluation method作为透明观测窗；明确它与模型资源的交互，而非仅报告两个方法的平均gap。
4. **idea来源（RECONSTRUCTED）：** developmental psychology task demands/construct validity→Hu&Levy2023 metalinguistic差距、production/forced-choice文献→可检验预测：较少参数/训练应承受更大demand gap→跨4领域、两类评测对比。增量是interaction与问题视角，不是gap重新命名。
5. **近邻距离：** Hu&Levy概率/提示对比已有，此文增加资源交互；Schaeffer emergence度量已有，此文辅助task操作；Webb/Hagendorff analogical/reflective能力报告为资产，此文重评推断；developmental infant-production观点为理论来源，不声称小模型就是儿童；Lepori2026随后把一般部署gap落实到latent geometry/downstream。
6. **方法/材料：** 13 base LMs，Pythia/OLMo/Gemma/Llama2/Mistral，1–70B；OLMo7B另10checkpoint。digit matrices与CRT：自由产生/强制候选；LAMBADA与BLiMP等：metalinguistic/direct。BLiMP13类各50=650；digit候选joint LP、CRT平均token LP（不同读数不是统一能力尺度）。两句语法顺序交换，单prompt，不跑无穷prompt控制。GLMM correct~size*method+(size*method|family)，word LP线性；training另log(step)*method。
7. **结果/边界：** size交互analogical p=.009、grammar .0461、word .005，reflective不显著；Pythia部分flat、OLMo语法高需求约chance；training只analogical/word，另两域因末checkpoint高需求低而未测。CRT小模型候选相对正确但整体更偏atypical输出，说明候选成功不等于真实产生成功。家族size/data/architecture不全匹配、task-demand概念informal，公开数据潜在污染不保证method差不受影响；未因果定位attention或表示机制。作者强调选指标应服务构念，非所有场合必须用概率。
8. **可借动作：** 把测量方式与所关心资源/更新操作交叉，找可以推翻解释的交互；操作同一个目标对象，别由“更易成功”直接认证纯能力。
9. **对我们：** E71整句二候选概率是低需求关系选择，只能先回答正确P1消费路径的作用；它不是完整复述能力证明。E53/E67自然产生另提供功能用途证据，二者要连接而非替代。当前实验不追加一串形式控制；若E71候选已经满分，按预登记直接说明未重现生成失败，回真实断言脚印改问题。
