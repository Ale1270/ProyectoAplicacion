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


def simular_sistema_cuk(Vin, L1, C1, L2, C2, R, D, f_sw, t_simulacion):
    """
    Simulación dinámica de un convertidor Ćuk usando el método de Runge-Kutta de 4to orden (RK4).
    """
    T = 1.0 / f_sw
    pasos_por_ciclo = 70
    dt = T / pasos_por_ciclo

    num_steps = int(t_simulacion / dt)
    if num_steps <= 0:
        num_steps = 1

    t = np.linspace(0, t_simulacion, num_steps)

    iL1 = np.zeros(num_steps)
    vC1 = np.zeros(num_steps)
    iL2 = np.zeros(num_steps)
    Vo = np.zeros(num_steps)

    for k in range(num_steps - 1):
        t_ciclo = t[k] % T

        # Variables actuales para simplificar la lectura de fórmulas
        y1, y2, y3, y4 = iL1[k], vC1[k], iL2[k], Vo[k]

        if t_ciclo < D * T:
            # ==========================================
            # ESTADO 1: MOSFET ON / DIODO OFF
            # ==========================================
            # K1 (Pendientes al inicio del intervalo)
            k1_1 = Vin / L1
            k1_2 = y3 / C1
            k1_3 = (-y2 - y4) / L2
            k1_4 = (y3 - y4 / R) / C2

            # K2 (Pendientes en el punto medio, usando k1)
            y2_mid = y2 + k1_2 * dt / 2
            y3_mid = y3 + k1_3 * dt / 2
            y4_mid = y4 + k1_4 * dt / 2

            k2_1 = Vin / L1
            k2_2 = y3_mid / C1
            k2_3 = (-y2_mid - y4_mid) / L2
            k2_4 = (y3_mid - y4_mid / R) / C2

            # K3 (Pendientes en el punto medio, usando k2)
            y2_mid2 = y2 + k2_2 * dt / 2
            y3_mid2 = y3 + k2_3 * dt / 2
            y4_mid2 = y4 + k2_4 * dt / 2

            k3_1 = Vin / L1
            k3_2 = y3_mid2 / C1
            k3_3 = (-y2_mid2 - y4_mid2) / L2
            k3_4 = (y3_mid2 - y4_mid2 / R) / C2

            # K4 (Pendientes al final del intervalo, usando k3)
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
            # K1
            k1_1 = (Vin - y2) / L1
            k1_2 = y1 / C1
            k1_3 = -y4 / L2
            k1_4 = (y3 - y4 / R) / C2

            # K2
            y1_mid = y1 + k1_1 * dt / 2
            y2_mid = y2 + k1_2 * dt / 2
            y3_mid = y3 + k1_3 * dt / 2
            y4_mid = y4 + k1_4 * dt / 2

            k2_1 = (Vin - y2_mid) / L1
            k2_2 = y1_mid / C1
            k2_3 = -y4_mid / L2
            k2_4 = (y3_mid - y4_mid / R) / C2

            # K3
            y1_mid2 = y1 + k2_1 * dt / 2
            y2_mid2 = y2 + k2_2 * dt / 2
            y3_mid2 = y3 + k2_3 * dt / 2
            y4_mid2 = y4 + k2_4 * dt / 2

            k3_1 = (Vin - y2_mid2) / L1
            k3_2 = y1_mid2 / C1
            k3_3 = -y4_mid2 / L2
            k3_4 = (y3_mid2 - y4_mid2 / R) / C2

            # K4
            y1_end = y1 + k3_1 * dt
            y2_end = y2 + k3_2 * dt
            y3_end = y3 + k3_3 * dt
            y4_end = y4 + k3_4 * dt

            k4_1 = (Vin - y2_end) / L1
            k4_2 = y1_end / C1
            k4_3 = -y4_end / L2
            k4_4 = (y3_end - y4_end / R) / C2

        # ==========================================
        # PASO FINAL DE RK4: Promedio ponderado
        # ==========================================
        iL1[k + 1] = y1 + (dt / 6.0) * (k1_1 + 2 * k2_1 + 2 * k3_1 + k4_1)
        vC1[k + 1] = y2 + (dt / 6.0) * (k1_2 + 2 * k2_2 + 2 * k3_2 + k4_2)
        iL2[k + 1] = y3 + (dt / 6.0) * (k1_3 + 2 * k2_3 + 2 * k3_3 + k4_3)
        Vo[k + 1] = y4 + (dt / 6.0) * (k1_4 + 2 * k2_4 + 2 * k3_4 + k4_4)

    return t, iL1, vC1, iL2, Vo


