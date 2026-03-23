from PyQt5.QtWidgets import QMessageBox
# Importación relativa: el punto (.) significa "en esta misma carpeta"
try:
    from logica.calculos_cuk import calcular_diseno_cuk
except ImportError:
    from calculos_cuk import calcular_diseno_cuk
def obtener_valor_si(tab, nombre):
    """Obtiene el valor de un campo y lo convierte a unidades SI."""
    try:
        valor = float(tab.campos[nombre].text().replace(',', '.'))
        unidad = tab.combos[nombre].currentText()

        factores = {
            "V": 1, "mV": 1e-3, "µV": 1e-6,
            "W": 1, "mW": 1e-3,
            "A": 1, "mA": 1e-3, "µA": 1e-6,
            "Ω": 1, "kΩ": 1e3, "MΩ": 1e6
        }
        return valor * factores.get(unidad, 1)
    except:
        return None

def obtener_frecuencia_hz(tab):
    """Extrae la frecuencia en Hz del texto del combo."""
    texto = tab.combos["Frecuencia"].currentText()
    # Ejemplo: "Muy baja(25 kHz)" -> extrae 25 y multiplica por 1000
    try:
        valor_f = float(texto.split('(')[1].split(' ')[0])
        return valor_f * 1000
    except:
        return 25000.0


def ejecutar_accion(ventana, tabs):
    indice = tabs.currentIndex()
    tab_d = tabs.widget(0)
    tab_s = tabs.widget(1)

    if indice == 0:  # Pestaña DISEÑAR
        try:
            # 1. Capturar datos
            vin = obtener_valor_si(tab_d, "Vin")
            vout = obtener_valor_si(tab_d, "Vout")
            pout = obtener_valor_si(tab_d, "Pout")
            di = obtener_valor_si(tab_d, "ΔI")
            dv = obtener_valor_si(tab_d, "ΔV")
            freq = obtener_frecuencia_hz(tab_d)

            if None in [vin, vout, pout, di, dv]:
                QMessageBox.warning(ventana, "Error", "Verifique que todos los campos sean numéricos.")
                return

            # 2. Calcular usando el nuevo archivo de lógica
            resultados = calcular_diseno_cuk(vin, vout, pout, di, dv, freq)

            # 3. Pasar datos básicos y configuraciones
            tab_s.campos["Vin"].setText(tab_d.campos["Vin"].text())
            tab_s.combos["Vin"].setCurrentText(tab_d.combos["Vin"].currentText())
            tab_s.campos["Vout"].setText(tab_d.campos["Vout"].text())
            tab_s.combos["Vout"].setCurrentText(tab_d.combos["Vout"].currentText())
            tab_s.combos["Frecuencia"].setCurrentText(tab_d.combos["Frecuencia"].currentText())

            # 4. Escribir componentes calculados (con formato de unidades)
            tab_s.campos["Ciclo"].setText(f"{resultados['Ciclo'] * 100:.2f}")
            tab_s.campos["R"].setText(f"{resultados['R']:.2f}")

            # L1 y L2 en mH
            tab_s.campos["L1"].setText(f"{resultados['L1'] * 1000:.4f}")
            tab_s.combos["L1"].setCurrentText("mH")
            tab_s.campos["L2"].setText(f"{resultados['L2'] * 1000:.4f}")
            tab_s.combos["L2"].setCurrentText("mH")

            # C1 y C2 en uF
            tab_s.campos["C1"].setText(f"{resultados['C1'] * 1e6:.4f}")
            tab_s.combos["C1"].setCurrentText("µF")
            tab_s.campos["C2"].setText(f"{resultados['C2'] * 1e6:.4f}")
            tab_s.combos["C2"].setCurrentText("µF")

            tabs.setCurrentIndex(1)
            QMessageBox.information(ventana, "Diseño Exitoso", "Componentes calculados y transferidos a simulación.")

        except Exception as e:
            QMessageBox.critical(ventana, "Error de Cálculo", f"Hubo un problema procesando los datos: {str(e)}")

    else:  # Pestaña SIMULAR
        # Lógica de validación ya implementada
        QMessageBox.information(ventana, "Simulación", "Simulación en proceso...")