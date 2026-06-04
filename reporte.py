from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def valor_seguro(valor, defecto="N/A"):
    if valor is None:
        return defecto

    valor = str(valor).strip()

    if valor == "":
        return defecto

    return valor


def texto_pdf(valor, defecto="N/A") -> str:
    return escape(valor_seguro(valor, defecto))


def texto_pdf_corto(valor, limite: int, defecto="N/A") -> str:
    return escape(valor_seguro(valor, defecto)[:limite])


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


def es_red_abierta(red: dict) -> bool:
    auth = valor_seguro(red.get("autenticacion")).upper()
    cifrado = valor_seguro(red.get("cifrado")).upper()

    return "OPEN" in auth or "ABIERTA" in auth or "NONE" in cifrado


def usa_cifrado_obsoleto(red: dict) -> bool:
    cifrado = valor_seguro(red.get("cifrado")).upper()
    return "WEP" in cifrado or "TKIP" in cifrado


def tiene_senal_alta(red: dict) -> bool:
    return int(red.get("senal") or 0) >= 80


def contar_por_nivel(redes: list) -> dict:
    conteo = {}

    for red in redes:
        nivel = obtener_nivel(red.get("resultado") or {})
        conteo[nivel] = conteo.get(nivel, 0) + 1

    return conteo


def contar_ssids(redes: list) -> dict:
    ssid_counts = {}

    for red in redes:
        ssid = valor_seguro(red.get("ssid"))
        ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1

    return ssid_counts


def generar_hallazgos_principales(redes: list) -> list:
    total = len(redes)
    ssids_unicos = len(set(valor_seguro(r.get("ssid")) for r in redes))
    niveles = contar_por_nivel(redes)
    redes_abiertas = sum(1 for r in redes if es_red_abierta(r))
    cifrados_obsoletos = sum(1 for r in redes if usa_cifrado_obsoleto(r))
    senales_altas = sum(1 for r in redes if tiene_senal_alta(r))
    multiples_bssid = sum(1 for cantidad in contar_ssids(redes).values() if cantidad > 1)

    hallazgos = [
        f"Se analizaron {total} observaciones técnicas por BSSID asociadas a {ssids_unicos} SSID únicos.",
        (
            "Distribución de riesgo WSS: "
            f"crítico {niveles.get('CRÍTICO', 0)}, "
            f"alto {niveles.get('ALTO', 0)}, "
            f"medio {niveles.get('MEDIO', 0)} y "
            f"bajo {niveles.get('BAJO', 0)}."
        ),
    ]

    if redes_abiertas:
        hallazgos.append(
            f"Se identificaron {redes_abiertas} observaciones sin autenticación o sin cifrado efectivo."
        )

    if cifrados_obsoletos:
        hallazgos.append(
            f"Se identificaron {cifrados_obsoletos} observaciones con cifrado obsoleto WEP o TKIP."
        )

    if senales_altas:
        hallazgos.append(
            f"Se identificaron {senales_altas} observaciones con señal alta, relevante para la exposición técnica."
        )

    if multiples_bssid:
        hallazgos.append(
            f"Se detectaron {multiples_bssid} SSID asociados a más de un BSSID."
        )

    if len(hallazgos) == 2:
        hallazgos.append(
            "No se observaron configuraciones abiertas, cifrados obsoletos ni señales altas en los datos analizados."
        )

    return hallazgos


def generar_diagnostico_tecnico(redes: list) -> list:
    if not redes:
        return ["No se recibieron observaciones para analizar."]

    return [
        "La evaluación resume parámetros visibles desde Windows y conserva cada BSSID como unidad técnica de observación.",
        "El nivel de riesgo presentado corresponde al resultado WSS ya calculado por el sistema; este módulo no modifica el modelo de puntuación.",
        "Los factores más relevantes para interpretar el reporte son autenticación, cifrado, intensidad de señal y exposición técnica observada.",
    ]


def generar_recomendaciones(redes: list) -> list:
    recomendaciones = []

    hay_wpa2 = any("WPA2" in valor_seguro(r.get("autenticacion")).upper() for r in redes)
    hay_wep_tkip = any(usa_cifrado_obsoleto(r) for r in redes)
    hay_abierta = any(es_red_abierta(r) for r in redes)
    hay_senal_alta = any(tiene_senal_alta(r) for r in redes)
    hay_multiples_bssid = any(cantidad > 1 for cantidad in contar_ssids(redes).values())

    if hay_abierta:
        recomendaciones.append(
            (
                "Prioridad alta",
                "Evitar redes abiertas sin autenticación ni cifrado para entornos institucionales o empresariales.",
            )
        )

    if hay_wep_tkip:
        recomendaciones.append(
            (
                "Prioridad alta",
                "Reemplazar configuraciones que utilicen WEP o TKIP por CCMP/AES o WPA3, según compatibilidad del equipamiento.",
            )
        )

    if hay_senal_alta:
        recomendaciones.append(
            (
                "Prioridad media",
                "Revisar ubicación física y potencia de transmisión cuando la señal exceda el área necesaria.",
            )
        )

    if hay_multiples_bssid:
        recomendaciones.append(
            (
                "Prioridad media",
                "Documentar los BSSID asociados a cada SSID para mejorar la trazabilidad de la infraestructura.",
            )
        )

    if hay_wpa2:
        recomendaciones.append(
            (
                "Prioridad baja",
                "Mantener WPA2-Personal con CCMP/AES como configuración mínima aceptable y evaluar migración a WPA3 si el router lo permite.",
            )
        )

    recomendaciones.append(
        (
            "Prioridad baja",
            "Realizar revisiones periódicas y conservar reportes históricos para comparar cambios de configuración.",
        )
    )

    recomendaciones.append(
        (
            "Prioridad baja",
            "Separar, cuando sea posible, la red administrativa de una red de invitados.",
        )
    )

    return recomendaciones


