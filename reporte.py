from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime


def valor_seguro(valor, defecto="N/A"):
    if valor is None:
        return defecto

    valor = str(valor).strip()

    if valor == "":
        return defecto

    return valor


def numero_seguro(valor, defecto=0.0):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return defecto


def obtener_nivel(resultado: dict) -> str:
    if not resultado:
        return "N/A"

    return (
        resultado.get("nivel_riesgo")
        or resultado.get("nivel")
        or resultado.get("clasificacion")
        or "N/A"
    )


def obtener_score(resultado: dict) -> float:
    if not resultado:
        return 0.0

    return numero_seguro(
        resultado.get("puntaje_final")
        or resultado.get("score")
        or resultado.get("puntaje")
        or 0.0
    )


def obtener_vector(resultado: dict) -> str:
    if not resultado:
        return "N/A"

    return resultado.get("vector_wss") or "N/A"


def generar_comentario_tecnico(red: dict) -> str:
    ssid = valor_seguro(red.get("ssid"))
    auth = valor_seguro(red.get("autenticacion"))
    cifrado = valor_seguro(red.get("cifrado"))
    senal = int(red.get("senal") or 0)
    banda = valor_seguro(red.get("banda"))
    canal = valor_seguro(red.get("canal"))
    bssid = valor_seguro(red.get("bssid"))
    resultado = red.get("resultado") or {}
    nivel = obtener_nivel(resultado)
    score = obtener_score(resultado)

    comentarios = []

    comentarios.append(
        f"La observación correspondiente al SSID {ssid}, BSSID {bssid}, "
        f"opera en la banda {banda}, canal {canal}, con autenticación {auth} "
        f"y cifrado {cifrado}."
    )

    if "WPA3" in auth.upper():
        comentarios.append(
            "La autenticación WPA3 representa una configuración robusta dentro del modelo WSS."
        )
    elif "WPA2" in auth.upper() and ("CCMP" in cifrado.upper() or "AES" in cifrado.upper()):
        comentarios.append(
            "La configuración WPA2-Personal con CCMP/AES se considera aceptable; "
            "sin embargo, se recomienda migrar a WPA3 si el equipamiento lo permite."
        )
    elif "WEP" in cifrado.upper() or "TKIP" in cifrado.upper():
        comentarios.append(
            "El cifrado detectado se considera obsoleto y debería reemplazarse por CCMP/AES o WPA3."
        )
    elif "OPEN" in auth.upper() or "ABIERTA" in auth.upper() or "NONE" in cifrado.upper():
        comentarios.append(
            "La red no presenta mecanismos adecuados de autenticación o cifrado, "
            "por lo que requiere revisión inmediata."
        )

    if senal >= 80:
        comentarios.append(
            "La intensidad de señal es alta. Esto puede representar buena cobertura interna, "
            "pero también mayor exposición técnica si la señal excede el perímetro físico de la organización."
        )
    elif senal >= 50:
        comentarios.append(
            "La intensidad de señal es media, lo que representa una exposición técnica moderada."
        )
    else:
        comentarios.append(
            "La intensidad de señal es baja, lo que reduce la accesibilidad técnica desde la ubicación evaluada."
        )

    comentarios.append(
        f"El puntaje WSS calculado es {score:.2f}, con clasificación {nivel}."
    )

    return " ".join(comentarios)


def generar_recomendaciones(redes: list) -> list:
    recomendaciones = []

    hay_wpa2 = any("WPA2" in valor_seguro(r.get("autenticacion")).upper() for r in redes)
    hay_wep_tkip = any(
        "WEP" in valor_seguro(r.get("cifrado")).upper()
        or "TKIP" in valor_seguro(r.get("cifrado")).upper()
        for r in redes
    )
    hay_abierta = any(
        "OPEN" in valor_seguro(r.get("autenticacion")).upper()
        or "ABIERTA" in valor_seguro(r.get("autenticacion")).upper()
        or "NONE" in valor_seguro(r.get("cifrado")).upper()
        for r in redes
    )
    hay_senal_alta = any(int(r.get("senal") or 0) >= 80 for r in redes)

    ssid_counts = {}
    for r in redes:
        ssid = valor_seguro(r.get("ssid"))
        ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1

    hay_multiples_bssid = any(cantidad > 1 for cantidad in ssid_counts.values())

    if hay_wpa2:
        recomendaciones.append(
            "Mantener WPA2-Personal con CCMP/AES como configuración mínima aceptable y evaluar migración a WPA3 si el router lo permite."
        )

    if hay_wep_tkip:
        recomendaciones.append(
            "Reemplazar configuraciones que utilicen WEP o TKIP, debido a que son mecanismos obsoletos."
        )

    if hay_abierta:
        recomendaciones.append(
            "Evitar redes abiertas sin autenticación ni cifrado para entornos empresariales."
        )

    if hay_senal_alta:
        recomendaciones.append(
            "Revisar la ubicación física del router o potencia de transmisión si la señal se extiende fuera del área necesaria."
        )

    if hay_multiples_bssid:
        recomendaciones.append(
            "Documentar los BSSID asociados a cada SSID para diferenciar infraestructura legítima de posibles anomalías."
        )

    recomendaciones.append(
        "Realizar revisiones periódicas del estado de la red Wi-Fi y conservar reportes históricos para comparar cambios de configuración."
    )

    recomendaciones.append(
        "Separar, cuando sea posible, la red administrativa de una red de invitados."
    )

    return recomendaciones


