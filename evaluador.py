def calcular_score(auth, cifrado, senal):
    # Pesos (wi) y severidades (si) definidos en tu metodología [cite: 138, 147]
    w_auth, w_cifrado, w_rssi = 0.4, 0.4, 0.2 
    
    s_auth = {"WPA2-Personal": 0.3, "WPA3-Personal": 0.0}.get(auth, 0.5)
    s_cifrado = {"CCMP": 0.0, "TKIP": 0.6}.get(cifrado, 0.5)
    
    # Normalización del RSSI [cite: 132]
    if senal >= 80: s_rssi = 1.0 
    elif senal >= 50: s_rssi = 0.5
    else: s_rssi = 0.2 

    score = 10 * (w_auth * s_auth + w_cifrado * s_cifrado + w_rssi * s_rssi)
    return round(score, 2)

def obtener_riesgo(score):
    if score >= 9.0: return "CRÍTICO"
    if score >= 6.0: return "Alto"
    if score >= 3.0: return "Medio"
    return "Bajo"