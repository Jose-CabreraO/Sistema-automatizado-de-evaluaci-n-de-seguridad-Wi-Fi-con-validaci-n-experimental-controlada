import subprocess
import re
import json
import unicodedata
import locale
from datetime import datetime


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto para comparar líneas de netsh aunque existan:
    - tildes
    - errores de codificación
    - Windows en español o inglés
    """
    if texto is None:
        return ""

    reemplazos = {
        "¢": "o",
        "¤": "n",
        "Ã³": "o",
        "Ã±": "n",
        "Ã©": "e",
        "Ã¡": "a",
        "Ã­": "i",
        "Ãº": "u",
        "Â": "",
        "�": "",
    }

    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")

    return texto.lower().strip()


def extraer_valor(linea: str) -> str:
    """
    Extrae el valor después de ':'.
    """
    partes = linea.split(":", 1)

    if len(partes) == 2:
        valor = partes[1].strip()
        return valor if valor else "N/A"

    return "N/A"


def extraer_entero(linea: str) -> int:
    """
    Extrae el primer número encontrado en una línea.
    """
    match = re.search(r"(\d+)", linea)
    if match:
        return int(match.group(1))
    return 0


def decodificar_salida(resultado: bytes) -> str:
    """
    Prueba varias codificaciones comunes de Windows y selecciona
    la que mejor reconoce las palabras clave esperadas.
    """

    posibles_codificaciones = [
        locale.getpreferredencoding(False),
        "utf-8",
        "cp850",
        "cp437",
        "latin-1",
    ]

    mejor_texto = ""
    mejor_puntaje = -1

    for encoding in posibles_codificaciones:
        try:
            texto = resultado.decode(encoding, errors="replace")
            texto_norm = normalizar_texto(texto)

            puntaje = 0
            palabras_clave = [
                "ssid",
                "bssid",
                "cifrado",
                "encryption",
                "autentic",
                "authentication",
                "senal",
                "signal",
                "canal",
                "channel",
                "banda",
                "tipo de radio",
            ]

            for palabra in palabras_clave:
                if palabra in texto_norm:
                    puntaje += 1

            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_texto = texto

        except Exception:
            continue

    return mejor_texto


def guardar_debug_netsh(texto: str, filename="netsh_debug.txt"):
    """
    Guarda la salida completa de netsh para evidencia y depuración.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"Salida netsh guardada para depuración en: {filename}")


def es_linea_ssid(linea_norm: str) -> bool:
    return re.match(r"ssid\s+\d+\s*:", linea_norm) is not None


def es_linea_bssid(linea_norm: str) -> bool:
    return re.match(r"bssid\s+\d+\s*:", linea_norm) is not None


def crear_observacion(base_red: dict, bssid: str) -> dict:
    """
    Crea una observación técnica por cada BSSID detectado.
    Hereda los datos generales del SSID.
    """
    return {
        "ssid": base_red.get("ssid", "N/A"),
        "tipo_red": base_red.get("tipo_red", "N/A"),
        "autenticacion": base_red.get("autenticacion", "N/A"),
        "cifrado": base_red.get("cifrado", "N/A"),
        "bssid": bssid,
        "senal": 0,
        "canal": 0,
        "banda": "N/A",
        "tipo_radio": "N/A",
        "timestamp": datetime.now().isoformat()
    }


