# E06：一句格式指令能否恢复可评分回答（2026-10-02）

- **状态：** DONE
- **类型：** REPRO / readout control
- **对应：** C01、P03；不是新的能力主张。
- **问题（一句话）：** E02 原生回答中语言相关的解析损失，能否由一条仅规定输出格式的指令消除？
- **设置：** 与 E02 相同1,200原题、Qwen2.5-3B-Instruct固定revision、三次temperature=.5采样。只在user prompt尾部添加 `Return only the letter (A, B, C, D, or E) of the selected option.`；不要求literal、CoT或strict logic。max_new_tokens=16，batch=32，四语言独立单卡。英文格式指令也是显式混杂，不能把差异归因于语用表示。
- **读数：** invalid/truncated比率；240 maxim和60 literal分开准确率；原生版本与控制版本成对逐题分歧，三次采样按item聚合。
- **阳性对照：** 1,200项oracle/wrong-label roundtrip；多语言结论、boxed、歧义解析fixtures。回答不唯一仍算invalid，不挑最终有利答案。
- **噪声地板 + MIE：** 以三次采样与item cluster CI描述波动；E02/E06 token预算不同，凡截断单独报告，不给能力MIE。
- **混杂审计：** 先保存原生response与原scorer hash；重解析生成独立派生文件。agent校对被改变的解析结果并保留不确定，未做独立人审。不以格式提示效果证明latent knowledge或criterion。
- **决策表（跑之前写）：** A invalid大幅下降 → 使用格式控制作测量对照，保留原生parent读数；B仍不能评分 → 列出原文/截断并调整readout，不能归因能力；C accuracy也变化 → elicitation confound，须同模型direct probability核对后解释。无论结果均不直接计算FPR。
- **算力预算：** ≤0.1 GPU·时，GPU0–3独立；用户授权0–7全部可用。

## 结果
待运行。添加指令与token budget在本卡落盘后运行；不回写E02原始结果。

### 技术失败记录
首次启动使用了不存在的模型目录 `models/qwen25-3b-instruct`，四进程均在加载权重前退出，模型回答数=0。失败日志保留；正确目录为 `models/Qwen2.5-3B-Instruct`。修正后另用 `E06-*-r1` 目录，不覆盖失败资产。
