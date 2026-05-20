#!/usr/bin/env python3
"""
Sistema Automatizado de Evaluación de Seguridad Wi-Fi
Versión para Tesis - Febrero 2026
"""

import sys
import os
from datetime import datetime

# Importar módulos
from capturador import escanear_redes, guardar_json
from evaluador import calcular_wss
from reporte import generar_reporte_pdf


def mostrar_resumen(redes):
    """Muestra un resumen por consola de forma clara"""
    print("\n" + "="*90)
    print(" " * 30 + "RESULTADOS DE EVALUACIÓN WSS")
    print("="*90)
    print(f"{'SSID':<30} {'Autenticación':<20} {'Cifrado':<18} {'Señal':<8} {'Score':<6} {'Nivel'}")
    print("-"*90)

    for red in redes:
        res = red.get('resultado', {})
        ssid = red.get('ssid', 'N/A')[:28]
        auth = red.get('autenticacion', 'N/A')[:19]
        cipher = red.get('cifrado', 'N/A')[:17]
        signal = f"{red.get('senal', 0)}%"
        score = f"{res.get('puntaje_final', 0):.2f}"
        nivel = res.get('nivel_riesgo', 'N/A')
        
        print(f"{ssid:<30} {auth:<20} {cipher:<18} {signal:<8} {score:<6} {nivel}")


def main():
    print("Sistema Automatizado de Evaluación de Seguridad Wi-Fi")
    print(f"Fecha: {datetime.now().strftime('%d de %B de %Y, %H:%M')}\n")

    try:
        # 1. Escanear redes
        print("Escaneando redes Wi-Fi disponibles...")
        redes = escanear_redes()

        if not redes:
            print("No se detectaron redes Wi-Fi. Verifica que el Wi-Fi esté activado.")
            sys.exit(1)

        print(f"Se detectaron {len(redes)} redes.\n")

        # 2. Evaluar cada red con el modelo WSS
        print("Aplicando modelo Wireless Severity Score (WSS)...")
        for red in redes:
            resultado = calcular_wss(
                red.get('autenticacion', ''),
                red.get('cifrado', ''),
                red.get('senal', 0)
            )
            red['resultado'] = resultado

        # 3. Guardar datos en JSON
        guardar_json(redes, "redes_analizadas.json")

        # 4. Mostrar resultados en consola
        mostrar_resumen(redes)

        # 5. Generar reporte PDF
        print("\nGenerando reporte PDF...")
        generar_reporte_pdf(redes, "Reporte_Seguridad_WiFi.pdf")

        # Resumen final
        criticos = sum(1 for r in redes if r['resultado']['nivel_riesgo'] == "CRÍTICO")
        print("\n" + "="*90)
        print(f"ANÁLISIS COMPLETADO")
        print(f"   Total de redes: {len(redes)}")
        print(f"   Redes Críticas: {criticos}")
        print(f"   Archivos generados:")
        print(f"     • redes_analizadas.json")
        print(f"     • Reporte_Seguridad_WiFi.pdf")
        print("="*90)

    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()