# Archivo: logica/ayuda.py
from PyQt5.QtWidgets import QMessageBox


def mostrar_ayuda(parent):
    """
    Muestra un cuadro de diálogo con instrucciones sobre cómo usar el simulador.
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle("Ayuda - Convertidor CUK")

    # Texto de ayuda (puedes personalizarlo a tu gusto)
    texto = (
        "<b>Instrucciones de Uso:</b><br><br>"
        "<b>1. Diseñar:</b> Ingrese los parámetros de entrada y salida requeridos. "
        "El programa calculará automáticamente el ciclo de trabajo y los valores "
        "ideales para los inductores y capacitores.<br><br>"
        "<b>2. Simular:</b> En esta pestaña puede verificar el diseño obtenido o "
        "ajustar manualmente los componentes para ver cómo reacciona el circuito.<br><br>"
        "<b>3. Slider de Tiempo:</b> Ajuste la duración de la simulación. Tiempos más largos "
        "ayudan a ver el estado estable, pero pueden tardar un poco más en calcularse.<br><br>"
        "<b>4. Calcular Filtros:</b> Presione este botón para ejecutar la simulación y ver "
        "las gráficas de corriente y voltaje."
    )

    msg.setText(texto)
    msg.setIcon(QMessageBox.Information)
    msg.exec_()