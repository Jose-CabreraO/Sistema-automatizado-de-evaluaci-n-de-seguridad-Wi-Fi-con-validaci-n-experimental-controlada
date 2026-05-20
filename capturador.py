import subprocess
import re
import json
from datetime import datetime

def escanear_redes() -> list:
    """Captura y parsea la salida de netsh wlan show networks mode=bssid"""
    try:
        comando = "netsh wlan show networks mode=bssid"
        resultado = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT)
        texto = resultado.decode('cp850', errors='ignore')  # Windows suele usar cp850
        
        # Dividir por bloques de SSID
        bloques = re.split(r'(?=SSID \d+ :)', texto)[1:]  # Mejor split que el anterior
        
        redes = []
        for bloque in bloques:
            red = {
                "ssid": extraer_campo(bloque, r"SSID \d+ : (.+?)(?:\r?\n|$)"),
                "bssid": extraer_campo(bloque, r"BSSID \d+ : ([0-9a-fA-F:]+)"),
                "canal": extraer_campo(bloque, r"Canal\s*:\s*(\d+)", tipo=int),
                "senal": extraer_campo(bloque, r"Señal\s*:\s*(\d+)%", tipo=int),
                "autenticacion": extraer_campo(bloque, r"Autenticación\s*:\s*(.+)"),
                "cifrado": extraer_campo(bloque, r"Cifrado\s*:\s*(.+)"),
                "tipo_red": extraer_campo(bloque, r"Tipo de red\s*:\s*(.+)"),
                "timestamp": datetime.now().isoformat()
            }
            if red["ssid"]:
                redes.append(red)
        
        return redes
    except Exception as e:
        print(f"Error al escanear: {e}")
        return []


def extraer_campo(texto: str, patron: str, tipo=str):
    """Helper para extraer campos con regex de forma segura"""
    match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
    if match:
        valor = match.group(1).strip()
        return tipo(valor) if tipo != str else valor
    return None if tipo == str else 0


def guardar_json(redes: list, filename="redes_capturadas.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_redes": len(redes),
            "redes": redes
        }, f, indent=2, ensure_ascii=False)
    print(f"Datos guardados en {filename}")
    return filename


if __name__ == "__main__":
    redes = escanear_redes()
    print(f"Se detectaron {len(redes)} redes.")
    for r in redes[:3]:  # Muestra las primeras 3
        print(f"SSID: {r['ssid']} | Auth: {r['autenticacion']} | Cifrado: {r['cifrado']} | Señal: {r['senal']}%")
    guardar_json(redes)