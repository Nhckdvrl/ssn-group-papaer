# Localizing Task Recognition and Task Learning in In-Context Learning via Attention Head Analysis（ICLR2026，2509.24164v2）

**证据级别：正文定义/§3.2、§4.2开头、G.7/H.4逐段核对；余实验本轮未完整读。** [原文](https://arxiv.org/html/2509.24164v2)。Haolin Yang、Hakaze Cho、Naoya Inoue。

1. 形态：构念拆解＋head贡献测量＋消融/steering；不止定位哪些head降分。
2. 背景压力：head整体ablation accuracy不能区分能力环节；DLA最大值/和会混合label-space与correct-label作用。
3. 改变前提：TR明确为候选label空间识别，TL为该空间里text→label映射；不按两者名字直接认定先TR再TL。它们的数学定义不是广义的程序识别/执行。
4. idea来源（RECONSTRUCTED）：输入扰动TR/TL概念与组件研究不能互相解释，转为任务子空间几何量及分别可破坏的通道。正文结构不是完整发现日志。
5. 近邻：Pan/Wei的TR/TL，Wang/Cho induction与anchor，Hendel/Todd向量、Yin/Steinhardt specialized heads、Li just-in-time；本文已有alignment与within-space rotation、next-token TV局限。
6. 关键核对：label-unembedding span定义task空间，TR ratio为输出落该空间的比例，与accuracy分开；TR可晚于TL，因为task-label内部margin与task-vs-rest margin不同。H.4用Country–Capital+Antonym串行两个label空间，Task2 heads跨Task1消融；TR跨task较共通、TL较特化。不是同一label空间、不同Source函数的组合。
7. 短板/范围：head由预定top百分比及dataset读数选；TV参数/输出位置与反事实条件决定可消费内容，不可从几何自动读成完整算法。全文所有模型/数值本轮未复核，不用摘要列总规模作我们的证据。
8. 可迁移动作：先定义构念与读数，再让损坏不同通道产生不同签名；看到层序反常回到操作定义，别将位置顺序当推理顺序；同一表示可分类不等于下一任务可部署。
9. 对ICES：E77的copy与9−x共享数字label空间，operator-ID不等于该文TR。下一实验应区别函数识别、Source定位与数值应用，保持可能的查询型/全局function偏好解释；认出函数却不能apply尚未测，不能先宣布。若未来符号operator中间步骤有效，需越过已有JIT/next-token TV所有权，解释具体Source条件、接口与因果作用。
