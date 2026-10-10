# In-Context Learning as Conditioned Associative Memory Retrieval（ICML2025）

[会议记录](https://proceedings.mlr.press/v267/wu25k.html)，Wu / Hsiao / Hu / Zhang / Liu。2026-10-11经官方PDF读§3.1–3.2，全文临时缓存`/tmp/ices_wu25k.pdf`；其它实验/证明未完整读。

- **idea来源（RECONSTRUCTED）：** 将条件均值/Bayesian averaging代理attention写成Hopfield memory reshaping；再用ghost examples保持接口、比较有无真实context的等效K/V变换。
- **已占据范围：** context可改变匹配几何与value内容；不只通过新的答案词复制作用。ICL的宽记忆条件化解释早已存在。
- **方法边界：** §3.1 Remark 3.1明确式(5)是可分析的proxy，不是实际LLM attention；Gaussian线性模型的等效变换不能直接充当原生多Source算法的证据。Ghost inputs通过优化构造，同样不证明模型天然执行该构造。
- **对ICES：** 若提出retrieval metric/teacher空间的constructive operator，必须承认它可能新增了Task推断，随后另检验原生过程；不能因控制改变q/k就叫新算法。E97先辨别Goal、输入与答案形式，避免在尚不明确的对象上设计越来越细的projection。