def escanear_redes() -> list:
    """
    Captura y parsea la salida de:
    netsh wlan show networks mode=bssid

    Retorna una lista donde cada BSSID es una observación técnica independiente.
    """

    try:
        comando = "netsh wlan show networks mode=bssid"

        resultado = subprocess.check_output(
            comando,
            shell=True,
            stderr=subprocess.STDOUT
        )

        texto = decodificar_salida(resultado)
        guardar_debug_netsh(texto)

        observaciones = []

        base_red = {
            "ssid": "N/A",
            "tipo_red": "N/A",
            "autenticacion": "N/A",
            "cifrado": "N/A"
        }

        observacion_actual = None

        for linea in texto.splitlines():
            linea_original = linea.strip()
            linea_norm = normalizar_texto(linea_original)

            if not linea_original:
                continue

            # Nueva red SSID
            if es_linea_ssid(linea_norm):
                if observacion_actual:
                    observaciones.append(observacion_actual)
                    observacion_actual = None

                base_red = {
                    "ssid": extraer_valor(linea_original),
                    "tipo_red": "N/A",
                    "autenticacion": "N/A",
                    "cifrado": "N/A"
                }
                continue

            # Tipo de red
            if "tipo de red" in linea_norm or "network type" in linea_norm:
                base_red["tipo_red"] = extraer_valor(linea_original)

                if observacion_actual:
                    observacion_actual["tipo_red"] = base_red["tipo_red"]

                continue

            # Autenticación
            if "autentic" in linea_norm or "authentication" in linea_norm:
                base_red["autenticacion"] = extraer_valor(linea_original)

                if observacion_actual:
                    observacion_actual["autenticacion"] = base_red["autenticacion"]

                continue

            # Cifrado
            if "cifrado" in linea_norm or "encryption" in linea_norm:
                base_red["cifrado"] = extraer_valor(linea_original)

                if observacion_actual:
                    observacion_actual["cifrado"] = base_red["cifrado"]

                continue

            # Nuevo BSSID dentro del mismo SSID
            if es_linea_bssid(linea_norm):
                if observacion_actual:
                    observaciones.append(observacion_actual)

                observacion_actual = crear_observacion(
                    base_red=base_red,
                    bssid=extraer_valor(linea_original)
                )
                continue

            if observacion_actual is None:
                continue

            # Señal
            if "senal" in linea_norm or "signal" in linea_norm:
                observacion_actual["senal"] = extraer_entero(linea_original)
                continue

            # Tipo de radio
            if "tipo de radio" in linea_norm or "radio type" in linea_norm:
                observacion_actual["tipo_radio"] = extraer_valor(linea_original)
                continue

            # Banda
            if "banda" in linea_norm or "band" in linea_norm:
                observacion_actual["banda"] = limpiar_valor_visible(extraer_valor(linea_original))
                continue

            # Canal
            if "canal" in linea_norm or "channel" in linea_norm:
                observacion_actual["canal"] = extraer_entero(linea_original)
                continue

        if observacion_actual:
            observaciones.append(observacion_actual)

        return observaciones

    except subprocess.CalledProcessError as e:
        print("Error ejecutando netsh.")

        try:
            print(decodificar_salida(e.output))
        except Exception:
            print(e)

        return []

    except Exception as e:
        print(f"Error al escanear redes: {e}")
        return []

def limpiar_valor_visible(valor: str) -> str:
    if valor is None:
        return "N/A"

    valor = str(valor).strip()

    reemplazos = {
        "Â": "",
        "\xa0": " ",
        "Ã³": "ó",
        "Ã±": "ñ",
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ãº": "ú",
    }

    for malo, bueno in reemplazos.items():
        valor = valor.replace(malo, bueno)

    return " ".join(valor.split())

def guardar_json(redes: list, filename="redes_analizadas.json"):
    """
    Guarda el resultado de captura en JSON.
    Mantiene compatibilidad con el resto del proyecto.
    """

    data = {
        "metadata": {
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "autor": "Arturo Rafael Ferreira Cardozo - José Luis Cabrera Oviedo",
            "titulo": "Sistema automatizado de evaluación de seguridad Wi-Fi",
            "universidad": "Universidad del Norte",
            "version": "1.0"
        },
        "estadisticas": {
            "total_observaciones_bssid": len(redes),
            "ssids_unicos": len(set(r.get("ssid", "N/A") for r in redes)),
            "redes_criticas": sum(
                1 for r in redes
                if r.get("resultado", {}).get("nivel_riesgo") == "CRÍTICO"
                or r.get("resultado", {}).get("nivel") == "CRÍTICO"
            ),
            "redes_altas": sum(
                1 for r in redes
                if r.get("resultado", {}).get("nivel_riesgo") == "ALTO"
                or r.get("resultado", {}).get("nivel") == "ALTO"
            )
        },
        "redes": []
    }

    for red in redes:
        resultado = red.get("resultado") or {}

        red_limpia = {
            "ssid": red.get("ssid", "N/A"),
            "bssid": red.get("bssid", "N/A"),
            "canal": red.get("canal", 0),
            "senal": red.get("senal", 0),
            "banda": red.get("banda", "N/A"),
            "tipo_radio": red.get("tipo_radio", "N/A"),
            "autenticacion": red.get("autenticacion", "N/A"),
            "cifrado": red.get("cifrado", "N/A"),
            "tipo_red": red.get("tipo_red", "N/A"),
            "timestamp": red.get("timestamp", datetime.now().isoformat()),
            "wss": {
                "vector": resultado.get("vector_wss"),
                "puntaje_base": resultado.get("puntaje_base"),
                "puntaje_final": resultado.get("puntaje_final"),
                "nivel_riesgo": resultado.get("nivel_riesgo") or resultado.get("nivel"),
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

    print(f"Se detectaron {len(redes)} observaciones BSSID.")

    for r in redes:
        print(
            f"SSID: {r.get('ssid')} | "
            f"BSSID: {r.get('bssid')} | "
            f"Auth: {r.get('autenticacion')} | "
            f"Cifrado: {r.get('cifrado')} | "
            f"Señal: {r.get('senal')}% | "
            f"Banda: {r.get('banda')} | "
            f"Radio: {r.get('tipo_radio')} | "
            f"Canal: {r.get('canal')}"
        )

    guardar_json(redes)