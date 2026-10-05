# D0 数据审计（2026-10-05）

三个上游已下载到本地 cache，固定 revision、读取 LICENSE 并逐文件计算 SHA256；尚无题目复制进 git。机器可读全表见 [D0-source-audit.json](D0-source-audit.json)。

| 来源 | revision | repo license | 实际规模 |
|---|---|---|---|
| [Amouyal release](https://github.com/samsam3232/comparing_humans_llms_processing_difficulties/tree/072efefa01cb9716c2d14752eb1d4bf9830b0b81) | `072efefa01cb9716c2d14752eb1d4bf9830b0b81` | MIT，版权 samsam3232 2025 | E00 276 QA / 138 sentences / 69 完整配对；另外 6 个 CSV 共 928 rows |
| [Jurayj](https://github.com/wjurayj/garden-path-gpt2/tree/ad30c4248df5dcdda163bd6f05add419e1210c42) | `ad30c4248df5dcdda163bd6f05add419e1210c42` | Apache-2.0 | NP/Z 43、NP/S 19、MV/RR (`vawip.tsv`) 28 component rows |
| [Microsoft Turing Experiments](https://github.com/microsoft/turing-experiments/tree/f00115e793f5f728eccf13044bb299d64901de57) | `f00115e793f5f728eccf13044bb299d64901de57` | MIT，版权 Microsoft Corporation | 两个 TSV 各 48 sentences；各 12 个 lexical sets × OT/DOT/RAT/DRAT |

## 已核对
- 以上 CSV/TSV 均无空 cell、无完全重复 row；Amouyal 的 index 列不连续，保留原 row ID，不能用缺号判断漏下载。
- E00 每 set 4 条：同题同 gold 的 GP/nonGP × simple/GP question；完整性已在 loader 中强制断言。GP_prob/nonGP_prob 各 90 QA，GP_reflexive/nonGP_reflexive 各 48 QA。
- E00 simple gold 全 Yes、GP question 全 No。报告各项，但不把极性混杂的 simple>GP 本身解释为能力差异。主检验是同题 GP/nonGP 配对。
- 上游 regular open-source inference 是 raw continuation，而不是 Qwen chat template；16 个已保存 prefix 固定 few-shot 内容与句题顺序；没有随机重抽示例。
- Microsoft 数据是 grammaticality stimulus，不自带 comprehension question/gold。统一 schema 对这些字段保留 null；不得伪造“原始 comprehension gold”。Label 中 OT/RAT 是 GP，DOT/DRAT 是 comma control，RAT/DRAT 还涉及事件角色合理性。独立复现尚未跑。

## 生成前必须处理的风险
- DATA_PLAN 原写 NP/S 20、MV/RR 20，与 pinned source 实数不符，以 audited revision 为准，不补造缺行。
- NP/Z 的 blocker 有直接宾语、PP、adverbial 等不同类别；`for water`、`in poker` 不能不经核验就当成直接宾语 blocker。
- NP/S 的 lexical nonGP 和 MV/RR 的 unambiguous verb 替换改变词义；与 comma/that/unreduced 条件分开报告。
- MV/RR 内有不自然被动（例如部分 selected participle 与 RC contents 不兼容）；全部 canonical sentence 可缓存，但行为分析前逐条审计并保留 rejection/exclusion 理由。
- 这些数据沿用经典心理语言学材料。repo LICENSE 是本次可核对的发布许可；原始文献来源见上游 README。第三方原始材料的独立授权链未核对，不把 repo license 写成原始论文独立授权证明。初期只在本地缓存使用，并保留来源归属。

## 下载记录
用户追加“下载不得走代理”之后，立即停止原下载。默认环境此前含本地 HTTP/HTTPS/ALL proxy；GitHub 小数据 clone 和 HF 初始部分下载发生在追加约束之前。后续 `scripts/env.sh` 清除代理，ModelScope 下载额外使用 `requests.Session.trust_env=False`。HF 直连失败，ModelScope 官方镜像直连可用。模型 mirror revision 与实际 SHA256 另存 manifest；不声称镜像 bytes 与 HF revision 已独立核对。

补充核验：hf-mirror.com 无代理直连成功，HF revision 固定 b968826d9c46dd6066d109eabc6255188de91218。实际模型/tokenizer/config/LICENSE 的 14 个文件全部通过该 HF revision 的 LFS SHA256 或 git blob SHA1 校验，ModelScope 下载 bytes 可复用。[模型清单](D0-model-manifest.json)。
