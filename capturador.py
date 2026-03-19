import subprocess
import re

def escanear():
    try:
        comando = "netsh wlan show networks mode=bssid"
        resultado = subprocess.check_output(comando, shell=True).decode('cp850', errors='ignore')
        bloques = resultado.split("SSID")[1:] 
        redes = []
        for b in bloques:
            nombre = re.search(r": (.+)", b)
            auth = re.search(r"Auten.*?:\s*(.+)", b, re.IGNORECASE)
            cifrado = re.search(r"Cif.*?:\s*(.+)", b, re.IGNORECASE)
            senal = re.search(r"Se.*?:\s*(\d+)%", b, re.IGNORECASE)
            bssid = re.search(r"BSSID.*?:\s*([0-9a-fA-F:]+)", b, re.IGNORECASE)
            
            if nombre and auth and cifrado:
                redes.append({
                    "nombre": nombre.group(1).strip(),
                    "auth": auth.group(1).strip(),
                    "cifrado": cifrado.group(1).strip(),
                    "senal": int(senal.group(1)) if senal else 0,
                    "bssid": bssid.group(1).strip() if bssid else "Desconocido"
                })
        return redes
    except Exception as e:
        return []