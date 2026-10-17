# Learning Domain Invariant Representations in Goal-conditioned Block MDPs — NeurIPS2021

- 主源：[正式论文](https://proceedings.neurips.cc/paper_files/paper/2021/file/06d172404821f7d01060cc9629171b2e-Paper.pdf)。已读§3的aligned sampling、§4方法／Eq4、表1／图4；§2理论只核对设定，Appendix C.5／E尚未精读，作者代码未复现。
- **正文事实：** PA-SkewFit在goal-conditioned Block MDP中学习对域变化稳定的表示。跨域执行同一action sequence得到aligned数据，MMD拉近、difference项防止坍塌，再结合VAE与SAC；实验aligned数据占15%，这不是应移植给我们的科学bar。
- **实验事实：** Reach／Door／Pickup／Push，训练三个视觉域，测试新视频背景；图4对齐loss／数据采样消融报告七seed。既测表示误差也测任务控制，未只依靠embedding距离。
- **idea来源与距离：** 保持任务功能与去除无关差异已有完整方法。persona文字编辑是否无关，依赖作者目标与当前游戏状态；E37当前只做诊断，没有证明一般语义不变性。可以借用matched action/state的方法，研究角色中应保持与应改变的实际功能，而非重新宣称首次稳健表示。
