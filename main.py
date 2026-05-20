#!/usr/bin/env python3
"""
Sistema Automatizado de Evaluación de Seguridad Wi-Fi
Versión corregida y robusta - Febrero 2026
"""

import sys
from datetime import datetime

from capturador import escanear_redes, guardar_json
from evaluador import calcular_wss
from reporte import generar_reporte_pdf


def mostrar_resumen(redes):
    """Muestra resultados con protección contra None"""
    print("\n" + "="*100)
    print(" " * 35 + "RESULTADOS DE EVALUACIÓN WSS")
    print("="*100)
    print(f"{'SSID':<28} {'Auth':<22} {'Cifrado':<18} {'Señal':<7} {'Score':<6} {'Nivel'}")
    print("-"*100)

    for red in redes:
        ssid = red.get('ssid', 'N/A')[:27]
        auth = red.get('autenticacion') or 'N/A'
        cifrado = red.get('cifrado') or 'N/A'
        senal = red.get('senal', 0)

        resultado = red.get('resultado')
        
        if resultado is None:
            print(f"{ssid:<28} {auth:<22} {cifrado:<18} {senal:>3}%   ERROR   (Fallo en WSS)")
            continue

        score = resultado.get('puntaje_final', 0)
        nivel = resultado.get('nivel_riesgo', 'N/A')
        
        print(f"{ssid:<28} {auth[:20]:<22} {cifrado[:17]:<18} {senal:>3}%   {score:5.2f}   {nivel}")


def main():
    print("Sistema Automatizado de Evaluación de Seguridad Wi-Fi")
    print(f"Fecha: {datetime.now().strftime('%d de %B de %Y, %H:%M')}\n")

    try:
        print("Escaneando redes Wi-Fi...")
        redes = escanear_redes()

        if not redes:
            print("No se detectaron redes Wi-Fi.")
            return

        print(f"Se detectaron {len(redes)} redes.\n")

        print("Aplicando modelo Wireless Severity Score (WSS)...")
        for i, red in enumerate(redes):
            try:
                res = calcular_wss(
                    red.get('autenticacion', ''),
                    red.get('cifrado', ''),
                    red.get('senal', 0)
                )
                red['resultado'] = res
            except Exception as e:
                print(f"Error evaluando red {i} ({red.get('ssid', 'Sin SSID')}): {e}")
                red['resultado'] = None

        # Guardar JSON
        guardar_json(redes, "redes_analizadas.json")

        # Mostrar resultados
        mostrar_resumen(redes)

        # Generar PDF
        print("\nGenerando reporte PDF...")
        generar_reporte_pdf(redes, "Reporte_Seguridad_WiFi.pdf")

        print("\n¡Análisis completado!")

    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()