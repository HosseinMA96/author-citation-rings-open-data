"""F17 redaction (POSTHOC.md round 6 addendum, disclosure control; laptop). Reads the f17 record fetched from the VM
(run.json, stdout.log), removes the P18 profile fields of every author group smaller than MIN_CELL (percentile ranks and
flag shares; counts are kept), and writes record.json (the redacted run.json) and stdout.redacted.log into this run's
folder. Logs the SHA-256 of the originals and the removed field names, never their values. The originals stay on the
analysis VM; the laptop copies are deleted after this run (see runs/<F17_RUN>/REDACTED.md).
usage: python f17_redact.py RUN_ID F17_RUN
"""
import hashlib, json, sys
from pathlib import Path
from common import Run

MIN_CELL = 10
KEEP = {"authors", "already_positive_via_meta"}
F17 = sys.argv[2]
src = Path(__file__).resolve().parent / "runs" / F17
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
orig = {p.name: sha(p) for p in (src / "run.json", src / "stdout.log")}
listed = dict(reversed(l.split()) for l in (src / "SHA256SUMS").read_text().splitlines() if l.strip())
assert all(listed.get(k, v) == v for k, v in orig.items()), "fetched files differ from the run's SHA256SUMS"
run = Run(sys.argv[1], __file__, {"f17_run": F17, "min_cell": MIN_CELL, "original_sha256": orig})

rec = json.loads((src / "run.json").read_text())
p18 = rec["results"]["P18_frontiers"]
removed = {}
for grp, g in p18.items():
    if isinstance(g, dict) and "authors" in g and g["authors"] < MIN_CELL:
        drop = sorted(k for k in g if k not in KEEP)
        for k in drop:
            del g[k]
        if drop:
            g["profile_suppressed"] = f"fewer than {MIN_CELL} authors (POSTHOC.md round 6 addendum)"
        removed[grp] = {"authors": g["authors"], "fields_removed": drop}
(run.dir / "record.json").write_text(json.dumps(rec, indent=2))

lines, hits = [], 0
for line in (src / "stdout.log").read_text().splitlines():
    if "] P18_frontiers: " in line:
        line = line.split("] P18_frontiers: ")[0] + "] P18_frontiers: " + repr(p18); hits += 1
    lines.append(line)
assert hits == 1, hits
(run.dir / "stdout.redacted.log").write_text("\n".join(lines) + "\n")
for name in ("record.json", "stdout.redacted.log"):
    text = (run.dir / name).read_text()
    assert "pct_" not in text and "'share_" not in text and '"share_' not in text, f"profile field left in {name}"
run.log("removed", removed)
run.log("kept_counts", {g: v["authors"] for g, v in p18.items() if isinstance(v, dict) and "authors" in v})
run.finish()
