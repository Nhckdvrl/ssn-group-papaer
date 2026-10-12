#!/bin/sh
# Use the same TinyTeX pdfLaTeX + BibTeX setup as mechanism-population-dynamics.
set -eu
export PATH="$HOME/.TinyTeX/bin/x86_64-linux:$PATH"
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
"${ICES_PAPER_PYTHON:-python3}" "$here/../scripts/build_paper.py" --output "$tmp" "$@"
mkdir -p "$here/../results/paper"
for name in main.pdf main.tex manifest.json build.log; do
    if [ -f "$tmp/$name" ]; then
        cp "$tmp/$name" "$here/../results/paper/$name"
    fi
done
