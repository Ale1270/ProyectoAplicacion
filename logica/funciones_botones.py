from PyQt5.QtWidgets import QMessageBox
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# =========================================
# ECUACIONES DEL CONVERTIDOR ĆUK - MODELO COMPLETO
# =========================================
def duty_cycle_exact(vin, vout):
    return abs(vout) / (vin + abs(vout))

def calcular_componentes(vin, vout, pout, fs, delta_i, delta_v):
    D = duty_cycle_exact(vin, vout)
    R = vout**2 / pout
    Iin = pout / vin
    Iout = pout / abs(vout)

    L1 = (vin * D) / (fs * delta_i * Iin)
    L2 = (abs(vout) * (1 - D)) / (fs * delta_i * Iout)
    C1 = (Iout * D) / (fs * delta_v * (vin + abs(vout)))
    C2 = (Iout * (1 - D)) / (fs * delta_v * abs(vout))

    return {"L1": L1, "L2": L2, "C1": C1, "C2": C2, "R": R, "Duty": D}

# =========================================
# ECUACIONES DIFERENCIALES PARA SIMULACION
# =========================================
def cuk_ode(x, t, vin, L1, L2, C1, C2, R, D):
    iL1, iL2, vC1, vout = x
    diL1_dt = (vin - vC1 * (1 - D)) / L1
    diL2_dt = (vC1 - vout * (1 - D)) / L2
    dvC1_dt = (iL1 - iL2) / C1
    dvout_dt = (iL2 - vout / R) / C2
    return [diL1_dt, diL2_dt, dvC1_dt, dvout_dt]

def simular_cuk(vin, vout, pout, fs, delta_i, delta_v, t_max=0.01):
    comp = calcular_componentes(vin, vout, pout, fs, delta_i, delta_v)
    L1, L2, C1, C2, R, D = comp["L1"], comp["L2"], comp["C1"], comp["C2"], comp["R"], comp["Duty"]

    x0 = [0, 0, 0, 0]
    t = np.linspace(0, t_max, int(t_max * fs * 50))
    sol = odeint(cuk_ode, x0, t, args=(vin, L1, L2, C1, C2, R, D))
    return t, sol, comp

# =========================================
# FUNCIONES PYQT PARA INTERFAZ
# =========================================
def ejecutar_accion(ventana, tabs):
    indice = tabs.currentIndex()
    tab_d = tabs.widget(0)
    tab_s = tabs.widget(1)

    if indice == 0:  # Pestaña de diseño
        if not campos_completos(tab_d):
            QMessageBox.warning(ventana, "Campos incompletos", "Complete todos los campos de diseño.")
            return
        procesar_disenio(tab_d, tab_s)
        tabs.setCurrentIndex(1)
    else:  # Pestaña de simulación
        if not campos_completos(tab_s):
            QMessageBox.warning(ventana, "Campos incompletos", "Complete todos los campos antes de simular.")
            return
        try:
            vin = obtener_valor(tab_s, "Vin")
            vout = obtener_valor(tab_s, "Vout")

            # Se toman los parámetros críticos de la pestaña de diseño
            pout = obtener_valor(tab_d, "Pout")
            delta_i = obtener_valor(tab_d, "ΔI")
            delta_v = obtener_valor(tab_d, "ΔV")
            fs = obtener_frecuencia(tab_d)

            # Tiempo de simulación desde el slider (convertido a segundos)
            t_max = ventana.slider.obtener_valor_ms() / 1000.0  # convertir a segundos

            # Simulación
            t, sol, comp = simular_cuk(vin, vout, pout, fs, delta_i, delta_v, t_max)

            # ===============================
            # GRÁFICA NORMAL DE MATPLOTLIB
            # ===============================
            plt.figure(figsize=(8,5))
            plt.plot(t, sol[:,0], label="iL1 (A)")
            plt.plot(t, sol[:,1], label="iL2 (A)")
            plt.plot(t, sol[:,2], label="vC1 (V)")
            plt.plot(t, sol[:,3], label="Vout (V)")
            plt.xlabel("Tiempo (s)")
            plt.ylabel("Corriente / Voltaje")
            plt.title("Simulación Convertidor Ćuk")
            plt.grid(True)
            plt.legend()
            plt.show()

        except Exception as e:
            QMessageBox.critical(tab_s, "Error de simulación", str(e))

