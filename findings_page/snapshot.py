"""Copy what analysis.sql reads from the poller's data/ into
findings_page/snapshot/, so the page's queries never hold the live files
open (the poller appends to them and replaces latest.json every 10 s).
Later runs copy only the files that changed.

    .venv\\Scripts\\python findings_page\\snapshot.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SRC = REPO / "data"
DST = HERE / "snapshot"

n = 0
for sub in ("positions", "official", "arrivals", "schedule"):
    for f in (SRC / sub).rglob("*"):
        if not f.is_file() or f.suffix == ".tmp":
            continue
        out = DST / "data" / f.relative_to(SRC)
        st = f.stat()
        if out.exists() and out.stat().st_size == st.st_size and out.stat().st_mtime >= st.st_mtime:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
        n += 1
(DST / "data").mkdir(parents=True, exist_ok=True)
shutil.copy2(SRC / "latest.json", DST / "data" / "latest.json")
shutil.copy2(REPO / "stops.csv", DST / "stops.csv")
print(f"copied {n} changed files into {DST}")
