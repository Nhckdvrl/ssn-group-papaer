# 整理检查记录

本轮检查拟提交的当前文件；没有把归档旧规则当当前规则运行。

- 当前顶层Markdown：6份（原21份）；README：54行。
- 当前E卡：9份、9个唯一ID；I卡：7份、7个唯一ID。
- 相对链接检查：71条，目标存在于拟提交树或已读取的保留/归档树；未发现断链。
- 新卡的状态、来源、对应、阳性对照、噪声说明、决策表字段及代码围栏：检查通过。
- 共享workbench登记表：原文件字节SHA已匹配；只修改latent这一行的备注，状态/目标/截止/其他行不变。
- 外部URL：保留定位入口，不宣称本轮逐个联网检查。
- 全量原目录预期归档tree：`68694221bb6aec22b5ea28d488893c36dbcf953a`；原CLAIMS与日志以原blob复用。最终发布通过读取Git tree/ref另行核对。

**未执行：** 全仓`tools/process/check.py`（容器无法解析GitHub，未拉取完整仓库）、GPU训练、环境数值复现。这些未执行项不计为通过。实际部署仍执行E00/E01与仓库检查。


## Final coherence pass after method hardening

Latest main observed during this pass: `21f4e5764540a01840cf30a69f5c7a2de7a4dd44`.

Current live latent-WM subtree:
- top-level Markdown = 6: README / RESEARCH_PLAN / LOCAL_AGENT_PROMPT / ASSETS / CLAIMS / PAIN_LOG；
- experiments = 9 unique IDs: E00, E01, E11, E13, E14, E16, E17, E18, E19；
- ideas = 7 unique IDs: I07–I13；
- literature = CORE_READINGS + index；
- old 63-file pre-consolidation tree remains archived.

Repository search over current workbench returned no stale live hits for:
- `Tier A1/A2`；
- `first-priority mining lane`；
- `Decision-Critical Branching`；
- old P01–Pxx literature-count authority；
- explicit “red zone / kill” execution vocabulary.

The current first-wave method names are:
- H-A / I12 / E16 = **Planner-Boundary Branching (PBB)**；
- H-B / I08 / E13 = **Planner-Stage Multi-Fidelity / Elite-Preserving CEM**.

Second-wave cards are now concrete:
- E17 Selective Query Specialization；
- E18 Utility-Gated Recovery；
- E19 Selective Revaluation.

Additional public-code feasibility checks:
- stable-worldmodel CEM exposes candidate / cost / elite tensors to callbacks；
- Fast-LeWM `get_cost` computes direct rollout and conditionally an additional decomposed/self-consistency rollout；
- TwoRoom / PushT / OGBench envs expose public state-restoration interfaces sufficient for controlled branch-bank experiments, subject to replay-fidelity validation.

Not executed:
- GPU training；
- environment numeric reproduction；
- full repository `tools/process/check.py` in a cloned runtime.

Therefore science claim remains 0 and status remains PROPOSED.