# =========================================
# FUNCIONES AUXILIARES
# =========================================
def campos_completos(tab):
    return all(entrada.text().strip() != "" for entrada in tab.campos.values())

def obtener_valor(tab, nombre):
    texto = tab.campos[nombre].text().replace(',', '.')
    valor = float(texto)
    unidad = tab.combos[nombre].currentText()
    factores = {"mV":1e-3,"V":1,"mW":1e-3,"W":1,"mA":1e-3,"A":1,"µA":1e-6,"µV":1e-6}
    return valor * factores.get(unidad,1)

def obtener_frecuencia(tab):
    seleccion = tab.combos["Frecuencia"].currentText()
    mapa = {"Muy baja(25 kHz)":25e3,"Baja(50 kHz)":50e3,"Media(100 kHz)":100e3,"Alta(250 kHz)":250e3}
    if seleccion not in mapa:
        raise ValueError("Seleccione una frecuencia válida")
    return mapa[seleccion]

def copiar_basicos(tab_d, tab_s):
    for nombre in ["Vin","Vout"]:
        tab_s.campos[nombre].setText(tab_d.campos[nombre].text())
        tab_s.combos[nombre].setCurrentText(tab_d.combos[nombre].currentText())
    tab_s.combos["Frecuencia"].setCurrentText(tab_d.combos["Frecuencia"].currentText())

def formatear_capacitor(valor_f):
    if valor_f >= 1e-6: return valor_f*1e6,"µF"
    elif valor_f >= 1e-9: return valor_f*1e9,"nF"
    else: return valor_f*1e12,"pF"

def formatear_inductor(valor_h):
    if valor_h >= 1e-3: return valor_h*1e3,"mH"
    else: return valor_h*1e6,"µH"

def escribir_resultados(tab_s, r, vout, pout):
    tab_s.campos["Ciclo"].setText(f"{r['Duty']*100:.2f}")
    L1_val,L1_unit=formatear_inductor(r["L1"])
    L2_val,L2_unit=formatear_inductor(r["L2"])
    C1_val,C1_unit=formatear_capacitor(r["C1"])
    C2_val,C2_unit=formatear_capacitor(r["C2"])
    tab_s.campos["L1"].setText(f"{L1_val:.3f}"); tab_s.combos["L1"].setCurrentText(L1_unit)
    tab_s.campos["L2"].setText(f"{L2_val:.3f}"); tab_s.combos["L2"].setCurrentText(L2_unit)
    tab_s.campos["C1"].setText(f"{C1_val:.3f}"); tab_s.combos["C1"].setCurrentText(C1_unit)
    tab_s.campos["C2"].setText(f"{C2_val:.3f}"); tab_s.combos["C2"].setCurrentText(C2_unit)
    R_val = r["R"]
    if R_val >= 1e6: tab_s.campos["R"].setText(f"{R_val/1e6:.3f}"); tab_s.combos["R"].setCurrentText("MΩ")
    elif R_val >= 1e3: tab_s.campos["R"].setText(f"{R_val/1e3:.3f}"); tab_s.combos["R"].setCurrentText("kΩ")
    else: tab_s.campos["R"].setText(f"{R_val:.3f}"); tab_s.combos["R"].setCurrentText("Ω")

def procesar_disenio(tab_d, tab_s):
    try:
        vin = obtener_valor(tab_d, "Vin")
        vout = obtener_valor(tab_d, "Vout")
        pout = obtener_valor(tab_d, "Pout")
        delta_i = obtener_valor(tab_d, "ΔI")
        delta_v = obtener_valor(tab_d, "ΔV")
        fs = obtener_frecuencia(tab_d)
        resultados = calcular_componentes(vin, vout, pout, fs, delta_i, delta_v)
        copiar_basicos(tab_d, tab_s)
        escribir_resultados(tab_s, resultados, vout, pout)
    except Exception as e:
        QMessageBox.critical(None, "Error de cálculo", str(e))