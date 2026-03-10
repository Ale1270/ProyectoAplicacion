from PyQt5.QtWidgets import QSlider, QLabel
from PyQt5.QtCore import Qt


class CustomSlider(QSlider):
    """
    Slider personalizado para controlar el tiempo de simulación.

    Características:
    • Orientación horizontal
    • Cambio de color al interactuar
    • Etiqueta automática con unidades dinámicas
    • Diseño reutilizable
    """

    # ==============================
    # CONFIGURACIÓN GENERAL
    # ==============================
    MINIMO = 100
    MAXIMO = 3000
    VALOR_INICIAL = 100
    ANCHO = 220

    COLOR_NORMAL = "#888"
    COLOR_ACTIVO = "#00A8FF"
    COLOR_FONDO = "#444"

    # ==============================
    # INICIALIZACIÓN
    # ==============================
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)

        # Configuración básica
        self.setRange(self.MINIMO, self.MAXIMO)
        self.setValue(self.VALOR_INICIAL)
        self.setFixedWidth(self.ANCHO)

        # Aplicar estilo inicial
        self.setStyleSheet(self._estilo(self.COLOR_NORMAL))

        # Eventos de interacción
        self.sliderPressed.connect(self._activar_color)
        self.sliderReleased.connect(self._restaurar_color)

        # Etiqueta para mostrar valor actual
        self.valor_label = QLabel(parent)
        self.valor_label.setAlignment(Qt.AlignCenter)

        # Conectar actualización automática
        self.valueChanged.connect(self._actualizar_tiempo)
        self._actualizar_tiempo(self.value())

    # ==============================
    # ESTILOS DINÁMICOS
    # ==============================
    def _estilo(self, color_handle):
        """
        Genera el estilo visual del slider.
        Permite cambiar dinámicamente el color del botón.
        """
        return f"""
            QSlider::groove:horizontal {{
                background: {self.COLOR_FONDO};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {color_handle};
                width: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }}
        """

    def _activar_color(self):
        """Cambia el color al presionar el slider."""
        self.setStyleSheet(self._estilo(self.COLOR_ACTIVO))

    def _restaurar_color(self):
        """Restaura el color al soltar el slider."""
        self.setStyleSheet(self._estilo(self.COLOR_NORMAL))

    # ==============================
    # CONVERSIÓN DE UNIDADES
    # ==============================
    def _actualizar_tiempo(self, valor):
        """
        Convierte automáticamente el valor del slider
        a unidades legibles (µs o ms).
        """
        if valor < 1000:
            self.valor_label.setText(f"{valor} µs")
        else:
            self.valor_label.setText(f"{valor/1000:.2f} ms")

    # ==============================
    # MÉTODOS ÚTILES FUTUROS
    # ==============================
    def obtener_valor_us(self):
        """Devuelve el valor en microsegundos."""
        return self.value()

    def obtener_valor_ms(self):
        """Devuelve el valor en milisegundos."""
        return self.value() / 1000