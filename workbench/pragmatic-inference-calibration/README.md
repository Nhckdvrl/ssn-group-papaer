# Pragmatic Inference Calibration — 已关闭

**状态：CLOSED（2026-10-03，用户明确决定“不做了”）。** 不再排实验、训练、标注或自动探索；其他研究线不变。[关闭记录](CLOSE_RECORD.md)

原问题：模型什么时候应该读懂言外之意，什么时候应该停止脑补？有限核心检验没有形成可推进论文的条件结构；不把关闭等同于证明整个问题无效。

## 保留的结论与证据

- E65：低维全局响应映射在来源外相对直接沿用SFT，降低90.9%–96.2%的DPO分布预测误差；C03原任务观察仍L1，不解释为语用能力下降。
- E66：271材料、2285人类评分对应；243显示归一化匹配，其中16项有网页隐藏speech cue风险，227项另作敏感性。三态许可未裁决，不能直接算FPR/d′。
- E67：与E59同一OLMo2 SFT/DPO的控制、顺序gate未共同通过，阶段能力未识别。
- E68：Qwen8B/14B格式控制128/128、127/128；可描述graded语境响应，未得到超出parent的新结构。

[最终验收](logs/finite-reconstruction-2026-10-03.md) · [主张快照](CLAIMS.md) · [定位](POSITIONING.md) · [论文形态终态](PAPER_SHAPE.md)

只保留E65–E68四张最终实验卡、六份汇总及此前删除记录。完整旧实验卡/代码/结果从[关闭前Git快照](https://github.com/Nhckdvrl/ssn-group-papaer/tree/51a578c10b6ca1e7337669281a890e1f84265614/workbench/pragmatic-inference-calibration)追溯；原始模型输出未进Git，现已删除。

## 保留资产

- 环境：`/data1/xiangding/env/pragmatic-inference-calibration`（约5.7GiB），未卸载或更改依赖；[锁文件](requirements.lock.txt)、[入口](scripts/env.sh)。
- 模型：`/data1/xiangding/work/pragmatic-inference-calibration/models`（约362GiB），路径不变，922项文件/目录元数据核对未变；原completion/revision markers与模型清单保留。
- 辅助环境包：同资产根目录的`pdf-tools`、`download-tools`，合计约20MiB。
- 安装好的OpenCode及用户配置未动；[下载代理规则](NETWORK.md)和[直连wrapper](scripts/direct_download.sh)保留，不启动下载。
- 已删除：实验raw/OOF、任务数据与标注、上游code/data副本、论文PDF/TXT、图片、队列/日志/安装记录，以及旧实验runner与本仓库缓存。知识库论文卡保留。

[本轮实际删除清单](results/project-retirement-2026-10-03.json)。已删除4533个本地资产文件，占用约1.94GB；另清理429个仓库文件（含未跟踪缓存）。没有把废弃raw换目录继续占盘。

## 决策记录

用户本会话明确终止本题并要求清理；据此由PROPOSED改为CLOSED。正式重开只接受新的明确人类授权，不自动监控或生成下一轮实验。
