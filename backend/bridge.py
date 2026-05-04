import csv, json, os
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from backend.batch_renamer import scan_folder, execute_rename, export_log

class Bridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_widget = parent

    @pyqtSlot(result=str)
    def pick_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self._parent_widget, "Selecciona CSV", "",
            "Fitxers CSV (*.csv *.txt);;Tots (*)"
        )
        return path or ""

    @pyqtSlot(result=str)
    def pick_folder(self):
        path = QFileDialog.getExistingDirectory(
            self._parent_widget, "Selecciona carpeta"
        )
        return path or ""

    @pyqtSlot(str, result=str)
    def parse_csv(self, path: str) -> str:
        rows = []
        try:
            with open(path, newline="", encoding="utf-8") as f:
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample, delimiters=",;")
                reader = csv.reader(f, dialect)
                for row in reader:
                    if len(row) >= 2 and row[0].strip().lower() not in ("nom_original", "original"):
                        rows.append({"original": row[0].strip(), "new": row[1].strip()})
        except Exception as e:
            return json.dumps({"error": str(e)})
        return json.dumps({"rows": rows})

    @pyqtSlot(str, str, result=str)
    def scan_folder_js(self, folder: str, rows_json: str) -> str:
        try:
            rows = json.loads(rows_json)
            result = scan_folder(folder, rows)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @pyqtSlot(str, str, result=str)
    def execute_rename_js(self, folder: str, rows_json: str) -> str:
        try:
            rows = json.loads(rows_json)
            result = execute_rename(folder, rows)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @pyqtSlot(str, result=str)
    def export_log_js(self, results_json: str) -> str:
        try:
            results = json.loads(results_json)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})
        path, _ = QFileDialog.getSaveFileName(
            self._parent_widget,
            "Desa log",
            f"nomsmasters_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Fitxers de text (*.txt)"
        )
        if not path:
            return json.dumps({"ok": False, "error": "cancel·lat"})
        try:
            export_log(results, path)
            return json.dumps({"ok": True, "path": path})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(str, result=str)
    def confirm_rename(self, count: str) -> str:
        reply = QMessageBox.question(
            self._parent_widget,
            "Confirmar renombrat",
            f"Estàs a punt de renombrar {count} fitxers. Aquesta accio no es pot desfer. Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return "yes" if reply == QMessageBox.StandardButton.Yes else "no"
