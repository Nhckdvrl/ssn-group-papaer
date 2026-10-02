# E05：公开 MultiPragEval 标签补充可行性（2026-10-02）

- **状态：** DONE
- **类型：** REPRO（instrument audit）
- **对应：** C02、P02
- **问题（一句话）：** 不改parent原数据，能否可靠补充inference licensing与逐选项语义类别？
- **设置：** 按原category×gold字母25格各取最小id英语题，共25；对标注者隐藏gold。独立标注：inference_licensed yes/no/ambiguous；逐选项 literal/pragmatic-supported/pragmatic-unsupported/contradiction/irrelevant/none-of-above；解释依据与置信度。先OpenCode免费模型两条provider；实际不可用则保存错误并用本地与人工复核先做feasibility。派生文件另存、manifest/hash/annotator版本齐全，原CSV不动。未获得可靠标签不跑SDT。
- **读数：** 接口成功/失败、schema通过率、标注分歧率、歧义率、5个literal题与5个maxim题逐条人工抽查；单纯一致不保证gold。
- **阳性对照：** 原paper明确解释的literal item id与quantity/quality示例作核对，但示例不进confidence评估；隐藏gold，避免标签自证。
- **噪声地板 + MIE：** 25条仅可行性小pilot；任何系统性误把None-of-above当literal、删除语境当unwarranted都会阻止全量标注。逐项保留歧义，无通过阈值自动升级主张。
- **混杂审计：** 不用受测模型答案当gold；annotation与测试行为分离；free-provider未知训练污染；模型标注只作草案，缺human独立审阅明确标出；API不是主模型评测依赖。
- **决策表（跑之前写）：** A rubric稳定且核对通过 → 版本化派生标签再决定matched-context扩展；B 分歧/不可识别 → 修rubric或保留graded/ambiguous，不硬二值化；C free API不可用 → 本地annotation路径继续，不付费/不绑定凭据；不确定 → 人工抽查全部25条再决定。
- **算力预算：** 免费文本请求与本地小批 <0.1 GPU·时。**实际：** 待记录。

## 结果
待运行。

### 运行前冻结（本地 fallback）
OpenCode v1.18.34 官方CLI已安装；mimo-v2.5请求server error，big-pickle、mimo-v2.6、普通CLI模式均403 FreeTierError；不绕过限制。现用Qwen2.5-3B-Instruct与Qwen3-4B各自独立标注全部25条（同一家族，不能当独立gold）。revision分别aa8e72537993ba99e69dfaafa59ed015b17504d1、1cfa9a7208912126459214e8b04321603b3df60c；greedy、max_new_tokens=1024，batch=5，Qwen3 enable_thinking=False仅用于辅助标注。验证JSON/schema、统计分歧；人类复核尚未完成，派生标签不进主实验评分。GPU4/7，预计<0.1 GPU·时。
