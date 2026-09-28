"""Extra WMT19 directions for the breadth check (single-reference; the AR multi-reference
substrate exists only for En->De and stays the primary)."""
import html, os, re, sys, tarfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
SEG = re.compile(r'<seg id="\d+">(.*)</seg>')

PAIRS = {"deen": ("de", "en"), "enru": ("en", "ru"), "ruen": ("ru", "en")}


def extract(path):
    out = []
    for line in open(path, encoding="utf-8"):
        m = SEG.search(line.strip())
        if m:
            out.append(html.unescape(m.group(1)).strip())
    return out


def main():
    tgz = os.path.join(RAW, "wmt19_test.tgz")
    with tarfile.open(tgz) as tf:
        names = [n for n in tf.getnames()
                 if any(f"newstest2019-{p}" in n for p in PAIRS) and n.endswith(".sgm")]
        for n in names:
            tf.extract(n, RAW)
    for pair, (s, t) in PAIRS.items():
        src = extract(os.path.join(RAW, "sgm", f"newstest2019-{pair}-src.{s}.sgm"))
        ref = extract(os.path.join(RAW, "sgm", f"newstest2019-{pair}-ref.{t}.sgm"))
        assert len(src) == len(ref), (pair, len(src), len(ref))
        open(os.path.join(ROOT, "data", f"newstest2019.{pair}.src"), "w",
             encoding="utf-8").write("\n".join(src) + "\n")
        open(os.path.join(ROOT, "data", f"newstest2019.{pair}.ref"), "w",
             encoding="utf-8").write("\n".join(ref) + "\n")
        print(f"{pair}: {len(src)} segments")


if __name__ == "__main__":
    main()
