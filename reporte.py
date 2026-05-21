from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import json

def generar_reporte_pdf(redes_con_resultados: list, filename="Reporte_Seguridad_WiFi.pdf"):
    """Genera reporte PDF profesional"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, spaceAfter=30)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=12)
    
    elements = []
    
    # Cabecera
    elements.append(Paragraph("Sistema Automatizado de Evaluación de Seguridad Wi-Fi", title_style))
    elements.append(Paragraph(f"Reporte Técnico - {datetime.now().strftime('%d de %B de %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Resumen ejecutivo
    elements.append(Paragraph("Resumen Ejecutivo", heading_style))
    total = len(redes_con_resultados)
    criticos = sum(1 for r in redes_con_resultados if r.get('resultado', {}).get('nivel_riesgo') == "CRÍTICO")
    elements.append(Paragraph(f"Se detectaron <b>{total}</b> redes. <b>{criticos}</b> presentan riesgo crítico.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Tabla de resultados
    elements.append(Paragraph("Resultados de Evaluación", heading_style))
    
    data = [["SSID", "Autenticación", "Cifrado", "Señal", "Score", "Nivel"]]
    
    for red in redes_con_resultados:
        res = red.get('resultado') or {}
        auth = red.get('autenticacion') or 'N/A'
        cifrado = red.get('cifrado') or 'N/A'
        senal = red.get('senal', 0)
        score = res.get('puntaje_final', 0)
        nivel = res.get('nivel_riesgo', 'N/A')
        
        data.append([
            str(red.get('ssid', 'N/A'))[:25],
            str(auth)[:20],
            str(cifrado)[:15],
            f"{senal}%",
            f"{score:.2f}",
            nivel
        ])
    
    table = Table(data, colWidths=[120, 100, 90, 50, 50, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Vector WSS de ejemplo
    if redes_con_resultados and redes_con_resultados[0].get('resultado'):
        elements.append(Paragraph("Ejemplo de Vector WSS", heading_style))
        elements.append(Paragraph(f"<i>{redes_con_resultados[0]['resultado'].get('vector_wss', 'N/A')}</i>", styles['Normal']))
    
    doc.build(elements)
    print(f"Reporte PDF generado: {filename}")
    return filename