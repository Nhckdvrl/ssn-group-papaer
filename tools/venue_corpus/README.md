# venue_corpus — 顶会校准语料库（选题用）

**作用：** 让“这个方向热不热 / 顶会收不收这类论文 / 我们和最近邻差在哪”由**真实的顶会接收与拒稿数据**回答，而不是由 agent 在全 arXiv 上问“有没有人碰过”。后一个问题几乎总是返回“有”，而它并不是顶会审稿的判断标准（见 `../../search/PROCESS_DIAGNOSIS_2026-09-30.md`）。

## 覆盖范围（2026-09-30 构建）

| venue | 记录 | 说明 |
|---|---:|---|
| ICLR 2026 | 19,813 | **含 14,455 篇拒稿/撤稿**及平均审稿分 → 可做 accepted-vs-rejected 校准 |
| ICLR 2025 | 11,672 | 含拒稿/撤稿 |
| ICML 2026 / 2025 | 6,341 / 3,527 | 接收论文（2025 含少量公开拒稿） |
| NeurIPS 2025 / 2024 | 6,212 / 4,786 | 接收论文（含少量公开拒稿）；NeurIPS2026 官方 event 目录已公开，尚未并入本 corpus，见下方局限 |
| ACL 2026 / 2025, EMNLP 2025 / 2024, NAACL 2025 | ~7.7k | **只收 main（long/short）**；Findings、EACL、industry、demo、SRW、tutorial 全部排除（组内规定：档次不够，不作校准） |
| CVPR 2025, ICCV 2025 | 5.6k | 接收论文 |

数据来源：[`papercopilot/paperlists`](https://github.com/papercopilot/paperlists)（OpenReview 派生 JSON）与 [`acl-org/acl-anthology`](https://github.com/acl-org/acl-anthology)（XML）。数据不进 git（`data/` 已忽略），用脚本重建：

```bash
./fetch.sh          # 下载原始 JSON/XML（约 300MB）
python3 build.py    # 生成 data/corpus.jsonl
```

## 四个查询

```bash
# 1) 热度：某个切片在各 venue 的接收数；ICLR 同时给出切片接收率 vs 全会基准接收率
python3 query.py density "multi[- ]agent" "\b(LLMs?|language models?)\b" --show 10

# 2) 定位：给一段想法描述，返回最近的已接收论文和最近的被拒论文（near-miss）
python3 query.py nearest "cross-play evaluation of RL co-trained LLM teams with unseen partners" -k 15

# 3) 论文形态：该切片被接收 vs 被拒的摘要里 method / finding / theory / benchmark / failure 线索比例与平均分
python3 query.py shapes "sparse auto[- ]?encoders?|\bSAEs?\b"

# 4) 读摘要
python3 query.py show "Multi-Agent Teams Hold Experts Back"
```

## 怎么用（与新选题流程的关系）

- **热度是数字，不是判决。** 切片接收率明显高于基准（如 ICLR 2026 attention sink 47% vs 27%）说明审稿人欢迎；明显低于基准（如 ICLR 2026 多智能体 LLM 22%）说明供给过剩、审稿人挑剔——需要更强的基线纪律，而不是自动放弃。
- **nearest 用来写定位表，不用来杀题。** 对每个近邻写一句“我们的 claim / 设定 / 方法 / 证据与它差在哪”。只有“同一 claim + 同一类证据 + 同一设定”才算撞车，而且撞车时优先调整 delta，而不是放弃 territory。
- **near-miss 拒稿最有信息量。** 高分被拒的论文告诉我们审稿人在这个方向上卡什么（常见：基线不公平、只在一个模型上、缺消融、贡献像工程拼装）。
- **不同 venue 的分数量表不同**（ICLR 0–10 偶数制，NeurIPS/ICML 1–6 或 1–5），不要跨 venue 比较 `score`。
- 正则是粗筛，`--show` 抽查命中结果，避免宽泛模式带来的误报（例如 `\bGUI` 会命中 guidance，要写成 `\bGUI\b`）。

## 已知局限

- **2026-10-03 更新：** [NeurIPS2026 Downloads](https://neurips.cc/Downloads/2026)已公开，本次抓到9,230条event，混有非main内容，不能作为main接收总数。带来源的本地快照在`data/neurips2026_directory_2026-10-03.json`（不进git）；单篇track未全核、PaperCopilot `nips2026.json` 当时404，因此未覆盖已有corpus。目录收录、作者自报与正式主会proceedings分别标注，待上游有完整分轨数据再用`fetch.sh`/`build.py`重建。
- 只有具有较完整接收/拒稿分母的ICLR切片可比较接受比例；以接收列表为主的NeurIPS/ICML的accepted/listed不是会场接收率。切片比例不能单独证明拥挤程度或拒稿原因。
- 最新 arXiv 不在语料中：环视领域时仍需结合 arXiv / awesome 列表（见 `library/` 各题材页的来源列表）。
- 摘要线索（“we propose/find”）是粗粒度信号，只用于比较分布，不用于判断单篇论文。
