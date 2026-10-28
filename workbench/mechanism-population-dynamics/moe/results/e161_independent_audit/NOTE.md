# E161 独立 CPU 校对

对应 C14 与 E161。独立重算固定国家/关系交叉映射，校验四个答案 token 不同；根据真实全词表 top1 将结果分为原答案、实体混合、关系混合、完整 donor、其他五类，不使用四候选子集 argmax。输出五类比例及相对自然基线变化、四标签 LP 增益、KL、关系/实体混合相对 donor 的偏好、R 与 attention 偏好差和所有指标的 A−P/B−P。24 国家成对 bootstrap 1000 次、seed 161001、两关系等权；共同四查询在三模型均 top1 正确的次集仅报点和计数。首 token 与固定探针的范围不外推为完整事实生成能力。

CPU 合成自检：`~/.venvs/mechpop/bin/python -B moe/results/e161_independent_audit/audit.py --self-test`。涵盖四标签映射、类别分割与词表外 other、路径轴、偏好符号、配对统计和预算。没有读取 E161 新数据、加载模型或运行 GPU。

完成后以 `--audit --output <审计输出>` 重算；读取 raw 前检查完整预算与 cap、plan/manifest、源代码/数据/参考/暂存清单哈希、旧轨迹和参数/buffer/cal 身份，读取后核对 outcome map、原生选中 LP/top10、共同 top10 门槛和 source 正控。KL 只存全词表 KL 标量，不能从封存数据重算分布；工程身份以 manifest 声明及封存引用复核。汇总比较器已接入，正式运行时附加 `--summary <summary.json>`；当前尚未读取正式数据，不能声称独立校对通过。
