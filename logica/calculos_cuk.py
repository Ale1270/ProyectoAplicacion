def disenar_cuk(vin, vout, pout, fs, delta_i, delta_v):
    D = duty_cycle_ideal(vin, vout)

    Iout = pout / abs(vout)

    L1 = (vin * D) / (fs * delta_i)
    L2 = (abs(vout) * (1 - D)) / (fs * delta_i)

    C1 = (Iout * D) / (fs * delta_v)
    C2 = Iout / (8 * fs * delta_v)

    return {
        "Duty": D,
        "L1": L1,
        "L2": L2,
        "C1": C1,
        "C2": C2
    }