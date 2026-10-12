"""Build the manuscript and appendix using the unchanged official ACL style.

PAPER_DRAFT.md and PAPER_APPENDIX.md remain the scientific prose sources.
Requires pypandoc (with pandoc), pdflatex, and bibtex; performs no web access.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "paper"
CAPTIONS = [
    "Native operation removal and restricted restoration, n32 confirmation. Signed B-rule contrasts in nats with context-bootstrap 95\\% CIs.",
    "Fixed formation and query policies on dual-aspect rules, n32 confirmation. Mean candidate accuracy in percent; complete CIs and source tradeoffs are in the appendix.",
    "Real SST text: private functions, formation magnitudes, and coefficient-one reconstruction. Confirmation n32; each private direction has n16 contexts.",
    "Real-text private rules with shared words: policy consequences, confirmation n32. Percent accuracy and paired changes with context-bootstrap 95\\% CIs.",
    "Information-equivalent backgrounds and joint cache use. Confirmation n32; paired coherence differences with context-bootstrap 95\\% CIs. The separate-word reference uses a different world scope.",
    "The same formation, native-operation, and real-text function chain across model sizes. Within-family matched confirmation contexts, n32; full-output accuracy and signed native effects.",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def escape(text):
    text = text.replace("`", "")
    text = re.sub(r"([\\&%$#_{}])", lambda m: "\\" + m[1], text)
    return text.replace("^", r"\textasciicircum{}").replace("~", r"\textasciitilde{}")


def latex(text):
    converted = pypandoc.convert_text(text, "latex",
        format="markdown+raw_tex+tex_math_single_backslash",
        extra_args=["--wrap=none", "--shift-heading-level-by=-1"])
    # Permit line breaks in repository paths and long hashes without changing text.
    def break_code(match):
        value = match[1]
        if re.fullmatch(r"[a-fA-F0-9]{32,}", value):
            value = r"\allowbreak{}".join(value[i:i+8] for i in range(0, len(value), 8))
        elif "/" in value:
            value = value.replace("/", r"/\allowbreak{}").replace(r"\_", r"\_\allowbreak{}")
        return r"\texttt{" + value + "}"
    return re.sub(r"\\texttt\{([^{}]+)\}", break_code, converted)


def render(text, references, appendix=False):
    counts = {"figures": 0, "tables": 0}
    if appendix:
        # File title and its local status line are repository navigation.
        text = "\n".join(text.splitlines()[4:])
        text = re.sub(r"^(#{2,3}) [A-Z]\.?(?:\d+)?\.?(?= )", r"\1", text, flags=re.M)
    else:
        text = "\n".join(text.splitlines()[4:])
        text = text.replace("## Abstract\n", "\\begin{abstract}\n", 1)
        text = text.replace("## 1. Introduction\n", "\\end{abstract}\n\n## Introduction\n", 1)
        text = re.sub(r"^(#{2,3}) \d+(?:\.\d+)?\.?(?= )", r"\1", text, flags=re.M)
    text = text.replace(
        "H_A=F_A(D_A,D_B),\\qquad H_B=F_B(D_A,D_B),\\qquad z=R(q,H_A,H_B).",
        r"\begin{aligned}H_A&=F_A(D_A,D_B),\quad H_B=F_B(D_A,D_B),\\ z&=R(q,H_A,H_B).\end{aligned}")
    text = re.sub(r"\[([^]]+)\]\((https://[^)]+)\)",
        lambda m: m[1] + r" \citep{" + references[m[2]] + "}" if m[2] in references else m[0], text)

    def figure(match):
        _, filename, _, caption = match.groups()
        asset = ROOT / Path(filename).with_suffix(".pdf")
        assert asset.is_file(), asset
        counts["figures"] += 1
        return "\n\\begin{figure*}[t]\n\\centering\n\\includegraphics[width=\\textwidth]{" + str(asset) + "}\n\\caption{" + latex(caption).strip() + "}\n\\end{figure*}\n"

    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)\n\n\*Figure (\d+)\. ([^\n]+)\*", figure, text)

    def unnumbered_figure(match):
        caption, filename = match.groups()
        asset = ROOT / Path(filename).with_suffix(".pdf")
        assert asset.is_file(), asset
        counts["figures"] += 1
        return "\n\\begin{figure*}[t]\n\\centering\n\\includegraphics[width=\\textwidth]{" + str(asset) + "}\n\\caption{" + escape(caption) + "}\n\\end{figure*}\n"

    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", unnumbered_figure, text)

    def table(match):
        counts["tables"] += 1
        rows = [line.strip().strip("|").split("|") for line in match[0].splitlines()]
        data = [rows[0]] + rows[2:]
        n = len(rows[0])
        assert all(len(row) == n for row in data), rows
        spec = r">{\raggedright\arraybackslash}X" + r">{\raggedleft\arraybackslash}X" * (n - 1)
        cells = [" & ".join(latex(cell.strip()).strip() for cell in row) + r" \\" for row in data]
        caption = ("Complete supplementary readouts; " + escape(rows[0][0].strip()) + ".") if appendix else CAPTIONS[counts["tables"] - 1]
        return "\n\\begin{table*}[t]\n\\small\n\\begin{tabularx}{\\textwidth}{" + spec + "}\n\\toprule\n" + cells[0] + "\n\\midrule\n" + "\n".join(cells[1:]) + "\n\\bottomrule\n\\end{tabularx}\n\\caption{" + caption + "}\n\\end{table*}\n"

    text = re.sub(r"(?m)^\|[^\n]+\|\n\|[-: |]+\|\n(?:\|[^\n]+\|\n)+", table, text)
    return latex(text), counts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=ROOT / "results/paper")
    p.add_argument("--no-appendix", action="store_true")
    p.add_argument("--source-only", action="store_true")
    args = p.parse_args()
    dest = args.output.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    records = json.loads((ASSETS / "bibliography_sources.json").read_text())
    refs = {row["url"]: row["citekey"] for row in records}
    main_source = ROOT / "PAPER_DRAFT.md"
    appendix_source = ROOT / "PAPER_APPENDIX.md"
    main_tex, main_counts = render(main_source.read_text(), refs)
    appendix_tex, appendix_counts = ("", {}) if args.no_appendix else render(appendix_source.read_text(), refs, True)
    header = r"""\documentclass[11pt]{article}
