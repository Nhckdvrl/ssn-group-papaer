# E157 独立 CPU 审计器

依据实验卡、冻结plan及run的存储接口独立实现，本次未阅读或复用E157分析源码；不是盲法设计审计。语法和合成已知答案自检通过，未读取E157科学raw或运行模型。

重算范围：全部12个固定组 full、subject标签构成的on/off复合、native重放；每格相对PP、同S下P_R及整bank的成对差；A/B同源/异源符号和相对整bank配套差；仅on-domain引用E156旧masked数据。每项在128全体和固定44题（36/8）上计算subject等权点值及seed157001、1000次subject-major成对bootstrap CI；校验来源身份、任务字段和native重放逐位相同。

真实使用须E157预算和manifest完整，先校验plan、E157 raw及E156 reference SHA，再读数据。主agent提供无数值summary字段后已接入逐项自动比较；差异返回非零。合成内存完整schema比较通过7020项，并验证故意篡改CI会被发现；真实结果仍未审计。首token全词表KL只存标量，不能重算词表分布，只能核对其汇总、差值与CI。

```sh
~/.venvs/mechpop/bin/python -B moe/results/e157_independent_audit/audit.py --self-test
```

完成后人工运行（不自动写结果文件）：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e157_independent_audit/audit.py \
  --raw "$HOME/mechpop_cache/e157_task_subbank_reintegration/scores.npz" \
  --previous-raw "$HOME/mechpop_cache/e156_common_parent_cross/scores.npz" \
  --summary moe/results/e157/summary.json
```
真实完成后运行：7020个点/宏平均与分科CI/来源对比误差≤1.7763568394002505e−15，全部通过（report.json）；此前7020合成检查与本次真实审计严格分列。首token KL只复核raw标量汇总，on-domain masked仍是E156继承，并非本次新前向。
