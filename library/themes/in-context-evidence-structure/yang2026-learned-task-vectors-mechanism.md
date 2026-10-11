# Yang / Cho 等：Task Vectors, Learned Not Extracted（ICLR 2026）

原文：https://arxiv.org/html/2509.24169 （当前v3）；会议信息：https://proceedings.iclr.cc/paper_files/paper/2026/hash/79ada0f9bc4e41192ad5a80d13c8ca7e-Abstract-Conference.html 。2026-10-11读§3、§4.1–4.3；未穷尽58页附录和代码。

- **问题/idea来源：** 既有抽取TV随层、位置高度不稳定，又没有解释TV怎样作用于模型。先直接训练更有效的任务状态，再反推其计算作用；这是正文论证次序，不是作者真实发现历史。
- **方法区别：** LTV以真实query-label监督优化注入向量，不是从模型自然ICL状态无监督抽出。多层/多位置设置各有不同向量；不可将构造性成功升级为原生早已拥有同一计算。
- **有信息量的转折：** 跨任务相似性提示label space限制迁移；SNLI→RTE可迁移而到其它任务弱。English→French与Masculine→Feminine的向量相加可改善组合任务。因此完整函数运输、标签坐标依赖与某些组合能力都已有强近邻，不能由ICES命名为首次。
- **机制链：** 将TV经OV变换的合成消息作为新注入向量，并恢复末层残差项；能恢复相当效果，MLP版本较弱。用有TV时saliency选top10% heads，与随机10%消融比较，检验实际消费者。之后用噪声探测拟合线性transport，比较早/晚注入的旋转与缩放作用。
- **证据审计：** norm匹配本身不保证on-manifold；saliency选出的heads服务于已训练TV，不等于原生ICL完整电路。线性reconstruction是在测试的注入附近支持近似，并非所有ICL全局线性。作者承认多层、多位置并非处处有益。
- **设计学习：** 提高一个构造接口的作用不是终点；用机制重建、替代路径和必要性检验去解释作用，且把早/晚状态分开比较，而非把某一成功读出当规则本体。
- **ICES具体距离：** E56逐层query模块、E56c标签依赖与E94完整Source-field切换，都不能单独成为新TV理论。E102已说明其中一个有效接口主要为地址。E105检验的是从来源分组必要的私人示例中推断的共同criterion，能否与另一Actor独立私人映射组合；其阳性仍需解释形成与消费，不能仅因有不同cache称novelty。
