def mapear_severidad_auth(auth: str) -> float:
    """Según tabla de la tesis"""
    auth = auth.upper() if auth else ""
    if "WPA3" in auth:
        return 0.1
    elif "WPA2" in auth:
        return 0.3
    elif "WPA" in auth or "WEP" in auth:
        return 0.7
    else:  # Open o desconocido
        return 1.0


def mapear_severidad_cifrado(cifrado: str) -> float:
    cifrado = cifrado.upper() if cifrado else ""
    if "CCMP" in cifrado or "AES" in cifrado:
        return 0.1
    elif "TKIP" in cifrado:
        return 0.8
    elif "WEP" in cifrado:
        return 0.9
    else:
        return 1.0


def mapear_factor_explotabilidad(senal: int) -> float:
    """Factor según RSSI / señal % (tesis)"""
    if senal >= 80:
        return 1.0
    elif senal >= 50:
        return 0.8
    else:
        return 0.5


def calcular_wss(auth: str, cifrado: str, senal: int) -> dict:
    """Calcula Base Score + Score Final + Vector WSS"""
    s_auth = mapear_severidad_auth(auth)
    s_cifrado = mapear_severidad_cifrado(cifrado)
    
    # Puntaje Base (tesis ecuación 1)
    pb = (s_auth + s_cifrado) / 2
    
    # Factor de Explotabilidad
    f_exp = mapear_factor_explotabilidad(senal)
    
    # Score Final (tesis ecuación 2)
    score_final = round(pb * f_exp * 10, 2)
    
    # Vector WSS (formato propuesto en tesis)
    vector_wss = f"WSS:1.0/AU:{s_auth:.1f}/EN:{s_cifrado:.1f}/EX:{f_exp:.1f}"
    
    return {
        "puntaje_base": round(pb * 10, 2),
        "puntaje_final": score_final,
        "vector_wss": vector_wss,
        "nivel_riesgo": clasificar_riesgo(score_final),
        "detalles": {
            "severidad_auth": s_auth,
            "severidad_cifrado": s_cifrado,
            "factor_explotabilidad": f_exp
        }
    }


def clasificar_riesgo(score: float) -> str:
    if score >= 9.0:
        return "CRÍTICO"
    elif score >= 6.0:
        return "ALTO"
    elif score >= 3.0:
        return "MEDIO"
    else:
        return "BAJO"