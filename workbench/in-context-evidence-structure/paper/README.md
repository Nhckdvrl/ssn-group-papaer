# ARR 投稿稿（LaTeX，2026-10-12 重写）

**标题：** *Whose Rule Is It? How Language Models Mix and Separate Source-Specific Rules in In-Context Learning*（可改）

从 2026-10-12 起，**本目录的 `main.tex` + `appendix.tex` 是论文唯一正本**。原来用 pandoc 从 [PAPER_DRAFT.md](../PAPER_DRAFT.md)、[PAPER_APPENDIX.md](../PAPER_APPENDIX.md) 转出 TeX 的流程（`scripts/build_paper.py`）停用，两个 Markdown 文件保留为历史稿和实验记录索引。

- [main.pdf](main.pdf)：当前 PDF。正文 8 页写满，第 9 页页首开始 Limitations，然后是 Ethical Considerations、参考文献、附录 A–J。
- `main.tex`：正文。第 1 页的 Figure 1 是 TikZ 示意图，直接写在 `main.tex` 里。
- `appendix.tex`：附录。表格行在 `tables/app_*.tex` 中，由脚本生成；E122/E124–E128/E119 的表格从已审计的 PAPER_APPENDIX.md 转写。
- `figures/`：Figure 2–5 和 `numbers.json`（正文所有数字的出处），由 [scripts/paper_figures_v2.py](../scripts/paper_figures_v2.py) 直接从 `results/` 的确认批次原始文件计算。重算散点图的相关系数时，会与已保存的 analysis 断言一致。
- `references.bib`：原 24 条，加上 15 条经典文献（ACL Anthology 官方 BibTeX 或 arXiv API 核对过 ID 与标题）。

## 模板与格式

与 [mechanism-population-dynamics/paper-acl-v3](../../mechanism-population-dynamics/paper-acl-v3/main.tex) 一致：`acl.sty`、`acl_natbib.bst` 与其逐字节相同，导言区为同一套（11pt article、`[review]{acl}`、times、T1/utf8、microtype、inconsolata、booktabs、makecell、amsmath、xcolor、enumitem）。本稿另外用了 `tikz`（Figure 1）和 `adjustbox`（表格超宽时只缩小、不放大）。纸张为 A4，带行号，匿名，所有字体都已嵌入（`pdffonts` 已核对）。

## 构建

```sh
~/miniconda3/envs/verl-clean/bin/python scripts/paper_figures_v2.py   # 在 workbench 根目录运行：图、numbers.json、附录表
sh paper/build.sh                                                     # TinyTeX pdfLaTeX + BibTeX，输出 paper/main.pdf
```

`build.sh` 在临时目录里编译，把 `main.log` 和 `warnings.log` 放到 `results/paper/`。当前构建没有 Overfull，也没有未定义的引用。

## 数字写法

调研了 5 篇同题材已录用的 ACL/EMNLP/NAACL 论文（Sun et al. ACL'25、Yu & Ananiadou EMNLP'24、Lepori et al. NAACL'25、Li et al. ACL'24、PCW ACL'23），正文里都没有 `x [lo, hi]` 这种写法。因此本稿的约定是：

- 正文只给点估计（百分点保留 1 位小数，nats 和相关系数保留 2 位）。
- 区间放在图的误差棒和附录表里。主表用灰色标出区间跨 0 的项。

## 事后（post-hoc）补充

以下两处是在确认批次跑完之后，从已保存的逐 query 数据中计算的，没有新增模型运行，附录中已注明：

- §3 中 A 的准确率随 B 的约定冲突或一致而变化的差值。
- Table 2 中“一句指令”这一列的聚合值，以及它的配对区间。
