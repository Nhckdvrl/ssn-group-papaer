# Rethinking Label Consistency of In-Context Learning（2026-10-11核对）

作者Haoyang Chen、Richong Zhang、Junfan Chen；原文：https://arxiv.org/html/2512.12175v1；AAAI 2026官方：https://ojs.aaai.org/index.php/AAAI/article/download/40273/44234。

正文§Methodology/Label Propagation、实验§Analysis of Label Consistency已核对。论文从Bayesian latent concept和transductive smoothness推导语义相似/label一致的意义，设计TopK-SD示例检索/合成方法，测分类性能与label consistency。未以原生activation interchange证明label-to-label attention就是传播算法；其latent concept与传播权重为理论框架，不能把它当未测量的原生电路。

idea来源（论证重建）：TopK语义相似未保证监督一致→把检索质量转写为label传播误差→将label信息加入检索embedding→验证方法。其认识所有权包括label consistency/传播视角，不能用“pooling”一词包装ICES新意。

ICES具体距离：本项目有合法相反私人规则，不能假定相似评论应全context共用一个label。query仅访问本Source之后是否仍继承其它Source关联，是不同的原生形成反事实。这里需要新的因果解释，并非原文方法失败或理论错误；Source条件化的smoothness假设须显式限定。