def crear_tabla_resultados(redes: list) -> Table:
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
            "Nivel",
        ]
    ]

    for red in redes:
        resultado = red.get("resultado") or {}

        data.append(
            [
                texto_pdf_corto(red.get("ssid"), 18),
                texto_pdf_corto(red.get("bssid"), 17),
                texto_pdf_corto(red.get("autenticacion"), 16),
                texto_pdf_corto(red.get("cifrado"), 10),
                f"{texto_pdf(red.get('senal'), '0')}%",
                texto_pdf_corto(red.get("banda"), 10),
                texto_pdf_corto(red.get("canal"), 6, "0"),
                texto_pdf_corto(red.get("tipo_radio"), 10),
                f"{obtener_score(resultado):.2f}",
                texto_pdf(obtener_nivel(resultado)),
            ]
        )

    table = Table(
        data,
        colWidths=[90, 105, 90, 60, 45, 60, 40, 65, 45, 60],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
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
            ]
        )
    )

    return table


def agregar_lista(elements: list, items: list, style):
    for item in items:
        elements.append(Paragraph(f"- {texto_pdf(item)}", style))
        elements.append(Spacer(1, 5))


def agregar_recomendaciones(elements: list, recomendaciones: list, style):
    for prioridad, recomendacion in recomendaciones:
        elements.append(
            Paragraph(
                f"- <b>{texto_pdf(prioridad)}:</b> {texto_pdf(recomendacion)}",
                style,
            )
        )
        elements.append(Spacer(1, 5))


def generar_reporte_pdf(redes_con_resultados: list, filename="Reporte_Seguridad_WiFi.pdf"):
    """
    Genera reporte PDF profesional.
    Incluye análisis por BSSID, hallazgos, recomendaciones y trazabilidad.
    """

    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=35,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=16,
        leading=20,
        spaceAfter=22,
        alignment=1,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=15,
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
    )

    elements = []
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    elements.append(
        Paragraph(
            "Sistema Automatizado de Evaluación de Seguridad Wi-Fi",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            f"Reporte técnico - {fecha_generacion}",
            normal_style,
        )
    )

    elements.append(Spacer(1, 15))

    total_observaciones = len(redes_con_resultados)
    ssids_unicos = len(set(valor_seguro(r.get("ssid")) for r in redes_con_resultados))
    niveles = contar_por_nivel(redes_con_resultados)
    criticos = niveles.get("CRÍTICO", 0)
    altos = niveles.get("ALTO", 0)

    elements.append(Paragraph("Resumen ejecutivo", heading_style))

    resumen = (
        f"Se detectaron <b>{ssids_unicos}</b> SSID únicos y "
        f"<b>{total_observaciones}</b> observaciones técnicas por BSSID. "
        f"<b>{criticos}</b> observaciones presentan nivel crítico y "
        f"<b>{altos}</b> presentan nivel alto. "
        "El análisis se basa en parámetros visibles desde Windows y no ejecuta pruebas activas."
    )

    elements.append(Paragraph(resumen, normal_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Hallazgos principales", heading_style))
    agregar_lista(elements, generar_hallazgos_principales(redes_con_resultados), small_style)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Resultados de evaluación por BSSID", heading_style))
    elements.append(crear_tabla_resultados(redes_con_resultados))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Diagnóstico técnico", heading_style))
    agregar_lista(elements, generar_diagnostico_tecnico(redes_con_resultados), small_style)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Recomendaciones priorizadas", heading_style))
    agregar_recomendaciones(elements, generar_recomendaciones(redes_con_resultados), small_style)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Ejemplo de Vector WSS", heading_style))

    if redes_con_resultados and redes_con_resultados[0].get("resultado"):
        vector = obtener_vector(redes_con_resultados[0]["resultado"])
    else:
        vector = "N/A"

    elements.append(Paragraph(f"<i>{texto_pdf(vector)}</i>", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Trazabilidad técnica", heading_style))
    trazabilidad = [
        f"Fecha y hora de generación: {fecha_generacion}.",
        "Fuente de datos: netsh wlan show networks mode=bssid.",
        "Tipo de análisis: pasivo/no intrusivo.",
    ]
    agregar_lista(elements, trazabilidad, small_style)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Limitaciones del análisis", heading_style))

    elements.append(
        Paragraph(
            "El análisis se basa exclusivamente en parámetros visibles desde el entorno Windows. "
            "El sistema no captura credenciales, no intercepta tráfico privado, no valida contraseñas "
            "y no ejecuta pruebas activas sobre las redes evaluadas. Los resultados representan "
            "indicadores relativos de severidad técnica y no una auditoría integral de seguridad.",
            small_style,
        )
    )

    doc.build(elements)

    print(f"Reporte PDF generado: {filename}")
    return filename
