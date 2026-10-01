# E05：CEM support drift → model optimism → false elite（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I02
- **问题（一句话）：** CEM 每轮优化是否系统把 action candidates 推离行为数据支持，并随后出现预测乐观、false elites 与真实 environment regret？
- **设置：** E01/E02 logger 校准后；先 TwoRoom + PushT（或当前可用的 navigation + contact-rich task）。每个 CEM iteration 保存 candidate；对 stratified subset 做 simulator real execution。support 至少两种：state/history-conditioned action-chunk kNN 与 BC log-likelihood；若 PLDM ensemble 可接入再加 disagreement。
- **读数：** stage-wise support score；predicted latent cost；encoded-real cost；true environment utility；optimism gap；false-elite rate；candidate-set regret；action norm/smoothness/bound violations；可选 ACID consistency / ensemble uncertainty。
- **阳性对照：** 从数据动作加大噪声/随机替换构造显式 OOD action chunks，support metric 应显著下降；true-dynamics scoring 或真实执行应暴露至少一类人为 model-optimistic candidate，否则 optimism 工具不可信。
- **噪声地板 + MIE：** 同 start-goal/candidate replay 重复；bootstrap over planning decisions/episodes；先在 E02 获取 rank/regret floor。MIE = support drift 在控制 action magnitude 后仍能预测 future false-elite/regret，并在至少两个任务方向一致。
- **混杂审计：**
  - planner iteration 与 action magnitude/smoothness同时入模/匹配；
  - candidate count/compute 固定；
  - support metric 不用 test utility 调参；
  - environment true utility 与 latent score分离；
  - candidate subsampling按预注册层级，不事后只执行“最怪”的；
  - dynamics/model checkpoint固定；
  - CEM random seeds完整记录。
- **决策表（跑之前写）：** support 下降先于并预测 false elite/regret → 扩 seed + uncertainty/ACID controls；false elite 有但 support 不解释 → 并入 I03 metric/dynamics lane；简单 ensemble/behavior prior 完全修复 → 记录强 baseline并 PARK复杂方法；相关性仅由 action norm解释 → REFUTED 当前机制。
- **算力预算：** 主要 evaluation；candidate real-execution 是瓶颈，先固定小 subsample，再按 CI 扩；各 eval group 独立单 GPU/CPU env。　**实际：** 待运行

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：未运行
- 结果文件：待生成
- 按决策表执行了什么：待运行
- 主张变化：无
- POST-HOC 分析：无