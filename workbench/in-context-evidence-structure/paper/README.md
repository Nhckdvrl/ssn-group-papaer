# 可重建的论文排版

科学正文以 [PAPER_DRAFT.md](../PAPER_DRAFT.md) 与 [PAPER_APPENDIX.md](../PAPER_APPENDIX.md) 为准。构建脚本转换引用、图表和公式，不修改主张、数字或科学段落。当前是研究稿；E131跨规模实验完成后继续整合结果。

`acl.sty`、`acl_natbib.bst` 原样来自官方 [acl-style-files](https://github.com/acl-org/acl-style-files/tree/d5adc823ff0f80f98c80405ca0ab66c68e684409)，未改变字体、页边距或行距。`references.bib` 的24项来源与原始BibTeX校验值见 `bibliography_sources.json`；包括已在正文引用的ACL 2025 Sun等工作。

编译配置与 [mechanism-population-dynamics 最终稿](../../mechanism-population-dynamics/paper-acl-v3/README.md) 对齐：11pt article、官方 ACL review、Times 正文字体、Inconsolata 等宽字体、T1/UTF-8、microtype，TinyTeX 的 pdfLaTeX＋BibTeX，至少四次 pdfLaTeX。共同导言见 `acl_preamble.tex`；参考配置文件的 SHA256 见 `compilation_configuration.json`。ICES 另用 array/calc/tabularx 支持 Markdown 表格，样式文件保持原字节。编译器遇错即停止，交叉引用未收敛时补编译。

需要 `pdflatex`、`bibtex` 和带Pandoc的Python环境。可使用独立conda环境：

```sh
conda create -n ices-paper python=3.12
conda run -n ices-paper python -m pip install pypandoc_binary
conda run -n ices-paper python scripts/build_paper.py
```

从workbench根目录运行。默认输出 `results/paper/main.pdf`，包含正文、参考文献、全部附录。`--no-appendix`只构建正文和参考文献；`--source-only`生成可检查的TeX，不调用编译器。`--output`指定输出目录。

也可调用与参考工作台相同的临时目录构建入口：

```sh
ICES_PAPER_PYTHON=/path/to/conda/env/bin/python sh paper/build.sh
```

该入口只把 PDF、TeX、构建记录复制到 `results/paper/`；科学段落继续在两个 Markdown 源文件修改。

每次构建记录正文/附录/脚本/样式/参考文献及最终PDF的SHA256。编译成功不等于满足页数限制、研究全部完成或可被接收；版式与最终科学证据分别核对。

当前稿已逐页核：正文为八页，第九页页首为独立、无编号的 Limitations；参考文献随后，附录在参考文献之后以同一官方双栏版式编译。附录A集中列出模型pins、材料划分、序列化、干预图、评分与bootstrap；其余附录保留全部结果。
