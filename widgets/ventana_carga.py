from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint


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
    Ventana de carga emergente que se posiciona de forma fija
    sobre el espacio reservado de la ventana principal.
    """

    def __init__(self, parent=None, widget_referencia=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._inicializar_ui()

        # Si nos pasan el widget reservado, nos superponemos exactamente sobre él
        if widget_referencia:
            self.posicionar_sobre(widget_referencia)

    def _inicializar_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2E2E2E;
                border: 1px solid #555555;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background-color: #AAAAAA;
                border-radius: 5px;
            }
        """)

        layout.addWidget(self.progress_bar)

    def posicionar_sobre(self, widget_destino):
        """Calcula las coordenadas globales del espacio reservado y se posiciona encima."""
        pos_global = widget_destino.mapToGlobal(QPoint(0, 0))
        self.setGeometry(
            pos_global.x(),
            pos_global.y(),
            widget_destino.width(),
            widget_destino.height()
        )

    def actualizar_progreso(self, valor):
        self.progress_bar.setValue(valor)