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