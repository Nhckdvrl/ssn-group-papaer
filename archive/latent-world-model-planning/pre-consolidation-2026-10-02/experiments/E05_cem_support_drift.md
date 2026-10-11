# E05：Conditional planner-reachable support diagnostic（2026-10-02）

- **状态：** PLANNED
- **类型：** EXPLORE
- **对应：** I03；I02 已 PARKED
- **触发条件：** 只有 E06 / I03 显示 proposal/search/off-support layer 可能是 binding bottleneck 时运行；**不要作为独立 story 自动铺开。**
- **问题（一句话）：** 在已定位的 search-limited regime 中，CEM candidate distribution 是否出现 planner-reachable fidelity / support degradation，并且现有 P40-style fidelity / PLDM uncertainty 不能充分解释真实 false elites？
- **设置：** 固定 E06 checkpoint / task / H/K / candidate budget。每个 CEM iteration保存 candidates；对预注册 stratified subset做 simulator execution。
- **读数：**
  - behavior action-chunk kNN / BC likelihood；
  - P40-style planner-reachable prediction / plan-cost discrepancy proxy（能实现时）；
  - ensemble disagreement（PLDM-style，可用时）；
  - predicted vs real endpoint / utility；
  - false-elite rate；
  - candidate regret；
  - action norm/smoothness/bounds；
  - optional ACID/MEND score。
- **阳性对照：** 人工OOD action chunks必须让support/fidelity指标有响应；true-dynamics或真实执行能暴露人为 optimistic cases。
- **噪声地板 + MIE：** same candidate replay；cluster bootstrap by planning decision。只有“新增 metric / mechanism比P40/uncertainty显著增加解释力，并改变 intervention选择”才值得重开I02。
- **混杂审计：**
  - CEM iteration与action magnitude/smoothness匹配/控制；
  - candidate count/compute固定；
  - support metric不用test outcome调；
  - candidate subsample预注册；
  - H/K/scoring-index固定；
  - dynamics/checkpoint固定；
  - planner seeds完整。
- **决策表：**
  - P40 fidelity / uncertainty 已解释 → 保持diagnostic，不扩seed；
  - 存在稳定 residual failure law，跨至少2 tasks → 提议重开I02并新建idea amendment；
  - 相关性由action norm等平凡量解释 → 当前机制 REFUTED；
  - false elite本身不稳定 → 回E06，不造detector。
- **算力预算：** 主要evaluation；candidate execution先小subsample。  
- **实际：** 待运行

## 结果
未运行。