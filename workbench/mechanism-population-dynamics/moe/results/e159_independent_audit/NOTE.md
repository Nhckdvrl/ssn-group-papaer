# E159 独立 CPU 校对

对应 C14、实验卡 E159。独立实现 `audit.py`，未依据主分析器实现计算；当前仅运行合成小数据自检，没有读取 E159 科学 raw，也没有产生科学结果。系统 Python 无 NumPy；使用已有 `~/.venvs/mechpop/bin/python`，只导入 NumPy 和标准库，不加载模型或使用 GPU。

运行 `~/.venvs/mechpop/bin/python moe/results/e159_independent_audit/audit.py --self-test`：验证来源轴与方向、所有 8 个二进制依赖形态、恒定差值配对 bootstrap、33 题统计逻辑。实验完成并获执行信号后，用 `--output <输出路径>` 执行；它先验证 complete manifest、全部预算尝试状态和总费用、plan / 代码 / 模型小文件 / 任务 / 继承参考 / raw 的 SHA，再核对维度、来源、分科、固定队列、P 重放与参考身份。科学计算的 CI 为每学科内题目配对抽样 1000 次，seed 159001，学科等权；所有对比由同一题级抽样得到。次分析为固定 33 题，报告 pooled 与等学科权重及分科 8×8 转移，不给 CI。

输出中指标轴依次 raw accuracy、per-character accuracy、choice CE、真实答案的每 token NLL；主格轴为 R、S（P/A/B/zero），对比保留 A−P、B−P 的符号。准确率支撑为 full 减移除，损失支撑为移除减 full；balance 为 shared 支撑减 routed 支撑。所有模式均要求 full 成功，位 4/2/1 分别代表 D-only、仅 R、仅 S 正确；模式 0 是 D 和两条单路径均失败。

主分析器汇总结构与数值尚未提供，因此比较器尚未连接，尚不能声称独立校对通过或升级主张。此审计不区分参数固定时输入状态和下游路径的变化。

已独立复算 E155/E156 继承端点并比对 `known_border_posthoc.json`：4 指标、3 来源、完整质量及原生与移植支撑均一致；最大点误差 1.78e-15，分科点及总体/分科 CI 最大误差 3.55e-15，固定 33 题所有计数一致，三源参数和 buffer 哈希匹配。结果见 `known_border_review.json`。复现命令：`~/.venvs/mechpop/bin/python moe/results/e159_independent_audit/audit.py --known-border-review --output moe/results/e159_independent_audit/known_border_review.json`。这是事后重用旧端点，零新 forward，不能隔离固定 D/G 下伙伴替换的效应；未读取 E159 新 raw。

完整 E159 汇总比较器已按预先提供的无数值 schema 接入：在正式执行命令加 `--compare-summary <汇总JSON>`。比较全部预注册主表、支撑、固定伙伴、对角与原生对比，以及 33 题点值、模式和转移；输出最大点/区间误差与计数匹配状态。合成映射自检包含故意修改一个对比以验证能检测不一致；尚未读取任何 E159 新原始数据。

E150/E151 旧语言模型端点独立核对见 `known_lm_border_review.json`：所有点估计完全一致，20 文件簇 bootstrap CI 最大误差 1.78e-15；两源原生逐 token 重放、参数/buffer 哈希和有效掩码一致（30,994 个目标）。命令：`~/.venvs/mechpop/bin/python moe/results/e159_independent_audit/audit.py --known-lm-review --output moe/results/e159_independent_audit/known_lm_border_review.json`。背景包含 D/G 和另一分支，不能单独解释为伙伴作用；零新 forward。
