"""Build the manuscript and appendix using the unchanged official ACL style.

PAPER_DRAFT.md and PAPER_APPENDIX.md remain the scientific prose sources.
Requires pypandoc (with pandoc), pdflatex, and bibtex; performs no web access.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "paper"
table_captions = json.loads((ASSETS / "table_captions.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def escape(text):
    text = text.replace("`", "")
    text = re.sub(r"([\\&%$#_{}])", lambda m: "\\" + m[1], text)
    return text.replace("^", r"\textasciicircum{}").replace("~", r"\textasciitilde{}")


def latex(text):
    converted = pypandoc.convert_text(text, "latex",
        format="markdown+raw_tex+tex_math_single_backslash",
        extra_args=["--wrap=none", "--shift-heading-level-by=-1", "--syntax-highlighting=none"])
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
        text = text.replace("## Limitations\n",
                            "\\clearpage\n\\section*{Limitations}\n\\label{sec:limitations}\n", 1)
        text = re.sub(r"^(#{2,3}) \d+(?:\.\d+)?\.?(?= )", r"\1", text, flags=re.M)
    text = text.replace(
        "H_A=F_A(D_A,D_B),\\qquad H_B=F_B(D_A,D_B),\\qquad z=R(q,H_A,H_B).",
        r"\begin{aligned}H_A&=F_A(D_A,D_B),\quad H_B=F_B(D_A,D_B),\\ z&=R(q,H_A,H_B).\end{aligned}")
    def citation(match):
        label, url = match.groups()
        if url not in references:
            return match[0]
        author_label = "et al." in label or label in {
            "Feng and Steinhardt", "Yu and Ananiadou", "Crosbie and Shutova"}
        if author_label:
            return r"\citet{" + references[url] + "}"
        return label + r" \citep{" + references[url] + "}"

    text = re.sub(r"\[([^]]+)\]\((https://[^)]+)\)", citation, text)

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
        caption = table_captions["appendix" if appendix else "main"][counts["tables"] - 1]
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
    header = (ASSETS / "acl_preamble.tex").read_text() + r"""
% Support the Markdown renderer's tables and symbols.
\usepackage{array,calc,tabularx}
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
    tail = "\n\\bibliography{references}\n"
    if appendix_tex:
        tail += "\\clearpage\n\\appendix\n" + appendix_tex
    (dest / "main.tex").write_text(header + main_tex + tail + "\n\\end{document}\n")
    manifest = {
        "scientific_prose_sources": {str(x.relative_to(ROOT)): digest(x) for x in [main_source, appendix_source]},
        "scientific_prose_changed": False, "main": main_counts, "appendix": appendix_counts,
        "official_acl_style_revision": "d5adc823ff0f80f98c80405ca0ab66c68e684409",
        "acl_style_sha256": digest(ASSETS / "acl.sty"),
        "acl_bibliography_style_sha256": digest(ASSETS / "acl_natbib.bst"),
        "preamble_sha256": digest(ASSETS / "acl_preamble.tex"),
        "table_captions_sha256": digest(ASSETS / "table_captions.json"),
        "compilation_configuration": json.loads((ASSETS / "compilation_configuration.json").read_text()),
        "bibliography_sha256": digest(ASSETS / "references.bib"),
        "build_script_sha256": digest(Path(__file__)),
        "pandoc_version": str(pypandoc.get_pandoc_version()),
        "status": "SOURCE_ONLY" if args.source_only else "BUILDING",
        "limits": "Formatting artifact; does not certify page limits, acceptance, or scientific completeness."
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if not args.source_only:
        # Match mechanism-population-dynamics/paper-acl-v3/build.sh.
        tex_env = os.environ.copy()
        tex_bin = Path.home() / ".TinyTeX/bin/x86_64-linux"
        tex_env["PATH"] = str(tex_bin) + os.pathsep + tex_env.get("PATH", "")
        manifest["compilers"] = {
            name: {"path": shutil.which(name, path=tex_env["PATH"]),
                   "version": subprocess.check_output([name, "--version"], env=tex_env, text=True).splitlines()[0]}
            for name in ["pdflatex", "bibtex"]
        }
        commands = [["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                    ["bibtex", "main"],
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]]
        with (dest / "build.log").open("w") as log:
            for command in commands:
                subprocess.run(command, cwd=dest, env=tex_env, stdout=log, stderr=subprocess.STDOUT, check=True)
            # Long two-column appendices can need additional passes for line numbers.
            for _ in range(3):
                status = (dest / "main.log").read_text()
                needs_pass = "Line number reference failed" in status or "Label(s) may have changed" in status
                if not needs_pass:
                    break
                subprocess.run(commands[-1], cwd=dest, env=tex_env, stdout=log, stderr=subprocess.STDOUT, check=True)
        final_log = (dest / "main.log").read_text()
        assert "Line number reference failed" not in final_log and "Label(s) may have changed" not in final_log
        manifest["final_latex_checks"] = {
            "warning_count": final_log.count("Warning"),
            "undefined_count": final_log.count("undefined"),
            "overfull_count": final_log.count("Overfull"),
            "line_numbers_converged": True,
        }
        assert manifest["final_latex_checks"]["undefined_count"] == 0
        assert manifest["final_latex_checks"]["overfull_count"] == 0
        if shutil.which("pdftotext"):
            pages = subprocess.check_output(
                ["pdftotext", "-layout", str(dest / "main.pdf"), "-"], text=True).split("\f")
            limitations = [i + 1 for i, page in enumerate(pages) if "Limitations" in page]
            assert limitations == [9], limitations
            manifest["pagination"] = {"main_content_pages": 8, "limitations_start_page": 9,
                                      "total_pages": sum(bool(page.strip()) for page in pages),
                                      "appendix_format": "official ACL two-column, after references"}
        manifest["status"] = "BUILT"
        manifest["pdf_sha256"] = digest(dest / "main.pdf")
        (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(dest / ("main.tex" if args.source_only else "main.pdf"))


if __name__ == "__main__":
    main()
