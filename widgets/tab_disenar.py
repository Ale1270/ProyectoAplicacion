from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QVBoxLayout, QComboBox, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class TabDisenar(QWidget):
    """
    Pestaña para ingresar los parámetros eléctricos necesarios
    para el diseño del convertidor Ćuk.
    """

    def __init__(self):
        super().__init__()

        # ==============================
        # Parámetros visuales configurables
        # ==============================
        self.ESPACIADO_HORIZONTAL = 20
        self.ESPACIADO_VERTICAL = 8
        self.ANCHO_ENTRADA = 180
        self.ALTO_ENTRADA = 30
        self.ANCHO_COMBO = 70
        self.ALTO_COMBO = 30
        self.ANCHO_COMBO_FREC = 160
        self.ALTO_COMBO_FREC = 30
        self.FUENTE = "Segoe UI"
        self.TAMANO_FUENTE = 10

        # ==============================
        # Opciones del selector de frecuencia
        # ==============================
        self.OPCIONES_FRECUENCIA = [
            "Muy baja(25 kHz)",
            "Baja(50 kHz)",
            "Media(100 kHz)",
            "Alta(250 kHz)"
        ]

        # Diccionarios para acceder luego a entradas y unidades
        self.campos = {}
        self.combos = {}

        # Construir interfaz
        self._crear_interfaz()

    def _crear_interfaz(self):
        """
        Crea la estructura principal de la pestaña usando un grid layout.
        """
        layout_principal = QGridLayout()

        # Configuración de los campos eléctricos y sus unidades disponibles
        configuracion_campos = {
            "Vin": ["V", "mV"],
            "Vout": ["V", "mV"],
            "Pout": ["W", "mW"],
            "ΔI": ["A", "mA", "µA"],
            "ΔV": ["V", "mV", "µV"],
            "Frecuencia": None
        }

        # Generar posiciones automáticas en formato de 2 columnas
        posiciones = [(i // 2, i % 2) for i in range(len(configuracion_campos))]

        # Crear cada bloque de entrada
        for (fila, columna), nombre in zip(posiciones, configuracion_campos.keys()):

            # Si es frecuencia, crear selector especial
            if nombre == "Frecuencia":
                widget_campo = self._crear_selector_frecuencia()
            else:
                widget_campo = self._crear_campo(nombre, configuracion_campos[nombre])

            layout_principal.addWidget(widget_campo, fila, columna, Qt.AlignCenter)

        # Aplicar espaciados configurables
        layout_principal.setHorizontalSpacing(self.ESPACIADO_HORIZONTAL)
        layout_principal.setVerticalSpacing(self.ESPACIADO_VERTICAL)

        self.setLayout(layout_principal)

    def _crear_campo(self, nombre, unidades):
        """
        Crea un bloque individual compuesto por:
        - Etiqueta del parámetro
        - Caja de texto para ingreso numérico
        - Selector de unidades
        """
        contenedor_vertical = QVBoxLayout()

        etiqueta = QLabel(nombre)
        etiqueta.setAlignment(Qt.AlignCenter)
        etiqueta.setFont(QFont(self.FUENTE, self.TAMANO_FUENTE, QFont.Bold))

        contenedor_horizontal = QHBoxLayout()

        entrada = QLineEdit()
        entrada.setPlaceholderText(f"Ingrese {nombre}")
        entrada.setObjectName(f"entrada_{nombre.lower()}")
        entrada.setFixedSize(self.ANCHO_ENTRADA, self.ALTO_ENTRADA)
        entrada.setStyleSheet(self._estilo_entrada())

        combo = QComboBox()
        combo.setObjectName(f"combo_{nombre.lower()}")
        combo.setFixedSize(self.ANCHO_COMBO, self.ALTO_COMBO)
        combo.addItems(unidades)
        combo.setStyleSheet(self._estilo_combo())

        contenedor_horizontal.addWidget(entrada)
        contenedor_horizontal.addWidget(combo)

        contenedor_vertical.addWidget(etiqueta)
        contenedor_vertical.addLayout(contenedor_horizontal)

        subwidget = QWidget()
        subwidget.setLayout(contenedor_vertical)

        self.campos[nombre] = entrada
        self.combos[nombre] = combo

        return subwidget

    def _crear_selector_frecuencia(self):
        """
        Crea el selector desplegable de frecuencia de conmutación.
        """
        contenedor_vertical = QVBoxLayout()

        etiqueta = QLabel("Frecuencia")
        etiqueta.setAlignment(Qt.AlignCenter)
        etiqueta.setFont(QFont(self.FUENTE, self.TAMANO_FUENTE, QFont.Bold))

        combo = QComboBox()
        combo.setFixedSize(self.ANCHO_COMBO_FREC, self.ALTO_COMBO_FREC)
        combo.addItems(self.OPCIONES_FRECUENCIA)
        combo.setStyleSheet(self._estilo_combo())

        contenedor_vertical.addWidget(etiqueta)
        contenedor_vertical.addWidget(combo, alignment=Qt.AlignCenter)

        subwidget = QWidget()
        subwidget.setLayout(contenedor_vertical)

        self.combos["Frecuencia"] = combo

        return subwidget

    def _estilo_entrada(self):
        """
        Devuelve el estilo visual de las cajas de entrada.
        """
        return """
            background-color: #333;
            border: 1px solid #555;
            padding: 6px;
            border-radius: 5px;
            font-size: 12px;
            color: white;
        """

    def _estilo_combo(self):
        """
        Devuelve el estilo visual de los selectores desplegables.
        """
        return """
            QComboBox {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding-left: 8px;
                font-size: 12px;
            }
        """