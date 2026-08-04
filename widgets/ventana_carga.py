from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class HiloSimulacion(QThread):
    finalizado = pyqtSignal(tuple, dict)
    error = pyqtSignal(str)
    progreso = pyqtSignal(int)

    def __init__(self, fn_simular, fn_metricas, args_sim):
        super().__init__()
        self.fn_simular = fn_simular
        self.fn_metricas = fn_metricas
        self.args_sim = args_sim

    def run(self):
        try:
            def reportar_progreso(porcentaje):
                self.progreso.emit(porcentaje)

            t, iL1, vC1, iL2, Vo = self.fn_simular(*self.args_sim, callback_progreso=reportar_progreso)

            Vin, L1, C1, L2, C2, R, D, f_sw, t_sim = self.args_sim
            metricas = self.fn_metricas(Vin, R, D, t, iL1, iL2, Vo, f_sw)

            self.progreso.emit(100)
            self.finalizado.emit((t, iL1, vC1, iL2, Vo), metricas if metricas else {})
        except Exception as e:
            self.error.emit(str(e))


class VentanaCarga(QDialog):
    """
    Barra de progreso minimalista centrada sobre la app.
    Permite cambiar de programa en la PC libremente sin flotar sobre otras apps.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. Mantenemos sin marcos y fondo transparente,
        # PERO quitamos Qt.WindowStaysOnTopHint para que no tape otros programas del PC
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedSize(450, 10)
        self._inicializar_ui()

        # 2. Centrar la barra exactamente en medio de la ventana principal
        if parent:
            geo_parent = parent.geometry()
            x = geo_parent.x() + ((geo_parent.width() - self.width()) // 2) - 25
            y = geo_parent.y() + ((geo_parent.height() - self.height()) // 2) + 35
            self.move(x, y)

    def _inicializar_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        # Estilos adaptados al tema oscuro de la aplicación principal
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2E2E2E;
                border: 1px solid #555555;
                border-radius: 8px;
            }
            QProgressBar::chunk {
                background-color: #AAAAAA;
                border-radius: 7px;
            }
        """)

        layout.addWidget(self.progress_bar)

    def actualizar_progreso(self, valor):
        self.progress_bar.setValue(valor)