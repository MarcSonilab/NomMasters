import os
import platform
from datetime import datetime

def scan_folder(folder: str, rows: list) -> list:
    # Only consider files, not subdirectories
    entries = [e for e in os.listdir(folder) if os.path.isfile(os.path.join(folder, e))]
    # Windows NTFS is case-insensitive; normalise to avoid false "missing"
    is_windows = platform.system() == "Windows"
    if is_windows:
        existing_lower = {name.lower(): name for name in entries}
        def _norm(name): return name.lower()
    else:
        def _norm(name): return name

    # Projected disk state: updated as renames are planned, enabling permutation renames
    # (e.g. A->B, C->A works when B->C frees up B first in the batch)
    projected = set(existing_lower.keys() if is_windows else entries)

    result = []
    seen_targets = set()
    seen_origins = set()  # tracks origins consumed by case-only renames
    for row in rows:
        orig = row["original"]
        new  = row["new"]
        orig_norm = _norm(orig)
        new_norm  = _norm(new)
        if orig_norm not in projected:
            status = "missing"
        elif orig == new:
            status = "conflict"
        elif is_windows and orig.lower() == new.lower():
            # Case-only rename: valid on NTFS, but block duplicate origins
            if orig_norm in seen_origins:
                status = "conflict"
            else:
                seen_origins.add(orig_norm)
                seen_targets.add(new_norm)
                status = "found"
        elif orig_norm in seen_origins:
            # Origin already consumed by a case-only rename above
            status = "conflict"
        elif new_norm in projected and new_norm != orig_norm:
            status = "conflict"
        elif new_norm in seen_targets:
            status = "conflict"
        else:
            projected.discard(orig_norm)
            projected.add(new_norm)
            seen_targets.add(new_norm)
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
        # Re-validate just before renaming to avoid TOCTOU issues
        if not os.path.exists(src):
            results.append({**row, "ok": False, "error": "fitxer origen ja no existeix"})
            continue
        if os.path.exists(dst) and not (platform.system() == "Windows" and src.lower() == dst.lower()):
            results.append({**row, "ok": False, "error": "fitxer destí ja existeix (conflicte)"})
            continue
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
        ok_str = "OK" if r.get("ok") is True else f"ERROR: {r.get('error', '')}"
        lines.append(f"  {r['original']}  ->  {r['new']}  [{ok_str}]")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
