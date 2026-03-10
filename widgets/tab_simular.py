from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QVBoxLayout, QComboBox, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class TabSimular(QWidget):
    """
    Pestaña encargada de mostrar y permitir la edición de los
    parámetros eléctricos usados para simular el convertidor Ćuk.

    Aquí se reciben los valores calculados en la pestaña "Diseñar"
    y también se pueden ajustar manualmente para pruebas.
    """

    def __init__(self):
        super().__init__()

        # ==============================
        # Parámetros visuales configurables
        # ==============================

        # Número de columnas del grid principal
        self.COLUMNAS = 3

        # Espaciados entre widgets
        self.ESPACIADO_HORIZONTAL = 20
        self.ESPACIADO_VERTICAL = 8
        self.ESPACIADO_INTERNO = 20

        # Tamaños de cajas de texto
        self.ANCHO_ENTRADA = 120
        self.ALTO_ENTRADA = 25

        # Tamaños de combos normales
        self.ANCHO_COMBO = 60
        self.ALTO_COMBO = 25

        # Tamaño especial para combo de frecuencia
        self.ANCHO_COMBO_FREC = 120
        self.ALTO_COMBO_FREC = 25

        # Fuente general
        self.FUENTE = "Segoe UI"
        self.TAMANO_FUENTE = 10

        # ==============================
        # Opciones de frecuencia de conmutación
        # ==============================
        self.OPCIONES_FRECUENCIA = [
            "Muy baja(25 kHz)",
            "Baja(50 kHz)",
            "Media(100 kHz)",
            "Alta(250 kHz)"
        ]

        # ==============================
        # Diccionarios de acceso rápido
        # ==============================
        # Permiten acceder a cada campo desde otras partes del programa
        self.campos = {}   # QLineEdit
        self.combos = {}   # QComboBox

        # Construcción de la interfaz
        self._crear_interfaz()

    # ==========================================================
    # CREACIÓN DE INTERFAZ PRINCIPAL
    # ==========================================================
    def _crear_interfaz(self):
        """
        Crea el layout principal tipo grilla y distribuye
        todos los parámetros eléctricos de simulación.
        """

        layout_principal = QGridLayout()

        # Lista de parámetros a mostrar
        campos = [
            "Vin", "R", "C1", "C2",
            "L1", "L2", "Ciclo",
            "Vout", "Frecuencia"
        ]

        # Unidades disponibles por parámetro
        opciones_por_campo = {
            "Vin": ["V", "mV"],
            "Vout": ["V", "mV"],
            "R": ["Ω", "kΩ", "MΩ"],
            "C1": ["µF", "nF", "pF"],
            "C2": ["µF", "nF", "pF"],
            "L1": ["mH", "µH"],
            "L2": ["mH", "µH"],
            "Ciclo": ["%"],
        }

        # Genera posiciones automáticas en la grilla
        posiciones = [(i // self.COLUMNAS, i % self.COLUMNAS) for i in range(len(campos))]

        # Crear cada widget de parámetro
        for (fila, columna), nombre in zip(posiciones, campos):

            # Frecuencia usa un diseño especial
            if nombre == "Frecuencia":
                widget_campo = self._crear_selector_frecuencia()
            else:
                widget_campo = self._crear_campo(nombre, opciones_por_campo[nombre])

            layout_principal.addWidget(widget_campo, fila, columna, Qt.AlignCenter)

        # Espaciado visual
        layout_principal.setHorizontalSpacing(self.ESPACIADO_HORIZONTAL)
        layout_principal.setVerticalSpacing(self.ESPACIADO_VERTICAL)

        self.setLayout(layout_principal)

    # ==========================================================
    # CREAR CAMPOS NORMALES (Etiqueta + Entrada + Unidad)
    # ==========================================================
    def _crear_campo(self, nombre, unidades):
        """
        Crea un bloque compuesto por:
        • Etiqueta del parámetro
        • Caja de texto para valor
        • Selector de unidades
        """

        contenedor_vertical = QVBoxLayout()

        # Etiqueta superior
        etiqueta = QLabel(nombre)
        etiqueta.setAlignment(Qt.AlignCenter)
        etiqueta.setFont(QFont(self.FUENTE, self.TAMANO_FUENTE, QFont.Bold))

        # Layout horizontal para entrada + unidades
        contenedor_horizontal = QHBoxLayout()
        contenedor_horizontal.setSpacing(self.ESPACIADO_INTERNO)

        # Caja de texto
        entrada = QLineEdit()
        entrada.setPlaceholderText(f"Ingrese {nombre}")
        entrada.setFixedSize(self.ANCHO_ENTRADA, self.ALTO_ENTRADA)
        entrada.setStyleSheet(self._estilo_entrada())

        # Combo de unidades
        combo = QComboBox()
        combo.addItems(unidades)
        combo.setFixedSize(self.ANCHO_COMBO, self.ALTO_COMBO)
        combo.setStyleSheet(self._estilo_combo())

        # Añadir al layout horizontal
        contenedor_horizontal.addWidget(entrada)
        contenedor_horizontal.addWidget(combo)

        # Añadir al layout vertical
        contenedor_vertical.addWidget(etiqueta)
        contenedor_vertical.addLayout(contenedor_horizontal)

        # Widget contenedor final
        subwidget = QWidget()
        subwidget.setLayout(contenedor_vertical)

        # Guardar referencias para uso externo
        self.campos[nombre] = entrada
        self.combos[nombre] = combo

        return subwidget

    # ==========================================================
    # CREAR SELECTOR DE FRECUENCIA
    # ==========================================================
    def _crear_selector_frecuencia(self):
        """
        Crea el selector desplegable de frecuencia de conmutación.
        Esta frecuencia afecta el rizado y tamaño de componentes.
        """

        contenedor = QVBoxLayout()

        etiqueta = QLabel("Frecuencia")
        etiqueta.setAlignment(Qt.AlignCenter)
        etiqueta.setFont(QFont(self.FUENTE, self.TAMANO_FUENTE, QFont.Bold))

        combo = QComboBox()
        combo.addItems(self.OPCIONES_FRECUENCIA)
        combo.setFixedSize(self.ANCHO_COMBO_FREC, self.ALTO_COMBO_FREC)
        combo.setStyleSheet(self._estilo_combo())

        contenedor.addWidget(etiqueta)
        contenedor.addWidget(combo, alignment=Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(contenedor)

        # Guardar referencia para usarla en cálculos
        self.combos["Frecuencia"] = combo

        return widget

    # ==========================================================
    # ESTILOS VISUALES
    # ==========================================================
    def _estilo_entrada(self):
        """Estilo visual de las cajas de entrada."""
        return """
            background-color: #333;
            border: 1px solid #555;
            padding: 6px;
            border-radius: 5px;
            font-size: 12px;
            color: white;
        """

    def _estilo_combo(self):
        """Estilo visual de los menús desplegables."""
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