\usepackage[review]{acl}
\usepackage{times,latexsym,amsmath,amssymb,booktabs,graphicx,array,calc,hyperref,microtype,tabularx}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\DeclareUnicodeCharacter{2192}{\ensuremath{\rightarrow}}
\DeclareUnicodeCharacter{00D7}{\ensuremath{\times}}
\DeclareUnicodeCharacter{2260}{\ensuremath{\ne}}
\DeclareUnicodeCharacter{2212}{\ensuremath{\mathchar"2200}}
\DeclareUnicodeCharacter{03B4}{\ensuremath{\delta}}
\DeclareUnicodeCharacter{00BD}{\ensuremath{\tfrac{1}{2}}}
\newcommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\newcommand{\pandocbounded}[1]{#1}
\title{""" + main_source.read_text().splitlines()[0][2:] + r"""}
\author{Anonymous research draft}
\begin{document}
\maketitle
"""
    for name in ["acl.sty", "acl_natbib.bst", "references.bib"]:
        shutil.copy(ASSETS / name, dest / name)
    tail = "\n\\clearpage\n\\bibliography{references}\n"
    if appendix_tex:
        tail += "\\clearpage\n\\appendix\n" + appendix_tex
    (dest / "main.tex").write_text(header + main_tex + tail + "\n\\end{document}\n")
    manifest = {
        "scientific_prose_sources": {str(x.relative_to(ROOT)): digest(x) for x in [main_source, appendix_source]},
        "scientific_prose_changed": False, "main": main_counts, "appendix": appendix_counts,
        "official_acl_style_revision": "d5adc823ff0f80f98c80405ca0ab66c68e684409",
        "acl_style_sha256": digest(ASSETS / "acl.sty"),
        "bibliography_sha256": digest(ASSETS / "references.bib"),
        "build_script_sha256": digest(Path(__file__)),
        "pandoc_version": str(pypandoc.get_pandoc_version()),
        "status": "SOURCE_ONLY" if args.source_only else "BUILDING",
        "limits": "Formatting artifact; does not certify page limits, acceptance, or scientific completeness."
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if not args.source_only:
        commands = [["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                    ["bibtex", "main"],
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]]
        with (dest / "build.log").open("w") as log:
            for command in commands:
                subprocess.run(command, cwd=dest, stdout=log, stderr=subprocess.STDOUT, check=True)
            # Long two-column appendices can need additional passes for line numbers.
            for _ in range(3):
                status = (dest / "main.log").read_text()
                needs_pass = "Line number reference failed" in status or "Label(s) may have changed" in status
                if not needs_pass:
                    break
                subprocess.run(commands[-1], cwd=dest, stdout=log, stderr=subprocess.STDOUT, check=True)
        final_log = (dest / "main.log").read_text()
        assert "Line number reference failed" not in final_log and "Label(s) may have changed" not in final_log
        manifest["status"] = "BUILT"
        manifest["pdf_sha256"] = digest(dest / "main.pdf")
        (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(dest / ("main.tex" if args.source_only else "main.pdf"))


if __name__ == "__main__":
    main()
