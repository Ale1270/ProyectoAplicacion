import numpy as np


def calcular_diseno_cuk(vin, vout, pout, di, dv, freq):
    """
    Realiza los cálculos estáticos para un convertidor Ćuk en CCM.
    """
    try:
        vout_abs = abs(vout)
        # Ciclo de trabajo D
        d = vout_abs / (vin + vout_abs)

        # Resistencia de carga
        r_carga = (vout_abs ** 2) / pout
        io = vout_abs / r_carga

        # Inductancias (en Henrios)
        l1 = (vin * d) / (freq * di)
        l2 = (vin * d) / (freq * di)

        # Capacitancias (en Faradios)
        # C1 basado en 5% de rizado de Vin como estándar de transferencia
        vc1_ripple = 0.05 * vin
        c1 = (io * d) / (freq * vc1_ripple)

        # C2 basado en el rizado de voltaje de salida deseado
        c2 = di / (8 * freq * dv)

        return {
            "Ciclo": d,
            "R": r_carga,
            "L1": l1,
            "L2": l2,
            "C1": c1,
            "C2": c2
        }
    except Exception as e:
        print(f"Error en calculos_cuk: {e}")
        return None

def simular_sistema_cuk(Vin, L1, C1, L2, C2, R, D, f_sw, t_simulacion, callback_progreso=None):
    """
    Simulación dinámica de un convertidor Ćuk usando el método de Runge-Kutta de 4to orden (RK4).
    Implementa "dithering" del ciclo de trabajo para asegurar precisión absoluta en el voltaje de salida.
    """
    T = 1.0 / f_sw

    # Aumentamos ligeramente la resolución base a 100 para un rizado más fiel
    pasos_por_ciclo = 100
    dt = T / pasos_por_ciclo

    num_steps = int(t_simulacion / dt)
    if num_steps <= 0:
        num_steps = 1

    t = np.linspace(0, t_simulacion, num_steps)

    iL1 = np.zeros(num_steps)
    vC1 = np.zeros(num_steps)
    iL2 = np.zeros(num_steps)
    Vo = np.zeros(num_steps)

    paso_notificacion = max(1, num_steps // 100)

    # Pre-calculamos el valor flotante de pasos para aplicar el compensador
    pasos_on_float = D * pasos_por_ciclo

    for k in range(num_steps - 1):
        if callback_progreso and (k % paso_notificacion == 0):
            porcentaje = int((k / num_steps) * 100)
            callback_progreso(porcentaje)

        ciclo_actual = k // pasos_por_ciclo
        paso_dentro_ciclo = k % pasos_por_ciclo

        # SOLUCIÓN: Dithering del duty cycle
        # Rastreamos el error decimal acumulado y ajustamos los pasos ON ciclo a ciclo
        # Esto elimina el error de estado estable en el voltaje de salida.
        pasos_on = int((ciclo_actual + 1) * pasos_on_float) - int(ciclo_actual * pasos_on_float)

        es_estado_on = paso_dentro_ciclo < pasos_on

        y1, y2, y3, y4 = iL1[k], vC1[k], iL2[k], Vo[k]

        if es_estado_on:
            # ==========================================
            # ESTADO 1: MOSFET ON / DIODO OFF
            # ==========================================
            k1_1 = Vin / L1
            k1_2 = y3 / C1
            k1_3 = (-y2 - y4) / L2
            k1_4 = (y3 - y4 / R) / C2

            y2_mid = y2 + k1_2 * dt / 2
            y3_mid = y3 + k1_3 * dt / 2
            y4_mid = y4 + k1_4 * dt / 2

            k2_1 = Vin / L1
            k2_2 = y3_mid / C1
            k2_3 = (-y2_mid - y4_mid) / L2
            k2_4 = (y3_mid - y4_mid / R) / C2

            y2_mid2 = y2 + k2_2 * dt / 2
            y3_mid2 = y3 + k2_3 * dt / 2
            y4_mid2 = y4 + k2_4 * dt / 2

            k3_1 = Vin / L1
            k3_2 = y3_mid2 / C1
            k3_3 = (-y2_mid2 - y4_mid2) / L2
            k3_4 = (y3_mid2 - y4_mid2 / R) / C2

            y2_end = y2 + k3_2 * dt
            y3_end = y3 + k3_3 * dt
            y4_end = y4 + k3_4 * dt

            k4_1 = Vin / L1
            k4_2 = y3_end / C1
            k4_3 = (-y2_end - y4_end) / L2
            k4_4 = (y3_end - y4_end / R) / C2

        else:
            # ==========================================
            # ESTADO 2: MOSFET OFF / DIODO ON
            # ==========================================
            k1_1 = (Vin - y2) / L1
            k1_2 = y1 / C1
            k1_3 = -y4 / L2
            k1_4 = (y3 - y4 / R) / C2

            y1_mid = y1 + k1_1 * dt / 2
            y2_mid = y2 + k1_2 * dt / 2
            y3_mid = y3 + k1_3 * dt / 2
            y4_mid = y4 + k1_4 * dt / 2

            k2_1 = (Vin - y2_mid) / L1
            k2_2 = y1_mid / C1
            k2_3 = -y4_mid / L2
            k2_4 = (y3_mid - y4_mid / R) / C2

            y1_mid2 = y1 + k2_1 * dt / 2
            y2_mid2 = y2 + k2_2 * dt / 2
            y3_mid2 = y3 + k2_3 * dt / 2
            y4_mid2 = y4 + k2_4 * dt / 2

            k3_1 = (Vin - y2_mid2) / L1
            k3_2 = y1_mid2 / C1
            k3_3 = -y4_mid2 / L2
            k3_4 = (y3_mid2 - y4_mid2 / R) / C2

            y1_end = y1 + k3_1 * dt
            y2_end = y2 + k3_2 * dt
            y3_end = y3 + k3_3 * dt
            y4_end = y4 + k3_4 * dt

            k4_1 = (Vin - y2_end) / L1
            k4_2 = y1_end / C1
            k4_3 = -y4_end / L2
            k4_4 = (y3_end - y4_end / R) / C2

        # Integración RK4
        iL1[k + 1] = y1 + (dt / 6.0) * (k1_1 + 2 * k2_1 + 2 * k3_1 + k4_1)
        vC1[k + 1] = y2 + (dt / 6.0) * (k1_2 + 2 * k2_2 + 2 * k3_2 + k4_2)
        iL2[k + 1] = y3 + (dt / 6.0) * (k1_3 + 2 * k2_3 + 2 * k3_3 + k4_3)
        Vo[k + 1] = y4 + (dt / 6.0) * (k1_4 + 2 * k2_4 + 2 * k3_4 + k4_4)

    return t, iL1, vC1, iL2, Vo

def calcular_caracteristicas_estado_estable(Vin, R, D, t, iL1, iL2, Vo, f_sw, V_diodo=0.4, R_ds_on=0.05, R_L=0.1):
    """
    Analiza las curvas generadas por la simulación para determinar
    potencias reales, eficiencia y tiempo de estabilización.
    Corrige las fórmulas de corriente combinada (iL1 + iL2) para la topología Ćuk.
    """
    try:
        n_total = len(t)
        if n_total < 2:
            raise ValueError("No hay suficientes datos de tiempo.")

        dt = t[1] - t[0]
        puntos_por_ciclo = max(1, int((1.0 / f_sw) / dt))
        puntos_totales_analisis = max(1, puntos_por_ciclo * 10)

        # -------------------------------------------------------
        # Zona estable para calcular el valor final de referencia
        # -------------------------------------------------------
        if n_total < puntos_totales_analisis * 2:
            idx_estable = n_total // 2
        else:
            idx_estable = n_total - puntos_totales_analisis

        Vo_steady_arr = Vo[idx_estable:]
        iL1_steady_arr = iL1[idx_estable:]
        iL2_steady_arr = iL2[idx_estable:]

        # -------------------------------------------------------
        # Cálculo de Potencias y Pérdidas (Fórmulas Ćuk)
        # -------------------------------------------------------
        # Potencia de entrada proveniente de la fuente
        Pin = Vin * np.mean(iL1_steady_arr)

        if Pin > 0:
            # Corrientes promedio y RMS de las bobinas
            I_L1_avg = np.mean(iL1_steady_arr)
            I_L2_avg = np.mean(np.abs(iL2_steady_arr))

            I_L1_rms = np.sqrt(np.mean(iL1_steady_arr ** 2))
            I_L2_rms = np.sqrt(np.mean(iL2_steady_arr ** 2))

            # 1. Pérdidas en MOSFET: conduce (iL1 + iL2) durante tiempo D
            I_sw_rms = (I_L1_rms + I_L2_rms) * np.sqrt(D)
            P_perdida_mosfet = (I_sw_rms ** 2) * R_ds_on

            # 2. Pérdidas en Diodo: conduce (iL1 + iL2) durante tiempo (1 - D)
            I_diodo_avg = (I_L1_avg + I_L2_avg) * (1 - D)
            P_perdida_diodo = I_diodo_avg * V_diodo

            # 3. Pérdidas en Bobinas (ESR/DCR)
            P_perdida_bobinas = (I_L1_rms ** 2) * R_L + (I_L2_rms ** 2) * R_L

            # Potencia total de pérdidas
            P_perdidas_totales = P_perdida_mosfet + P_perdida_diodo + P_perdida_bobinas

            # Potencia real de salida y Eficiencia
            Pout_ideal = np.mean((Vo_steady_arr ** 2) / R)
            Pout_real = max(Pout_ideal - P_perdidas_totales, 0.0)

            eficiencia = (Pout_real / Pin) * 100.0
            # Limitar eficiencia a rango físicamente válido
            eficiencia = min(max(eficiencia, 0.0), 100.0)
            Pout_mostrar = Pout_real
        else:
            eficiencia = 0.0
            Pout_mostrar = 0.0
            Pin = 0.0

        # -------------------------------------------------------
        # Tiempo de estabilización - Enfoque de Envolvente (0.5%)
        # -------------------------------------------------------
        Vo_mean = np.mean(Vo_steady_arr)

        # 1. Filtro de media móvil del tamaño de 1 ciclo
        kernel = np.ones(puntos_por_ciclo) / puntos_por_ciclo
        Vo_suavizado = np.convolve(Vo, kernel, mode='valid')
        t_suavizado = t[puntos_por_ciclo - 1:]

        # 2. Tolerancia del 0.2%
        tolerancia = abs(0.002 * Vo_mean)

        # 3. Búsqueda de último índice fuera de la tolerancia
        indices_fuera = np.where(np.abs(Vo_suavizado - Vo_mean) > tolerancia)[0]

        t_estable_str = "No estabilizado"

        if len(indices_fuera) == 0:
            t_estable_str = "0.0 µs"
        else:
            ultimo_idx_fuera = indices_fuera[-1]
            puntos_margen = puntos_por_ciclo * 20

            if (len(Vo_suavizado) - ultimo_idx_fuera) > puntos_margen:
                idx_estable_real = ultimo_idx_fuera + 1
                if idx_estable_real < len(t_suavizado):
                    t_estable = t_suavizado[idx_estable_real]

                    if t_estable < 1e-3:
                        t_estable_str = f"{t_estable * 1e6:.1f} µs"
                    elif t_estable < 1:
                        t_estable_str = f"{t_estable * 1e3:.1f} ms"
                    else:
                        t_estable_str = f"{t_estable:.2f} s"

        return {
            "Pin": Pin,
            "Pout": Pout_mostrar,
            "Eficiencia": eficiencia,
            "Tiempo": t_estable_str
        }

    except Exception as e:
        print(f"Error analizando estado estable: {e}")
        return None