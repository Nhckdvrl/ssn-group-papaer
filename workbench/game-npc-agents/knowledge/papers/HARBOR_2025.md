# HARBOR — IJCNLP-AACL 2025 Long 141

- 原文<https://aclanthology.org/2025.ijcnlp-long.141/>；作者<https://github.com/Emory-FLARE/HARBOR> pin9cf0b1d178d81da860389ab97df0c405a056f04b；PDF SHA08fc05eba4a70600b4c759eb5d6c122b366f7223baa43e72c6080c1dd8598b09。
- 已读§3环境/策略、§4.3–5主表/ToM、附录persona/ExpertAct与DPO样本设置；未本地复现。系统/策略研究，拍卖中的角色偏好、收益与社会推断，不是无状态问卷。
- **DOCUMENTED事实：** persona按住房偏好选择可能降低利润；Table1无persona34.56%，有persona31.75%，竞争persona25.22%。ToM/已知真实竞争persona可改变Master收益（Table2例23.45→35.81）。ExpertAct六条规则，RLAct/DPO使用约1k专家样本，表格预算/是否知真persona需分开。
- **RECONSTRUCTED来源：** 经济agent既要角色偏好又要应对竞争者→用角色条件拍卖与profiling评估策略。不能从低利润推出角色失效，角色偏好本来可接受经济代价。
- **源码事实/范围：** 阅读src策略/环境入口；README引用的root run_auction.py在本pin不存在，公开仓库仍在建设。现有模块不能自动声称完整复现主表；未执行API。
- **我们的解释/竞争解释：** persona×utility tradeoff和ToM提升均有owner；真实NPC的物理机会/自身目标仍需独立来源。完整代码、所有裁判/数据来源尚未逐行审完，已读范围不覆盖真实玩家体验。
