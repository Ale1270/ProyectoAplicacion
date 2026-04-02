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

def simular_sistema_cuk(params, t_final, f_sw):
    try:
        dt = 1 / (f_sw * 100)
        steps = int(t_final / dt)

        if steps > 400000:
            steps = 400000
            dt = t_final / steps

        steps = max(1000, steps)
        t = np.linspace(0, t_final, steps)
        T = 1 / f_sw

        Vin, L1, L2, C1, C2, R = params['Vin'], params['L1'], params['L2'], params['C1'], params['C2'], params['R']

        # --- NUEVOS PARÁMETROS (Con valores por defecto si no existen) ---
        rL1 = params.get('rL1', 0.05)  # 50 mΩ por defecto
        rL2 = params.get('rL2', 0.05)

        # Variables PID
        lazo_cerrado = params.get('LazoCerrado', False)
        Vref = abs(params.get('Vout', 12.0))  # Meta del PID (valor absoluto)
        Kp = params.get('Kp', 0.005)
        Ki = params.get('Ki', 2.0)

        # Estado inicial del Duty Cycle
        D_actual = params['D']
        integral_e = 0.0

        il1, il2, vc1, vc2 = np.zeros(steps), np.zeros(steps), np.zeros(steps), np.zeros(steps)
        duty_array = np.zeros(steps)

        for i in range(steps - 1):
            # --- LÓGICA DE CONTROL ---
            if lazo_cerrado:
                # El Cuk invierte, medimos el valor absoluto
                error = Vref - abs(vc2[i])
                integral_e += error * dt

                # Anti-windup básico
                integral_e = max(-0.5 / Ki, min(0.5 / Ki, integral_e)) if Ki != 0 else 0

                D_actual = (Kp * error) + (Ki * integral_e)
                D_actual = max(0.1, min(0.9, D_actual))  # Limitar entre 10% y 90%

            duty_array[i] = D_actual
            estado_on = (t[i] % T) < (D_actual * T)

            # --- MODELADO FÍSICO CON PÉRDIDAS (rL1 y rL2) ---
            if estado_on:
                dil1 = (Vin - (il1[i] * rL1)) / L1
                dil2 = (vc1[i] + vc2[i] - (il2[i] * rL2)) / L2
            else:
                dil1 = (Vin - vc1[i] - (il1[i] * rL1)) / L1
                dil2 = (vc2[i] - (il2[i] * rL2)) / L2

            il1[i + 1] = il1[i] + dil1 * dt
            il2[i + 1] = il2[i] + dil2 * dt

            if estado_on:
                dvc1 = -il2[i + 1] / C1
                dvc2 = (-il2[i + 1] - vc2[i] / R) / C2
            else:
                dvc1 = il1[i + 1] / C1
                dvc2 = (-il2[i + 1] - vc2[i] / R) / C2

            vc1[i + 1] = vc1[i] + dvc1 * dt
            vc2[i + 1] = vc2[i] + dvc2 * dt

            if not np.isfinite(vc2[i + 1]):
                break

        duty_array[-1] = duty_array[-2]

        # Solo retornamos Duty si estamos en Lazo Cerrado para no saturar gráficas innecesariamente
        resultados = {
            "iL1": il1[:i + 2],
            "iL2": il2[:i + 2],
            "vC1": vc1[:i + 2],
            "Vo": vc2[:i + 2]
        }
        if lazo_cerrado:
            resultados["Duty Cycle (PID)"] = duty_array[:i + 2]

        return t[:i + 2], resultados
    except Exception as e:
        raise Exception(f"Error en cálculos físicos: {str(e)}")


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

            # 3. Ahora sí, empaquetamos

            params = {k: obtener_valor_si(tab_actual, k) for k in ["Vin", "R", "L1", "L2", "C1", "C2"]}

            params['D'] = D_calculado  # Usamos el D que acabamos de recalcular

            f_sw = obtener_frecuencia_hz(tab_actual)

            t_ms = (ventana.slider.value() / ventana.slider.maximum()) ** 2 * ventana.slider.maximum()

            t, resultados = simular_sistema_cuk(params, t_ms / 1000.0, f_sw)

            if hasattr(ventana, 'dialogo_graficas'):
                ventana.dialogo_graficas.close()

            ventana.dialogo_graficas = VentanaGraficas(t, resultados, ventana)

            ventana.dialogo_graficas.show()

    except Exception as e:
        QMessageBox.critical(ventana, "Error Crítico", f"Ocurrió un fallo inesperado:\n{str(e)}")