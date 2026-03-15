from PyQt5.QtWidgets import QMessageBox

# =========================================
# ECUACIONES DEL CONVERTIDOR ĆUK - MODELO COMPLETO
# =========================================
def duty_cycle_exact(vin, vout):
    return abs(vout) / (vin + abs(vout))


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
        #calcular los componentes
        tabs.setCurrentIndex(1)
    else:  # Pestaña de simulación
        if not campos_completos(tab_s):
            QMessageBox.warning(ventana, "Campos incompletos", "Complete todos los campos antes de simular.")
            return
        # try:
            #graficas
        #except Exception as e:
        #   QMessageBox.critical(tab_s, "Error de simulación", str(e))

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

def copiar_valores