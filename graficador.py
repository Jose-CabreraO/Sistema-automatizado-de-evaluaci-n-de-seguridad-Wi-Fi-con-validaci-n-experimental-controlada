import matplotlib.pyplot as plt

def generar_grafico_resultados(redes_evaluadas):
    """
    Crea un gráfico de barras comparativo de los scores de riesgo.
    """
    if not redes_evaluadas:
        print("[-] No hay datos para graficar.")
        return

    # 1. Extraemos los datos (usamos 'ssid' y 'score' de la lista procesada)
    nombres = [r['ssid'] for r in redes_evaluadas]
    scores = [r['score'] for r in redes_evaluadas]
    
    # 2. Definimos los colores según el puntaje (Lógica de semáforo)
    colores = []
    for s in scores:
        if s >= 9.0: colores.append('#8B0000') # Rojo Oscuro (Crítico)
        elif s >= 6.0: colores.append('#FF0000') # Rojo (Alto)
        elif s >= 3.0: colores.append('#FFA500') # Naranja (Medio)
        else: colores.append('#008000')           # Verde (Bajo)

    # 3. Configuramos el lienzo
    plt.figure(figsize=(12, 7))
    plt.style.use('ggplot') # Un estilo más limpio y profesional
    
    barras = plt.bar(nombres, scores, color=colores, edgecolor='black')
    
    # 4. Etiquetas y títulos
    plt.title("Evaluación de Severidad Técnica Wi-Fi - Auditoría Local", fontsize=14, fontweight='bold')
    plt.xlabel("Identificador de Red (SSID)", fontsize=12)
    plt.ylabel("Puntaje de Riesgo (0.0 - 10.0)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 10.5) # Dejamos un margen arriba para el texto
    
    # Agregamos el valor numérico exacto sobre cada barra
    for barra in barras:
        yval = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2, yval + 0.2, yval, ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    
    # 5. Guardamos la imagen
    nombre_archivo = "grafico_riesgo_wifi.png"
    plt.savefig(nombre_archivo, dpi=300) # Alta resolución para la impresión de la tesis
    plt.close()
    
    print(f"[+] Evidencia visual generada: {nombre_archivo}")