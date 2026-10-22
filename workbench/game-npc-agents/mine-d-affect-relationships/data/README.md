# 人物适应学习的数据入口

本目录只放数据契约和划分政策。第三方原文、原生训练样本、SQLite、导出训练集都在仓库外；统一位置和revision见[ASSETS](../ASSETS.md)。不重建合成故事，不将发布训练资料改称官方测试集。

对应方法候选：[D-I01](../ideas/D-I01-learning-character-adaptation.md)。目前提供**单步更新示范与后续任务连接**，没有开始训练，也没有生成新的成长金标。

## 三种对象分别访问

| 对象 | 数据来源与接口 | 可用于什么 |
|---|---|---|
| 更新器输入 | 原生更新任务前两条system/human；`update_messages(row)` | 人物旧状态、已发生的完整场景、场景起点动机；不含assistant目标或未来任务 |
| 状态监督 | 同记录assistant；`update_target(row)` | 原生SFT目标或评测参照；明确在输入之外 |
| 后续互动 | 同人物下一发布出场的动机/互动任务ID；`future_readout_ids(store, id)` | 后续行为学习/评测的来源入口；不自动拼入更新器输入 |

**同场景互动不是该场景末更新的未来查询。** 当前场景已发生的行为已经在更新输入里，再预测它们不能证明变化迁移。下一出场的原生动机与状态仍可能是教师提供，使用时应标明哪些是输入、哪些是待预测对象；本接口不将其全部拼成一个无区分prompt。

每条视图记录保留原生row ID、作品/人物/场景、输入与目标hash、原文件记录hash、变化标志、后继引用及前后态连接读数。只保存指针，不复制整个4.18GB源文件。调用原生数据仍由`ExperienceStore.get()`逐记录核对原字节hash。

## 划分与来源资格

[固定政策](adaptation_view_policy.json)先于新模型运行保存：已检查模型结果的9作品只作`observed_development`；其他作品按固定SHA排序，前6部`test`、之后4部`validation`、其余`train`。整部作品及全部人物归同一划分，不按更新标志、角色出场次数或模型效果筛题。

这些名称是**我们后续训练的内部划分**。所有材料都来自EvolvingWorld发布的`train`，既有专用模型可能已经训练过它们，基础模型预训练也不受此隔离认证。`test`不能称未见IP或官方held-out；发布基线如已见这些书，应单列暴露身份。已公开阅读的参考资料也不能宣称完全盲测。

相邻连接保留发布文件的数字顺序。状态字符串衔接只证明发布资料内部接续，**不证明原著时间顺序、人物可知范围或因果充分性**。详见[来源资格](../results/D-EW-SOURCE-QUALIFICATION-2026-10-22.md)。旁白类条目也保留，未认证全部是可扮演NPC；后续实验如需要角色资格筛选，应在运行前规定并保留排除清单。

原生`profile_updated`是老师的持久变化判断。false也可能有情绪、动机或隐含压力更新；true不等于“好成长”。两类都保留，其数量不是模型准确率。

## 重建与使用

```sh
python3 workbench/game-npc-agents/mine-d-affect-relationships/scripts/build_adaptation_views.py --index /var/tmp/ssn-game-npc-d/data/EvolvingWorld/experience_index.sqlite build --policy workbench/game-npc-agents/mine-d-affect-relationships/data/adaptation_view_policy.json --out-dir /var/tmp/adaptation-views-rebuild

python3 workbench/game-npc-agents/mine-d-affect-relationships/scripts/build_adaptation_views.py --index /var/tmp/ssn-game-npc-d/data/EvolvingWorld/experience_index.sqlite export-sft --views /var/tmp/adaptation-views-rebuild/episodes.jsonl --partition train --out /var/tmp/adaptation-native-train.jsonl
```

导出包含`messages`（只有system/user）和独立`completion`，保留原文，不添加“正确心理”解释。训练器须只对completion计算监督损失；推理器只读messages。该命令只导出数据，**不会启动训练**。拒绝覆盖已有视图/导出，源hash或覆盖不符会失败。

[全量构建清单](../results/D-ADAPTATION-VIEWS.json)记录实际覆盖、每作品划分、原生变化标志、连接资格与脚本hash。后续token长度筛选、演员输入、训练预算及行为读数仍须在对应模型实验卡冻结，不由数据接口暗中决定。

实际原生训练导出14,079条、202,960,875字节；[token库存](../results/D-ADAPTATION-TRAIN-BUDGET.json)使用固定Qwen3-8B tokenizer：输入34,457,857、目标8,491,686，合计42,949,543 tokens；中位2,789、最大17,962。8,192总长度能完整容纳13,991条，另88条超出；32,768可容纳全部。这里只统计，没有截断或剔除长样本，也未测GPU吞吐。
