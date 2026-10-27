# E156 独立 CPU 原始结果审计器

依据实验卡与原始存储字段独立编写；本次未重新读取或复用作者分析实现，也未读取正在运行的科学结果；此前在静态接口审阅中曾接触该文件。
真实审计应待完整 raw、summary、manifest 和预算全部 complete 后，由主 agent 手动执行：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e156_independent_audit/audit.py \
  --raw "$HOME/mechpop_cache/e156_common_parent_cross/scores.npz" \
  --summary moe/results/e156/summary.json
```

程序先验证预算/manifest完整、raw路径和SHA及summary绑定，再逐项对比各格及native的 raw/per-char准确率、choice CE、真实答案token NLL、预算损伤、PP差、AB配对对比、分科与等权macro的1000次配对bootstrap CI。校验PP复用和共同成功集由原native full计算且36/8。无任何写入；不一致会返回非零并列明差异。

局限：raw只保存全词表首token KL标量，未保存概率分布；可复算其汇总和对比及CI，不能独立从概率计算该KL或确认模型前向。四选项 score KL可从raw重算。

CPU合成最小自检：`~/.venvs/mechpop/bin/python -B moe/results/e156_independent_audit/audit.py --self-test`；覆盖已知分数/答案长度、KL恒等、AB方向及排除PP、双科等权bootstrap。未运行真实结果审计。