def calcular_caracteristicas_estado_estable(Vin, R, D, t, iL1, iL2, Vo, f_sw):
    """
    Analiza las curvas generadas por la simulación para determinar
    potencias reales, eficiencia y tiempo de estabilización.

    Versión 2 - Correcciones:
    - Tolerancia reducida a 2% para detección más precisa
    - N_ciclos_estables aumentado a 20 para mayor confiabilidad
    - Algoritmo de ventana optimizado con numpy (sin bucle Python lento)
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
        # Cálculo de potencias y eficiencia
        # -------------------------------------------------------
        Pout_ideal = np.mean((Vo_steady_arr ** 2) / R)
        Pin = Vin * np.mean(iL1_steady_arr)

        if Pin > 0:
            if Pout_ideal > Pin:
                Pout_ideal = Pin

            V_diodo = 0.7
            R_ds_on = 0.05
            R_L = 0.1

            I_L1_rms = np.sqrt(np.mean(iL1_steady_arr ** 2))
            I_L2_rms = np.sqrt(np.mean(iL2_steady_arr ** 2))
            Vo_prom = abs(np.mean(Vo_steady_arr))
            I_out_avg = (Pout_ideal / Vo_prom) if Vo_prom > 0 else 0.0

            P_perdida_mosfet = (I_L1_rms ** 2) * D * R_ds_on
            P_perdida_diodo = I_out_avg * V_diodo * (1 - D)
            P_perdida_bobinas = (I_L1_rms ** 2) * R_L + (I_L2_rms ** 2) * R_L

            Pout_real = Pout_ideal - (P_perdida_mosfet + P_perdida_diodo + P_perdida_bobinas)
            Pout_real = max(Pout_real, 0.0)

            eficiencia = (Pout_real / Pin) * 100.0
            Pout_mostrar = Pout_real
        else:
            eficiencia = 0.0
            Pout_mostrar = 0.0
            Pin = 0.0

        # -------------------------------------------------------
        # Tiempo de estabilización — versión corregida
        # -------------------------------------------------------
        Vo_mean = np.mean(Vo_steady_arr)

        # CORRECCIÓN 1: Tolerancia reducida a 2% (antes 5%)
        tolerancia = abs(0.02 * Vo_mean)

        # CORRECCIÓN 2: Más ciclos consecutivos requeridos (antes 5)
        N_ciclos_estables = 40
        puntos_necesarios = N_ciclos_estables * puntos_por_ciclo

        t_estable_str = "No estabilizado"

        if len(Vo) > puntos_necesarios:

            # OPTIMIZACIÓN: En lugar de bucle Python, usar operaciones numpy
            # 1. Crear máscara booleana: True donde está dentro de la banda
            dentro_banda = np.abs(Vo - Vo_mean) < tolerancia

            # 2. Calcular suma acumulada de puntos FUERA de la banda
            #    Cada vez que un punto está fuera, el contador sube
            fuera_banda = (~dentro_banda).astype(np.int32)

            # 3. Suma acumulada: permite saber cuántos puntos fuera hay
            #    desde el inicio hasta cada índice
            suma_acum = np.cumsum(fuera_banda)

            # 4. Para cada ventana [i, i+N], contar puntos fuera de banda
            #    usando la diferencia de sumas acumuladas
            #    Si suma_acum[i+N] - suma_acum[i] == 0, toda la ventana está dentro
            suma_inicio = suma_acum[:-puntos_necesarios]
            suma_fin = suma_acum[puntos_necesarios:]
            puntos_fuera = suma_fin - suma_inicio

            # 5. Buscar la primera ventana completamente dentro de la banda
            ventanas_estables = np.where(puntos_fuera == 0)[0]

            if len(ventanas_estables) > 0:
                idx_primer_estable = ventanas_estables[0]
                t_estable = t[idx_primer_estable]

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