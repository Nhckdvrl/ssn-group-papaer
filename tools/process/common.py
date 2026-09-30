"""Shared helpers for the research-process tools (stdlib only)."""
import datetime as dt
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
WB = ROOT / "workbench"
TEMPLATES = ROOT / "templates"
STATUSES = {"ACTIVE-MAIN", "ACTIVE-EXPLORE", "PROPOSED", "PAUSED", "CLOSED"}
LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def today(arg=None):
    return dt.date.fromisoformat(arg) if arg else dt.date.today()


def parse_date(text):
    m = DATE.search(text or "")
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(0))
    except ValueError:
        return None


def md_rows(lines, start):
    """Yield cell lists of a markdown table whose header is lines[start]."""
    for line in lines[start + 2:]:
        if not line.strip().startswith("|"):
            break
        yield [c.strip() for c in line.strip().strip("|").split("|")]


def registry():
    """Parse the registry table in workbench/README.md (header starts with '| workbench |')."""
    lines = (WB / "README.md").read_text().splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^\|\s*workbench\s*\|", line):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            rows = []
            for cells in md_rows(lines, i):
                row = dict(zip(header, cells))
                row["name"] = re.sub(r"[`\[\]]|\(.*?\)", "", row.get("workbench", "")).strip().rstrip("/")
                rows.append(row)
            return header, rows
    return None, []


def claims(path):
    """Parse the first table in a CLAIMS.md whose header has 'ID' and '等级'."""
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("|") and "ID" in line and "等级" in line:
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            return [dict(zip(header, cells)) for cells in md_rows(lines, i)]
    return []


def field(text, name):
    """Value of a '- **name：** value' line in a card, or None."""
    m = re.search(r"^\s*-\s*\*\*" + re.escape(name) + r"[：:]\*\*\s*(.*)$", text, re.M)
    return m.group(1).strip() if m else None


def choice(value, options):
    """Return the chosen option if the template's 'A / B / C' list was narrowed down."""
    if value is None:
        return None
    found = [o for o in options if re.search(r"\b" + re.escape(o) + r"\b", value)]
    return found[0] if len(found) == 1 else None
