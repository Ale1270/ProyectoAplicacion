import numpy as np
import sys
import os
from PyQt5.QtWidgets import QMessageBox

# --- CONFIGURACIÓN DE RUTAS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from widgets.ventana_graficas import VentanaGraficas
    from logica.calculos_cuk import calcular_diseno_cuk
except ImportError:
    from ventana_graficas import VentanaGraficas
    from calculos_cuk import calcular_diseno_cuk


# ==========================================================
# 1. VALIDACIÓN RIGUROSA (Anti-Letras y Anti-Vacíos)
# ==========================================================

def validar_entradas(tab):
    """
    Revisa cada campo. Si hay una letra o está vacío, devuelve (False, mensaje).
    Si es correcto, devuelve (True, None).
    """
    for nombre, entrada in tab.campos.items():
        texto = entrada.text().strip().replace(',', '.')

        # 1. Verificar si está vacío
        if not texto:
            return False, f"El campo '{nombre}' está vacío."

        # 2. Verificar si es un número válido (no letras)
        try:
            valor = float(texto)
        except ValueError:
            return False, f"Error en '{nombre}': '{texto}' no es un número válido. Elimine las letras."

        # 3. Verificar que no sea cero o negativo (excepto Vout y Ciclo que pueden variar)
        if valor <= 0 and nombre not in ["Vout", "Ciclo"]:
            return False, f"El valor de '{nombre}' debe ser mayor a cero."

    return True, None


def obtener_valor_si(tab, nombre):
    """Ya validado previamente, solo realiza la conversión y escala."""
    texto = tab.campos[nombre].text().replace(',', '.')
    valor = float(texto)
    unidad = tab.combos[nombre].currentText()

    factores = {
        "V": 1, "mV": 1e-3, "µV": 1e-6, "W": 1, "mW": 1e-3,
        "A": 1, "mA": 1e-3, "µA": 1e-6, "Ω": 1, "kΩ": 1e3, "MΩ": 1e6,
        "mH": 1e-3, "µH": 1e-6, "µF": 1e-6, "nF": 1e-9, "pF": 1e-12
    }
    return valor * factores.get(unidad, 1)


def obtener_frecuencia_hz(tab):
    try:
        texto = tab.combos["Frecuencia"].currentText()
        valor_f = float(texto.split('(')[1].split(' ')[0])
        return valor_f * 1000
    except:
        return 50000.0


def auto_formatear(valor, tipo="C"):
    if tipo == "C":
        if valor < 1e-9:
            return valor * 1e12, "pF"
        elif valor < 1e-6:
            return valor * 1e9, "nF"
        else:
            return valor * 1e6, "µF"
    elif tipo == "L":
        if valor < 1e-3:
            return valor * 1e6, "µH"
        else:
            return valor * 1e3, "mH"
    return valor, ""


# ==========================================================
# 2. MOTOR DE SIMULACIÓN (CONMUTADA Y SEGURA)
# ==========================================================

def simular_sistema_cuk(Vin, L1, C1, L2, C2, R, D, f_sw, t_simulacion):
    """
    Simulación dinámica de un convertidor Ćuk usando el método de Euler.
    """
    # 1. Configuración de tiempo
    T = 1.0 / f_sw
    pasos_por_ciclo = 400  # Alta resolución para garantizar estabilidad numérica
    dt = T / pasos_por_ciclo

    num_steps = int(t_simulacion / dt)
    if num_steps <= 0:
        num_steps = 1

    t = np.linspace(0, t_simulacion, num_steps)

    # 2. Inicialización de variables de estado
    iL1 = np.zeros(num_steps)  # Corriente inductor entrada
    vC1 = np.zeros(num_steps)  # Voltaje capacitor intermedio
    iL2 = np.zeros(num_steps)  # Corriente inductor salida
    Vo = np.zeros(num_steps)  # Voltaje de salida (en C2)

    # 3. Bucle de Simulación (Integración numérica)
    for k in range(num_steps - 1):
        t_ciclo = t[k] % T

        if t_ciclo < D * T:
            # ==========================================
            # ESTADO 1: MOSFET ON / DIODO OFF
            # ==========================================
            diL1_dt = Vin / L1
            dvC1_dt = iL2[k] / C1  # Signo corregido para descarga correcta
            diL2_dt = (-vC1[k] - Vo[k]) / L2
            dVo_dt = (iL2[k] - Vo[k] / R) / C2
        else:
            # ==========================================
            # ESTADO 2: MOSFET OFF / DIODO ON
            # ==========================================
            diL1_dt = (Vin - vC1[k]) / L1
            dvC1_dt = iL1[k] / C1
            diL2_dt = -Vo[k] / L2
            dVo_dt = (iL2[k] - Vo[k] / R) / C2

        # 4. Aplicación del Método de Euler
        iL1[k + 1] = iL1[k] + diL1_dt * dt
        vC1[k + 1] = vC1[k] + dvC1_dt * dt
        iL2[k + 1] = iL2[k] + diL2_dt * dt
        Vo[k + 1] = Vo[k] + dVo_dt * dt

    return t, iL1, vC1, iL2, Vo


