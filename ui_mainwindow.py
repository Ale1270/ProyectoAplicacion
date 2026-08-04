import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGridLayout, QLineEdit, QComboBox,
    QApplication
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QGuiApplication
from PyQt5.QtCore import Qt, QTimer

from widgets.tab_disenar import TabDisenar
from widgets.tab_simular import TabSimular
from widgets.custom_slider import CustomSlider
from logica.funciones_botones import ejecutar_accion

from widgets.ayuda import mostrar_ayuda
from widgets.acerca_de import mostrar_acerca_de
from widgets.ventana_ejemplos import VentanaEjemplos
from widgets.guia_interactiva import CuadroExplicativo


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

    # 2. Buscar un nivel arriba
    ruta_nivel_superior = os.path.join(os.path.dirname(directorio_actual), relative_path)
    if os.path.exists(ruta_nivel_superior):
        return ruta_nivel_superior

    # 3. Caída por defecto
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
        self.guia = None
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

        # Estilo exclusivo para los ToolTips a nivel global de la aplicación
        app = QApplication.instance()
        if app:
            app.setStyleSheet("""
                QToolTip {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 5px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                }
            """)

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
        self._asignar_tooltips_pestanas()

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

            # -------------------------------------------------------------
            # ESPACIO RESERVADO PARA LA VENTANA DE CARGA
            # -------------------------------------------------------------
            self.espacio_carga = QWidget()
            self.espacio_carga.setFixedHeight(25)  # Reserva de espacio fija

            self.tabs = self._crear_tabs()

            # Añadimos al layout en el orden deseado:
            layout.addWidget(titulo)
            layout.addWidget(self.imagen)
            layout.addWidget(self.espacio_carga)  # <--- Espacio exclusivo reservado
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

        self.tab_disenar = TabDisenar()
        self.tab_simular = TabSimular()

        tabs.addTab(self.tab_disenar, "Diseñar")
        tabs.addTab(self.tab_simular, "Simular")

        tabs.setTabToolTip(0, "Diseño y cálculo de componentes del convertidor.")
        tabs.setTabToolTip(1, "Simulación y análisis dinámico del convertidor.")

        return tabs

    def _asignar_tooltips_pestanas(self):
        """Asigna descripciones breves al pasar el cursor por los componentes de las pestañas."""
        if hasattr(self.tab_disenar, "campos"):
            tooltips_campos = {
                "Vin": "Voltaje de entrada del convertidor.",
                "Vout": "Voltaje de salida deseado.",
                "Pout": "Potencia de salida.",
                "ΔI": "Rizado de corriente.",
                "ΔV": "Rizado de voltaje.",
                "Frecuencia": "Frecuencia de conmutación."
            }
            for clave, widget in self.tab_disenar.campos.items():
                if clave in tooltips_campos:
                    widget.setToolTip(tooltips_campos[clave])

        if hasattr(self.tab_disenar, "combos"):
            tooltips_combos = {
                "Vin": "Unidad del voltaje de entrada.",
                "Vout": "Unidad del voltaje de salida.",
                "Pout": "Unidad de la potencia de salida.",
                "ΔI": "Unidad del rizado de corriente.",
                "ΔV": "Unidad del rizado de voltaje.",
                "Frecuencia": "Frecuencia de conmutación."
            }
            for clave, widget in self.tab_disenar.combos.items():
                if clave in tooltips_combos:
                    widget.setToolTip(tooltips_combos[clave])

        for tab in (self.tab_disenar, self.tab_simular):
            for edit in tab.findChildren(QLineEdit):
                if not edit.toolTip():
                    edit.setToolTip("Ingresar valor.")
            for combo in tab.findChildren(QComboBox):
                if not combo.toolTip():
                    combo.setToolTip("Seleccionar unidad.")
            for btn in tab.findChildren(QPushButton):
                if not btn.toolTip():
                    btn.setToolTip("Ejecutar acción.")

    # ==============================
    # PANEL DERECHO (CONTROLES)
    # ==============================
    def _crear_panel_derecho(self):
        layout = QVBoxLayout()

        panel_caracteristicas_widget = self._crear_panel_caracteristicas()
        slider_contenedor = self._crear_slider_simulacion()
        boton_ejecutar = self._crear_boton_ejecutar()
        boton_ejemplos = self._crear_boton_ejemplos()
        botones_extra = self._crear_botones_extra()

        layout.addStretch(1)
        layout.addWidget(panel_caracteristicas_widget)

        layout.addSpacing(80)

        layout.addLayout(slider_contenedor)
        layout.addSpacing(15)
        layout.addWidget(boton_ejecutar, alignment=Qt.AlignHCenter)

        layout.addSpacing(70)
        layout.addWidget(boton_ejemplos, alignment=Qt.AlignHCenter)

        layout.addStretch(3)
        layout.addLayout(botones_extra)

        return layout

    # ==============================
    # CARACTERÍSTICAS ESTADO ESTABLE
    # ==============================
    def _crear_panel_caracteristicas(self):
        self.panel_caracteristicas = QWidget()
        layout = QVBoxLayout(self.panel_caracteristicas)
        layout.setContentsMargins(0, 0, 0, 0)
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
        return self.panel_caracteristicas

    # ==============================
    # SLIDER DE TIEMPO
    # ==============================
    def _crear_slider_simulacion(self):
        layout = QVBoxLayout()

        label = QLabel("Tiempo de simulación")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont(self.FUENTE, 11, QFont.Bold))

        self.slider = CustomSlider()
        self.slider.setToolTip("Tiempo de simulación.")
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
        self.btn_ejecutar.setToolTip("Diseñar o simular según la pestaña activa.")
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
        self.btn_ejemplos.setToolTip("Cargar ejemplos predefinidos.")
        self.btn_ejemplos.setFixedSize(130, 35)
        self.btn_ejemplos.setCursor(Qt.PointingHandCursor)
        self.btn_ejemplos.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover { 
                background-color: #505050; 
                border: 1px solid #777;
            }
            QPushButton:pressed { 
                background-color: #2e2e2e; 
            }
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
        boton_ayuda.setToolTip("Guía de uso y ayuda.")

        boton_acerca = QPushButton("Acerca de")
        boton_acerca.setToolTip("Información de la aplicación.")

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

            if ancho > 20 and alto > 20:
                pixmap = self.pixmap_original.scaled(
                    ancho,
                    alto,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.imagen.setPixmap(pixmap)
            else:
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
        """Instancia y muestra la ventana de ejemplos de forma no modal."""
        from PyQt5.QtCore import Qt

        self.ventana_ej = VentanaEjemplos(self)
        self.ventana_ej.setWindowModality(Qt.NonModal)
        self.ventana_ej.show()
        self.ventana_ej.raise_()
        self.ventana_ej.activateWindow()

    def cargar_datos_en_interfaz(self, datos):
        """
        Recibe un diccionario con parámetros de ejemplo y los asigna
        a los campos del diccionario 'campos' y 'combos' de TabDisenar.
        """
        self.tabs.setCurrentIndex(0)
        tab_disenar = self.tabs.widget(0)

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

        if hasattr(tab_disenar, "combos") and "Frecuencia" in tab_disenar.combos:
            frec_index = datos.get("frec_index", 1)
            tab_disenar.combos["Frecuencia"].setCurrentIndex(frec_index)

    def iniciar_guia_interactiva(self, seccion="todos"):
        """
        Configura y lanza el tour guiado paso a paso por secciones.
        Incluye el paso interactivo para seleccionar un caso del catálogo de ejemplos.
        """
        # Localizar el widget exacto de Frecuencia dentro de tab_disenar
        tab_d = self.tab_disenar
        widget_frecuencia = tab_d  # Respaldo por defecto

        if hasattr(tab_d, "combos") and "Frecuencia" in tab_d.combos:
            widget_frecuencia = tab_d.combos["Frecuencia"]
        elif hasattr(tab_d, "campos") and "Frecuencia" in tab_d.campos:
            widget_frecuencia = tab_d.campos["Frecuencia"]

        widget_ayuda = getattr(
            self, "btn_ayuda", getattr(self, "btn_acerca", self.btn_ejecutar)
        )

        # Identificar la pestaña o área de gráficas dinámicamente
        widget_graficas = getattr(
            self, "tab_graficas", getattr(self, "area_graficas", getattr(self, "canvas", self.tabs))
        )

        todos_los_pasos = [
            # =========================================================
            # SUBDIVISIÓN 1: DESCRIPCIÓN GENERAL Y SECCIONES
            # =========================================================
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.imagen,
                "titulo": "Convertidor Ćuk DC-DC",
                "texto": "Esta aplicación permite realizar el diseño completo y la simulación dinámica de convertidores DC-DC de tipo Ćuk de forma interactiva.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.tabs,
                "titulo": "Pestañas de Trabajo",
                "texto": "Ubicadas justo debajo de la imagen, te permiten alternar entre 'Diseñar' (cálculo de inductores y capacitores) y 'Simular' (análisis gráfico temporal).",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.tab_disenar,
                "titulo": "Panel de Ingreso de Datos",
                "texto": "Aquí introducirás los parámetros requeridos para calcular el circuito o simular su comportamiento según la pestaña seleccionada.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.tab_disenar,
                "titulo": "Formato para Ingresar Datos",
                "texto": "Los campos aceptan valores enteros o decimales. Recuerda utilizar siempre el punto (.) como separador decimal (ejemplo: 12.5).",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.tab_disenar,
                "titulo": "Unidades Disponibles",
                "texto": "Cada variable cuenta con un desplegable a su derecha para seleccionar la escala adecuada (V, mV, A, mA, %, etc.).",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": widget_frecuencia,
                "titulo": "Selección de Frecuencia",
                "texto": "A mayor frecuencia de conmutación, los inductores y capacitores requeridos son más pequeños y el circuito se estabiliza más rápido. Una frecuencia baja exige componentes de mayor tamaño físico y un tiempo de asentamiento más prolongado.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.slider,
                "titulo": "Control de Tiempo de Simulación",
                "texto": "Esta barra deslizante permite ajustar la ventana temporal del análisis dinámico (desde 100 µs hasta 1.0 s) para observar transitorios cortos o el estado estable.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.btn_ejecutar,
                "titulo": "Botón de Acción",
                "texto": "Ejecuta los cálculos de dimensionamiento o la simulación temporal en función de la pestaña en la que te encuentres ubicado.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": self.btn_ejemplos,
                "titulo": "Casos de Prueba Predefinidos",
                "texto": "Permite seleccionar y cargar instantáneamente configuraciones típicas del convertidor Ćuk sin tener que digitar todos los valores manualmente.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": getattr(self, "panel_caracteristicas", self.lbl_val_pin),
                "titulo": "Resumen de Estado Estable",
                "texto": "Muestra los indicadores permanentes de desempeño del convertidor: potencia consumida, entregada, eficiencia global y tiempo de asentamiento.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "general",
                "categoria": "1. Descripción General",
                "widget": widget_ayuda,
                "titulo": "Ayuda e Información",
                "texto": "Acceso a la guía interactiva por secciones específicas y a los datos de versión y créditos de la aplicación.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },

            # =========================================================
            # SUBDIVISIÓN 2: CARGA DE EJEMPLOS PREDEFINIDOS
            # =========================================================
            {
                "seccion_key": "ejemplos",
                "categoria": "2. Cargar Ejemplos",
                "widget": self.btn_ejemplos,
                "offset": (0, -8),
                "titulo": "Apertura del Menú de Ejemplos",
                "texto": "Presiona el botón 'Cargar Ejemplos' en el panel lateral para desplegar la ventana con configuraciones preseteadas del convertidor.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "ejemplos",
                "categoria": "2. Cargar Ejemplos",
                "posicion_pantalla": "centro",
                "titulo": "Catálogo de Casos Disponibles",
                "texto": "En esta ventana desplegada encontrarás diversas aplicaciones típicas de prueba (diseños de bajo voltaje, alta potencia, etc.).",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "ejemplos",
                "categoria": "2. Cargar Ejemplos",
                "posicion_pantalla": (0, 0.5),
                "titulo": "¡Prueba Cargar un Ejemplo!",
                "texto": "Selecciona cualquiera de las opciones disponibles en la lista para ver cómo los datos del caso se rellenan y actualizan automáticamente en los campos de entrada de la aplicación.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },

            # =========================================================
            # SUBDIVISIÓN 3: EJEMPLO DE USO DE DISEÑO
            # =========================================================
            {
                "seccion_key": "diseno",
                "categoria": "3. Ejemplo de Diseño",
                "widget": self.tab_disenar,
                "titulo": "Ingreso de Especificaciones",
                "texto": "Con los datos cargados manualmente o mediante un ejemplo, en esta sección se definen Vin, Vout, Pout, los rizados permisibles y la frecuencia de trabajo.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },
            {
                "seccion_key": "diseno",
                "categoria": "3. Ejemplo de Diseño",
                "widget": self.btn_ejecutar,
                "offset": (0, -50),
                "titulo": "Diseñar Filtros",
                "texto": "Al presionar este botón se calcularán automáticamente los inductores L₁ y L₂ y los capacitores C₁ y C₂ requeridos para el diseño.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            },

            # =========================================================
            # SUBDIVISIÓN 4: EJEMPLO DE SIMULACIÓN
            # =========================================================
            {
                "seccion_key": "simulacion",
                "categoria": "4. Ejemplo de Simulación",
                "widget": self.tab_simular,
                "titulo": "Parámetros de Simulación",
                "texto": "En esta pestaña puedes modificar libremente los componentes físicos para validar la respuesta temporal del circuito.",
                "accion": lambda: self.tabs.setCurrentIndex(1)
            },
            {
                "seccion_key": "simulacion",
                "categoria": "4. Ejemplo de Simulación",
                "widget": self.slider,
                "offset": (0, -50),
                "titulo": "Ajuste de Tiempo",
                "texto": "Ajusta la duración del análisis dinámico con este slider (desde 100 µs hasta 1.0 s).",
                "accion": lambda: self.tabs.setCurrentIndex(1)
            },
            {
                "seccion_key": "simulacion",
                "categoria": "4. Ejemplo de Simulación",
                "widget": self.btn_ejecutar,
                "offset": (0, -50),
                "titulo": "Ejecutar Simulación",
                "texto": "Con la pestaña 'Simular' activa, al presionar este botón se generarán las gráficas temporales del convertidor.",
                "accion": lambda: self.tabs.setCurrentIndex(1)
            },

            # =========================================================
            # SUBDIVISIÓN 5: VISUALIZACIÓN DE GRÁFICAS
            # =========================================================
            {
                "seccion_key": "graficas",
                "categoria": "5. Visualización de Gráficas",
                "widget": self.btn_ejecutar,
                "offset": (0, -50),  # <--- Ubicado justo arriba del botón de acción
                "titulo": "Generación de Gráficas",
                "texto": "Al presionar este botón con la pestaña 'Simular' activa, el sistema resuelve el modelo dinámico y genera las respuestas temporales en pantalla.",
                "accion": lambda: self.tabs.setCurrentIndex(1)
            },
            {
                "seccion_key": "graficas",
                "categoria": "5. Visualización de Gráficas",
                "posicion_pantalla": (0.15, 0.78),  # <--- Esquina inferior izquierda de la ventana
                "titulo": "Análisis de Transitorios y Rizado",
                "texto": "Desde este sector podrás observar el comportamiento inicial de encendido (sobrepico y tiempo de asentamiento) y el nivel de rizado en estado estable.",
                "accion": lambda: self.tabs.setCurrentIndex(1)
            },
            {
                "seccion_key": "graficas",
                "categoria": "5. Visualización de Gráficas",
                "widget": widget_graficas,
                "titulo": "Tipos de Gráficas Disponibles",
                "texto": "La aplicación permite visualizar y alternar las curvas temporales del Voltaje de Salida (Vout), Corrientes en Inductores (iL₁ e iL₂) y Voltaje en el Capacitor vC₁.",
                "accion": lambda: self.tabs.setCurrentIndex(1)
            },

            # =========================================================
            # SUBDIVISIÓN 6: INTERPRETACIÓN DE ESTADO ESTABLE
            # =========================================================
            {
                "seccion_key": "estable",
                "categoria": "6. Características en Estable",
                "widget": getattr(self, "panel_caracteristicas", self.lbl_val_pin),
                "titulo": "Panel de Métricas Permanentes",
                "texto": "Ubicado en el lateral derecho, este panel resume el desempeño final del convertidor: potencia consumida (Pin), entregada (Pout), eficiencia (%) y tiempo de asentamiento.",
                "accion": lambda: self.tabs.setCurrentIndex(0)
            }
        ]

        if seccion != "todos":
            pasos_filtrados = [p for p in todos_los_pasos if p.get("seccion_key") == seccion]
        else:
            pasos_filtrados = todos_los_pasos

        if not pasos_filtrados:
            return

        # Cerrar tour anterior si estuviera activo
        if hasattr(self, "guia") and self.guia:
            self.guia.close()

        self.guia = CuadroExplicativo(pasos_filtrados, self)
        self.guia.iniciar_tour()