def generar_reporte_pdf(redes_con_resultados: list, filename="Reporte_Seguridad_WiFi.pdf"):
    """
    Genera reporte PDF profesional.
    Incluye análisis por BSSID, diagnóstico técnico y recomendaciones.
    """

    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=16,
        leading=20,
        spaceAfter=22,
        alignment=1
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=15,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=9,
        leading=12
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )

    elements = []

    elements.append(
        Paragraph(
            "Sistema Automatizado de Evaluación de Seguridad Wi-Fi",
            title_style
        )
    )

    elements.append(
        Paragraph(
            f"Reporte Técnico - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            normal_style
        )
    )

    elements.append(Spacer(1, 15))

    total_observaciones = len(redes_con_resultados)
    ssids_unicos = len(set(r.get("ssid", "N/A") for r in redes_con_resultados))

    criticos = sum(
        1 for r in redes_con_resultados
        if obtener_nivel(r.get("resultado") or {}) == "CRÍTICO"
    )

    altos = sum(
        1 for r in redes_con_resultados
        if obtener_nivel(r.get("resultado") or {}) == "ALTO"
    )

    elements.append(Paragraph("Resumen Ejecutivo", heading_style))

    resumen = (
        f"Se detectaron <b>{ssids_unicos}</b> SSID únicos y "
        f"<b>{total_observaciones}</b> observaciones técnicas por BSSID. "
        f"<b>{criticos}</b> observaciones presentan nivel crítico y "
        f"<b>{altos}</b> presentan nivel alto. "
        f"El análisis se basa en parámetros visibles desde Windows y no ejecuta pruebas activas."
    )

    elements.append(Paragraph(resumen, normal_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Resultados de Evaluación por BSSID", heading_style))

    data = [
        [
            "SSID",
            "BSSID",
            "Auth",
            "Cifrado",
            "Señal",
            "Banda",
            "Canal",
            "Radio",
            "Score",
            "Nivel"
        ]
    ]

    for red in redes_con_resultados:
        resultado = red.get("resultado") or {}

        data.append([
            valor_seguro(red.get("ssid"))[:18],
            valor_seguro(red.get("bssid"))[:17],
            valor_seguro(red.get("autenticacion"))[:16],
            valor_seguro(red.get("cifrado"))[:10],
            f"{valor_seguro(red.get('senal'), '0')}%",
            valor_seguro(red.get("banda"))[:10],
            valor_seguro(red.get("canal"), "0"),
            valor_seguro(red.get("tipo_radio"))[:10],
            f"{obtener_score(resultado):.2f}",
            valor_seguro(obtener_nivel(resultado))
        ])

    table = Table(
        data,
        colWidths=[90, 105, 90, 60, 45, 60, 40, 65, 45, 60],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("FONTSIZE", (0, 1), (-1, -1), 6.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Diagnóstico Técnico", heading_style))

    for red in redes_con_resultados:
        comentario = generar_comentario_tecnico(red)
        elements.append(Paragraph(f"• {comentario}", small_style))
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Recomendaciones Generales", heading_style))

    recomendaciones = generar_recomendaciones(redes_con_resultados)

    for rec in recomendaciones:
        elements.append(Paragraph(f"• {rec}", small_style))
        elements.append(Spacer(1, 5))

    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Ejemplo de Vector WSS", heading_style))

    if redes_con_resultados and redes_con_resultados[0].get("resultado"):
        vector = obtener_vector(redes_con_resultados[0]["resultado"])
    else:
        vector = "N/A"

    elements.append(Paragraph(f"<i>{valor_seguro(vector)}</i>", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Limitaciones del análisis", heading_style))

    elements.append(
        Paragraph(
            "El análisis se basa exclusivamente en parámetros visibles desde el entorno Windows. "
            "El sistema no captura credenciales, no intercepta tráfico privado, no valida contraseñas "
            "y no ejecuta pruebas activas sobre las redes evaluadas. Los resultados representan "
            "indicadores relativos de severidad técnica y no una auditoría integral de seguridad.",
            small_style
        )
    )

    doc.build(elements)

    print(f"Reporte PDF generado: {filename}")
    return filename