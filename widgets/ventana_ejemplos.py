from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class VentanaEjemplos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Ejemplos de Diseño - Convertidor Ćuk")

        # 1. Ocultar la barra de título del sistema operativo (Ventana sin marco)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # 2. Ajustar tamaño amplio y definir tamaño mínimo
        self.resize(900, 640)
        self.setMinimumSize(850, 600)

        # Estilo global con borde tenue para delimitar la ventana sin marco
        self.setStyleSheet("""
            QDialog {
                background-color: #212121;
                color: white;
                border: 1px solid #555555;
            }
        """)

        self._inicializar_ui()

    def _inicializar_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 15, 20, 20)
        layout_principal.setSpacing(15)

        # -------------------------------------------------------------
        # ENCABEZADO: TÍTULO CENTRADO CON BOTÓN 'X' A LA DERECHA
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        lbl_titulo = QLabel("Seleccione un ejemplo")
        lbl_titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #ffffff; border: none;")

        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(32, 32)
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.setToolTip("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #AAAAAA;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E81123;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #BF0F1D;
            }
        """)
        btn_cerrar.clicked.connect(self.reject)

        # Se agrega un espaciador de 32px a la izquierda para equilibrar el botón 'X'
        # y mantener el título perfectamente centrado
        header_layout.addSpacing(32)
        header_layout.addStretch()
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(btn_cerrar)

        layout_principal.addLayout(header_layout)

        # -------------------------------------------------------------
        # GRILLA DE EJEMPLOS (2x2)
        # -------------------------------------------------------------
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # Definición de los 4 casos de estudio detallados
        self.ejemplos = [
            {
                "titulo": "1. Fuente Simétrica (Reductor)",
                "descripcion": (
                    "<b>Uso típico:</b> Alimentación de amplificadores operacionales y circuitos analógicos de precisión.<br><br>"
                    "<b>Importancia:</b> Genera un riel negativo limpio (-12V) a partir de una barra principal de +24V. "
                    "A diferencia del Buck-Boost, la corriente de salida continua del Ćuk minimiza el ruido en señales sensibles."
                ),
                "datos": {
                    "vin": "24",
                    "vout": "12",
                    "pout": "36",
                    "delta_i": "0.5",
                    "delta_v": "0.1",
                    "frec_index": 1  # 50 kHz
                }
            },
            {
                "titulo": "2. Elevador Industrial / Automotriz",
                "descripcion": (
                    "<b>Uso típico:</b> Sistemas automotrices (12V) que requieren polarización negativa de mayor voltaje (-24V).<br><br>"
                    "<b>Importancia:</b> Permite elevar la magnitud del voltaje manteniendo rizado ultra bajo. "
                    "Muy usado para excitar actuadores piezoeléctricos o cargas capacitivas sin generar interferencias de radiofrecuencia."
                ),
                "datos": {
                    "vin": "12",
                    "vout": "24",
                    "pout": "48",
                    "delta_i": "0.3",
                    "delta_v": "0.05",
                    "frec_index": 2  # 100 kHz
                }
            },
            {
                "titulo": "3. Inversor Unitario (1:1)",
                "descripcion": (
                    "<b>Uso típico:</b> Generación de rieles simétricos espejo (de +15V a -15V) en instrumentación médica.<br><br>"
                    "<b>Importancia:</b> Opera con ciclo de trabajo D = 0.5. "
                    "En este punto, la transferencia de energía a través del capacitor de acoplamiento es óptima y simétrica, maximizando la eficiencia de los componentes pasivos."
                ),
                "datos": {
                    "vin": "15",
                    "vout": "15",
                    "pout": "22.5",
                    "delta_i": "0.4",
                    "delta_v": "0.1",
                    "frec_index": 0  # 25 kHz
                }
            },
            {
                "titulo": "4. Alta Frecuencia / Solar (MPPT)",
                "descripcion": (
                    "<b>Uso típico:</b> Algoritmos de seguimiento del punto de máxima potencia (MPPT) en paneles solares.<br><br>"
                    "<b>Importancia:</b> Al conmutar a 250 kHz se reduce dramáticamente el tamaño de inductores y capacitores. "
                    "La corriente de entrada sin interrupciones evita oscilaciones de potencia en el panel fotovoltaico."
                ),
                "datos": {
                    "vin": "48",
                    "vout": "24",
                    "pout": "120",
                    "delta_i": "0.1",
                    "delta_v": "0.02",
                    "frec_index": 3  # 250 kHz
                }
            }
        ]

        # Crear y posicionar cada tarjeta en la cuadrícula (2 filas x 2 columnas)
        posiciones = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i, ej in enumerate(self.ejemplos):
            tarjeta = self._crear_tarjeta_ejemplo(ej)
            row, col = posiciones[i]
            grid_layout.addWidget(tarjeta, row, col)

        layout_principal.addLayout(grid_layout)

    def _crear_tarjeta_ejemplo(self, info_ejemplo):
        """Crea un marco estilizado (tarjeta) para cada ejemplo de la cuadrícula."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2e2e2e;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                border: 1px solid #AAAAAA;
            }
        """)

        layout_card = QVBoxLayout(card)
        layout_card.setSpacing(8)

        # 1. Título blanco en negrita
        lbl_titulo = QLabel(info_ejemplo["titulo"])
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #FFFFFF; border: none;")

        # 2. Descripción
        lbl_desc = QLabel(info_ejemplo["descripcion"])
        lbl_desc.setFont(QFont("Segoe UI", 9))
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #CCCCCC; border: none; line-height: 120%;")

        # 3. Botón de cargar ejemplo
        btn_cargar = QPushButton("Cargar Ejemplo")
        btn_cargar.setCursor(Qt.PointingHandCursor)
        btn_cargar.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                border: 1px solid #555555;
                border-radius: 4px;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #2E2E2E;
            }
        """)
        btn_cargar.clicked.connect(lambda checked, d=info_ejemplo["datos"]: self._al_cargar_ejemplo(d))

        layout_card.addWidget(lbl_titulo)
        layout_card.addWidget(lbl_desc)
        layout_card.addStretch()
        layout_card.addWidget(btn_cargar)

        return card

    def _al_cargar_ejemplo(self, datos):
        """Envía los datos a la ventana principal y cierra este diálogo."""
        if self.parent_window and hasattr(self.parent_window, "cargar_datos_en_interfaz"):
            self.parent_window.cargar_datos_en_interfaz(datos)
        self.accept()