import subprocess
import re
import json
from datetime import datetime

def extraer_campo(texto: str, patron: str, tipo=str):
    """Helper robusto para extraer campos"""
    match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
    if match:
        valor = match.group(1).strip()
        if valor and valor.lower() not in ['n/a', '']:
            try:
                return tipo(valor) if tipo != str else valor
            except:
                return valor if tipo == str else 0
    return None if tipo == str else 0


def escanear_redes() -> list:
    """Captura y parsea la salida de netsh wlan show networks mode=bssid"""
    try:
        comando = "netsh wlan show networks mode=bssid"
        resultado = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT)
        texto = resultado.decode('cp850', errors='replace')

        # Split mejorado
        bloques = re.split(r'(?=SSID \d+ :)', texto)[1:]
        
        redes = []
        for bloque in bloques:
            red = {
                "ssid": extraer_campo(bloque, r"SSID \d+ : (.+?)(?:\r?\n|$)"),
                "bssid": extraer_campo(bloque, r"BSSID \d+ : ([0-9a-fA-F:]+)"),
                "canal": extraer_campo(bloque, r"Canal\s*:\s*(\d+)", int),
                "senal": extraer_campo(bloque, r"Señal\s*:\s*(\d+)%", int),
                "autenticacion": extraer_campo(bloque, r"Autenticación\s*:\s*(.+)"),
                "cifrado": extraer_campo(bloque, r"Cifrado\s*:\s*(.+)"),
                "tipo_red": extraer_campo(bloque, r"Tipo de red\s*:\s*(.+)"),
                "timestamp": datetime.now().isoformat()
            }
            if red.get("ssid"):
                redes.append(red)
        
        return redes
    except Exception as e:
        print(f"Error al escanear: {e}")
        return []


def guardar_json(redes: list, filename="redes_analizadas.json"):
    """JSON profesional para documentación de la tesis"""
    data = {
        "metadata": {
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "autor": "Arturo Rafael Ferreira Cardozo - José Luis Cabrera Oviedo",
            "titulo": "Sistema automatizado de evaluación de seguridad Wi-Fi",
            "universidad": "Universidad del Norte",
            "version": "1.0"
        },
        "estadisticas": {
            "total_redes_detectadas": len(redes),
            "redes_criticas": sum(1 for r in redes if r.get('resultado', {}).get('nivel_riesgo') == "CRÍTICO"),
            "redes_altas": sum(1 for r in redes if r.get('resultado', {}).get('nivel_riesgo') == "ALTO")
        },
        "redes": []
    }

    for red in redes:
        resultado = red.get("resultado") or {}
        red_limpia = {
            "ssid": red.get("ssid"),
            "bssid": red.get("bssid"),
            "canal": red.get("canal"),
            "senal": red.get("senal"),
            "autenticacion": red.get("autenticacion"),
            "cifrado": red.get("cifrado"),
            "wss": {
                "vector": resultado.get("vector_wss"),
                "puntaje_base": resultado.get("puntaje_base"),
                "puntaje_final": resultado.get("puntaje_final"),
                "nivel_riesgo": resultado.get("nivel_riesgo"),
                "detalles": resultado.get("detalles")
            }
        }
        data["redes"].append(red_limpia)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"JSON completo guardado en: {filename}")
    return filename


if __name__ == "__main__":
    redes = escanear_redes()
    print(f"Se detectaron {len(redes)} redes.")
    for r in redes[:3]:
        print(f"SSID: {r.get('ssid')} | Auth: {r.get('autenticacion')} | Cifrado: {r.get('cifrado')} | Señal: {r.get('senal')}%")
    guardar_json(redes)