# E01：公开源码的测量与执行边界检查（2026-10-13）

- **状态：** DONE（先在本地写卡，再运行；静态阅读发现已发生，不冒充预注册盲发现）。
- **类型：** REPRO / CPU artifact-contract audit，不是模型实验。
- **对应：** E00 的环境/评价准入；验证是否有资格将接口和曲线解释成游戏状态/一致性。
- **设置：** 固定 NCP metrics.py blob 4ba08045919c9860a35d7b14c6f1244bea71c43f 和 CPDC action_functions_0001.py blob a5eaf793635d1d7303d09997ea68540d12253aff。读取连接器返回的全文，本地字节哈希必须一致。仅抽取原 survival_curve 函数执行；动作文件只做 AST 检查，不导入 LangChain、不调用模型。
- **读数：** 相同记录长度、不同终止类型是否给同一曲线；长度改变时曲线变化；空集/负上限错误；零阈值；CPDC 指定文件动作函数是否只有 docstring+pass。
- **阳性对照：** 输入 1/3 回合时阈值2的通过比例应为0.5；改变真实 turn_count 能被测到。原函数空集和负上限保护须触发。
- **噪声地板 + MIE：** 确定性单元检查，无统计推断。MIE 不适用；每个 case 是接口合约，不是独立游戏样本。
- **决策表（跑之前写）：** 若 survival 只依赖时长→禁止将其单独等同完成率/矛盾 hazard；动作只有 pass→将该发行版登记为 schema/gold-replay 接口而非交易引擎。若 source hash 或控制不一致，停止、核对版本；不宣称论文结论作废。
- **算力预算：** CPU 秒级、不调用网络/模型；GPU·时=0。不启动用户服务器任务。

## 结果
2026-10-13 在当前工作容器执行：8/8 项源代码合约检查通过；Python 3.13.5；0 次模型调用，0 GPU·时。结果见 `../results/E01_source_contracts.json`，程序见 `../scripts/audit_source_contracts.py`。

两份文件的 Git blob 哈希与连接器返回值一致。只执行原始 survival_curve 函数，不导入整套 NCP；CPDC 文件仅做 AST 检查。合成输入是指标的单元测试记录，不是 NPC 研究数据。

按事前决策：NCP 曲线只能按到达回合阈值解释，需另报终止类型/推进；CPDC 指定样例只能视为动作声明，不能冒充交易引擎。没有模型性能结论、没有官方分数重现，不认为论文或竞赛因此失效；不提升任何 C##。E00 的完整基线准入仍未完成。

复现命令（从 workbench 根目录，输入必须是哈希一致的原文件）：
```bash
python scripts/audit_source_contracts.py --metrics /path/to/ncp/metrics.py --actions /path/to/cpdc/action_functions_0001.py --out results/E01_source_contracts.rerun.json
```

原始源文件未重新分发到本仓库；获取入口与 blob ID 见 `../knowledge/SOURCE_AUDIT_2026-10-13.md`。没有运行全仓库 tools/process/check.py；本检查范围仅为上述两个源码合约。
