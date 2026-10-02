# Cognitive Models Can Reveal Interpretable Value Trade-offs in Language Models (ICLR2026)

来源：[primary](https://proceedings.iclr.cc/paper_files/paper/2026/hash/dc74a7c09fcf71705f433b52067edc05-Abstract-Conference.html)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** v4正文1–10页和附录C.1/C.2已读，其余HMC/附录未全读；many-wolves repo ab174020e19d0974518485cc70a54e26fb366152已核对。作者Kempner blog全文已读，2025旧版不能代替2026v4。
2. **背景与压力：** Alignment改变多种交际目标，不是单一有用性scalar。
3. **改变前提 / idea来源：** RSA S2把informational/social/presentational weights与rationality分开拟合。DOCUMENTED：polite speech和决策模型移植。
4. **方法 / 数据 / 证据：** Qwen2.5-7B/Llama3.1-8B×HH/UltraFeedback×DPO/PPO；另9闭源模型×4goal×3role。literalθ从自身52次yes/no Beta-binomial估计，4NUTS chains；holdoutMSE .03 vs random .06。
5. **短板与校对：** 预测fit不是latent参数因果identifiability证明；数据、reward model、algorithm联动。Early训练shift、goal prompt effect与generic偏好已拥有。
6. **最近邻与claim ownership：** 泛post-training moves inference policy不是贡献；若要解释语用边界，需固定speaker、候选命题与norm，在不同epistemic/QUD条件验证结构。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
