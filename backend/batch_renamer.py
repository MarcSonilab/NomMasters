import os
from datetime import datetime

def scan_folder(folder: str, rows: list) -> list:
    existing = set(os.listdir(folder))
    result = []
    for row in rows:
        orig = row["original"]
        new = row["new"]
        if orig not in existing:
            status = "missing"
        elif new in existing:
            status = "conflict"
        else:
            status = "found"
        result.append({**row, "status": status})
    return result

def execute_rename(folder: str, rows: list) -> list:
    results = []
    for row in rows:
        if row.get("status") != "found":
            continue
        src = os.path.join(folder, row["original"])
        dst = os.path.join(folder, row["new"])
        try:
            os.rename(src, dst)
            results.append({**row, "ok": True, "error": None})
        except OSError as e:
            results.append({**row, "ok": False, "error": str(e)})
    return results

def export_log(results: list, path: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"NomsMasters - Log d'execucio - {ts}", "=" * 60, ""]
    for r in results:
        ok_str = "OK" if r.get("ok") else f"ERROR: {r.get('error', '')}"
        lines.append(f"  {r['original']}  ->  {r['new']}  [{ok_str}]")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
