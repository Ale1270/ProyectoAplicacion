# Archivo: logica/acerca_de.py
from PyQt5.QtWidgets import QMessageBox


def mostrar_acerca_de(parent):
    """
    Muestra un cuadro de diálogo con información sobre la aplicación y sus creadores.
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle("Acerca de")

    texto = (
        "<b>Simulador Convertidor Ćuk</b><br>"
        "Versión 1.0<br><br>"
        "Esta aplicación ha sido diseñada para facilitar el cálculo, diseño "
        "y simulación de convertidores DC-DC tipo Ćuk.<br><br>"
        "<i>Desarrollado con Python y PyQt5.</i>"
    )

    msg.setText(texto)
    msg.setIcon(QMessageBox.Information)
    msg.exec_()