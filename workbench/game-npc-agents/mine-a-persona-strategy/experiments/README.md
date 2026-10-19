# 实验记录

**矿区A已终止（2026-10-19用户决定）。** 本目录仅保存历史设置、来源、对照和正负结果；全部旧“下一步”取消。先读[终止总结](../CLOSEOUT.md)，边界见[AGENTS](../AGENTS.md)，统计和资产见[结果索引](../results/README.md)。原DONE实验保持DONE，不为关闭改写历史；未运行E43及合作路径设计取消。

[合作路径设计](COOPERATION_PATH_DESIGN.md)已取消且从未运行，保留来源与竞争解释作为历史，不属于下面79张卡或执行队列。

## 编号与执行范围

- 当前79张实验卡的逐项索引见[本页完整索引](#all-experiments)。编号不是79项独立发现，也不代表79批互不重叠场景。
- E01是源码合约检查；E06是总体准入协议，不另计独立运行；E07–E77、E80–E85按各卡结果读取。
- E43为未运行的小MLP诊断；E42只有原八条件完成，追加规则知情条件未跑。LLM白盒的实际记录见E50/E52/E62。
- E78/E79没有实际结果。旧E00/E02–E05已按用户决定退出当前树，原历史见[旧版本](https://github.com/Nhckdvrl/ssn-group-papaer/tree/37f4e9ba4152c3a21c36c73830897221a186924b/workbench/game-npc-agents/experiments)，不恢复。

## 如何复核历史实验

主读数、正负结果、无效版本及改读数记录仍保留在原卡、结果JSON、[CLAIMS](../CLAIMS.md)和按日日志中。此次整理没有重跑实验、修改原图/种子或提高证据等级。

冻结旧执行线、作废版本和一次性调度脚本已从当前树清理。历史卡中的原命令、脚本名和SHA是当时的复现记录；需要完整旧代码时，按[scripts说明](../scripts/README.md)取清理前的精确Git版本，不能将当前缺少旧启动器解释成实验未执行。大raw和模型缓存仍按manifest保存。

<a id="all-experiments"></a>
## 全部实验卡覆盖索引

| 实验族 | 原始卡片 | 执行与解释范围 |
|---|---|---|
| 来源与总体协议 | [E01](E01-source-contracts.md)、[E06](E06-persona-strategy-baseline.md) | E01已执行源码检查；E06为统领设计，无独立重复run |
| 原生接口与准入 | [E07](E07-native-actioncastle-closure.md)、[E08](E08-pcsp-gradient-and-protocol-audit.md)、[E09](E09-viewpoint-grounding-control.md)、[E10](E10-strong-native-action-interface.md)、[E11](E11-light-natural-quest-native-gate.md)、[E12](E12-native-per-action-tool-loop.md) | 已执行，含PCSP初始源码审计 |
| LIGHT目标、抽样与自然冲突 | [E14](E14-light-author-goal-npc-episodes.md)、[E15](E15-intention-action-sampling-floor.md)、[E16](E16-native-private-goal-conflict-gate.md)、[E20](E20-native-two-character-resource-episodes.md)、[E21](E21-native-dialogue-action-protocol-control.md)、[E22](E22-native-storage-access-belief-control.md)、[E31](E31-native-human-goal-order-qualification.md) | 已执行；E22部分测量资格失败已降级 |
| PCSP读出、编码与短控制 | [E13](E13-pcsp-released-policy-native-rollout.md)、[E17](E17-pcsp-frozen-policy-readout-control.md)、[E18](E18-pcsp-focal-actor-attribution.md)、[E19](E19-policy-likelihood-identity-control.md)、[E23](E23-persona-encoding-context-invariance.md)、[E24](E24-native-policy-utility-under-encoding-context.md)、[E25](E25-corrected-baseline-gradient-route-pilot.md)、[E26](E26-semantic-role-control-qualification.md)、[E27](E27-role-code-versus-engine-body-attribution.md)、[E28](E28-auxiliary-feature-frame-control.md) | 已执行，旧执行线冻结 |
| PCSP功能、全预算与独立环境 | [E32](E32-semantic-selectivity-versus-weak-control.md)、[E33](E33-single-interest-compositional-control.md)、[E34](E34-full-budget-corrected-baseline.md)、[E36](E36-projection-versus-policy-response.md)、[E37](E37-matched-role-edit-functional-geometry.md)、[E38](E38-independent-strategic-environment.md)、[E39](E39-cross-role-direction-transport.md)、[E40](E40-preference-control-and-need-dynamics.md)、[E41](E41-interventional-persona-coverage.md) | 已执行；E41无效v1保留、有效版本完成；旧线冻结 |
| 生成式NPC与自然后续 | [E29](E29-native-generative-npc-physical-goal-gate.md)、[E30](E30-local-goal-planner-provenance-gate.md)、[E35](E35-original-three-npc-goal-loop.md)、[E44](E44-natural-duty-context-restoration.md)、[E45](E45-natural-persona-and-goal-adoption.md)、[E46](E46-grounded-plan-progress-control.md)、[E47](E47-dialogue-budget-confound-control.md)、[E48](E48-conversation-plan-update-ablation.md)、[E49](E49-cross-role-commitment-causality.md) | 已执行；局部人物和无实体终点边界保留；不再漫游 |
| 强LLM参考与未运行旧诊断 | [E42](E42-native-llm-persona-utility-reference.md)、[E43](E43-shared-utility-versus-preference-direction.md) | E42八条件已完成、追加条件未跑；E43仅登记未跑 |
| 一致人物与确认 | [E50](E50-commitment-decision-snapshots.md)、[E51](E51-stage-persona-causal-transfer.md)、[E52](E52-dialogue-goal-binding-causal-probe.md)、[E53](E53-direct-goal-status-versus-persona-choice.md)、[E54](E54-natural-dialogue-data-labels.md)、[E55](E55-independent-native-role-confirmation.md)、[E56](E56-native-state-belief-and-action.md) | 已执行；E52独立N=1，E54为DATA，E56纠正阶段范围 |
| 双角色、分量及因果诊断 | [E57](E57-native-private-goal-interaction.md)、[E58](E58-disposition-and-priority-components.md)、[E59](E59-fixed-history-state-invariance.md)、[E60](E60-common-commitment-native-choice.md)、[E61](E61-common-history-direct-decision.md)、[E62](E62-native-recipient-causal-diagnostic.md) | 已执行；语义与白盒负结果保留 |
| 目标资产与规则范围 | [E63](E63-native-dependency-and-explicit-priority.md)、[E64](E64-native-reciprocal-goal-negotiation.md)、[E65](E65-constraint-scope-and-permission.md)、[E66](E66-native-action-logit-competition.md) | 已执行；E64小N、E66概率与真实后果分开 |
| 真实执行与任务类型 | [E67](E67-stage-rule-physical-cross-swap.md)、[E68](E68-clean-reserve-rule-predictions.md)、[E69](E69-matched-task-and-motivation-window.md) | 已执行；E68独立图、E69已知图与适应性控制分开 |
| 请求方向、前提与后果 | [E70](E70-native-goal-request-and-execution-preconditions.md)、[E71](E71-unsolicited-authored-goal-baseline.md)、[E72](E72-native-candidate-feedback-and-goal-execution.md)、[E73](E73-equal-initial-native-feedback.md)、[E74](E74-physical-consequence-prediction-and-choice.md) | 已执行；同源图重复使用不增加独立N |
| 取物前提、固定历史与后果指派 | [E75](E75-native-retrieval-task-transfer.md)、[E76](E76-fixed-dialogue-and-native-access.md)、[E77](E77-dialogue-and-assigned-outcome-execution.md) | 已执行；E76/E77含复用，读数不双计 |
| 响应玩家、原作者合作与改约 | [E80](E80-responsive-player-and-grounded-execution.md)、[E81](E81-authored-cooperation-and-partner-response.md)、[E82](E82-minecraft-original-cooperation-baseline.md)、[E83](E83-npc-quest-receipt-and-reward-baseline.md)、[E84](E84-independent-goals-and-alternative-cooperation.md)、[E85](E85-partner-performance-and-revision.md) | 已执行；E82仅CPU、E83明确重建、E85后暂停 |
