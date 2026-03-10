import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QGuiApplication
from PyQt5.QtCore import Qt, QTimer

from widgets.tab_disenar import TabDisenar
from widgets.tab_simular import TabSimular
from widgets.custom_slider import CustomSlider
from logica.funciones_botones import ejecutar_accion


def resource_path(relative_path):
    """
    Obtiene la ruta absoluta de recursos.
    Compatible cuando la app se ejecuta como .exe
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class VentanaPrincipal(QMainWindow):
    """
    Ventana principal de la aplicación del convertidor Ćuk.
    Contiene:
        • Imagen del convertidor
        • Pestañas de Diseño y Simulación
        • Panel de control lateral
    """

    # ==============================
    # CONFIGURACIÓN GLOBAL VISUAL
    # ==============================
    COLOR_FONDO = "#212121"
    COLOR_PANEL = "#2e2e2e"
    FUENTE = "Segoe UI"

    def __init__(self, ancho=870, alto=600):
        super().__init__()
        self.size = (ancho, alto)
        self._inicializar_ui()

    # ==============================
    # INICIALIZACIÓN GENERAL
    # ==============================
    def _inicializar_ui(self):
        self._configurar_apariencia()
        self._crear_widgets()
        self._centrar_en_pantalla()
        self.show()

        # Ajustar imagen tras cargar completamente la ventana
        QTimer.singleShot(0, self._ajustar_imagen)

    # ==============================
    # CONFIGURACIÓN VISUAL VENTANA
    # ==============================
    def _configurar_apariencia(self):
        self.setWindowTitle("Convertidor CUK")
        self.resize(*self.size)
        self.setStyleSheet(f"background-color: {self.COLOR_FONDO}; color: white;")
        self.setWindowOpacity(0.98)
        self.setMaximumSize(900, 700)
        self.setMinimumSize(800, 580)
        self.setWindowIcon(QIcon(resource_path("recursos/logo.png")))
        self.setFont(QFont(self.FUENTE, 10))
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

    # ==============================
    # CREACIÓN DE WIDGETS
    # ==============================
    def _crear_widgets(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(15, 10, 15, 10)

        layout_principal.addLayout(self._crear_panel_izquierdo(), stretch=3)
        layout_principal.addLayout(self._crear_panel_derecho(), stretch=1)

        central_widget.setLayout(layout_principal)

    # ==============================
    # PANEL IZQUIERDO
    # ==============================
    def _crear_panel_izquierdo(self):
        layout = QVBoxLayout()

        titulo = QLabel("Conversor CUK")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont(self.FUENTE, 22, QFont.Bold))
        titulo.setStyleSheet(f"background-color: {self.COLOR_PANEL}; padding: 10px; border-radius: 8px;")
        titulo.setMaximumHeight(70)

        self.imagen = QLabel()
        self.imagen.setAlignment(Qt.AlignCenter)
        self.imagen.setStyleSheet(f"background-color: {self.COLOR_PANEL}; border-radius: 8px; padding: 5px;")
        self.pixmap_original = QPixmap(resource_path("recursos/Convertidor.png"))

        self.tabs = self._crear_tabs()

        layout.addWidget(titulo)
        layout.addWidget(self.imagen)
        layout.addWidget(self.tabs)

        return layout

    # ==============================
    # PESTAÑAS
    # ==============================
    def _crear_tabs(self):
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #555; background-color: #2b2b2b; }
            QTabBar::tab {
                background: #3d3d3d; color: white; padding: 10px 20px; border: 1px solid #555;
            }
            QTabBar::tab:hover { background: #484848; }
            QTabBar::tab:selected { background: #1e1e1e; border-bottom: 3px solid #aaa; }
        """)
        tabs.addTab(TabDisenar(), "Diseñar")
        tabs.addTab(TabSimular(), "Simular")
        return tabs

    # ==============================
    # PANEL DERECHO (CONTROLES)
    # ==============================
    def _crear_panel_derecho(self):
        layout = QVBoxLayout()

        slider_contenedor = self._crear_slider_simulacion()
        boton = self._crear_boton_ejecutar()

        layout.addStretch()
        layout.addLayout(slider_contenedor)
        layout.addSpacing(15)
        layout.addWidget(boton, alignment=Qt.AlignHCenter)
        layout.addStretch()

        return layout

    # ==============================
    # SLIDER DE TIEMPO
    # ==============================
    def _crear_slider_simulacion(self):
        layout = QVBoxLayout()

        label = QLabel("Tiempo de simulación")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont(self.FUENTE, 11, QFont.Bold))

        self.slider = CustomSlider()
        self.slider.valueChanged.connect(self._actualizar_tiempo)

        self.valor_label = QLabel()
        self.valor_label.setAlignment(Qt.AlignCenter)
        self.valor_label.setFont(QFont(self.FUENTE, 10))

        etiquetas = QHBoxLayout()
        min_lbl = QLabel("0 ms")
        max_lbl = QLabel("3.0 s")

        for lbl in (min_lbl, max_lbl):
            lbl.setFont(QFont(self.FUENTE, 9))
            lbl.setStyleSheet("color: #aaa;")

        etiquetas.addWidget(min_lbl)
        etiquetas.addStretch()
        etiquetas.addWidget(max_lbl)

        layout.addWidget(label)
        layout.addWidget(self.slider, alignment=Qt.AlignHCenter)
        layout.addLayout(etiquetas)
        layout.addWidget(self.valor_label)

        self._actualizar_tiempo(self.slider.value())
        return layout

    # ==============================
    # BOTÓN DE ACCIÓN
    # ==============================
    def _crear_boton_ejecutar(self):
        boton = QPushButton("Ejecutar acción")
        boton.setFixedSize(160, 45)
        boton.setCursor(Qt.PointingHandCursor)
        boton.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                padding: 6px;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #2e2e2e; }
        """)
        boton.clicked.connect(lambda: ejecutar_accion(self, self.tabs))
        return boton

    # ==============================
    # FUNCIONES AUXILIARES
    # ==============================
    def _actualizar_tiempo(self, valor):
        valor_normalizado = (valor / self.slider.maximum()) ** 2
        valor_real = int(valor_normalizado * self.slider.maximum())

        if valor_real < 1000:
            self.valor_label.setText(f"{valor_real} ms")
        else:
            self.valor_label.setText(f"{valor_real/1000:.2f} s")

    def _ajustar_imagen(self):
        if self.pixmap_original and not self.pixmap_original.isNull():
            pixmap = self.pixmap_original.scaled(
                self.imagen.width(),
                self.imagen.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.imagen.setPixmap(pixmap)

    def resizeEvent(self, event):
        self._ajustar_imagen()
        super().resizeEvent(event)

    def _centrar_en_pantalla(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )