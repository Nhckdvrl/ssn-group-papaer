#!/bin/sh
# Build the de-anonymized arXiv version from the ARR source (main.tex stays the submitted, anonymous version).
# Output: arxiv/ (source tree with main.bbl), arxiv/main.pdf, and arxiv_source.tar.gz ready for upload.
# Changes relative to main.tex: [review] -> [preprint] (no line numbers, page numbers kept), author block,
# and the supplementary-code sentence. Run ./build.sh first if figures or tables changed.
set -eu
export PATH="$HOME/.TinyTeX/bin/x86_64-linux:$PATH"
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
out="$here/arxiv"
rm -rf "$out" "$here/arxiv_source.tar.gz"
mkdir -p "$out/figures" "$out/tables"
cp "$here/appendix.tex" "$here/references.bib" "$here/acl.sty" "$here/acl_natbib.bst" "$out/"
cp "$here"/tables/*.tex "$out/tables/"
cp "$here"/figures/*.pdf "$out/figures/"

python3 - "$here/main.tex" "$out/main.tex" <<'EOF'
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
edits = [
    (r"\usepackage[review]{acl}", r"\usepackage[preprint]{acl}"),
    (r"\author{Anonymous ACL submission}",
     "\\author{Xiang Ding\\\\\n  Nagoya University\\\\\n  \\texttt{xiang.ding.i8@s.mail.nagoya-u.ac.jp}\n"
     "  \\And\n  Tiancheng Xing\\\\\n  Institute of Science Tokyo\\\\\n  \\texttt{xing.t.13fb@m.isct.ac.jp}}"),
    (r"and code for all experiments is provided in the supplementary material.",
     r"and code for all experiments will be released."),
]
for old, new in edits:
    if s.count(old) != 1:
        sys.exit(f"expected exactly one occurrence of: {old}")
    s = s.replace(old, new)
open(dst, "w").write(s)
EOF

cd "$out"
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build.log
bibtex main >> build.log
for i in 1 2 3; do pdflatex -interaction=nonstopmode -halt-on-error main.tex >> build.log; done
if grep -q "undefined" main.log; then echo "undefined references in arxiv build" >&2; exit 1; fi
grep -E "Overfull" main.log || true
# arXiv compiles the source itself; ship main.bbl so it does not need BibTeX
tar -czf "$here/arxiv_source.tar.gz" main.tex main.bbl appendix.tex acl.sty acl_natbib.bst references.bib figures tables
rm -f main.aux main.blg main.out build.log
echo "pages: $(pdfinfo main.pdf | awk '/^Pages/ {print $2}')"
