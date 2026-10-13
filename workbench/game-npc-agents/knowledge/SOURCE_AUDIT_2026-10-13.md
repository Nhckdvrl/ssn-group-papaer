# 源码与实验使用范围审计｜2026-10-13

这是**使用资产的边界审计**，不是对论文作者的有效性判决。公开 sample 不代表私有官方评测；论文、README、后续代码的版本不可混用。

## 一、实际读取的源码/资料

| 来源及相对路径 | Git blob | 本轮范围/判断 |
|---|---|---|
| NLP2CT/NCP-Bench: src/ncpbench/metrics.py | `4ba08045919c9860a35d7b14c6f1244bea71c43f` | 全文读取；E01 抽取原始 survival_curve 执行；按记录长度而非终止标签计算 |
| NLP2CT/NCP-Bench: src/ncpbench/evaluator.py | `c65c03cbd98e57bf3d6d5f6c737cd98398ca2397` | 110–300 行：模型抽事实、判冲突/复核、判轨迹/承诺，不是独立游戏物理状态 |
| KomeijiForce/Codified_Decision_Tree: codified_decision_tree.py | `418db7bde3aca65e9e2251df4ba969d6766a5cb9` | 1–210 行：模型加载、默认配置、数据对齐/切分入口 |
| KomeijiForce/Codified_Decision_Tree: run_benchmark.py | `6d5318065014f21ebf37c6b473bdcb2ef29c1db8` | 1–265 行：语义条件判断、grounding 后生成、与原作行动 NLI 评分 |
| MahammadNuriyev62/CPDC-challenge-2025-solution: function_call_langchain/action_functions_0001.py | `a5eaf793635d1d7303d09997ea68540d12253aff` | 全文读取；E01 AST 核查 sell/equip 声明，没有状态变更实现 |
| 同一 CPDC 公开实现: function_call_langchain/executor.py | `a587083041f511ac62a29d2c024f910a83b54432` | 全文：sample gold matcher；作者明确与真实官方 evaluator 不同 |
| 同一 CPDC 公开实现: local_run_task1_test.py | `57b4fc4957fff6fb526c2c3724d5a41e6258ea9f` | 全文：参考历史/返回、本地归一化匹配，不是完整 on-policy 游戏评估 |
| yoosunghong/pcsp: research/docs/evaluations/independent-behavior.md | `d472e016b2c973bf3d77b2497013df55ed589e49` | 全文协议/作者结果，不等于我们已经读完或重跑相应 evaluator 源码 |

可按 `https://api.github.com/repos/OWNER/REPO/git/blobs/BLOB_SHA` 获取上述版本，并按 Git blob 算法校验。原作者全文/源码不在本 workbench 重新分发；仅提交我们的审计程序、记录与小型结果。

## 二、E01 实际做了什么

连接器读取的两份完整源文件放入当前工作容器后，以 `SHA1('blob '+字节长度+'\\0'+原始字节)` 与上表 SHA 核对。分别为 6413 与 990 bytes，匹配通过。

执行 [scripts/audit_source_contracts.py](../scripts/audit_source_contracts.py)：只抽取 NCP 的原始纯函数，不导入有外部依赖/服务的完整包；CPDC 文件只解析 AST。八项检查全部通过，结果在 [E01_source_contracts.json](../results/E01_source_contracts.json)。复跑结果一致，Python 3.13.5，0 次模型调用、0 GPU·时。

输入是确定性的指标合约记录，不是自然游戏 episode，不构成任何 NPC 能力证据。此处不存在统计“显著性”；8/8 也不是 task accuracy。

## 三、它为什么仍值得现在做

这一步及时排除了后续会浪费大量算力的对象混淆：接口名字像交易，不代表交易执行了；状态字段结构化，不代表真值独立；运行更长，不等于完成任务。我们据此修正测量说明，而不是把三条工程常识包装成论文发现。

E01 只完成 E00 的一部分资产门槛。完整 baseline、数据获取许可、自然场景统计、模型部署、GPU 预算和真实轨迹都尚未完成。未运行整个仓库的 `tools/process/check.py`，不宣称仓库全局验证通过。
