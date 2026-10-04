#!/bin/sh
# Build main.pdf exactly as Overleaf does (pdfLaTeX + BibTeX), in a scratch directory so the folder stays clean.
# Usage: ./build.sh [final]   ("final" builds the camera-ready layout to final.pdf, for aclpubcheck)
set -e
export PATH="$HOME/.TinyTeX/bin/x86_64-linux:$PATH"
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d)
cp -r "$here"/main.tex "$here"/refs.bib "$here"/acl.sty "$here"/acl_natbib.bst "$here"/figures "$tmp"/
cd "$tmp"
out=main
if [ "$1" = "final" ]; then sed 's/\\usepackage\[review\]{acl}/\\usepackage{acl}/' main.tex > final.tex; out=final; fi
pdflatex -interaction=nonstopmode $out > /dev/null || true
bibtex $out > bibtex.log || true
for i in 1 2 3; do pdflatex -interaction=nonstopmode $out > /dev/null || true; done
grep -E "^!|LaTeX Error|undefined|Overfull" $out.log | sort | uniq -c || true
grep -i -E "^warning|error" bibtex.log || true
cp $out.pdf "$here"/$out.pdf
rm -rf "$tmp"
