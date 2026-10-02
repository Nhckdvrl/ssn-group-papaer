# 概念与任务状态表征：近期论文卡

2026-10-03。全部数字为原作者报告，未复现。下列阅读强度分别注明；idea来源不混同作者私人灵感。

## Hierarchical Concept Geometry in Language Models Emerges from Word Co-occurrence

[2026全文](https://arxiv.org/html/2605.23821v1)，定向读动机、理论假设、实验及局限；NeurIPS2026目录收录，main未核。

- **形态/压力：** 对既有概念几何给出更简单的分布统计解释。DOCUMENTED动机是功能公理能描述几何，却未解释几何如何产生；RECONSTRUCTED动作是退到word2vec和共现这个更便宜模型，导出能在LLM再次检查的预测。
- **改变前提与近邻：** 对Park2025层级几何追问来源；对Levy/Goldberg2014 PMI视角加入层级kernel；对近期离散/连续属性共现理论扩展到hypernymy。其结果不等于否定LLM具有概念功能。
- **方法/数据：** WordNet子树、词共现、word2vec谱结构及Gemma2B unembedding；在衰减/正性等条件下预测粗到细的几何分离。层级统计是条件性模型，不是所有自然概念的完整理论。
- **资产/短板：** 没有核到完整公开code；大语料预处理可能比GPU更慢。先借成熟parent的向量和代码测量，不能把“无GPU训练”当无成本。
- **可迁移动作：** 用更弱模型/更简单数据机制解释强模型的现象；再检验剩余差异有无实际推理后果。“共现产生层级几何”本身已占。

## The Lattice Representation Hypothesis of Large Language Models

[ICLR2026正式页](https://proceedings.iclr.cc/paper_files/paper/2026/hash/208853db0e806d03f6be769a3fae1ecd-Abstract-Conference.html)；[全文](https://arxiv.org/html/2603.01227v1)，定向读动机、定义、数据与实验/局限；未逐行校验证明。

- **形态：** 理论构念+经验测量。DOCUMENTED来源为Formal Concept Analysis与Linear Representation Hypothesis；RECONSTRUCTED研究动作是把“类别有哪些成员”和“成员共享什么属性”放进同一表示。
- **近邻距离：** Mikolov线性关系、Park2024二元属性、Park2025类别层级提供parent；本工作增加对象/属性双视角及概念交并的形式化，不是首次发现层级。
- **方法/数据：** 五个WordNet域，三个具体、两个抽象；对象与属性向量、阈值和半空间形成可测概念关系。属性schema与矩阵由GPT4o生成并当作gold，不能转述成对人类概念结构的独立验证。
- **边界：** 形式化结构成立需要假设；几何重建不自动证明模型在自然推理中执行该代数。循环/连续概念线性假设可能不适用；代码supp声明与实际独立发布分开。
- **启发：** 一个自然对象可以支持理论与测量结合，但不应为了“数学感”先找lattice。优先可操作的问题与行为后果。

## Transformers Linearly Represent Highly Structured World Models

[2026全文](https://arxiv.org/html/2605.18847v1)；[代码](https://github.com/kameronton/sudoku-residual)；NeurIPS2026目录已见，main未核。正文方法与主实验定向阅读，附录部分核对。

- **形态：** 任务表示组织→回路→干预。DOCUMENTED从Othello单格表示转问约束满足任务的组织单位；RECONSTRUCTED动作是改变有科学意义的任务结构，看既有解释是否仍成立，而不只是换个游戏刷分。
- **近邻：** Othello线性world-state、chess/maze读出、Norvig式Sudoku求解轨迹；增量是表示按约束子结构组织并联系决策，不是首次probe出world model。
- **方法/数字：** 8层transformer；原作者训练后单格98.4%、整盘97.5%；分析行/列/宫与cell探针、干预和最后MLP中的naked-single回路。一个模型/任务的结论不能直接外推通用LLM。
- **资产：** 现成checkpoint、trace与脚本；复现不必重训。完整activation需本地重建，注意弱I/O；基础模型冻结但probe要拟合。
- **启发：** 选对研究对象的表示单位，比更换probe打分更有信息量；“Sudoku按substructure组织”及固定阈值跨step失真已属于本文。

## Large Language Models Develop Belief State Geometry In-Context（定位卡）

[2026-09论文](https://arxiv.org/abs/2609.17376)，正文/限制由本轮前段定向阅读；最终收尾复核摘要与目录，完整代码未找到。NeurIPS2026目录项，main未独立核准。

承接NeurIPS2024 toy transformer的belief-state工作，使用六个开放LLM和40个HMM，线性读出后做patching/steering及替代解释检查。DOCUMENTED前提变化是从专门训练到上下文推断生成过程；RECONSTRUCTED启发是用可求真值的隐状态检验模型如何压缩历史。它已经提供功能相关性证据，不能仅以“读得到是否等于用得到”宣称novel。20k-token设置和多层缓存有开销，代码未核使其不是首个开箱baseline。HMM在这里是认知实验工具，不把任务转成时间序列算法研究。
