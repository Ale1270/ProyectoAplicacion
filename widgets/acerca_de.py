# Archivo: logica/acerca_de.py
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QDesktopServices, QIcon


class VentanaAcercaDe(QDialog):
    """
    Diálogo modal con pestañas para mostrar información institucional,
    créditos y detalles técnicos alineados con el diseño principal de la app
    y sin barra de título superior.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de - Convertidor Ćuk")
        self.setFixedSize(620, 530)

        # Ocultar la barra de título del sistema operativo (Ventana sin marco)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Variable para almacenar la posición de arrastre de la ventana
        self._drag_pos = None

        self._aplicar_estilos()
        self._inicializar_ui()

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
        # Mismos colores y bordes que ui_mainwindow con marco delimitador tenue
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
                padding: 8px 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #2E2E2E;
            }
            /* Botón de GitHub en modo oscuro */
            QPushButton#btn_github {
                background-color: #2B2E33;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 0px;
            }
            QPushButton#btn_github:hover {
                background-color: #3B3E43;
                border-color: #AAAAAA;
            }
        """)

    def _inicializar_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Contenedor de pestañas
        tabs = QTabWidget()
        tabs.addTab(self._crear_tab_general(), "General & Créditos")
        tabs.addTab(self._crear_tab_tecnica(), "Información Técnica")

        # Botón GitHub (Solo Icono)
        btn_github = QPushButton()
        btn_github.setObjectName("btn_github")
        btn_github.setCursor(Qt.PointingHandCursor)
        btn_github.setToolTip("Abrir repositorio en GitHub")
        btn_github.setFixedSize(140, 40)

        # Cargar icono 'github_logo' desde la carpeta 'recursos'
        ruta_recursos = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'recursos'))
        for ext in ['.png', '.svg', '.jpg', '']:
            path_prueba = os.path.join(ruta_recursos, f'github_logo{ext}')
            if os.path.exists(path_prueba):
                btn_github.setIcon(QIcon(path_prueba))
                btn_github.setIconSize(QSize(300, 30))
                break

        btn_github.clicked.connect(self._abrir_repositorio_github)

        # Botón de cierre
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.clicked.connect(self.accept)

        # Fila inferior de botones
        layout_btn = QHBoxLayout()
        layout_btn.addWidget(btn_github)
        layout_btn.addStretch()
        layout_btn.addWidget(btn_cerrar)

        layout_principal.addWidget(tabs)
        layout_principal.addSpacing(14)
        layout_principal.addLayout(layout_btn)

    def _crear_tab_general(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(25)

        # Encabezado principal
        lbl_titulo = QLabel("Ćuk Converter Designer & Simulator")
        lbl_titulo.setStyleSheet("font-size: 17px; font-weight: bold; color: #FFFFFF;")

        lbl_version = QLabel("Versión 1.2.0 | 2026")
        lbl_version.setStyleSheet("color: #888888; font-style: italic; font-size: 12px;")

        desc = (
            "Herramienta interactiva para el diseño, dimensionamiento "
            "de componentes pasivos y simulación en régimen dinámico del "
            "convertidor DC-DC tipo Ćuk."
        )
        lbl_desc = QLabel(desc)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("line-height: 1.4;")

        # Línea divisoria
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: #555555; border: none; max-height: 1px;")

        # Tabla de créditos con la paleta uniforme
        creditos_html = """
        <table style='width:100%; border-spacing: 0px 15px; font-size: 14px;'>
            <tr>
                <td style='width: 130px; font-weight: bold; color: #FFFFFF;'>Autor 1:</td>
                <td>Diego Alejandro Estepa Nieto</td>
            </tr>
            <tr>
                <td style='font-weight: bold; color: #FFFFFF;'>Autor 2:</td>
                <td>Luis David Patarroyo Gutierrez</td>
            </tr>
            <tr>
                <td style='font-weight: bold; color: #FFFFFF;'>Autor 3:</td>
                <td>Oscar Mauricio Hernandez Gomez</td>
            </tr>
            <tr>
                <td style='font-weight: bold; color: #FFFFFF;'>Institución:</td>
                <td>Universidad Pedagógica y Tecnológica de Colombia (UPTC)</td>
            </tr>
            <tr>
                <td style='font-weight: bold; color: #FFFFFF;'>Licencia:</td>
                <td>Uso Libre</td>
            </tr>
        </table>
        """
        lbl_creditos = QLabel(creditos_html)
        lbl_creditos.setWordWrap(True)

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_version)
        layout.addSpacing(4)
        layout.addWidget(lbl_desc)
        layout.addSpacing(4)
        layout.addWidget(linea)
        layout.addWidget(lbl_creditos)
        layout.addStretch()

        return tab

    def _crear_tab_tecnica(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(22, 22, 22, 22)

        tecnica_html = """
        <div style='line-height: 1.5;'>
            <p style='color: #FFFFFF; font-weight: bold; font-size: 14px; margin-bottom: 6px;'>
                Motor de Simulación Numérica
            </p>
            Integración mediante el algoritmo <b>Runge-Kutta de 4º Orden (RK4)</b> con conmutación discreta en tiempo real.<br><br>

            <p style='color: #FFFFFF; font-weight: bold; font-size: 14px; margin-bottom: 6px;'>
                Modelado de Estado
            </p>
            • <b>MOSFET ON:</b> L<sub>1</sub> almacena energía de V<sub>in</sub>; C<sub>1</sub> transfiriendo energía a C<sub>2</sub> y carga.<br>
            • <b>MOSFET OFF:</b> L<sub>1</sub> recarga a C<sub>1</sub>; L<sub>2</sub> mantiene corriente constante en la salida.<br><br>

            <p style='color: #FFFFFF; font-weight: bold; font-size: 14px; margin-bottom: 6px;'>
                Tecnologías e Infraestructura
            </p>
            • <b>Python:</b> Motor lógico y ecuaciones dinámicas.<br>
            • <b>PyQt5:</b> Interfaz gráfica reactiva y procesamiento multihilo (QThread).<br>
            • <b>NumPy & Matplotlib:</b> Cálculo vectorial y renderizado de formas de onda.
        </div>
        """
        lbl_tecnica = QLabel(tecnica_html)
        lbl_tecnica.setWordWrap(True)

        layout.addWidget(lbl_tecnica)
        layout.addStretch()

        return tab

    def _abrir_repositorio_github(self):
        """Abre la URL del repositorio en el navegador predeterminado del sistema."""
        url_provisional = "https://github.com/Ale1270/ProyectoAplicacion"
        QDesktopServices.openUrl(QUrl(url_provisional))


def mostrar_acerca_de(parent):
    """
    Punto de entrada original compatible con las llamadas previas de la app.
    """
    dialogo = VentanaAcercaDe(parent)
    dialogo.exec_()