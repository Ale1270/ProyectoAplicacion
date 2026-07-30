import sys
import os
from PyQt5.QtWidgets import QApplication
from ui_mainwindow import VentanaPrincipal


def obtener_ruta_recurso(ruta_relativa):
    """
    Obtiene la ruta absoluta para recursos, compatible con desarrollo
    y con el ejecutable generado por PyInstaller.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())

