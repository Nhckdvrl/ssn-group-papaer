# ACL / ARR 长文稿：Born to Copy, Taught to Trust

叙事见 `../experiments/A08-acl-narrative.md`；ICML / ICLR 版大纲见 `../experiments/A03-paper-outline.md`。

## 文件
| 文件 | 说明 |
|---|---|
| `main.tex` | 正文 + Limitations + Ethics + 附录（ARR 长文：正文 ≤ 8 页） |
| `refs.bib` | 参考文献：ACL Anthology 条目直接取自 Anthology 的 BibTeX；其余由 arXiv API 元数据生成，出处按已发表会议填写 |
| `acl.sty`、`acl_natbib.bst` | 官方模板（github.com/acl-org/acl-style-files，2026-06 版），未修改 |
| `template_acl_latex.tex` | 官方模板示例，仅供对照，不参与编译 |
| `figures/*.pdf` | 由 `../scripts/figs_acl.py` 生成；图的尺寸即印刷尺寸（单栏 3.03 in、双栏 6.3 in），字体为 TrueType 的 Liberation Serif / Mono（与 Times 同宽度，嵌入为 Type 42，不含 Type 3 字体） |
| `tables/*.tex` | 由 `../scripts/tables_acl.py` 从结果文件直接生成（正文 Table 1 / 3 与附录 Table 4–10），不要手改 |
| `checklist.md` | ARR Responsible NLP checklist 的作答草稿（提交时填在 OpenReview 表单里） |
| `build.sh` | 与 Overleaf 相同的 pdfLaTeX + BibTeX 编译（`./build.sh final` 编终版用于 aclpubcheck） |

## 编译（与 Overleaf 相同：pdfLaTeX + BibTeX）
```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main && pdflatex main
```
Overleaf：上传本文件夹（不需要 `template_acl_latex.tex`），Compiler 选 pdfLaTeX，主文件 `main.tex`；Overleaf 用 latexmk 自动编到稳定。
- 本地已用 TeX Live 2026（pdfTeX 1.40.29）+ BibTeX 编译：无错误、无未定义引用、无溢出；终版模式下 aclpubcheck “All Clear!”；所有字体嵌入，无 Type 3。
- 审稿版的行号由 lineno 宏包生成，需要多编几遍才能定位稳定（少编一遍时，带通栏图的页面上行号可能画进版心）。

## 重画图
```bash
cd ../scripts && ~/.venvs/mechpop/bin/python figs_acl.py && ~/.venvs/mechpop/bin/python tables_acl.py
```

## ARR 要点（2026 CFP）
- 正文 ≤ 8 页；`Limitations`（必需，标题必须叫 Limitations，放在结论后、参考文献前，不计页数）；Ethics 可选；附录在参考文献后，必须双栏。
- 审稿版用 `\usepackage[review]{acl}`（行号、页码、匿名）；录用后改 `final`，多 1 页。
- 用过 AI 写作辅助：在 Responsible NLP checklist 中申报，录用后在 Acknowledgements 写明范围。
