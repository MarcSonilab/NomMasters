import os, pytest
from backend.batch_renamer import scan_folder, execute_rename, export_log

@pytest.fixture
def folder(tmp_path):
    (tmp_path / "original_a.mov").write_text("")
    (tmp_path / "original_b.wav").write_text("")
    (tmp_path / "conflict_new.mov").write_text("")
    return tmp_path

def test_found_status(folder):
    rows = [{"original": "original_a.mov", "new": "renamed_a.mov"}]
    result = scan_folder(str(folder), rows)
    assert result[0]["status"] == "found"

def test_missing_status(folder):
    rows = [{"original": "does_not_exist.mov", "new": "renamed.mov"}]
    result = scan_folder(str(folder), rows)
    assert result[0]["status"] == "missing"

def test_conflict_status(folder):
    rows = [{"original": "original_a.mov", "new": "conflict_new.mov"}]
    result = scan_folder(str(folder), rows)
    assert result[0]["status"] == "conflict"

def test_execute_rename_renames_found(folder):
    rows = [{"original": "original_a.mov", "new": "renamed_a.mov", "status": "found"}]
    results = execute_rename(str(folder), rows)
    assert results[0]["ok"] is True
    assert (folder / "renamed_a.mov").exists()
    assert not (folder / "original_a.mov").exists()

def test_execute_rename_skips_non_found(folder):
    rows = [{"original": "does_not_exist.mov", "new": "new.mov", "status": "missing"}]
    results = execute_rename(str(folder), rows)
    assert results == []

def test_export_log_creates_file(folder, tmp_path):
    results = [{"original": "a.mov", "new": "b.mov", "ok": True, "error": None}]
    log_path = str(tmp_path / "log.txt")
    export_log(results, log_path)
    assert os.path.exists(log_path)
    content = open(log_path).read()
    assert "a.mov" in content
    assert "b.mov" in content
