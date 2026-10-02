# E05：translated-qa-supervision-audit（2026-10-02）

- **状态：** DONE（仅CPU资产审计，不启动额外GPU训练）
- **类型：** REPRO（有效translate-train竞争基线的准备）
- **对应：** P03/P04
- **问题（一句话）：** 官方SQuAD德语译料能否为固定英语监督池提供结构上有效的生成式QA监督？
- **设置：** E03固定16384英语train与E04固定4096独立new单位；同官方XTREME对象generation1591613668067959及SHA256。按原始ID核对，不重新翻译、不按模型分数选择。现有tokenizer与E03完整单位1024长度门槛，仅报告不重写任何实验输入。脚本 `scripts/audit_translated_qa.py`。
- **读数：** 各池官方ID覆盖率、非空答案、原始offset精确匹配、任一答案字符串存在于context、完整prompt+answer长度≤1024、满足以上条件的共同监督数；每个失败原因均报告，可重叠。保留逐ID审计在ignored artifacts，轻量汇总及hash进git。
- **阳性对照：** 英语原始SQuAD train同样执行offset/containment检查；ID唯一性和官方对象hash必须通过。完整输入长度不以gold选窗。
- **噪声地板 + MIE：** 固定有限语料的确定性计数，无统计CI/seed方差；有效覆盖是否足以构建预算明确的竞争基线由实际数量决定，不把5%等比例当科学否决器。
- **混杂审计：** 字符串/offset有效不证明语义翻译正确；官方MT缺失原因未知。未来监督训练必须独立预注册共同样本及预算，不能把本卡生成的幸存集合偷换为E04 CPT；CPT仍不使用答案。
- **决策表（跑之前写）：** hash或ID来源失败→停止；结构可用→后续有意义训练比较独立注册；大量缺失/损伤→先建立有效监督而非宣布翻译无用。结果不升级新idea。
- **算力预算：** CPU≤0.2小时，GPU0。 **实际：** GPU0，CPU审计完成。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 运行校对：首次CPU进程在输出前主动停止，长度实现未显式复用E03的BOS/答案strip/EOS编码。改为直接调用冻结的 `qa.encode` 后重跑；没有GPU、结果或训练池变更。
- 数字：EN16384全部offset/containment/长度通过；官方DE可取得15449，5个空答案、2个完整单位超1024，15442有效（94.25%）。E04固定4096独立new单位中4095合规，1个DE完整单位超1024。
- 结果文件：`results/e05_translated_supervision_audit.json`；逐ID audit在 `artifacts/qa_learning/translated_supervision_audit.json`，hash在汇总中。
- 按决策表：有效translate-train资产存在；后续训练独立预注册预算与样本，不改变E03/E04输入。本卡只确认结构，不证明语义正确或方法更优。
- 主张变化：无C##升级，无新idea。重跑曾因translated记录缺少id在输出前失败，补id后完整通过；失败不是可用结果，不隐去。
