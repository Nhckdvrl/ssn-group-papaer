# E16：Hu同题训练阶段解释前的elicitation对照（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 confound control
- **对应：** C02、P06；E12 bare输入可能不适合post-trained模型。
- **问题（一句话）：** 同题numeric choice的stage或模型差是否在其正常chat接口和明确答数指令下恢复或反转？
- **设置：** Qwen2.5-3B、Qwen3-4B、Qwen1.5-14B及OLMoE Base/SFT/DPO，revision沿用原卡。Hu原1,365×各checkpoint，问题、选项、五order保持原样；统一prepend “Reply with only the number of the selected answer.”，causal用各官方chat template、关闭thinking、无额外special tokens，Flan相同prepend但encoder原格式。与bare原读数paired，不做generation/CoT、不换gold。
- **读数：** 各phenomenon gold probability、argmax、human JS/modal、order稳定度与bare差；保留全部项与no-story单独condition，item cluster CI。Base template若不存在或tokenizer变更则显式失败，不发明template。
- **阳性对照：** 每项source data SHA和原choice mapping一致；单token numeric断言；各job固定首末batch1/8概率delta<1e-3。原Flan选择与author匹配作为bare仪器对照。
- **噪声地板 + MIE：** frozen deterministic；bootstrap2000 item draws seed0；stage同源checkpoint不是训练seed，不给普适RLHF因果CI。
- **混杂审计：** chat/directive改变elicitation，不等于语用representation变化，也可能改变任务解释。bare/chat不比较全输入token hash相等；stage同condition比较才核对token SHA。恢复只能削弱能力缺失解释，不能证明模型知识完全正常。无binary warrant，不能从恢复推导criterion。
- **决策表（跑之前写）：** A stage排序/差仍在 → 削弱bare-interface失配解释，许可与human歧义仍未控制；B差恢复/反转 → 把当前stage能力解释降级为elicitation依赖；C只个别phenomenon → 登记边界，不把平均差当unified policy；D control失败 → 不进入解释。
- **算力预算：** GPU5/6/7在E14后先三小模型，GPU3的14B在E15后；OLMoE各卡在E12同卡后接chat。独立单卡FP32，各≤90GB；无训练/API。资源锁保证与已排队stage不重叠。

## 结果
跑前冻结。用户要求精准实验，这个对照是E12 stage归因的前提，不预设任何结果方向。

### 开跑前补充：OLMoE共同模板
三stage下载尚未完成、尚未开始E12/E16 stage推理时冻结：Base无原生chat接口，因此OLMoE三stage的chat condition全部使用官方SFT tokenizer_config已发布的同一个chat_template，仅替换template字串，不改各checkpoint tokenizer词表。这是相同输入呈现的受控对照，不能叫Base的正常chat接口。记录template来源、各输入token hash；template未提供或同condition token不匹配则该stage比较不成立，不临时发明模板。其他Qwen仍各原生template。

完成范围校对：Qwen对照完成；旧OL聊天模板字符串不足控制BOS/special映射，相关stage解释隔离；E27完整tokenizer修正协议单列，不覆写旧run。结果E22-E26-stage-controls.json与E27-token-matched-stage-summary.json。
