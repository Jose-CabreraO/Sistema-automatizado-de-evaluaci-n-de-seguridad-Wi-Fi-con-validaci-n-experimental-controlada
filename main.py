import capturador
import evaluador
import detector
import graficador
import reportador

def ejecutar_sistema():
    print("--- [1] INICIANDO CAPTURA DE REDES ---")
    redes_crudas = capturador.escanear()
    
    if not redes_crudas:
        print("[-] Error: No se detectaron redes. Revisa tu adaptador Wi-Fi.")
        return

    print(f"--- [2] ANALIZANDO {len(redes_crudas)} REDES ---")
    sospechosas = detector.buscar_evil_twin(redes_crudas)
    
    # Lista procesada para el reporte
    redes_procesadas = []
    
    for r in redes_crudas:
        # Si la red es sospechosa de Evil Twin, score máximo
        if r['nombre'] in sospechosas:
            score = 10.0
            riesgo = "CRÍTICO (Posible Evil Twin)"
        else:
            score = evaluador.calcular_score(r['auth'], r['cifrado'], r['senal'])
            riesgo = evaluador.obtener_riesgo(score)
            
        redes_procesadas.append({
            "info": r,
            "score": score,
            "riesgo": riesgo,
            "ssid": r['nombre'] # Para el graficador
        })
        
        print(f"Detectada: {r['nombre']} | Score: {score} | Riesgo: {riesgo}")

    print("--- [3] GENERANDO EVIDENCIA VISUAL ---")
    # Generamos el gráfico PNG
    nombre_imagen = "grafico_riesgo_wifi.png"
    graficador.generar_grafico_resultados(redes_procesadas)

    print("--- [4] COMPILANDO REPORTE PDF ---")
    # Generamos el PDF usando los datos y la imagen anterior
    reportador.generar_pdf(redes_procesadas, nombre_imagen)
    
    print("\n[!] PROCESO COMPLETADO CON ÉXITO")
    print("Archivos generados: reporte_seguridad.json, grafico_riesgo_wifi.png, Reporte_Auditoria_WiFi.pdf")

if __name__ == "__main__":
    ejecutar_sistema()