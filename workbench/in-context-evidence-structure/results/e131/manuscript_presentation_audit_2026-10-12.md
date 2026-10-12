# 当前 ACL 构建呈现独立校对（非科学完整性判断）

2026-10-12；按 EXECUTION §5。最终结论：科学源、原三项认识、数字与全部图表的转换保留通过；初版两项呈现问题均已修正，当前构建呈现校对通过。没有重跑 GPU、修改科学源或调整主张级别。

源快照：`PAPER_DRAFT.md` = `a049e1af407026126cf294fd19643d40b197e84d6d2ec2e26ac06c2e5f38cb9d`；`PAPER_APPENDIX.md` = `ddc6ba4a68621bfc6d14af279d9a9d6bde28c422fad34869529baf5983ca516b`。两者均与作者构建 manifest 一致，独立构建后字节未变。构建脚本 SHA = `4e40aa899cdc04c99fd2fef6e45ec11447ca49f90d29a4ba853b7993adcdee34`。

- 独立 `--source-only` 重建的 `main.tex` 与作者产物逐字相同；另在独立 `/tmp/ices-independent-paper-full` 完整编译成功。
- 正文 6 图、5 表，附录 9 图、25 表；PDF 中 15 图及 30 表的标题均存在。全部 42 个源标题、744 个表格单元保留；源中的 1,493 次小数文本出现均未发现计数缺失。该检查是转换完整性核对，未重算实验数字。
- 摘要与 Introduction 三项认识保留；接口公式只改为双行排版，没有更换符号定义或推论。没有因 E129/E130 有限 Cue 响应收缩原三项认识。
- 22 条文献的 source URL、唯一 citekey、实际 `.bib`、TeX 引用、aux 和最终 bbl 集合完全对应。22 份原始缓存 BibTeX 均与来源记录 SHA 一致，合并书目条目逐项保留原始内容，没有悬空引用。
- `acl.sty` / `acl_natbib.bst` 与[官方固定 revision](https://github.com/acl-org/acl-style-files/tree/d5adc823ff0f80f98c80405ca0ab66c68e684409)的 raw 文件逐字相同，构建副本也相同。样式 SHA 分别为 `19dfeddc2c0e448f3926a0bef048a9db3f3611b46265b760caabd7ada4f361de` / `6fbb306202290f4b68e74ac1460a8b27398500cb6dfeb4492e74c457eae7cd1e`。

初版作者 PDF 为 30 页，前 13 页是正文与参考文献；末轮没有 undefined/Overfull，但有 76 条 Underfull 和两项 lineno/label 重编译提示。视检第 1、4、10、12、22、26、30 页：正文、统计表、图及最后 E130 表没有缺失/裁切；第 10、12、22、26 页可见部分行号移入文字区域。初版需追加编译至行号/引用收敛，再重记 manifest 的 PDF SHA；下述最终版已完成。我在独立目录额外运行一次 `pdflatex` 后提示归零，页数仍为 30；第 22、26 页再视检确认行号恢复在外侧，科学 TeX 不变。

另一项可选排版修正：附录证据索引表将 Markdown 链接作为 `[E...](experiments/...)` 原样显示。内容仍在，但路径撑长表格并降低导航可读性；建议转换单元内的 inline link。部分附录正文数字与单词相连（例如 `comprise96contexts`）原本就在 Markdown 源中，不是转换丢空格，可在后续文字润色时处理。大图浮动页有空白，未观察到图表不可读；不据此作页数限制或接受判断。

阅读范围：完整构建代码/资产记录、全部源标题/图表与生成 TeX、摘要/三项认识及数学接口、22 份书目源，以及上述七个典型 PDF 页；未把本次呈现审核当成每个原始科学结果或全论文科学价值的重新审计。PDF 时间戳等元数据会改变文件 SHA，因此没有宣称跨构建 PDF 逐字相同；确定可重建的是科学源和 TeX 内容。

## 最终修正快照

构建器 SHA `6fe763c8fee13332061ac8180138f622d657490ce9b55500d6a46e8bdf0a4671`；最终 PDF SHA `5e1d5a3db4f81c85597eb5b83f4f6db7b39e08b3f686ebc3fb9058ad97267918`。科学正文与附录 SHA 不变，官方样式与书目不变。

只复核了本轮两项呈现修正：构建器按 warning 最多再运行 3 轮 LaTeX，并断言最终行号/label 已收敛；表格单元使用 inline Markdown 转换。末轮 warning、undefined、Overfull 均为 0。最终独立 `--source-only` 重建仍与作者 TeX 逐字相同；全部表格外 TeX 与旧版逐字相同，30 个表格的小数文本多重集逐表完全不变。附录索引链接的标签与目标保留，显示从原 MD 路径串变为可读标签。视检新版第 12、21、22、26 页，行号均在外侧，证据索引可读。页数仍为 30，PDF 仍有 15 图、30 表，当前呈现封版通过。原始发现、旧 SHA 与独立第四轮证据保留在 JSON 历史记录中。
