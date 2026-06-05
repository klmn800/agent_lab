"""One-shot maintenance helper: split research_log.md into active (>=2026-05-14)
and an archive season file (<=2026-05-13). Byte-exact move. Self-removes."""
import os, re

WS = r"E:\options_scanner\agents\earnings_researcher"
SRC = os.path.join(WS, "memory", "research_log.md")
ARCHIVE = os.path.join(WS, "memory", "archive", "research_log_2026-Q2_spring-earnings.md")
CUTOFF = "2026-05-14"  # blocks with date >= CUTOFF stay active

with open(SRC, encoding="utf-8") as f:
    text = f.read()
lines = text.splitlines(keepends=True)

# Partition into preamble + session blocks (a block starts at a '## Session:' line).
preamble = []
blocks = []  # list of list-of-lines
cur = None
for ln in lines:
    if ln.startswith("## Session:"):
        if cur is not None:
            blocks.append(cur)
        cur = [ln]
    else:
        if cur is None:
            preamble.append(ln)
        else:
            cur.append(ln)
if cur is not None:
    blocks.append(cur)

date_re = re.compile(r"## Session:\s*(\d{4}-\d{2}-\d{2})")
time_re = re.compile(r"(\d{1,2}):(\d{2})\s*(AM|PM)")

def keyfor(block):
    head = block[0]
    d = date_re.search(head).group(1)
    m = time_re.search(head)
    mins = 0
    if m:
        h = int(m.group(1)); mn = int(m.group(2)); ap = m.group(3)
        if ap == "PM" and h != 12: h += 12
        if ap == "AM" and h == 12: h = 0
        mins = h * 60 + mn
    return d, mins

tagged = [(keyfor(b), b) for b in blocks]
active = [t for t in tagged if t[0][0] >= CUTOFF]
archive = [t for t in tagged if t[0][0] < CUTOFF]

# active: newest first (date,time desc, stable); archive: chronological asc, stable
active.sort(key=lambda t: t[0], reverse=True)
archive.sort(key=lambda t: t[0])

def render(tlist):
    return "".join("".join(b) for (_, b) in tlist)

# --- archive file ---
season_header = (
    "# Earnings Research Log — Archive: 2026 Spring Earnings Season\n\n"
    "> Spring 2026 earnings season — Q1 calendar results (and the fiscal quarters\n"
    "> reported in this wave), announced ~mid-Apr through mid-May 2026. Rolled off the\n"
    "> active `research_log.md` during the 2026-05-28 weekly maintenance session.\n"
    "> Sessions below are in chronological order (oldest first).\n\n---\n\n"
)
os.makedirs(os.path.dirname(ARCHIVE), exist_ok=True)
with open(ARCHIVE, "w", encoding="utf-8") as f:
    f.write(season_header + render(archive))

# --- new active log (placeholders for authored top/bottom matter) ---
new_active = (
    "# Earnings Research Log\n\n"
    "__LEDGER_AND_CARRYOVERS__\n\n"
    "---\n\n# Research Sessions (newest first)\n\n"
    + render(active)
    + "\n---\n\n# Maintenance History\n\n__MAINT_ENTRY__\n"
)
with open(SRC, "w", encoding="utf-8") as f:
    f.write(new_active)

# --- verification report ---
print("ACTIVE blocks ({}):".format(len(active)))
for (k, b) in active:
    print("  ", k, "|", b[0].rstrip())
print("ARCHIVE blocks ({}):".format(len(archive)))
for (k, b) in archive:
    print("  ", k, "|", b[0].rstrip())
print("preamble lines:", len(preamble), "| preamble repr:", repr("".join(preamble)))
print("archive file lines:", season_header.count(chr(10)) + render(archive).count(chr(10)))
print("active file lines:", new_active.count(chr(10)))
print("total original blocks:", len(blocks), "= active", len(active), "+ archive", len(archive))

os.remove(os.path.abspath(__file__))
print("removed self.")
