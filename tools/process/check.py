#!/usr/bin/env python3
"""Check the repository against the research process (workbench/README.md, EXECUTION.md).
No schedule checks: the process advances on state and evidence, not on calendar time.

Usage: python3 tools/process/check.py [--today YYYY-MM-DD] [--strict]
Exit code 1 if any ERROR (or any WARN with --strict).
"""
import argparse
import re
import sys

from common import LEVELS, ROOT, STATUSES, WB, choice, claims, field, parse_date, registry, today

README_MAX_LINES = 200
CARD_FIELDS = ["对应", "阳性对照", "噪声地板", "决策表（跑之前写）"]


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, where, msg):
        self.items.append((level, where, msg))

    def count(self, level):
        return sum(1 for i in self.items if i[0] == level)


def check_registry(rep, now):
    header, rows = registry()
    if header is None:
        rep.add("ERROR", "workbench/README.md", "找不到登记表（表头以 '| workbench |' 开头）")
        return []
    for col in ["状态", "目标会议", "截稿", "主张账本", "上次人审"]:
        if col not in header:
            rep.add("ERROR", "workbench/README.md", f"登记表缺少列：{col}")
    names = {r["name"] for r in rows}
    for d in sorted(p.name for p in WB.iterdir() if p.is_dir()):
        if d not in names:
            rep.add("WARN", f"workbench/{d}", "目录不在登记表中")
    for status in ("ACTIVE-MAIN", "ACTIVE-EXPLORE"):
        active = [r["name"] for r in rows if r.get("状态") == status]
        if len(active) > 1:
            rep.add("ERROR", "workbench/README.md", f"{status} 超过 1 条：{', '.join(active)}（容量规则 §1）")
    for r in rows:
        where = f"workbench/{r['name']}"
        if r.get("状态") not in STATUSES:
            rep.add("ERROR", where, f"状态 {r.get('状态')!r} 不在 {sorted(STATUSES)}")
        if not (WB / r["name"]).is_dir():
            rep.add("ERROR", where, "登记表中的目录不存在")
            continue
        deadline = parse_date(r.get("截稿"))
        if (r.get("状态", "").startswith("ACTIVE") or r.get("状态") == "PROPOSED") and deadline and deadline < now:
            rep.add("WARN", where, f"截稿日 {deadline} 已过，请更新目标会议（够投就投，不够就下一个会）")
    return rows


def check_active(rep, row):
    name = row["name"]
    d = WB / name
    where = f"workbench/{name}"
    readme = d / "README.md"
    if not readme.exists():
        rep.add("ERROR", where, "缺少 README.md")
        return
    n = len(readme.read_text().splitlines())
    if n > README_MAX_LINES:
        rep.add("WARN", where, f"README {n} 行 > {README_MAX_LINES}（过程细节移到 logs/ 或 results/）")
    ledger = re.sub(r"[`]", "", row.get("主张账本", "")).strip()
    if not ledger or ledger in {"—", "-"}:
        rep.add("ERROR", where, "登记表未指定主张账本（CLAIMS.md）")
    elif not (d / ledger).exists():
        rep.add("ERROR", where, f"主张账本 {ledger} 不存在")
    if not parse_date(row.get("上次人审")):
        rep.add("WARN", where, "没有人审记录（人审在决策点触发，见 EXECUTION.md §9）")
    if not (d / "PAIN_LOG.md").exists() and "痛点" not in readme.read_text():
        rep.add("WARN", where, "没有痛点日志（PAIN_LOG.md）")


def check_cards(rep, d):
    for card in sorted((d / "experiments").glob("E*.md")) if (d / "experiments").is_dir() else []:
        text = card.read_text()
        where = card.relative_to(ROOT)
        if field(text, "状态") is None:
            continue  # not a v4 experiment card (legacy notes)
        missing = [f for f in CARD_FIELDS if field(text, f) in (None, "")]
        if missing:
            rep.add("WARN", where, f"实验卡缺少字段：{', '.join(missing)}")
        status = choice(field(text, "状态"), ["PLANNED", "RUNNING", "DONE", "VOID"])
        plan = field(text, "决策表（跑之前写）") or ""
        if status in ("RUNNING", "DONE") and re.fullmatch(r"结果 A → ；结果 B → ；不确定 →\s*", plan):
            rep.add("WARN", where, "已运行但决策表为空（EXECUTION.md §2）")
        if status is None:
            rep.add("WARN", where, "状态未填（PLANNED / RUNNING / DONE / VOID）")
    for card in sorted((d / "ideas").glob("I*.md")) if (d / "ideas").is_dir() else []:
        text = card.read_text()
        src = field(text, "来源（必填，只能是其一）")
        if src is not None and src.startswith("痛点 P## / 测量异常"):
            rep.add("WARN", card.relative_to(ROOT), "idea 卡未写来源（IDEA_EXPLORATION.md §1）")


def check_claims(rep, d):
    path = d / "CLAIMS.md"
    for c in claims(path):
        col = lambda key: next((v for k, v in c.items() if key in k), "")
        cid, level = c.get("ID", "?"), col("等级").strip()
        if not col("主张").strip():
            continue  # empty template row
        where = path.relative_to(ROOT)
        if level not in LEVELS:
            rep.add("WARN", where, f"{cid} 等级 {level!r} 不在 L0–L5")
        elif LEVELS.index(level) >= 2 and not re.search(r"E\d+", col("证据")):
            rep.add("WARN", where, f"{cid} 为 {level} 但没有引用实验卡 E##")
        elif LEVELS.index(level) >= 3 and "未校对" in (col("校对") or "未校对"):
            rep.add("WARN", where, f"{cid} 为 {level} 但未校对（EXECUTION.md §5）")


def check_kills(rep):
    for f in sorted((ROOT / "failed").glob("*.md")):
        text = f.read_text()
        heads = [(m.start(), int(m.group(1))) for m in re.finditer(r"^#+ .*?\bK(\d{3,4})\b", text, re.M)]
        for i, (pos, kid) in enumerate(heads):
            if kid < 254:
                continue
            end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
            if "证据类别" not in text[pos:end]:
                rep.add("ERROR", f.relative_to(ROOT), f"K{kid} 缺少“证据类别”（templates/close_record.md）")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    now = today(args.today)
    rep = Report()
    rows = check_registry(rep, now)
    for row in rows:
        d = WB / row["name"]
        if not d.is_dir():
            continue
        if row.get("状态", "").startswith("ACTIVE"):
            check_active(rep, row)
        if row.get("状态") in {"ACTIVE-MAIN", "ACTIVE-EXPLORE", "PROPOSED"}:
            check_cards(rep, d)
            check_claims(rep, d)
    check_kills(rep)
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for level, where, msg in sorted(rep.items, key=lambda i: (order[i[0]], str(i[1]))):
        print(f"{level:5} {where}: {msg}")
    e, w = rep.count("ERROR"), rep.count("WARN")
    print(f"\n{e} error(s), {w} warning(s)")
    sys.exit(1 if e or (args.strict and w) else 0)


if __name__ == "__main__":
    main()