# ==========================================================
# 3. LÓGICA PRINCIPAL (PUNTO DE ENTRADA)
# ==========================================================

def ejecutar_accion(ventana, tabs):
    idx = tabs.currentIndex()
    tab_actual = tabs.widget(idx)
    tab_s = tabs.widget(1)  # Referencia a simulación

    # --- PASO 1: VALIDAR FORMATO (Letras, Vacíos, Ceros) ---
    es_valido, mensaje_error = validar_entradas(tab_actual)
    if not es_valido:
        QMessageBox.critical(ventana, "Error de Entrada", mensaje_error)
        return

    # --- PASO 2: EJECUTAR SEGÚN PESTAÑA ---
    try:
        if idx == 0:  # MODO DISEÑO
            vin = obtener_valor_si(tab_actual, "Vin")
            vout = obtener_valor_si(tab_actual, "Vout")
            pout = obtener_valor_si(tab_actual, "Pout")
            di = obtener_valor_si(tab_actual, "ΔI")
            dv = obtener_valor_si(tab_actual, "ΔV")
            f_hz = obtener_frecuencia_hz(tab_actual)

            res = calcular_diseno_cuk(vin, vout, pout, di, dv, f_hz)

            # Transferencia Completa
            tab_s.campos["Vin"].setText(tab_actual.campos["Vin"].text())
            tab_s.combos["Vin"].setCurrentText(tab_actual.combos["Vin"].currentText())
            tab_s.campos["Vout"].setText(tab_actual.campos["Vout"].text())
            tab_s.combos["Vout"].setCurrentText(tab_actual.combos["Vout"].currentText())
            tab_s.combos["Frecuencia"].setCurrentText(tab_actual.combos["Frecuencia"].currentText())

            tab_s.campos["Ciclo"].setText(f"{res['Ciclo'] * 100:.2f}")
            tab_s.campos["R"].setText(f"{res['R']:.2f}")

            for comp, tipo in [("L1", "L"), ("L2", "L"), ("C1", "C"), ("C2", "C")]:
                val, uni = auto_formatear(res[comp], tipo)
                tab_s.campos[comp].setText(f"{val:.3f}")
                tab_s.combos[comp].setCurrentText(uni)

            tabs.setCurrentIndex(1)


        else:  # MODO SIMULACIÓN

            # 1. Leer Vin y el Vout deseado de la pestaña simulación

            Vin_sim = obtener_valor_si(tab_actual, "Vin")

            Vout_sim = obtener_valor_si(tab_actual, "Vout")

            # 2. Forzar el recálculo del Ciclo de Trabajo (D) basándonos en el nuevo Vout

            # Fórmula del Cuk: |Vout|/Vin = D / (1 - D)  =>  D = |Vout| / (|Vout| + Vin)

            D_calculado = abs(Vout_sim) / (abs(Vout_sim) + Vin_sim)

            # Actualizamos la interfaz para que el usuario vea el nuevo Duty usado

            tab_actual.campos["Ciclo"].setText(f"{D_calculado * 100:.2f}")

            # 3. Recopilar todos los parámetros físicos

            params = {k: obtener_valor_si(tab_actual, k) for k in ["Vin", "R", "L1", "L2", "C1", "C2"]}

            f_sw = obtener_frecuencia_hz(tab_actual)

            t_ms = ventana.slider.obtener_valor_ms()

            t_sim_segundos = t_ms / 1000.0  # Convertir a segundos

            # 4. EJECUTAR SIMULACIÓN (Pasando los 9 parámetros exactos)

            t, iL1, vC1, iL2, Vo = simular_sistema_cuk(

                Vin=params["Vin"],

                L1=params["L1"],

                C1=params["C1"],

                L2=params["L2"],

                C2=params["C2"],

                R=params["R"],

                D=D_calculado,

                f_sw=f_sw,

                t_simulacion=t_sim_segundos

            )

            # 5. Empaquetar las señales para la VentanaGraficas

            resultados = {

                "iL1": iL1,

                "vC1": vC1,

                "iL2": iL2,

                "Vo": Vo

            }

            # 6. Lanzar la gráfica

            if hasattr(ventana, 'dialogo_graficas'):
                ventana.dialogo_graficas.close()

            ventana.dialogo_graficas = VentanaGraficas(t, resultados, ventana)

            ventana.dialogo_graficas.show()

    except Exception as e:

        QMessageBox.critical(ventana, "Error Crítico", f"Ocurrió un fallo inesperado:\n{str(e)}")