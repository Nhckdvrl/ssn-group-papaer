# I14｜有限数据下保留真实动作后果（2026-10-04）

- **状态：** PILOT；方法增量尚未确认，不登记科学主张。
- **对应：** P04/P10、R1/R2/R4；人审建议首选。
- **来源：** 强充分训练base38/48与弱base差异；FIRM common-reset、SMWM/AD-WM动作表示；反馈要求连续发展完整方法。
- **研究动作：** 分解公共预测误差与分支后果误差，联合训练表示/动力学；检验动作方向/历史的必要性，再改结构。
- **如果为真，主张是：** 有限经验下，训练应保留控制可用的真实后果差异，而非无条件最大化原始动作可恢复性；这是待验证观点。

| 近邻 | 已有内容 | 待验证增量 |
|---|---|---|
| SMWM/AD-WM | joint encoder、真实/预测端点inverse/action recovery | 同数据充分训练概率inverse之外的后果机制与闭环收益 |
| FIRM | common-reset branches、配置/动态记忆分离、多horizon物理监督 | 像素监督权限一致、作用共享而仍保持动态可控性 |
| 动作抽象/结构化动力学 | action equivalence、state-dependent effect、bilinear控制 | history/action相关结构在现代像素WM的新查询/新目标价值 |

- **最便宜pilot：** [E20](../experiments/E20-action-consequence-learning.md)，先合法动作完整小branch bank/重复一致性，再同数据plain vs effect/inverse训练；不把数据诊断当方法证明。
- **不同结果的信息增益：** plain已解决→方法loss不包装，研究数据组织；probabilistic inverse解决→作为强基线；相对后果误差下降但闭环不变→修任务/部署接口；动态丢失→加入history/action依赖，不能降秩整个方向；有稳定control gain→新goal/第二task/新评估集确认。
- **阳性对照：** 同动作重复与跨动作真实轨迹、非接触agent移动；隐藏状态只诊断，不额外训练某个方法。
- **噪声地板：** primitive state/pixels重复误差，独立training seeds；candidate pairs按anchor聚类，不能伪重复。
- **预期论文形态：** 重要动作后果问题+可训练结构/目标+强同数据对照+控制证据；单独centered loss不是novel贡献。
