"""Run bookkeeping shared by the F scripts (copied from D/E; same Run class): run folder, run.json, SHA256SUMS.
Never overwrites a run. Identical copy in every experiments/<exp>/ folder so each folder runs on its own."""
import hashlib, json, os, platform, socket, sys, time
from pathlib import Path

F_ROOT = Path(__file__).resolve().parents[2]
C_WORK = Path(os.environ.get("C_WORK", "/home/azureuser/c/data/work/c6_full_20261031_02"))   # C graph tables, read only
D_WORK = Path(os.environ.get("D_WORK", "/home/azureuser/d/data/work"))                        # D tables, read only
META_DIR = Path(os.environ.get("META_DIR", "/home/azureuser/c/data/raw/meta_csv"))           # Meta CSV dump v7, read only
F_DATA = Path(os.environ.get("F_DATA", "/home/azureuser/f/data/work"))                        # F work tables (VM only)

def sha256(path, buf=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(buf):
            h.update(b)
    return h.hexdigest()

class Run:
    def __init__(self, run_id, script, config):
        self.dir = Path(script).resolve().parent / "runs" / run_id
        if self.dir.exists():
            sys.exit(f"{self.dir} exists; never overwrite a run (use a new run id)")
        self.dir.mkdir(parents=True)
        self.t0 = time.time()
        self.info = {"run_id": run_id, "script": Path(script).name, "script_sha256": sha256(script),
                     "common_sha256": sha256(Path(__file__)),
                     "config": config, "host": socket.gethostname(), "python": sys.version.split()[0],
                     "platform": platform.platform(), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     "results": {}}

    def log(self, key, value):
        self.info["results"][key] = value
        print(f"[{time.time() - self.t0:8.1f}s] {key}: {value}", flush=True)

    def finish(self):
        self.info["seconds"] = round(time.time() - self.t0, 1)
        (self.dir / "run.json").write_text(json.dumps(self.info, indent=2, default=str))
        sums = [f"{sha256(p)}  {p.name}" for p in sorted(self.dir.iterdir()) if p.is_file() and p.name != "SHA256SUMS"]
        (self.dir / "SHA256SUMS").write_text("\n".join(sums) + "\n")
        print(f"done in {self.info['seconds']} s -> {self.dir}")

def duck(threads=8, memory="44GB", path=None):
    """DuckDB connection with the F settings; path = on-disk database file for very large intermediate tables."""
    import duckdb
    tmp = F_DATA / "tmp"; tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path) if path else ":memory:")
    con.execute(f"SET threads={threads}; SET memory_limit='{memory}'; SET preserve_insertion_order=false; "
                f"SET temp_directory='{tmp}'")
    return con
