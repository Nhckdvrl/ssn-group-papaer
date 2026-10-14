# PERSONA：组合人格控制的已有边界

- **来源：** [ICLR 2026 官方稿](https://openreview.net/pdf?id=QZvGqaNBlU)、[arXiv](https://arxiv.org/abs/2602.15669)、[代码](https://github.com/xcfcode/persona)。venue corpus 标为 Poster。
- **阅读：** §2.2–2.5、Appendix A.11–A.12/A.18–A.21；未逐条检查全部提示。PDF `/tmp/npc_persona_algebra_2026.pdf`，SHA256 `70bb33aefcde79827ae72be1d4c0bd27f7f3421664c0b23cbb34da7172b91dcb`。
- **论文事实：** 对比激活提取 OCEAN 方向，支持缩放、相加、相减及上下文系数动态组合。BFI-44 改写成情景回答，由 GPT 评分；Persona-Evolve 为100人物×8轮文本比较。A.11报告跨维副作用，A.18消融系数、历史窗口和稀疏阈值。组合性和动态调整不是空白。
- **源码事实：** pin `c947fc1b22ceda8a542048cd4e65e0c89850d686`，`eval/eval_bfi.py` 调用 `OpenAiJudge`；`scripts/eval_fusion_bfi.sh` 列出八个组合。已读 `eval/eval_dialog_ranking.py` 固定 steered=A、baseline=B，未见随机交换；不能外推全部实验有位置偏差。未运行 API。
- **解释／竞争解释：** 拥有语言人格组合控制；其评分是否预测单项利益改动后的原生策略仍须另证。PCSP 新组合失败也可能来自短训练、身体相关性或文本偏移，不能径称原型锁定。
- **idea 来源／距离：** E32显示改写稳健性与跨人物区分并存。可检验是否同时保留作者定义的单项利益编辑和实际回报；不冒领向量算术本身。
