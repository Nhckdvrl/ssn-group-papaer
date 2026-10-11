# paper-acl-v3 — 最终工作稿（已收尾）

**标题：** *Which Head Does the Work? How Attention-Head Circuit Findings Carry Over Between Related Language Models*  
**状态：** 2026-10-11 研究已终止；这是最后一次成稿版本，不等于已投递、已录用或获得独立复现认证。

- [main.pdf](main.pdf)、[main.tex](main.tex)：已保存 PDF 与 LaTeX。  
- [refs.bib](refs.bib)、`acl.sty`、`acl_natbib.bst`：参考文献及模板。  
- `figures/`、`tables/`：当前论文采用的图表文件；`figures/numbers.json`：图表数字。
- [build.sh](build.sh)：在已有 figures/tables 的情况下调用 pdfLaTeX、BibTeX 构建论文；会覆盖 `main.pdf`，请用临时克隆运行。
- [scripts/figs_v3.py](../scripts/figs_v3.py)：重新生成部分图表的程序，依赖 [结果](../results/) 与尚未全部进入 Git 的原始 `.npz`（尤其是 `results/e81/`、`e83/`）。**不应声称只 clone HEAD 即可重绘全部图。**
- [结项综述](../CLOSEOUT.md)、[资产索引](../ASSET_INDEX.md)、[E81](../experiments/E81-carrier-inheritance.md)、[E83](../experiments/E83-carrier-chosen-at-emergence.md)、[E85/E86](../experiments/E85-candidate-gap-and-swaps.md)、[E87/E88 终止记录](../experiments/E87-E88-review-checks.md)。

旧 [software-submission/](../software-submission/) 是与 v1 同名论文配套的历史包，不能误当作 v3 复现所需全部资产。
