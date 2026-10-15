# Wang, Hoogland, van Wingerden, Furman, Murfet (ICLR 2025) — Differentiation and Specialization of Attention Heads via the Refined Local Learning Coefficient

**原文**：[arXiv 2410.02984](https://arxiv.org/html/2410.02984)；[ICLR 页面](https://proceedings.iclr.cc/paper_files/paper/2025/hash/fad7c708dda11f3e72cc1629bb130379-Abstract-Conference.html)。**阅读范围**：正文前半；附录 F（设置）、G（种子）未读到。

## 问题与做法
把 LLC 限定到单个组件（权重细化 wrLLC）或单个数据分布（数据细化 drLLC），在 2 层纯注意力模型上跟踪每个头的复杂度随训练的曲线。

## 结果
- 各头曲线先相近、后分化；对曲线聚类可还原 previous-token / current-token / induction / multigram 等类型（“计算方式不同的头，发育方式也不同”）。
- 末态 wrLLC 低的头对应简单算法（induction、括号匹配），高的头记忆大量 n-gram / skip n-gram（multigram）；数据细化可把两个看似相同的 induction 头分开（1:6 更专门处理代码）。
- 发现 multigram 回路：第 0 层 multigram 头在 LM3 前后“忘掉”部分简单 multigram、转为辅助角色；部分 multigram 在 8.5k–50k 步从第 0 层迁到第 1 层；multigram 头与 induction 头之间的组合在 LM4 下降（竞争 / 重排的迹象）。
- 局限：LLC 估计在非极小点处的精度无保证；只在小模型；不讨论哪个头成为哪类。

## 与我们的距离
这是“组件群体发育”的最直接近邻，但在 2 层小模型、单种子为主。自然大模型里：组件分化何时完成、功能是否跨层迁移、为何某些组件早早锁定而另一些持续换人（E83 vs E90 对照组）——仍未解释。
