def calcular_score(auth, cifrado, senal):
    # Pesos basados en la jerarquía del estándar 802.11
    # La autenticación y el cifrado definen la Base del riesgo
    
    # Mapeo de severidad (0 a 1)
    s_auth = {"WPA3-Personal": 0.1, "WPA2-Personal": 0.3, "WPA-Personal": 0.7}.get(auth, 1.0)
    s_cifrado = {"CCMP": 0.1, "TKIP": 0.8}.get(cifrado, 0.9)
    
    # Base Score: Promedio de seguridad técnica
    base_score = (s_auth + s_cifrado) / 2
    
    # Factor de Proximidad (Señal): Si la señal es muy baja, 
    # es más difícil explotar la red, bajamos levemente el riesgo.
    if senal >= 80: f_senal = 1.0    # Muy cerca
    elif senal >= 50: f_senal = 0.8  # Rango medio
    else: f_senal = 0.5             # Muy lejos
    
    final_score = (base_score * f_senal) * 10
    return round(final_score, 2)

def obtener_riesgo(score):
    if score >= 9.0: return "CRÍTICO"
    if score >= 6.0: return "Alto"
    if score >= 3.0: return "Medio"
    return "Bajo"
