from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QGridLayout
)
from PyQt5.QtCore import Qt


class VentanaAyuda(QDialog):
    """
    Ventana de Ayuda con el mismo diseño estético que 'Acerca de' (sin barra de título,
    panel oscuro, bordes limpios y pestañas unificadas), libre de emojis y enfocada
    exclusivamente en el lanzamiento de las guías interactivas.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guía de Uso y Ayuda - Convertidor Ćuk")
        self.setFixedSize(620, 560)

        # Ventana sin marco del sistema operativo para mantener el mismo diseño que Acerca de
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Variable para almacenar la posición de arrastre de la ventana
        self._drag_pos = None

        self._aplicar_estilos()
        self._crear_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def _aplicar_estilos(self):
        # Mismos colores y bordes que VentanaAcercaDe
        self.setStyleSheet("""
            QDialog {
                background-color: #212121;
                color: #FFFFFF;
                border: 1px solid #555555;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2B2B2B;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #3D3D3D;
                color: #FFFFFF;
                padding: 10px 22px;
                border: 1px solid #555555;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                min-width: 160px;
            }
            QTabBar::tab:hover {
                background-color: #484848;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border-bottom: 3px solid #AAAAAA;
            }
            QLabel {
                color: #DDDDDD;
                font-size: 13px;
                border: none;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #2E2E2E;
            }
            QPushButton#btn_iniciar_seccion {
                background-color: #3A3A3A;
                border: 1px solid #555555;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#btn_iniciar_seccion:hover {
                background-color: #007ACC;
                border-color: #0099FF;
            }
        """)

    def _crear_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        tabs = QTabWidget()

        # Pestaña única: Tours Guiados
        tabs.addTab(self._crear_tab_tours(), "Guías Interactivas")

        # Botón de cierre inferior
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.clicked.connect(self.accept)

        layout_btn = QHBoxLayout()
        layout_btn.addStretch()
        layout_btn.addWidget(btn_cerrar)

        layout_principal.addWidget(tabs)
        layout_principal.addSpacing(14)
        layout_principal.addLayout(layout_btn)

    def _crear_tab_tours(self):
        tab_tours = QWidget()
        layout_tours = QVBoxLayout(tab_tours)
        layout_tours.setContentsMargins(20, 16, 20, 16)
        layout_tours.setSpacing(10)

        lbl_intro = QLabel("Selecciona la sección sobre la que deseas recibir asistencia guiada:")
        lbl_intro.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        layout_tours.addWidget(lbl_intro)

        secciones = [
            ("1. Descripción General", "Conoce la estructura básica de la aplicación y sus pestañas.", "general"),
            ("2. Cargar Ejemplos", "Descubre cómo utilizar configuraciones y casos predefinidos.", "ejemplos"),
            ("3. Ejemplo de Diseño", "Aprende a ingresar parámetros y calcular los filtros L y C.", "diseno"),
            ("4. Ejemplo de Simulación", "Configura tiempos de análisis y genera respuestas temporales.", "simulacion"),
            ("5. Visualización de Gráficas", "Analiza las curvas dinámicas, transitorios y rizado.", "graficas"),
            ("6. Características en Estable", "Interpreta potencias, eficiencias y tiempo de asentamiento.", "estable"),
        ]

        grid = QGridLayout()
        grid.setSpacing(8)

        for i, (titulo, desc, clave) in enumerate(secciones):
            lbl_info = QLabel(f"<b>{titulo}</b><br><span style='color: #aaaaaa; font-size: 11px;'>{desc}</span>")
            lbl_info.setWordWrap(True)

            btn = QPushButton("Iniciar")
            btn.setObjectName("btn_iniciar_seccion")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(80, 28)
            btn.clicked.connect(lambda checked, c=clave: self._lanzar_tour(c))

            grid.addWidget(lbl_info, i, 0)
            grid.addWidget(btn, i, 1)

        layout_tours.addLayout(grid)
        layout_tours.addSpacing(6)

        btn_completo = QPushButton("Iniciar Tour Completo (Todos los pasos)")
        btn_completo.setCursor(Qt.PointingHandCursor)
        btn_completo.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #0099FF; }
            QPushButton:pressed { background-color: #005999; }
        """)
        btn_completo.clicked.connect(lambda: self._lanzar_tour("todos"))

        layout_tours.addWidget(btn_completo, alignment=Qt.AlignCenter)
        layout_tours.addStretch()

        return tab_tours

    def _lanzar_tour(self, clave_seccion):
        """Cierra el diálogo y solicita al padre iniciar la sección seleccionada."""
        self.accept()
        if self.parent() and hasattr(self.parent(), "iniciar_guia_interactiva"):
            self.parent().iniciar_guia_interactiva(seccion=clave_seccion)


def mostrar_ayuda(parent=None):
    ventana = VentanaAyuda(parent)
    ventana.exec_()