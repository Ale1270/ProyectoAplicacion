import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QRadioButton, QButtonGroup, QFrame
from PyQt5.QtCore import Qt
import numpy as np


class VentanaGraficas(QDialog):
    def __init__(self, t, resultados, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resultados de la Simulación - Convertidor Cuk")
        self.resize(800, 600)

        # --- Eliminar el símbolo de interrogación ('?') de la barra de título ---
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Guardar los datos
        self.t = t
        self.resultados = resultados

        # --- Reorganizar la lista para que 'Vo' sea la primera señal ---
        claves = list(resultados.keys())
        if 'Vo' in claves:
            claves.remove('Vo')
            self.nombres_senales = ['Vo'] + claves
        else:
            self.nombres_senales = claves

        # Layout principal
        layout = QVBoxLayout()

        # ==========================================
        # NUEVO: Título Grande
        # ==========================================
        titulo_principal = QLabel("Visualización de Gráficas")
        titulo_principal.setStyleSheet("font-size: 22px; font-weight: bold; margin-top: 10px;")
        titulo_principal.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo_principal)

        # ==========================================
        # NUEVO: Contenedor con fondo gris para las opciones
        # ==========================================
        contenedor_opciones = QFrame()
        # Usamos rgba para dar un gris sutil que combine con tu tema oscuro, y bordes redondeados
        contenedor_opciones.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1); 
                border-radius: 8px;
                margin-bottom: 10px;
            }
            QLabel, QRadioButton {
                background-color: transparent; 
            }
        """)

        # El layout ahora vive dentro del QFrame
        layout_selector = QHBoxLayout(contenedor_opciones)
        layout_selector.setContentsMargins(15, 15, 15, 15)  # Espacio interno del cuadro

        label_selector = QLabel("Elija la gráfica que desea visualizar:")
        label_selector.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout_selector.addWidget(label_selector)

        # Grupo de botones para asegurar que solo uno se active a la vez
        self.grupo_botones = QButtonGroup(self)

        for i, nombre in enumerate(self.nombres_senales):
            radio_btn = QRadioButton(nombre)
            radio_btn.setStyleSheet("font-size: 14px; padding: 5px;")

            # Añadir al grupo dándole un ID único (su índice)
            self.grupo_botones.addButton(radio_btn, i)
            layout_selector.addWidget(radio_btn)

            # Seleccionar el primero por defecto ('Vo')
            if i == 0:
                radio_btn.setChecked(True)

        # Conectar el cambio de botón con la función que redibuja
        self.grupo_botones.idClicked.connect(self.actualizar_grafica)

        layout_selector.addStretch()  # Empuja los botones hacia la izquierda

        # Añadimos el cuadro gris al layout principal
        layout.addWidget(contenedor_opciones)

        # --- Configuración de Matplotlib ---
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
        Limpia el lienzo y dibuja solo la señal seleccionada en los RadioButtons.
        """
        nombre_senal = self.nombres_senales[index]
        datos = self.resultados[nombre_senal]

        # Limpiar la gráfica anterior
        self.ax.clear()

        # Colores dinámicos basados en el índice
        # (El primero 'Vo' será rojo, los demás varían)
        colores = ['#d62728', '#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']
        color = colores[index % len(colores)]

        # Convertir el tiempo a milisegundos multiplicando el arreglo por 1000
        t_ms = self.t * 1000

        # Dibujar la nueva señal usando el tiempo en ms
        self.ax.plot(t_ms, datos, color=color, linewidth=1.5)
        self.ax.set_title(f"Señal: {nombre_senal}", fontsize=12, fontweight='bold')
        self.ax.grid(True, linestyle=':', alpha=0.7)
        # Cambiar la etiqueta del eje X a milisegundos
        self.ax.set_xlabel("Tiempo (ms)", fontsize=10)
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