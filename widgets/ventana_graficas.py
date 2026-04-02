import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QHBoxLayout
import numpy as np


class VentanaGraficas(QDialog):
    def __init__(self, t, resultados, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resultados de la Simulación - Convertidor Cuk")
        self.resize(800, 600)

        # Guardar los datos para usarlos al cambiar de señal
        self.t = t
        self.resultados = resultados
        self.nombres_senales = list(resultados.keys())

        # Layout principal
        layout = QVBoxLayout()

        # --- Selector de Gráficas (Combobox) ---
        layout_selector = QHBoxLayout()

        label_selector = QLabel("Seleccione la señal a visualizar:")
        label_selector.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.combo_senales = QComboBox()
        self.combo_senales.addItems(self.nombres_senales)
        self.combo_senales.setStyleSheet("font-size: 14px; padding: 5px;")

        # Conectar el cambio de selección con la función que redibuja
        self.combo_senales.currentIndexChanged.connect(self.actualizar_grafica)

        layout_selector.addWidget(label_selector)
        layout_selector.addWidget(self.combo_senales)
        layout_selector.addStretch()  # Empuja el selector hacia la izquierda

        layout.addLayout(layout_selector)

        # --- Configuración de Matplotlib (Una sola gráfica) ---
        self.figure, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Dibujar la primera gráfica por defecto al abrir la ventana
        self.actualizar_grafica(0)

    def actualizar_grafica(self, index):
        """
        Limpia el lienzo y dibuja solo la señal seleccionada en el ComboBox.
        """
        nombre_senal = self.nombres_senales[index]
        datos = self.resultados[nombre_senal]

        # Limpiar la gráfica anterior
        self.ax.clear()

        # Colores dinámicos basados en el índice (para que cambien al seleccionar)
        colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        color = colores[index % len(colores)]

        # Dibujar la nueva señal
        self.ax.plot(self.t, datos, color=color, linewidth=1.5)
        self.ax.set_title(f"Señal: {nombre_senal}", fontsize=12, fontweight='bold')
        self.ax.grid(True, linestyle=':', alpha=0.7)
        self.ax.set_xlabel("Tiempo (s)", fontsize=10)
        self.ax.set_ylabel("Amplitud", fontsize=10)

        # Ajuste de escala dinámico
        if len(datos) > 0:
            y_min, y_max = np.min(datos), np.max(datos)
            rango = y_max - y_min
            # Dar un margen del 10% arriba y abajo, o 0.5 si el rango es 0
            margin = rango * 0.1 if rango > 0 else 0.5
            self.ax.set_ylim(y_min - margin, y_max + margin)

        # Refrescar el lienzo
        self.figure.tight_layout()
        self.canvas.draw()