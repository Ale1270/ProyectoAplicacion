from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt


class CustomSlider(QSlider):
    MIN_STEPS = 0
    MAX_STEPS = 1000

    # Rango físico real
    T_MIN_US = 100  # 100 µs
    T_MAX_US = 1000000  # 1 s (1,000,000 µs)

    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setRange(self.MIN_STEPS, self.MAX_STEPS)
        self.setValue(0)
        self.setFixedWidth(220)
        self.setStyleSheet(self._estilo("#888"))

        self.sliderPressed.connect(self._activar_color)
        self.sliderReleased.connect(self._restaurar_color)

    def obtener_valor_us(self):
        """Usa una curva cúbica para un avance súper suave."""
        paso_normalizado = self.value() / self.MAX_STEPS

        # Fórmula cúbica: Suaviza la transición y evita saltos bruscos
        valor_us = self.T_MIN_US + (self.T_MAX_US - self.T_MIN_US) * (paso_normalizado ** 3)
        return valor_us

    def obtener_valor_ms(self):
        return self.obtener_valor_us() / 1000.0

    def _estilo(self, color_handle):
        return f"""
            QSlider::groove:horizontal {{
                background: #444;
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

    def _activar_color(self): self.setStyleSheet(self._estilo("#00A8FF"))

    def _restaurar_color(self): self.setStyleSheet(self._estilo("#888"))