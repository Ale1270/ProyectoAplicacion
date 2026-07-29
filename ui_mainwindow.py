import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGridLayout
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QGuiApplication
from PyQt5.QtCore import Qt, QTimer

from widgets.tab_disenar import TabDisenar
from widgets.tab_simular import TabSimular
from widgets.custom_slider import CustomSlider
from logica.funciones_botones import ejecutar_accion

# --- NUEVAS IMPORTACIONES ---
from logica.ayuda import mostrar_ayuda
from logica.acerca_de import mostrar_acerca_de
from widgets.ventana_ejemplos import VentanaEjemplos


def resource_path(relative_path):
    """
    Obtiene la ruta absoluta de recursos compatible con .exe (PyInstaller)
    y ejecuciones desde cualquier directorio.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    # 1. Buscar relativo al archivo actual
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_relativa_archivo = os.path.join(directorio_actual, relative_path)

    if os.path.exists(ruta_relativa_archivo):
        return ruta_relativa_archivo

    # 2. Buscar un nivel arriba (por si ui_mainwindow está en una subcarpeta como 'gui/' o 'widgets/')
    ruta_nivel_superior = os.path.join(os.path.dirname(directorio_actual), relative_path)
    if os.path.exists(ruta_nivel_superior):
        return ruta_nivel_superior

    # 3. Caída por defecto a la ruta del directorio de trabajo actual
    return os.path.join(os.path.abspath("."), relative_path)


class VentanaPrincipal(QMainWindow):
    """
    Ventana principal de la aplicación del convertidor Ćuk.
    Contiene:
        • Imagen del convertidor
        • Pestañas de Diseño y Simulación
        • Panel de control lateral con características, slider y ejemplos
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

        self.tabs.currentChanged.connect(self._actualizar_texto_boton)
        self._actualizar_texto_boton(self.tabs.currentIndex())

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

        panel_caracteristicas = self._crear_panel_caracteristicas()
        slider_contenedor = self._crear_slider_simulacion()
        boton_ejecutar = self._crear_boton_ejecutar()
        boton_ejemplos = self._crear_boton_ejemplos()  # Botón creado
        botones_extra = self._crear_botones_extra()

        layout.addStretch(1)
        layout.addLayout(panel_caracteristicas)

        layout.addSpacing(80)

        layout.addLayout(slider_contenedor)
        layout.addSpacing(15)
        layout.addWidget(boton_ejecutar, alignment=Qt.AlignHCenter)

        # Ubicado debajo del botón principal y arriba de ayuda / acerca de
        layout.addSpacing(70)
        layout.addWidget(boton_ejemplos, alignment=Qt.AlignHCenter)

        layout.addStretch(3)
        layout.addLayout(botones_extra)

        return layout

    # ==============================
    # CARACTERÍSTICAS ESTADO ESTABLE
    # ==============================
    def _crear_panel_caracteristicas(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        titulo = QLabel("Características en estado\nestable del convertidor")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont(self.FUENTE, 10, QFont.Bold))
        titulo.setStyleSheet("color: #cccccc;")

        layout.addWidget(titulo)
        layout.addSpacing(5)

        grid = QGridLayout()
        grid.setSpacing(5)

        self.lbl_val_pin = QLabel("--")
        self.lbl_val_pout = QLabel("--")
        self.lbl_val_eficiencia = QLabel("--")
        self.lbl_val_t_estable = QLabel("--")

        filas = [
            ("Pin:", self.lbl_val_pin),
            ("Pout:", self.lbl_val_pout),
            ("Eficiencia:", self.lbl_val_eficiencia),
            ("Tiempo en estable:", self.lbl_val_t_estable)
        ]

        for i, (texto, lbl_valor) in enumerate(filas):
            lbl_texto = QLabel(texto)
            lbl_texto.setFont(QFont(self.FUENTE, 9))
            lbl_texto.setStyleSheet("color: #aaaaaa;")

            lbl_valor.setFont(QFont(self.FUENTE, 9, QFont.Bold))
            lbl_valor.setStyleSheet("color: #ffffff;")
            lbl_valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            grid.addWidget(lbl_texto, i, 0)
            grid.addWidget(lbl_valor, i, 1)

        layout.addLayout(grid)
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
        etiquetas.setContentsMargins(5, 0, 5, 0)

        min_lbl = QLabel("100 µs")
        max_lbl = QLabel("1.0 s")

        for lbl in (min_lbl, max_lbl):
            lbl.setFont(QFont(self.FUENTE, 9))
            lbl.setStyleSheet("color: #aaa;")

        etiquetas.addWidget(min_lbl)
        etiquetas.addStretch()
        etiquetas.addWidget(max_lbl)

        layout.addWidget(label)
        layout.addWidget(self.slider)
        layout.addLayout(etiquetas)
        layout.addWidget(self.valor_label)

        self._actualizar_tiempo(self.slider.value())
        return layout

    # ==============================
    # BOTÓN DE ACCIÓN
    # ==============================
    def _crear_boton_ejecutar(self):
        self.btn_ejecutar = QPushButton("Calcular filtros")
        self.btn_ejecutar.setFixedSize(160, 45)
        self.btn_ejecutar.setCursor(Qt.PointingHandCursor)
        self.btn_ejecutar.setStyleSheet("""
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
        self.btn_ejecutar.clicked.connect(lambda: ejecutar_accion(self, self.tabs))
        return self.btn_ejecutar

    # ==============================
    # BOTÓN CARGAR EJEMPLOS
    # ==============================
    def _crear_boton_ejemplos(self):
        self.btn_ejemplos = QPushButton("Cargar Ejemplos")
        self.btn_ejemplos.setFixedSize(120, 35)
        self.btn_ejemplos.setCursor(Qt.PointingHandCursor)
        self.btn_ejemplos.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                border: 1px solid #555;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover { background-color: #005A9E; }
            QPushButton:pressed { background-color: #004578; }
        """)
        self.btn_ejemplos.clicked.connect(self.abrir_ventana_ejemplos)
        return self.btn_ejemplos

    # ==============================
    # BOTONES EXTRA (AYUDA / ACERCA DE)
    # ==============================
    def _crear_botones_extra(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        boton_ayuda = QPushButton("Ayuda")
        boton_acerca = QPushButton("Acerca de")

        estilo = """
            QPushButton {
                background-color: transparent;
                border: 1px solid #555;
                border-radius: 4px;
                color: #aaaaaa;
                font-size: 11px;
                padding: 5px 10px;
            }
            QPushButton:hover { background-color: #333333; color: white; border: 1px solid #777;}
            QPushButton:pressed { background-color: #1a1a1a; }
        """

        for boton in (boton_ayuda, boton_acerca):
            boton.setStyleSheet(estilo)
            boton.setCursor(Qt.PointingHandCursor)

        boton_ayuda.clicked.connect(lambda: mostrar_ayuda(self))
        boton_acerca.clicked.connect(lambda: mostrar_acerca_de(self))

        layout.addWidget(boton_ayuda)
        layout.addWidget(boton_acerca)

        return layout

    # ==============================
    # FUNCIONES AUXILIARES
    # ==============================
    def _actualizar_tiempo(self, valor):
        t_us = self.slider.obtener_valor_us()
        if t_us < 1000:
            self.valor_label.setText(f"{int(t_us)} µs")
        elif t_us < 1000000:
            self.valor_label.setText(f"{t_us / 1000:.2f} ms")
        else:
            self.valor_label.setText(f"{t_us / 1000000:.2f} s")

    def _actualizar_texto_boton(self, index):
        """Cambia el texto del botón dependiendo de la pestaña activa."""
        if index == 0:
            self.btn_ejecutar.setText("Diseñar filtros")
        elif index == 1:
            self.btn_ejecutar.setText("Simular diseño")

    def _ajustar_imagen(self):
        """Ajusta la imagen al tamaño actual de la etiqueta sin deformarla."""
        if hasattr(self, 'pixmap_original') and self.pixmap_original and not self.pixmap_original.isNull():
            ancho = self.imagen.width()
            alto = self.imagen.height()

            # Evita escalar la imagen a 0x0 píxeles durante el inicio de la ventana
            if ancho > 20 and alto > 20:
                pixmap = self.pixmap_original.scaled(
                    ancho,
                    alto,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.imagen.setPixmap(pixmap)
            else:
                # Asigna la imagen en tamaño original si el layout aún no ha medido el widget
                self.imagen.setPixmap(self.pixmap_original)
        else:
            print("[ADVERTENCIA] No se pudo cargar la imagen del convertidor Ćuk.")

    def resizeEvent(self, event):
        self._ajustar_imagen()
        super().resizeEvent(event)

    def _centrar_en_pantalla(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def abrir_ventana_ejemplos(self):
        """Instancia y muestra la ventana de ejemplos como un diálogo."""
        self.ventana_ej = VentanaEjemplos(self)
        self.ventana_ej.exec_()

    def cargar_datos_en_interfaz(self, datos):
        """
        Recibe un diccionario con parámetros de ejemplo y los asigna
        a los campos del diccionario 'campos' y 'combos' de TabDisenar.
        """
        # Ir a la pestaña de Diseñar (índice 0)
        self.tabs.setCurrentIndex(0)
        tab_disenar = self.tabs.widget(0)

        # 1. Asignar valores a los QLineEdit dentro del diccionario campos
        if hasattr(tab_disenar, "campos"):
            if "Vin" in tab_disenar.campos:
                tab_disenar.campos["Vin"].setText(datos.get("vin", ""))
            if "Vout" in tab_disenar.campos:
                tab_disenar.campos["Vout"].setText(datos.get("vout", ""))
            if "Pout" in tab_disenar.campos:
                tab_disenar.campos["Pout"].setText(datos.get("pout", ""))
            if "ΔI" in tab_disenar.campos:
                tab_disenar.campos["ΔI"].setText(datos.get("delta_i", ""))
            if "ΔV" in tab_disenar.campos:
                tab_disenar.campos["ΔV"].setText(datos.get("delta_v", ""))

        # 2. Seleccionar opción en el QComboBox de Frecuencia
        if hasattr(tab_disenar, "combos") and "Frecuencia" in tab_disenar.combos:
            frec_index = datos.get("frec_index", 1)  # Índice de la opción
            tab_disenar.combos["Frecuencia"].setCurrentIndex(frec_index)