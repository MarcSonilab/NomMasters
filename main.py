import sys, os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript, QWebEngineSettings, QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QFile, QIODevice
from backend.bridge import Bridge

FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "index.html")

def _load_qwebchannel_js():
    f = QFile(":/qtwebchannel/qwebchannel.js")
    if not f.open(QIODevice.OpenModeFlag.ReadOnly):
        raise RuntimeError(
            "Cannot open Qt resource :/qtwebchannel/qwebchannel.js — "
            "check that PyQt6-Qt6-WebChannel is installed correctly."
        )
    js = bytes(f.readAll()).decode()
    f.close()
    return js

class DebugPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, source):
        print(f"JS [{line}] {msg}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NomsMasters")
        self.setMinimumSize(1024, 768)
        self.resize(1280, 800)

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        page = DebugPage(self.view)
        self.view.setPage(page)

        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        script = QWebEngineScript()
        script.setName("qwebchannel")
        script.setSourceCode(_load_qwebchannel_js())
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        page.scripts().insert(script)

        self.channel = QWebChannel(page)
        self.bridge = Bridge(self)
        self.channel.registerObject("bridge", self.bridge)
        page.setWebChannel(self.channel)

        self.view.setUrl(QUrl.fromLocalFile(FRONTEND))

def _run():
    app = QApplication(sys.argv)
    app.setApplicationName("NomsMasters")
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())

if __name__ == "__main__":
    _run()
