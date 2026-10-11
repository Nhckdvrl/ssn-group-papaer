#!/usr/bin/env python3
"""Scaffold process files from templates/.

  python3 tools/process/new.py workbench <name>
  python3 tools/process/new.py experiment <workbench> <slug>
  python3 tools/process/new.py idea <workbench> <slug>

Numbers (E##, I##) continue from the highest number already used anywhere in the workbench.
Opening a workbench does not register it: add a PROPOSED row to workbench/README.md §9 and
let a human change it to ACTIVE.
"""
import argparse
import datetime as dt
import re
import sys

from common import ROOT, SLUG, TEMPLATES, WB


def next_number(d, prefix):
    used = [0]
    for f in d.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".py", ".json", ".sh"}:
            used += [int(n) for n in re.findall(rf"\b{prefix}(\d{{2,3}})\b", f.name)]
            if f.suffix == ".md":
                used += [int(n) for n in re.findall(rf"\b{prefix}(\d{{2,3}})\b", f.read_text(errors="ignore"))]
    return max(used) + 1


def write(path, text):
    if path.exists():
        sys.exit(f"已存在：{path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(f"created {path.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["workbench", "experiment", "idea"])
    ap.add_argument("names", nargs="+")
    args = ap.parse_args()
    date = dt.date.today().isoformat()
    for n in args.names:
        if not SLUG.match(n):
            sys.exit(f"名字只能用小写字母、数字和连字符：{n}")

    if args.kind == "workbench":
        (name,) = args.names
        d = WB / name
        if d.exists():
            sys.exit(f"已存在：{d.relative_to(ROOT)}")
        readme = (TEMPLATES / "workbench_readme.md").read_text().replace("<Workbench 名字>", name, 1)
        write(d / "README.md", readme)
        write(d / "CLAIMS.md", (TEMPLATES / "claims.md").read_text())
        write(d / "PAIN_LOG.md", (TEMPLATES / "pain_log.md").read_text())
        for sub in ("experiments", "ideas", "logs", "results"):
            write(d / sub / ".gitkeep", "")
        print("下一步：在 workbench/README.md §9 登记表加一行 PROPOSED；人确认后改为 ACTIVE-MAIN / ACTIVE-EXPLORE。")
        return

    if len(args.names) != 2:
        sys.exit("用法：new.py experiment|idea <workbench> <slug>")
    wb, slug = args.names
    d = WB / wb
    if not d.is_dir():
        sys.exit(f"workbench 不存在：{wb}")
    prefix, sub, tpl, title = {
        "experiment": ("E", "experiments", "experiment_card.md", "# E##：<名字>（<日期>）"),
        "idea": ("I", "ideas", "idea_card.md", "# I##：<一句话>（<日期>）"),
    }[args.kind]
    num = f"{prefix}{next_number(d, prefix):02d}"
    text = (TEMPLATES / tpl).read_text()
    text = text.replace(title, title.replace(f"{prefix}##", num).replace("<名字>", slug).replace("<一句话>", slug).replace("<日期>", date), 1)
    write(d / sub / f"{num}-{slug}.md", text)


if __name__ == "__main__":
    main()
