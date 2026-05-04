import sys, os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QFile, QIODevice
from backend.bridge import Bridge

FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "index.html")

def _load_qwebchannel_js():
    f = QFile(":/qtwebchannel/qwebchannel.js")
    f.open(QIODevice.OpenModeFlag.ReadOnly)
    js = bytes(f.readAll()).decode()
    f.close()
    return js

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NomsMasters")
        self.setMinimumSize(1024, 768)
        self.resize(1280, 800)

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        # Inject qwebchannel.js before page scripts run
        script = QWebEngineScript()
        script.setName("qwebchannel")
        script.setSourceCode(_load_qwebchannel_js())
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        self.view.page().scripts().insert(script)

        # Register bridge on QWebChannel
        self.channel = QWebChannel(self.view.page())
        self.bridge = Bridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)

        self.view.setUrl(QUrl.fromLocalFile(FRONTEND))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("NomsMasters")
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())
