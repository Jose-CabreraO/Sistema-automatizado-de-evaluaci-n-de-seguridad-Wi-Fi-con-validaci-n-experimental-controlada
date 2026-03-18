import subprocess
import re
import json
from datetime import datetime

def capturar_redes():
    try:
        comando = "netsh wlan show networks mode=bssid"
        resultado = subprocess.check_output(comando, shell=True).decode('cp850', errors='ignore')
        
        bloques = resultado.split("SSID")[1:] 
        redes_finales = []
        
        for bloque in bloques:
            nombre = re.search(r": (.+)", bloque)
            auth = re.search(r"Auten.*?:\s*(.+)", bloque, re.IGNORECASE)
            cifrado = re.search(r"Cif.*?:\s*(.+)", bloque, re.IGNORECASE)
            
            # CAMBIO 1: Filtro ultra-flexible para la señal (buscamos "Se" y luego el número)
            # Esto ignora si dice Señal, SeÃ±al o Signal
            senal = re.search(r"Se.*?:\s*(\d+)%", bloque, re.IGNORECASE)
            
            # Verificamos que tengamos al menos los datos básicos
            if nombre and auth and cifrado:
                # Si no encuentra la señal, le ponemos 0 por defecto para que no explote
                valor_senal = int(senal.group(1)) if senal else 0
                
                redes_finales.append({
                    "nombre": nombre.group(1).strip(),
                    "auth": auth.group(1).strip(),
                    "cifrado": cifrado.group(1).strip(),
                    "senal": valor_senal
                })
        
        return redes_finales

    except Exception as e:
        print(f"Error técnico: {e}")
        return []

# --- FUNCIONES DE CÁLCULO ---

def calcular_severidad_robusta(auth, cifrado, porcentaje_senal):
    w_auth, w_cifrado, w_rssi = 0.4, 0.4, 0.2 

    # Diccionarios de severidad
    s_auth = {"WPA2-Personal": 0.3, "WPA3-Personal": 0.0}.get(auth, 0.5)
    s_cifrado = {"CCMP": 0.0, "TKIP": 0.6}.get(cifrado, 0.5)

    if porcentaje_senal >= 80: s_rssi = 1.0 
    elif porcentaje_senal >= 50: s_rssi = 0.5
    else: s_rssi = 0.2 

    score = 10 * (w_auth * s_auth + w_cifrado * s_cifrado + w_rssi * s_rssi)
    return round(score, 2)

# --- EJECUCIÓN FINAL ---

print("--- INICIANDO ESCANEO ---")
lista_redes = capturar_redes()

if not lista_redes:
    print("No se encontraron redes. Verifica que el Wi-Fi esté encendido.")
else:
    redes_para_reporte = []
    
    print(f"{'RED':<20} | {'SCORE':<10} | {'RIESGO'}")
    print("-" * 45)
    
    for red in lista_redes:
        # CAMBIO 2: Aquí le pasamos los TRES datos a la función
        valor_score = calcular_severidad_robusta(red['auth'], red['cifrado'], red['senal'])
        
        riesgo = "Bajo"
        if valor_score >= 9.0: riesgo = "CRÍTICO"
        elif valor_score >= 6.0: riesgo = "Alto"
        elif valor_score >= 3.0: riesgo = "Medio"
        
        print(f"{red['nombre']:<20} | {valor_score:<10} | {riesgo}")
        
        redes_para_reporte.append({
            "ssid": red['nombre'],
            "score": valor_score,
            "nivel_riesgo": riesgo,
            "detalles": red
        })

    # (Aquí podrías llamar a tu función de guardar JSON que ya tenías)
    # generar_reporte_json(redes_para_reporte)

print("\n--- FIN ---")