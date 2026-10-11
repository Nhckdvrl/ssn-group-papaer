# PCW与其再审：独立上下文的函数使用

- **主来源：** [Ratner et al., ACL2023 Main](https://aclanthology.org/2023.acl-long.352/)，[正文](https://arxiv.org/html/2212.10947)§2–3/4.2；[Yang et al.再审](https://arxiv.org/html/2305.15262)§2–3.2（接受状态未核）。2026-10-12读指定正文；没有重跑其代码。
- **研究动作：** PCW隔离窗口attention、复用position，query同时读全部窗口；原评价增加可见样本。再审引入等样本logit ensemble，发现多项分类分数相近；进一步用reasoning检查合并上下文是否保持逻辑关系。这是经验比较，不是PCW普遍等价ensemble的证明。
- **与ICES距离：** 不能首次宣称私有prefix可分开形成、query联合读取。E123保留globally distinct原position，来源分别有合法私人函数与输出词空间；没有复现PCW。它测试私有函数的共同使用，不是更多例子的长context方法收益。
- **idea来源/设计学习：** 单独规则可用不确保共同使用；先把需要共享的身份上下文与私人监督拆开。E124将无标签共同列表的可达阶段F/R交叉，整个query关闭而prefix可用时检验形成贡献。它仍需实际功能和graph no-op；列表不是已识别的binding ID，不把names-only失败当所有协调机制不存在。
