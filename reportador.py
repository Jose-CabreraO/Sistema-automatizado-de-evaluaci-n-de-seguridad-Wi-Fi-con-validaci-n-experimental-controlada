from fpdf import FPDF
from datetime import datetime

class ReporteSeguridad(FPDF):
    def header(self):
        # Configuración del encabezado profesional
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "UNIVERSIDAD DEL NORTE - FACULTAD DE INGENIERÍA", ln=True, align="C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, "Sistema Automatizado de Evaluación Wi-Fi", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()} | Generado por José Cabrera", align="C")

def generar_pdf(redes_evaluadas, nombre_grafico):
    pdf = ReporteSeguridad()
    pdf.add_page()
    
    # 1. Introducción
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Reporte de Evaluación de Riesgo Técnico", ln=True)
    pdf.set_font("Arial", "", 11)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f"Fecha de escaneo: {fecha}", ln=True)
    pdf.ln(5)

    # 2. Insertar el Gráfico (Módulo de Visualización)
    if nombre_grafico:
        pdf.image(nombre_grafico, x=10, y=None, w=180)
        pdf.ln(10)

    # 3. Tabla de Resultados
    pdf.set_font("Arial", "B", 11)
    pdf.cell(80, 10, "Nombre de Red (SSID)", 1)
    pdf.cell(40, 10, "Score (0-10)", 1)
    pdf.cell(40, 10, "Riesgo", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for red in redes_evaluadas:
        pdf.cell(80, 10, red['info']['nombre'], 1)
        pdf.cell(40, 10, str(red['score']), 1)
        pdf.cell(40, 10, red['riesgo'], 1)
        pdf.ln()

    # Guardar el archivo final
    pdf.output("Reporte_Auditoria_WiFi.pdf")
    print("\n[+] PDF generado: Reporte_Auditoria_WiFi.pdf")