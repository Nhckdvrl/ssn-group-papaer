# On the Position Bias of On-Policy Distillation（作者v1，接收未核）

`[证据级别：主文精读＋方法附录]` [原文](https://arxiv.org/abs/2606.22600v1)。Xidian/Georgia Tech/Amazon AGI（非Amazon内部工作）；21页，SHA d11b842811c501f1281046a79a5113d5ca1f8a0ee4b376134708b1dc2665eb93。当前arXiv v3已存在，本文卡仅所读v1；未核最终实现或接收。

1. **形态/问题：** 标准dense OPD在学生长轨迹后段收到质量较低的teacher监督→局部预算投影解释→自适应加权方法及训练。不是只报告position bias。
2. **idea来源（RECONSTRUCTED）：** 前30% token监督约等于全轨迹，后30%几乎不学，引出teacher对偏离自身分布的student prefix未必可靠；由有限更新预算导出将更多梯度分给仍兼容teacher的prefix。与通常“越后越接近答案越有价值”的直觉有距离。
3. **近邻：** GKD/MiniLLM/ExOPD有on-policy及reward设计；token选择/entropy credit已存在；新对象是当前prefix compatibility而非局部token entropy。普通token重加权与signed cancellation不能由我们再命名独占。
4. **理论/实现区别：** 理论teacher/student prefix likelihood-ratio半梯度须stop-gradient，不是完整轨迹梯度的无偏实现。实际使用累积绝对logprob差/全轨迹绝对差份额，权重1+0.5(1−累积份额)；这避免signed cancellation，单调衰减但并非精确density-ratio correction。原OPD作floor，不能说丢掉全部后段监督。
5. **训练/数据：** Qwen3 0.6/1.7/4B、4B/30B-A3B teacher，另235B→30B-A3B大规模表；DeepMath难度≥6约57k/Eurus code约25k，32GPU/4节点、batch1024、lr1e-5、response16384、3种子配对。数学mean@32、代码greedy EvalPlus；每10步以AIME24/25验证选择converged checkpoint，因此AIME并非完全未用作选择的test集。
6. **结果：** 30B→4B step10 AIME25 +6.9，最终平均+1.7；不是所有setting均+6.9。表4 adaptive+5.6，fixed30%+.4、linear+.7、manual+1.5；ideal ratio alone−1.2、blend+.6，实用surrogate alone+2.9。理论target不直接胜过工程代理，需承认这个间距。
7. **质量边界：** 三seed均值但主表未给完整CI；same-family为主。附录E称仅4B、future larger scale，和主文235B→30B新增表不一致，不能据附录抹去大模型证据，也不能假定文稿所有细节已同步。
8. **阅读范围：** main1–7 pp1–10全部；AppB算法及C设置/训练/评测 pp19–20全部、D/E p21全部；AppA只读末尾半梯度/stop-gradient pp18–19，不声称全部证明已核。表4 p9视觉核对；代码未读/run。
9. **对I07：** 不能讲普遍“prefix坏，suffix好”。这里监督学生生成轨迹，我们评分含有必须改读前缀的固定观察；可靠位置依赖评价对象和修订关系。若我们的故事只剩token权重则距离很小；若能揭示语义修订credit具体如何与被解释前缀竞争，才是对象和机制上的增量，不因主题相近关线。
