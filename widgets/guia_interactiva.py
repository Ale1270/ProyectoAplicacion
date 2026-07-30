from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QEvent
from PyQt5.QtGui import QFont, QGuiApplication


class CuadroExplicativo(QFrame):
    """
    Tarjeta flotante de la guía interactiva.
    Permite posicionamiento automático, relativo por porcentajes y
    desplazamientos finos mediante píxeles ('offset').
    """

    def __init__(self, pasos, parent=None):
        super().__init__(parent)
        # Se mantiene WindowStaysOnTopHint para estar siempre por encima de modales/ejemplos
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pasos = pasos
        self.paso_actual = 0
        self._tour_activo = False

        # Eventos de la ventana principal
        if parent:
            parent.installEventFilter(self)

        # Eventos globales de la aplicación (para ocultar al cambiar de app en la PC)
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

        self._crear_ui()

    def eventFilter(self, watched, event):
        """Maneja la visibilidad según el foco de la app global y la ventana principal."""
        app = QApplication.instance()

        # 1. SI SE CAMBIA DE APLICACIÓN EN EL SISTEMA OPERATIVO (Alt+Tab, clic en Chrome, etc.)
        if watched == app:
            if event.type() == QEvent.ApplicationDeactivate:
                self.hide()
            elif event.type() == QEvent.ApplicationActivate:
                if self._tour_activo and self.parent() and self.parent().isVisible() and not self.parent().isMinimized():
                    self.show()
                    self.raise_()

        # 2. SI LA VENTANA PRINCIPAL SE MINIMIZA O CIERRA
        elif watched == self.parent():
            if event.type() in (QEvent.Hide, QEvent.WindowStateChange):
                if self.parent().isMinimized() or not self.parent().isVisible():
                    self.hide()
                elif self._tour_activo:
                    self.show()
                    self.raise_()
            elif event.type() == QEvent.Close:
                self.close()

        return super().eventFilter(watched, event)

    def _crear_ui(self):
        self.setFixedSize(340, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #007acc;
                border-radius: 8px;
            }
            QLabel {
                border: none;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #666666;
                border-radius: 4px;
                color: white;
                font-size: 11px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        self.lbl_categoria = QLabel("SECCIÓN")
        self.lbl_categoria.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.lbl_categoria.setStyleSheet("color: #007acc; letter-spacing: 1px;")

        layout_header = QHBoxLayout()
        self.lbl_paso = QLabel("Paso 1/1")
        self.lbl_paso.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.lbl_paso.setStyleSheet("color: #aaaaaa;")

        self.btn_cerrar = QPushButton("X")
        self.btn_cerrar.setFixedSize(20, 20)
        self.btn_cerrar.setStyleSheet("border: none; color: #888888; font-weight: bold;")
        self.btn_cerrar.clicked.connect(self.close)

        layout_header.addWidget(self.lbl_paso)
        layout_header.addStretch()
        layout_header.addWidget(self.btn_cerrar)

        self.lbl_titulo = QLabel()
        self.lbl_titulo.setFont(QFont("Segoe UI", 10, QFont.Bold))

        self.lbl_texto = QLabel()
        self.lbl_texto.setWordWrap(True)
        self.lbl_texto.setFont(QFont("Segoe UI", 9))
        self.lbl_texto.setStyleSheet("color: #dddddd;")

        layout_botones = QHBoxLayout()
        self.btn_anterior = QPushButton("Anterior")
        self.btn_siguiente = QPushButton("Siguiente")

        self.btn_anterior.clicked.connect(self._anterior_paso)
        self.btn_siguiente.clicked.connect(self._siguiente_paso)

        layout_botones.addWidget(self.btn_anterior)
        layout_botones.addStretch()
        layout_botones.addWidget(self.btn_siguiente)

        layout.addWidget(self.lbl_categoria)
        layout.addLayout(layout_header)
        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_texto)
        layout.addStretch()
        layout.addLayout(layout_botones)

    def iniciar_tour(self):
        self.paso_actual = 0
        self._tour_activo = True
        self._mostrar_paso()
        self.show()
        self.raise_()

    def closeEvent(self, event):
        self._tour_activo = False
        super().closeEvent(event)

    def _mostrar_paso(self):
        info = self.pasos[self.paso_actual]

        if "accion" in info and callable(info["accion"]):
            info["accion"]()

        total = len(self.pasos)
        self.lbl_categoria.setText(info.get("categoria", "GUÍA INTERACTIVA").upper())
        self.lbl_paso.setText(f"Paso {self.paso_actual + 1} de {total}")
        self.lbl_titulo.setText(info["titulo"])
        self.lbl_texto.setText(info["texto"])

        self.btn_anterior.setEnabled(self.paso_actual > 0)
        if self.paso_actual == total - 1:
            self.btn_siguiente.setText("Finalizar")
        else:
            self.btn_siguiente.setText("Siguiente")

        parent_win = self.parent()
        screen = QGuiApplication.primaryScreen()
        screen_geom = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        if parent_win:
            pos_parent = parent_win.mapToGlobal(QPoint(0, 0))
            p_left, p_top = pos_parent.x(), pos_parent.y()
            p_width, p_height = parent_win.width(), parent_win.height()
        else:
            p_left, p_top = screen_geom.left(), screen_geom.top()
            p_width, p_height = screen_geom.width(), screen_geom.height()

        pos_custom = info.get("posicion_pantalla")

        # OPCIÓN 1: Centro de la ventana principal
        if pos_custom == "centro":
            x_pos = p_left + (p_width - self.width()) / 2
            y_pos = p_top + (p_height - self.height()) / 2

        # OPCIÓN 2: Proporción relativa a la ventana principal
        elif isinstance(pos_custom, tuple) and len(pos_custom) == 2:
            rx, ry = pos_custom
            x_pos = p_left + (p_width * rx) - (self.width() / 2)
            y_pos = p_top + (p_height * ry) - (self.height() / 2)

        # OPCIÓN 3: Algoritmo inteligente adyacente al widget
        else:
            target_widget = info.get("widget")
            if target_widget and target_widget.isVisible():
                pos_target = target_widget.mapToGlobal(QPoint(0, 0))
                w_target = target_widget.width()
                h_target = target_widget.height()

                p_right = p_left + p_width
                p_bottom = p_top + p_height

                if pos_target.x() + w_target + self.width() + 12 <= p_right:
                    x_pos = pos_target.x() + w_target + 12
                    y_pos = pos_target.y()
                elif pos_target.x() - self.width() - 12 >= p_left:
                    x_pos = pos_target.x() - self.width() - 12
                    y_pos = pos_target.y()
                elif pos_target.y() + h_target + self.height() + 12 <= p_bottom:
                    x_pos = pos_target.x() + 15
                    y_pos = pos_target.y() + h_target + 12
                elif pos_target.y() - self.height() - 12 >= p_top:
                    x_pos = pos_target.x() + 15
                    y_pos = pos_target.y() - self.height() - 12
                else:
                    x_pos = pos_target.x() + 20
                    y_pos = pos_target.y() + 20
            else:
                x_pos = p_left + (p_width - self.width()) / 2
                y_pos = p_top + (p_height - self.height()) / 2

        # APLICAR DESPLAZAMIENTO FINO (OFFSET)
        offset = info.get("offset", (0, 0))
        x_pos += offset[0]
        y_pos += offset[1]

        # MANTENER DENTRO DE LOS BORDES DE LA VENTANA
        min_x = max(p_left + 10, screen_geom.left() + 10)
        max_x = min(p_left + p_width - self.width() - 10, screen_geom.right() - self.width() - 10)
        min_y = max(p_top + 10, screen_geom.top() + 10)
        max_y = min(p_top + p_height - self.height() - 10, screen_geom.bottom() - self.height() - 10)

        x_pos = max(min_x, min(x_pos, max_x))
        y_pos = max(min_y, min(y_pos, max_y))

        self.move(QPoint(int(x_pos), int(y_pos)))
        self.raise_()

    def _siguiente_paso(self):
        if self.paso_actual < len(self.pasos) - 1:
            self.paso_actual += 1
            self._mostrar_paso()
        else:
            self.close()

    def _anterior_paso(self):
        if self.paso_actual > 0:
            self.paso_actual -= 1
            self._mostrar_paso()