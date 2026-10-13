#!/bin/sh
# Build main.pdf with the same TinyTeX pdfLaTeX + BibTeX setup as
# ../../mechanism-population-dynamics/paper-acl-v3/build.sh.
# Figures and appendix tables: python ../scripts/paper_figures_v2.py (run from the workbench root).
set -eu
export PATH="$HOME/.TinyTeX/bin/x86_64-linux:$PATH"
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
cp -r "$here/main.tex" "$here/appendix.tex" "$here/references.bib" "$here/acl.sty" \
      "$here/acl_natbib.bst" "$here/figures" "$here/tables" "$tmp/"
cd "$tmp"
# Figure 1 is TikZ (figures/fig_overview.tex, data from ../scripts/fig_overview_data.py).
(cd figures && pdflatex -interaction=nonstopmode -halt-on-error fig_overview.tex > /dev/null \
  && cp fig_overview.pdf "$here/figures/fig_overview.pdf")
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build.log
bibtex main >> build.log
for i in 1 2 3; do pdflatex -interaction=nonstopmode -halt-on-error main.tex >> build.log; done
if grep -q "Rerun to get cross-references right\|undefined" main.log; then
    pdflatex -interaction=nonstopmode -halt-on-error main.tex >> build.log
fi
grep -E "Warning|Overfull" main.log > warnings.log || true
cp main.pdf "$here/main.pdf"
mkdir -p "$here/../results/paper"
cp main.log warnings.log "$here/../results/paper/" 2>/dev/null || true
echo "pages: $(pdfinfo main.pdf | awk '/^Pages/ {print $2}')"
